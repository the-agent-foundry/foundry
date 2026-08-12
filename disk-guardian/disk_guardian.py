#!/usr/bin/env python3
"""Disk Guardian Community: fail-closed macOS/APFS pressure relief.

The engine deletes only exact, registered regenerable cache roots or exact
producer-retention contract candidates. It never asks a model what to delete.
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import fcntl
import hashlib
import json
import math
import os
import plistlib
import pwd
import re
import stat
import subprocess
import sys
import tempfile
import time
from pathlib import Path

GIB = 1024 ** 3
DATA_VOLUME = Path("/System/Volumes/Data")
POLICY_SCHEMA = "disk-guardian-community-policy/v1"
CONTRACT_SCHEMA = "disk-guardian-community-retention/v1"
AUTHORITY_SCHEMA = "disk-guardian-community-authority/v1"
RECEIPT_SCHEMA = "disk-guardian-community-receipt/v1"
SEVERITIES = ("GREEN", "YELLOW", "ORANGE", "RED", "CRITICAL")
MAX_POLICY_BYTES = 128 * 1024
MAX_CONTRACTS = 64
MAX_CONTRACT_BYTES = 64 * 1024
MAX_TREE_NODES = 200_000
MAX_TREE_DEPTH = 64
MAX_TREE_METADATA_BYTES = 64 * 1024 * 1024
MAX_RECEIPTS = 500
RECEIPT_MAX_AGE_SECONDS = 90 * 86400

CACHE_ROOTS = {
    "uv_cache": (".cache/uv", "Library/Caches/uv"),
    "pip_cache": ("Library/Caches/pip",),
    "npm_cache": (".npm/_cacache",),
    "homebrew_download_cache": ("Library/Caches/Homebrew/downloads",),
}
CACHE_PROCESS_TOKENS = {
    "uv_cache": ("uv", "uvx"),
    "pip_cache": ("pip",),
    "npm_cache": ("npm", "npx"),
    "homebrew_download_cache": ("brew",),
}
CONTRACT_ROOTS = {
    "worktree": ".hermes/worktrees",
    "backup": ".hermes/backups",
    "staging_qa": ".hermes/staging",
    "retired_runtime_cache": ".hermes/runtime-retired",
}
CONTRACT_PROOFS = {
    "worktree": {
        "true": {"registered_expected_repo", "clean", "reachable", "merged", "terminal"},
        "false": {"active", "locked", "quarantined", "current"},
    },
    "backup": {
        "true": {"archive_integrity", "restore_verified", "runtime_healthy", "superseded", "retention_floor_satisfied"},
        "false": {"latest_good"},
    },
    "staging_qa": {
        "true": {"terminal", "lease_expired", "promoted_or_failed", "evidence_retained"},
        "false": {"retained_failure_workspace"},
    },
    "retired_runtime_cache": {
        "true": {"retired", "replacement_healthy", "regenerable"},
        "false": {"rollback_reference"},
    },
}
NEVER_DELETE_RELATIVE_PREFIXES = (
    ".hermes/sessions", ".hermes/session", ".hermes/db", ".hermes/databases",
    ".hermes/vault", ".hermes/memory", ".hermes/models", ".hermes/containers",
)
POLICY_KEYS = {
    "schema", "state_directory", "thresholds", "cache_classes", "retention_contracts",
    "limits", "scheduled_healthy_stdout",
}
THRESHOLD_KEYS = {
    "yellow_free_percent", "orange_free_percent", "red_free_percent", "critical_free_percent",
    "target_free_percent", "yellow_free_bytes", "orange_free_bytes", "red_free_bytes",
    "critical_free_bytes", "target_free_bytes",
}
LIMIT_KEYS = {"max_delete_bytes", "max_candidate_bytes", "max_runtime_seconds"}
RETENTION_KEYS = {"enabled", "directory", "max_contract_age_seconds"}


class GuardianError(RuntimeError):
    pass


class AlreadyRunning(GuardianError):
    pass


class PartialDeletion(GuardianError):
    def __init__(self, reason, logical_deleted_bytes):
        super().__init__(reason)
        self.logical_deleted_bytes = logical_deleted_bytes


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def sha256_bytes(value):
    return hashlib.sha256(value).hexdigest()


def fsync_directory(path):
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0))
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def utc_now(timestamp=None):
    value = time.time() if timestamp is None else float(timestamp)
    return dt.datetime.fromtimestamp(value, tz=dt.timezone.utc).isoformat().replace("+00:00", "Z")


def passwd_home():
    return Path(pwd.getpwuid(os.getuid()).pw_dir).resolve()


def require_closed_keys(mapping, allowed, label):
    if not isinstance(mapping, dict):
        raise GuardianError(label + "_not_object")
    unknown = set(mapping) - set(allowed)
    if unknown:
        raise GuardianError(label + "_unknown_keys")


def require_int(value, label, minimum=0, maximum=None, allow_none=False):
    if value is None and allow_none:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise GuardianError(label + "_not_integer")
    if value < minimum or (maximum is not None and value > maximum):
        raise GuardianError(label + "_out_of_range")
    return value


def require_number(value, label, minimum, maximum):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise GuardianError(label + "_not_number")
    value = float(value)
    if value < minimum or value > maximum:
        raise GuardianError(label + "_out_of_range")
    return value


def load_json_regular(path, max_bytes, expected_uid=None, required_mode=None):
    path = Path(path)
    try:
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    except OSError as exc:
        raise GuardianError("json_unreadable") from exc
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode):
            raise GuardianError("json_not_regular")
        if expected_uid is not None and before.st_uid != expected_uid:
            raise GuardianError("json_wrong_owner")
        if required_mode is not None and stat.S_IMODE(before.st_mode) != required_mode:
            raise GuardianError("json_wrong_mode")
        if before.st_size > max_bytes:
            raise GuardianError("json_too_large")
        chunks = []
        remaining = max_bytes + 1
        while remaining:
            chunk = os.read(fd, min(64 * 1024, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        payload = b"".join(chunks)
        if len(payload) > max_bytes:
            raise GuardianError("json_too_large")
        value = json.loads(payload)
        after = os.fstat(fd)
    except GuardianError:
        raise
    except (OSError, ValueError) as exc:
        raise GuardianError("json_invalid") from exc
    finally:
        os.close(fd)
    if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns):
        raise GuardianError("json_changed_during_read")
    return value, payload, before


def default_policy():
    return {
        "schema": POLICY_SCHEMA,
        "state_directory": ".disk-guardian",
        "thresholds": {
            "yellow_free_percent": 15.0,
            "orange_free_percent": 10.0,
            "red_free_percent": 7.0,
            "critical_free_percent": 4.0,
            "target_free_percent": 20.0,
            "yellow_free_bytes": None,
            "orange_free_bytes": None,
            "red_free_bytes": None,
            "critical_free_bytes": None,
            "target_free_bytes": None,
        },
        "cache_classes": {name: True for name in CACHE_ROOTS},
        "retention_contracts": {
            "enabled": True,
            "directory": ".hermes/state/disk-guardian-community/contracts",
            "max_contract_age_seconds": 86400,
        },
        "limits": {
            "max_delete_bytes": 50 * GIB,
            "max_candidate_bytes": 20 * GIB,
            "max_runtime_seconds": 2700,
        },
        "scheduled_healthy_stdout": "",
    }


def validate_policy(policy):
    require_closed_keys(policy, POLICY_KEYS, "policy")
    if policy.get("schema") != POLICY_SCHEMA:
        raise GuardianError("policy_schema_invalid")
    state_dir = policy.get("state_directory")
    if not isinstance(state_dir, str) or not state_dir or state_dir.startswith("/") or ".." in Path(state_dir).parts:
        raise GuardianError("policy_state_directory_invalid")
    thresholds = policy.get("thresholds")
    require_closed_keys(thresholds, THRESHOLD_KEYS, "thresholds")
    percents = {}
    for key in ("yellow_free_percent", "orange_free_percent", "red_free_percent", "critical_free_percent", "target_free_percent"):
        percents[key] = require_number(thresholds.get(key), key, 0.5, 95.0)
    if not (
        percents["critical_free_percent"] < percents["red_free_percent"] <
        percents["orange_free_percent"] < percents["yellow_free_percent"] <
        percents["target_free_percent"]
    ):
        raise GuardianError("threshold_percent_order_invalid")
    for key in ("yellow_free_bytes", "orange_free_bytes", "red_free_bytes", "critical_free_bytes", "target_free_bytes"):
        require_int(thresholds.get(key), key, GIB, 10_000 * GIB, allow_none=True)
    byte_values = [thresholds.get(key) for key in (
        "critical_free_bytes", "red_free_bytes", "orange_free_bytes", "yellow_free_bytes", "target_free_bytes"
    )]
    if any(value is not None for value in byte_values):
        if any(value is None for value in byte_values) or byte_values != sorted(byte_values) or len(set(byte_values)) != len(byte_values):
            raise GuardianError("threshold_byte_order_invalid")
    cache_classes = policy.get("cache_classes")
    require_closed_keys(cache_classes, CACHE_ROOTS, "cache_classes")
    if any(type(value) is not bool for value in cache_classes.values()) or set(cache_classes) != set(CACHE_ROOTS):
        raise GuardianError("cache_classes_invalid")
    retention = policy.get("retention_contracts")
    require_closed_keys(retention, RETENTION_KEYS, "retention_contracts")
    if type(retention.get("enabled")) is not bool:
        raise GuardianError("retention_enabled_invalid")
    directory = retention.get("directory")
    if not isinstance(directory, str) or not directory or directory.startswith("/") or ".." in Path(directory).parts:
        raise GuardianError("retention_directory_invalid")
    require_int(retention.get("max_contract_age_seconds"), "max_contract_age_seconds", 3600, 7 * 86400)
    limits = policy.get("limits")
    require_closed_keys(limits, LIMIT_KEYS, "limits")
    require_int(limits.get("max_delete_bytes"), "max_delete_bytes", GIB, 500 * GIB)
    require_int(limits.get("max_candidate_bytes"), "max_candidate_bytes", 1024, 100 * GIB)
    require_int(limits.get("max_runtime_seconds"), "max_runtime_seconds", 30, 7200)

    if limits["max_candidate_bytes"] > limits["max_delete_bytes"]:
        raise GuardianError("candidate_cap_exceeds_transaction_cap")
    if policy.get("scheduled_healthy_stdout") != "":
        raise GuardianError("scheduled_healthy_stdout_must_be_empty")
    return policy


def load_policy(path=None):
    if path is None:
        return validate_policy(default_policy())
    value, _, st = load_json_regular(path, MAX_POLICY_BYTES, os.getuid())
    if stat.S_IMODE(st.st_mode) & 0o022:
        raise GuardianError("policy_group_or_world_writable")
    return validate_policy(value)


def parse_diskutil_plist(payload):
    try:
        info = plistlib.loads(payload)
    except Exception as exc:
        raise GuardianError("diskutil_plist_invalid") from exc
    if info.get("MountPoint") != str(DATA_VOLUME):
        raise GuardianError("data_volume_mount_invalid")
    if str(info.get("FilesystemType", "")).lower() != "apfs":
        raise GuardianError("data_volume_not_apfs")
    free = info.get("APFSContainerFree")
    size = info.get("APFSContainerSize")
    if isinstance(free, bool) or isinstance(size, bool) or not isinstance(free, int) or not isinstance(size, int):
        raise GuardianError("diskutil_capacity_invalid")
    if free < 0 or size <= 0 or free > size:
        raise GuardianError("diskutil_capacity_invalid")
    return {
        "measurement_contract": "diskutil-info-plist:/System/Volumes/Data:APFSContainerFree/APFSContainerSize",
        "free_bytes": free,
        "size_bytes": size,
        "used_percent": round((size - free) / size * 100.0, 4),
    }


def measure_data_volume(runner=subprocess.run):
    fixture = os.environ.get("DISK_GUARDIAN_TEST_DISKUTIL_PLIST")
    if fixture:
        if os.environ.get("DISK_GUARDIAN_TESTING") != "1":
            raise GuardianError("test_fixture_refused")
        return parse_diskutil_plist(Path(fixture).read_bytes())
    try:
        proc = runner(
            ["/usr/sbin/diskutil", "info", "-plist", str(DATA_VOLUME)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise GuardianError("diskutil_measurement_failed") from exc
    if proc.returncode != 0 or proc.stderr:
        raise GuardianError("diskutil_measurement_failed")
    return parse_diskutil_plist(proc.stdout)


def effective_thresholds(policy, size_bytes):
    values = {}
    thresholds = policy["thresholds"]
    for severity in ("yellow", "orange", "red", "critical", "target"):
        override = thresholds[severity + "_free_bytes"]
        values[severity] = override if override is not None else int(size_bytes * thresholds[severity + "_free_percent"] / 100.0)
    if not values["critical"] < values["red"] < values["orange"] < values["yellow"] < values["target"]:
        raise GuardianError("effective_threshold_order_invalid")
    return values


def classify_pressure(sample, thresholds):
    free = sample["free_bytes"]
    if free < thresholds["critical"]:
        return "CRITICAL"
    if free < thresholds["red"]:
        return "RED"
    if free < thresholds["orange"]:
        return "ORANGE"
    if free < thresholds["yellow"]:
        return "YELLOW"
    return "GREEN"


def safe_join(home, relative):
    relative_path = Path(relative)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise GuardianError("relative_path_invalid")
    result = home.joinpath(relative_path)
    try:
        common = os.path.commonpath((str(home), str(result)))
    except ValueError as exc:
        raise GuardianError("path_outside_home") from exc
    if common != str(home):
        raise GuardianError("path_outside_home")
    return result


def assert_beneath_home_no_symlink(home, path, require_exists=True):
    home = Path(home).resolve()
    path = Path(path)
    try:
        relative = path.relative_to(home)
    except ValueError as exc:
        raise GuardianError("path_outside_home") from exc
    current = home
    for part in relative.parts:
        current = current / part
        try:
            st = current.lstat()
        except FileNotFoundError:
            if require_exists:
                raise GuardianError("path_component_missing")
            return
        except OSError as exc:
            raise GuardianError("path_component_unreadable") from exc
        if stat.S_ISLNK(st.st_mode):
            raise GuardianError("path_component_symlink_prohibited")
        if not stat.S_ISDIR(st.st_mode) and current != path:
            raise GuardianError("path_component_not_directory")


def ensure_private_state_directory(home, path, uid):
    home = Path(home).resolve()
    path = Path(path)
    try:
        relative = path.relative_to(home)
    except ValueError as exc:
        raise GuardianError("state_path_outside_home") from exc
    current = home
    for part in relative.parts:
        current = current / part
        try:
            st = current.lstat()
        except FileNotFoundError:
            current.mkdir(mode=0o700)
            st = current.lstat()
        if stat.S_ISLNK(st.st_mode) or not stat.S_ISDIR(st.st_mode) or st.st_uid != uid:
            raise GuardianError("state_path_unsafe")
    os.chmod(path, 0o700)


def open_dir_no_follow(path, expected_uid=None, expected_device=None):
    # The caller must pass a canonical absolute path. Every component is opened
    # without following links; this function deliberately never calls realpath.
    path = Path(path)
    if not path.is_absolute():
        raise GuardianError("anchored_path_not_absolute")
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open("/", flags)
    try:
        for part in path.parts[1:]:
            next_fd = os.open(part, flags, dir_fd=fd)
            os.close(fd)
            fd = next_fd
        st = os.fstat(fd)
        if not stat.S_ISDIR(st.st_mode):
            raise GuardianError("anchored_root_not_directory")
        if expected_uid is not None and st.st_uid != expected_uid:
            raise GuardianError("anchored_root_wrong_owner")
        if expected_device is not None and st.st_dev != expected_device:
            raise GuardianError("anchored_root_cross_device")
        return fd, st
    except Exception:
        os.close(fd)
        raise


def metadata_line(name, st, link_text=None, content_sha256=None):
    fields = [name, str(st.st_dev), str(st.st_ino), str(st.st_uid), str(stat.S_IFMT(st.st_mode)), str(st.st_size), str(st.st_mtime_ns)]
    if link_text is not None:
        fields.append(link_text)
    if content_sha256 is not None:
        fields.append(content_sha256)
    return "\0".join(fields).encode("utf-8", "surrogateescape") + b"\n"


def hash_regular_file_at(parent_fd, name, expected):
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(name, flags, dir_fd=parent_fd)
    digest = hashlib.sha256()
    try:
        before = os.fstat(fd)
        identity = (before.st_dev, before.st_ino, before.st_uid, stat.S_IFMT(before.st_mode), before.st_size, before.st_mtime_ns)
        if identity != expected:
            raise GuardianError("file_identity_changed_during_hash")
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
        after = os.fstat(fd)
        after_identity = (after.st_dev, after.st_ino, after.st_uid, stat.S_IFMT(after.st_mode), after.st_size, after.st_mtime_ns)
        if after_identity != identity:
            raise GuardianError("file_changed_during_hash")
    finally:
        os.close(fd)
    return digest.hexdigest()


def fingerprint_at(parent_fd, name, allow_leaf_symlink=False, max_nodes=MAX_TREE_NODES, max_depth=MAX_TREE_DEPTH, max_metadata=MAX_TREE_METADATA_BYTES):
    digest = hashlib.sha256()
    counters = {"nodes": 0, "bytes": 0, "metadata": 0}
    inventory = {}
    root_identity = {"device": None, "uid": None}

    def add(payload, logical):
        counters["nodes"] += 1
        counters["bytes"] += logical
        counters["metadata"] += len(payload)
        if counters["nodes"] > max_nodes:
            raise GuardianError("tree_node_limit")
        if counters["metadata"] > max_metadata:
            raise GuardianError("tree_metadata_limit")
        digest.update(payload)

    def walk(dir_fd, child_name, relative, depth):
        if depth > max_depth:
            raise GuardianError("tree_depth_limit")
        st = os.stat(child_name, dir_fd=dir_fd, follow_symlinks=False)
        if root_identity["device"] is None:
            root_identity["device"] = st.st_dev
            root_identity["uid"] = st.st_uid
        if st.st_dev != root_identity["device"]:
            raise GuardianError("tree_cross_device")
        if st.st_uid != root_identity["uid"]:
            raise GuardianError("tree_wrong_owner")
        mode = stat.S_IFMT(st.st_mode)
        if stat.S_ISLNK(st.st_mode):
            if not allow_leaf_symlink:
                raise GuardianError("tree_symlink_prohibited")
            link_text = os.readlink(child_name, dir_fd=dir_fd)
            payload = metadata_line(relative, st, link_text)
            add(payload, st.st_size)
            inventory[relative] = {
                "device": st.st_dev, "inode": st.st_ino, "uid": st.st_uid,
                "type": mode, "size": st.st_size, "mtime_ns": st.st_mtime_ns,
                "link_text": link_text, "content_sha256": None,
            }
            return
        content_sha256 = None
        if stat.S_ISREG(st.st_mode):
            expected = (st.st_dev, st.st_ino, st.st_uid, mode, st.st_size, st.st_mtime_ns)
            content_sha256 = hash_regular_file_at(dir_fd, child_name, expected)
        add(metadata_line(relative, st, content_sha256=content_sha256), st.st_size if stat.S_ISREG(st.st_mode) else 0)
        inventory[relative] = {
            "device": st.st_dev, "inode": st.st_ino, "uid": st.st_uid,
            "type": mode, "size": st.st_size, "mtime_ns": st.st_mtime_ns,
            "link_text": None, "content_sha256": content_sha256,
        }
        if stat.S_ISREG(st.st_mode):
            return
        if not stat.S_ISDIR(st.st_mode):
            raise GuardianError("tree_special_file_prohibited")
        flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
        child_fd = os.open(child_name, flags, dir_fd=dir_fd)
        try:
            opened = os.fstat(child_fd)
            if (opened.st_dev, opened.st_ino, stat.S_IFMT(opened.st_mode)) != (st.st_dev, st.st_ino, mode):
                raise GuardianError("tree_identity_changed")
            if opened.st_dev != st.st_dev:
                raise GuardianError("tree_cross_device")
            for grandchild in sorted(os.listdir(child_fd)):
                walk(child_fd, grandchild, relative + "/" + grandchild, depth + 1)
            after = os.fstat(child_fd)
            if (after.st_dev, after.st_ino, after.st_mtime_ns) != (opened.st_dev, opened.st_ino, opened.st_mtime_ns):
                raise GuardianError("tree_changed_during_scan")
        finally:
            os.close(child_fd)

    walk(parent_fd, name, name, 0)
    st = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    return {
        "name": name,
        "device": st.st_dev,
        "inode": st.st_ino,
        "uid": st.st_uid,
        "type": stat.S_IFMT(st.st_mode),
        "mtime_ns": st.st_mtime_ns,
        "logical_bytes": counters["bytes"],
        "nodes": counters["nodes"],
        "tree_sha256": digest.hexdigest(),
        "newest_mtime_ns": max(row["mtime_ns"] for row in inventory.values()),
        "_inventory": inventory,
    }


def same_fingerprint(left, right):
    keys = ("name", "device", "inode", "uid", "type", "mtime_ns", "newest_mtime_ns", "logical_bytes", "nodes", "tree_sha256")
    return all(left.get(key) == right.get(key) for key in keys)


def delete_at(parent_fd, name, expected, allow_leaf_symlink=False):
    observed = fingerprint_at(parent_fd, name, allow_leaf_symlink=allow_leaf_symlink)
    if not same_fingerprint(observed, expected):
        raise GuardianError("delete_boundary_identity_changed")
    expected_inventory = observed["_inventory"]
    deleted = 0

    def remove(dir_fd, child_name, relative):
        nonlocal deleted
        st = os.stat(child_name, dir_fd=dir_fd, follow_symlinks=False)
        frozen = expected_inventory.get(relative)
        if frozen is None:
            raise GuardianError("delete_boundary_unregistered_node")
        current = {
            "device": st.st_dev, "inode": st.st_ino, "uid": st.st_uid,
            "type": stat.S_IFMT(st.st_mode), "size": st.st_size,
            "mtime_ns": st.st_mtime_ns,
            "link_text": os.readlink(child_name, dir_fd=dir_fd) if stat.S_ISLNK(st.st_mode) else None,
            "content_sha256": None,
        }
        if stat.S_ISREG(st.st_mode):
            expected_identity = (st.st_dev, st.st_ino, st.st_uid, stat.S_IFMT(st.st_mode), st.st_size, st.st_mtime_ns)
            current["content_sha256"] = hash_regular_file_at(dir_fd, child_name, expected_identity)
        if current != frozen:
            raise GuardianError("delete_boundary_node_changed")
        if stat.S_ISLNK(st.st_mode):
            if not allow_leaf_symlink:
                raise GuardianError("delete_symlink_prohibited")
            os.unlink(child_name, dir_fd=dir_fd)
            deleted += st.st_size
            return
        if stat.S_ISREG(st.st_mode):
            os.unlink(child_name, dir_fd=dir_fd)
            deleted += st.st_size
            return
        if not stat.S_ISDIR(st.st_mode):
            raise GuardianError("delete_special_file_prohibited")
        flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
        child_fd = os.open(child_name, flags, dir_fd=dir_fd)
        try:
            opened = os.fstat(child_fd)
            if (opened.st_dev, opened.st_ino, opened.st_uid, stat.S_IFMT(opened.st_mode)) != (
                frozen["device"], frozen["inode"], frozen["uid"], frozen["type"]
            ):
                raise GuardianError("delete_directory_identity_changed")
            for grandchild in sorted(os.listdir(child_fd)):
                remove(child_fd, grandchild, relative + "/" + grandchild)
            after = os.fstat(child_fd)
            if (after.st_dev, after.st_ino) != (opened.st_dev, opened.st_ino):
                raise GuardianError("delete_directory_identity_changed")
        finally:
            os.close(child_fd)
        os.rmdir(child_name, dir_fd=dir_fd)

    try:
        remove(parent_fd, name, name)
    except (GuardianError, OSError) as exc:
        if deleted:
            reason = str(exc) if isinstance(exc, GuardianError) else "partial_delete_os_error"
            raise PartialDeletion(reason, deleted) from exc
        raise
    return deleted


def parse_process_inventory(text):
    if not isinstance(text, str):
        raise GuardianError("process_inventory_not_text")
    rows = []
    if not text.strip():
        return rows
    for raw in text.splitlines():
        match = re.match(r"^\s*([0-9]+)\s+(.+?)\s*$", raw)
        if not match:
            raise GuardianError("process_inventory_malformed")
        rows.append((int(match.group(1)), match.group(2)))
    return rows


def process_inventory(runner=subprocess.run):
    try:
        proc = runner(["/usr/bin/pgrep", "-lf", "."], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=15, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise GuardianError("process_inventory_unavailable") from exc
    if proc.returncode not in (0, 1) or proc.stderr:
        raise GuardianError("process_inventory_unavailable")
    return parse_process_inventory(proc.stdout)


def class_process_clear(class_name, rows):
    tokens = CACHE_PROCESS_TOKENS[class_name]
    for pid, command in rows:
        if pid == os.getpid():
            continue
        try:
            words = __import__("shlex").split(command)
        except ValueError:
            raise GuardianError("process_command_ambiguous")
        if not words:
            raise GuardianError("process_command_ambiguous")
        while words and Path(words[0]).name.lower() in {"env", "nohup"}:
            words = words[1:]
            while words and (words[0].startswith("-") or ("=" in words[0] and not words[0].startswith("="))):
                words = words[1:]
        if not words:
            raise GuardianError("process_command_ambiguous")
        normalized = [Path(word).name.lower() for word in words]
        executable = normalized[0]
        active = executable in tokens or any(executable == token + ".py" for token in tokens)
        if class_name == "pip_cache" and re.fullmatch(r"pip(?:[0-9]+(?:\.[0-9]+)*)?", executable):
            active = True
        # Also recognize canonical module invocation without treating arbitrary
        # prompt/payload words as executable evidence.
        if executable.startswith("python") and len(normalized) >= 3 and normalized[1] == "-m" and normalized[2] in tokens:
            active = True
        if class_name == "pip_cache" and executable.startswith("python") and len(normalized) >= 2 and normalized[1].startswith("pip"):
            active = True
        if class_name == "npm_cache" and executable == "node" and len(normalized) >= 2 and normalized[1] in {"npm-cli.js", "npx-cli.js"}:
            active = True
        if executable in {"sh", "bash", "zsh"} and any(token in normalized[1:] for token in tokens):
            active = True
        if executable in {"sh", "bash", "zsh"} and "-c" in normalized:
            index = normalized.index("-c")
            if index + 1 >= len(words):
                raise GuardianError("process_command_ambiguous")
            try:
                nested = __import__("shlex").split(words[index + 1])
            except ValueError:
                raise GuardianError("process_command_ambiguous")
            if not nested:
                raise GuardianError("process_command_ambiguous")
            nested_executable = Path(nested[0]).name.lower()
            if nested_executable in tokens or any(nested_executable == token + ".py" for token in tokens):
                active = True
        if class_name == "homebrew_download_cache" and executable == "ruby" and len(normalized) >= 2 and normalized[1] == "brew.rb":
            active = True
        if active:
            return False
    return True


def lsof_clear(path, runner=subprocess.run):
    command = ["/usr/sbin/lsof", "-nP", "-F0pcfn"]
    try:
        if Path(path).is_dir():
            command.extend(["+D", str(path)])
        else:
            command.append(str(path))
        proc = runner(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise GuardianError("lsof_evidence_unavailable") from exc
    stdout = proc.stdout.decode("utf-8", "replace") if isinstance(proc.stdout, bytes) else proc.stdout
    stderr = proc.stderr.decode("utf-8", "replace") if isinstance(proc.stderr, bytes) else proc.stderr
    if proc.returncode not in (0, 1) or stderr:
        raise GuardianError("lsof_evidence_unavailable")
    if stdout:
        return False
    return True


@contextlib.contextmanager
def exclusive_lock(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd = os.open(path, os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0), 0o600)
    try:
        os.fchmod(fd, 0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise AlreadyRunning("guardian_already_running") from exc
        yield fd
    finally:
        with contextlib.suppress(OSError):
            fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def contract_identifier(payload):
    base = dict(payload)
    base.pop("contract_id", None)
    return sha256_bytes(canonical_json(base))


def validate_authority(proofs, class_name):
    if not isinstance(proofs, dict) or set(proofs) != CONTRACT_PROOFS[class_name]["true"] | CONTRACT_PROOFS[class_name]["false"]:
        raise GuardianError("contract_proofs_invalid")
    if any(type(flag) is not bool for flag in proofs.values()):
        raise GuardianError("contract_proof_type_invalid")
    if any(not proofs[name] for name in CONTRACT_PROOFS[class_name]["true"]):
        raise GuardianError("contract_positive_proof_missing")
    if any(proofs[name] for name in CONTRACT_PROOFS[class_name]["false"]):
        raise GuardianError("contract_negative_proof_active")
    return proofs


def validate_contract(value, filename, home, now, max_age):
    allowed = {"schema", "contract_id", "class", "root", "candidate", "issued_at_epoch", "expires_at_epoch", "minimum_age_seconds", "identity", "authority_sha256", "lock_identity"}
    require_closed_keys(value, allowed, "contract")
    if value.get("schema") != CONTRACT_SCHEMA:
        raise GuardianError("contract_schema_invalid")
    contract_id = value.get("contract_id")
    if not isinstance(contract_id, str) or not re.fullmatch(r"[0-9a-f]{64}", contract_id):
        raise GuardianError("contract_id_invalid")
    if filename != contract_id + ".json" or contract_identifier(value) != contract_id:
        raise GuardianError("contract_hash_mismatch")
    class_name = value.get("class")
    if class_name not in CONTRACT_ROOTS:
        raise GuardianError("contract_class_invalid")
    if value.get("root") != CONTRACT_ROOTS[class_name]:
        raise GuardianError("contract_root_invalid")
    if any(value["root"] == prefix or value["root"].startswith(prefix + "/") for prefix in NEVER_DELETE_RELATIVE_PREFIXES):
        raise GuardianError("contract_never_delete_root")
    candidate = value.get("candidate")
    if not isinstance(candidate, str) or candidate in ("", ".", "..") or "/" in candidate or "\x00" in candidate:
        raise GuardianError("contract_candidate_invalid")
    issued = value.get("issued_at_epoch")
    expires = value.get("expires_at_epoch")
    if isinstance(issued, bool) or isinstance(expires, bool) or not isinstance(issued, (int, float)) or not isinstance(expires, (int, float)) or not math.isfinite(float(issued)) or not math.isfinite(float(expires)):
        raise GuardianError("contract_time_invalid")
    if issued > now + 1 or expires <= now or expires - issued > max_age or now - issued > max_age:
        raise GuardianError("contract_expired_or_future")
    minimum_age = require_int(value.get("minimum_age_seconds"), "minimum_age_seconds", 3600, 365 * 86400)
    identity = value.get("identity")
    identity_keys = {"device", "inode", "uid", "type", "mtime_ns", "newest_mtime_ns", "logical_bytes", "nodes", "tree_sha256"}
    require_closed_keys(identity, identity_keys, "contract_identity")
    for key in ("device", "inode", "uid", "type", "mtime_ns", "newest_mtime_ns", "logical_bytes", "nodes"):
        require_int(identity.get(key), "identity_" + key, 0)
    if not isinstance(identity.get("tree_sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", identity["tree_sha256"]):
        raise GuardianError("contract_tree_hash_invalid")
    if now - identity["newest_mtime_ns"] / 1_000_000_000 < minimum_age:
        raise GuardianError("contract_candidate_too_young")
    if not isinstance(value.get("authority_sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", value["authority_sha256"]):
        raise GuardianError("contract_authority_hash_invalid")
    lock_identity = value.get("lock_identity")
    require_closed_keys(lock_identity, {"device", "inode", "uid", "type"}, "lock_identity")
    for key in ("device", "inode", "uid", "type"):
        require_int(lock_identity.get(key), "lock_identity_" + key, 0)
    root = safe_join(home, value["root"])
    return {"value": value, "root": root, "class": class_name, "contract_id": contract_id}


def make_contract(class_name, candidate_path, authority_sha256, lock_identity, issued_at=None, ttl_seconds=86400, minimum_age_seconds=3600):
    """Build a contract object from an exact candidate. Intended for producers."""
    if class_name not in CONTRACT_ROOTS:
        raise GuardianError("contract_class_invalid")
    candidate_path = Path(candidate_path)
    root = candidate_path.parent
    fd, _ = open_dir_no_follow(root, expected_uid=os.getuid())
    try:
        identity = fingerprint_at(fd, candidate_path.name, allow_leaf_symlink=False)
    finally:
        os.close(fd)
    identity.pop("name")
    identity.pop("_inventory")
    issued = time.time() if issued_at is None else float(issued_at)
    if not isinstance(authority_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", authority_sha256):
        raise GuardianError("contract_authority_hash_invalid")
    value = {
        "schema": CONTRACT_SCHEMA,
        "contract_id": "",
        "class": class_name,
        "root": CONTRACT_ROOTS[class_name],
        "candidate": candidate_path.name,
        "issued_at_epoch": issued,
        "expires_at_epoch": issued + ttl_seconds,
        "minimum_age_seconds": minimum_age_seconds,
        "identity": identity,
        "authority_sha256": authority_sha256,
        "lock_identity": lock_identity,
    }
    value["contract_id"] = contract_identifier(value)
    return value


class Guardian:
    def __init__(self, policy, home=None, measure_fn=None, runner=subprocess.run, now_fn=time.time):
        self.policy = validate_policy(policy)
        self.home = Path(home).resolve() if home is not None else passwd_home()
        self.uid = os.getuid()
        self.runner = runner
        self.now_fn = now_fn
        self.measure_fn = measure_fn or (lambda: measure_data_volume(self.runner))
        self.state_root = safe_join(self.home, policy["state_directory"])
        self.contract_dir = safe_join(self.home, policy["retention_contracts"]["directory"])
        self.receipt_dir = self.state_root / "receipts"
        self.claim_dir = self.state_root / "claims"
        self.operation_dir = self.state_root / "operations"
        self.lock_path = self.state_root / "guardian.lock"
        ensure_private_state_directory(self.home, self.state_root, self.uid)

    def sample(self):
        sample = self.measure_fn()
        thresholds = effective_thresholds(self.policy, sample["size_bytes"])
        sample = dict(sample)
        sample["thresholds"] = thresholds
        sample["severity"] = classify_pressure(sample, thresholds)
        sample["target_reached"] = sample["free_bytes"] >= thresholds["target"]
        return sample

    def cache_roots(self):
        rows = []
        for class_name, relatives in CACHE_ROOTS.items():
            if not self.policy["cache_classes"][class_name]:
                continue
            for relative in relatives:
                rows.append((class_name, safe_join(self.home, relative)))
        return rows

    def inspect_cache_root(self, class_name, root, process_rows=None):
        result = {"class": class_name, "root_id": str(root.relative_to(self.home)), "status": "blocked", "blocker": None, "logical_bytes": 0, "candidates": 0}
        try:
            root_lstat = root.lstat()
        except FileNotFoundError:
            result.update(status="absent", blocker=None)
            return result, []
        except OSError:
            result["blocker"] = "cache_root_unreadable"
            return result, []
        try:
            assert_beneath_home_no_symlink(self.home, root)
            home_device = self.home.stat().st_dev
            if stat.S_ISLNK(root_lstat.st_mode) or not stat.S_ISDIR(root_lstat.st_mode):
                raise GuardianError("cache_root_not_directory")
            if root_lstat.st_uid != self.uid:
                raise GuardianError("cache_root_wrong_owner")
            if root_lstat.st_dev != home_device:
                raise GuardianError("cache_root_cross_device")
            rows = process_rows if process_rows is not None else process_inventory(self.runner)
            if not class_process_clear(class_name, rows):
                raise GuardianError("cache_process_active")
            if not lsof_clear(root, self.runner):
                raise GuardianError("cache_open_handle")
            fd, _ = open_dir_no_follow(root, expected_uid=self.uid, expected_device=home_device)
            candidates = []
            try:
                for name in sorted(os.listdir(fd)):
                    candidate = fingerprint_at(fd, name, allow_leaf_symlink=(class_name == "uv_cache"))
                    if candidate["uid"] != self.uid or candidate["device"] != home_device:
                        raise GuardianError("cache_candidate_wrong_owner_or_device")
                    candidate["class"] = class_name
                    candidate["root_id"] = result["root_id"]
                    candidates.append(candidate)
            finally:
                os.close(fd)
            result.update(status="eligible" if candidates else "empty", logical_bytes=sum(row["logical_bytes"] for row in candidates), candidates=len(candidates))
            return result, candidates
        except (GuardianError, OSError) as exc:
            result["blocker"] = str(exc) if isinstance(exc, GuardianError) else "cache_inspection_failed"
            return result, []

    def load_contracts(self):
        results = []
        eligible = []
        retention = self.policy["retention_contracts"]
        if not retention["enabled"]:
            return results, eligible
        if not self.contract_dir.exists():
            return results, eligible
        try:
            assert_beneath_home_no_symlink(self.home, self.contract_dir)
            directory_stat = self.contract_dir.lstat()
            if stat.S_ISLNK(directory_stat.st_mode) or not stat.S_ISDIR(directory_stat.st_mode) or directory_stat.st_uid != self.uid or stat.S_IMODE(directory_stat.st_mode) != 0o700:
                raise GuardianError("contract_directory_not_private")
            names = sorted(name for name in os.listdir(self.contract_dir) if name.endswith(".json"))
            if len(names) > MAX_CONTRACTS:
                raise GuardianError("contract_count_limit")
        except (GuardianError, OSError) as exc:
            return [{"status": "blocked", "blocker": str(exc) if isinstance(exc, GuardianError) else "contract_directory_unreadable"}], []
        for name in names:
            summary = {"contract_id": name[:-5] if name.endswith(".json") else "invalid", "status": "blocked", "blocker": None}
            try:
                value, _, _ = load_json_regular(self.contract_dir / name, MAX_CONTRACT_BYTES, self.uid, 0o600)
                parsed = validate_contract(value, name, self.home, self.now_fn(), retention["max_contract_age_seconds"])
                if (self.claim_dir / (parsed["contract_id"] + ".json")).exists():
                    raise GuardianError("contract_already_claimed")
                assert_beneath_home_no_symlink(self.home, parsed["root"])
                root_stat = parsed["root"].lstat()
                if stat.S_ISLNK(root_stat.st_mode) or not stat.S_ISDIR(root_stat.st_mode) or root_stat.st_uid != self.uid:
                    raise GuardianError("contract_root_invalid_live")
                lock_path = parsed["root"] / ".disk-guardian-retention.lock"
                lock_stat = lock_path.lstat()
                if stat.S_ISLNK(lock_stat.st_mode) or not stat.S_ISREG(lock_stat.st_mode) or lock_stat.st_uid != self.uid or stat.S_IMODE(lock_stat.st_mode) != 0o600:
                    raise GuardianError("contract_lock_invalid")
                live_lock_identity = {
                    "device": lock_stat.st_dev, "inode": lock_stat.st_ino,
                    "uid": lock_stat.st_uid, "type": stat.S_IFMT(lock_stat.st_mode),
                }
                if live_lock_identity != value["lock_identity"]:
                    raise GuardianError("contract_lock_identity_changed")
                authority_dir = parsed["root"] / ".disk-guardian-authority"
                authority_path = authority_dir / (sha256_bytes(value["candidate"].encode("utf-8")) + ".json")
                authority, _, _ = load_json_regular(authority_path, MAX_CONTRACT_BYTES, self.uid, 0o600)
                self._validate_live_authority(authority, parsed)
                if sha256_bytes(canonical_json(authority)) != value["authority_sha256"]:
                    raise GuardianError("contract_authority_changed")
                fd, _ = open_dir_no_follow(parsed["root"], expected_uid=self.uid, expected_device=self.home.stat().st_dev)
                try:
                    observed = fingerprint_at(fd, value["candidate"], allow_leaf_symlink=False)
                finally:
                    os.close(fd)
                frozen = dict(value["identity"])
                frozen["name"] = value["candidate"]
                if not same_fingerprint(observed, frozen):
                    raise GuardianError("contract_identity_changed")
                if observed["logical_bytes"] > self.policy["limits"]["max_candidate_bytes"]:
                    raise GuardianError("contract_candidate_over_cap")
                if not lsof_clear(parsed["root"] / value["candidate"], self.runner):
                    raise GuardianError("contract_open_handle")
                parsed["fingerprint"] = observed
                parsed["lock_path"] = lock_path
                parsed["authority_path"] = authority_path
                parsed["lock_identity"] = live_lock_identity
                summary.update(status="eligible", blocker=None, **{"class": parsed["class"], "logical_bytes": observed["logical_bytes"]})
                eligible.append(parsed)
            except (GuardianError, OSError) as exc:
                summary["blocker"] = str(exc) if isinstance(exc, GuardianError) else "contract_inspection_failed"
            results.append(summary)
        return results, eligible

    def _validate_live_authority(self, authority, parsed):
        allowed = {"schema", "class", "root", "candidate", "proofs", "active_references", "updated_at_epoch"}
        require_closed_keys(authority, allowed, "authority")
        if authority.get("schema") != AUTHORITY_SCHEMA or authority.get("class") != parsed["class"]:
            raise GuardianError("authority_identity_invalid")
        if authority.get("root") != parsed["value"]["root"] or authority.get("candidate") != parsed["value"]["candidate"]:
            raise GuardianError("authority_identity_invalid")
        updated = authority.get("updated_at_epoch")
        if isinstance(updated, bool) or not isinstance(updated, (int, float)) or not math.isfinite(float(updated)):
            raise GuardianError("authority_time_invalid")
        if updated > self.now_fn() + 1 or updated < parsed["value"]["issued_at_epoch"] - 1:
            raise GuardianError("authority_time_invalid")
        validate_authority(authority.get("proofs"), parsed["class"])
        if authority.get("active_references") != []:
            raise GuardianError("contract_active_references")
        return authority

    def scan(self):
        sample = self.sample()
        cache_results = []
        cache_candidates = []
        process_blocker = None
        try:
            rows = process_inventory(self.runner)
        except GuardianError as exc:
            rows = None
            process_blocker = str(exc)
        for class_name, root in self.cache_roots():
            if rows is None:
                cache_results.append({"class": class_name, "root_id": str(root.relative_to(self.home)), "status": "blocked", "blocker": process_blocker, "logical_bytes": 0, "candidates": 0})
                continue
            result, candidates = self.inspect_cache_root(class_name, root, rows)
            cache_results.append(result)
            cache_candidates.extend((root, row) for row in candidates)
        contract_results, contracts = self.load_contracts()
        return {
            "schema": "disk-guardian-community-scan/v1",
            "sample": sample,
            "cache_classes": cache_results,
            "retention_contracts": contract_results,
            "eligible_cache_bytes": sum(row["logical_bytes"] for _, row in cache_candidates),
            "eligible_contract_bytes": sum(row["fingerprint"]["logical_bytes"] for row in contracts),
            "never_delete": ["sessions", "databases", "vaults", "memory", "models", "containers", "Time Machine snapshots", "uncontracted backups/worktrees"],
            "_cache_candidates": cache_candidates,
            "_contracts": contracts,
        }

    def doctor(self):
        scan = self.scan()
        sample = scan["sample"]
        candidates = [("cache", root, row) for root, row in scan["_cache_candidates"]]
        candidates += [("contract", row["root"], row) for row in scan["_contracts"]]
        _, recoverable = self._bounded_plan(candidates)
        deficit = max(0, sample["thresholds"]["target"] - sample["free_bytes"])
        blockers = sorted({row.get("blocker") for row in scan["cache_classes"] + scan["retention_contracts"] if row.get("blocker")})
        return {
            "schema": "disk-guardian-community-doctor/v1",
            "severity": sample["severity"],
            "free_bytes": sample["free_bytes"],
            "target_free_bytes": sample["thresholds"]["target"],
            "deficit_bytes": deficit,
            "proven_eligible_bytes": recoverable,
            "likely_to_restore_target": recoverable >= deficit,
            "blockers": blockers,
            "verdict": "actionable" if recoverable else ("healthy" if sample["severity"] == "GREEN" else "no_proven_autonomous_relief"),
        }

    def _bounded_plan(self, candidates):
        ordered = sorted(candidates, key=lambda item: (item[2].get("fingerprint", item[2])["newest_mtime_ns"], item[2].get("class", ""), item[2].get("contract_id", item[2].get("name", ""))))
        selected = []
        total = 0
        transaction_cap = self.policy["limits"]["max_delete_bytes"]
        candidate_cap = self.policy["limits"]["max_candidate_bytes"]
        for item in ordered:
            logical = item[2].get("fingerprint", item[2])["logical_bytes"]
            if logical > candidate_cap or logical > transaction_cap - total:
                continue
            selected.append(item)
            total += logical
        return selected, total

    def _claim_contract(self, contract):
        self.claim_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(self.claim_dir, 0o700)
        path = self.claim_dir / (contract["contract_id"] + ".json")
        payload = canonical_json({"schema": "disk-guardian-community-claim/v1", "contract_id": contract["contract_id"], "created_at": utc_now(self.now_fn())})
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            os.write(fd, payload)
            os.fsync(fd)
        finally:
            os.close(fd)
        fsync_directory(self.claim_dir)

    def _write_receipt(self, receipt):
        self.receipt_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(self.receipt_dir, 0o700)
        payload = canonical_json(receipt)
        name = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime(self.now_fn())) + "-" + sha256_bytes(payload)[:12] + ".json"
        path = self.receipt_dir / name
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            os.write(fd, payload)
            os.fsync(fd)
        finally:
            os.close(fd)
        fsync_directory(self.receipt_dir)
        self._prune_receipts()
        return name

    def _write_operation_record(self, payload):
        self.operation_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(self.operation_dir, 0o700)
        record = dict(payload)
        record["schema"] = "disk-guardian-community-operation/v1"
        record["created_at"] = utc_now(self.now_fn())
        data = canonical_json(record)
        identifier = sha256_bytes(data)
        path = self.operation_dir / (identifier + ".json")
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
        try:
            os.write(fd, data)
            os.fsync(fd)
        finally:
            os.close(fd)
        fsync_directory(self.operation_dir)
        return identifier

    def _prune_receipts(self):
        try:
            rows = []
            now = self.now_fn()
            for name in os.listdir(self.receipt_dir):
                if not name.endswith(".json"):
                    continue
                path = self.receipt_dir / name
                st = path.lstat()
                if stat.S_ISREG(st.st_mode) and not stat.S_ISLNK(st.st_mode):
                    rows.append((st.st_mtime, path))
            rows.sort(reverse=True)
            keep = {path for index, (mtime, path) in enumerate(rows) if index < MAX_RECEIPTS and now - mtime <= RECEIPT_MAX_AGE_SECONDS}
            for _, path in rows:
                if path not in keep:
                    with contextlib.suppress(OSError):
                        path.unlink()
        except OSError:
            return

    def cleanup(self, dry_run=False):
        started = self.now_fn()
        with exclusive_lock(self.lock_path):
            scan = self.scan()
            before = scan["sample"]
            receipt = {
                "schema": RECEIPT_SCHEMA,
                "started_at": utc_now(started),
                "dry_run": bool(dry_run),
                "severity_before": before["severity"],
                "free_before_bytes": before["free_bytes"],
                "target_free_bytes": before["thresholds"]["target"],
                "logical_deleted_bytes": 0,
                "planned_logical_bytes": 0,
                "apfs_observed_free_delta_bytes": 0,
                "deleted": [],
                "blocked": [],
                "stop_reason": None,
            }
            if before["severity"] == "GREEN" or before["target_reached"]:
                receipt["stop_reason"] = "pressure_resolved"
                receipt["severity_after"] = before["severity"]
                receipt["free_after_bytes"] = before["free_bytes"]
                receipt["receipt_file"] = self._write_receipt(receipt)
                return receipt
            candidates = [("cache", root, row) for root, row in scan["_cache_candidates"]]
            candidates += [("contract", row["root"], row) for row in scan["_contracts"]]
            candidates.sort(key=lambda item: (item[2].get("fingerprint", item[2])["newest_mtime_ns"], item[2].get("class", ""), item[2].get("contract_id", item[2].get("name", ""))))
            for kind, root, row in candidates:
                if self.now_fn() - started > self.policy["limits"]["max_runtime_seconds"]:
                    receipt["stop_reason"] = "runtime_cap"
                    break
                fingerprint = row["fingerprint"] if kind == "contract" else row
                consumed = receipt["logical_deleted_bytes"] if not dry_run else receipt["planned_logical_bytes"]
                remaining = self.policy["limits"]["max_delete_bytes"] - consumed
                if fingerprint["logical_bytes"] > remaining or fingerprint["logical_bytes"] > self.policy["limits"]["max_candidate_bytes"]:
                    receipt["blocked"].append({"kind": kind, "class": row["class"], "reason": "candidate_over_remaining_cap"})
                    continue
                if dry_run:
                    receipt["deleted"].append({"kind": kind, "class": row["class"], "logical_bytes": fingerprint["logical_bytes"], "dry_run": True})
                    receipt["planned_logical_bytes"] += fingerprint["logical_bytes"]
                    continue
                try:
                    if kind == "cache":
                        fresh_processes = process_inventory(self.runner)
                        if not class_process_clear(row["class"], fresh_processes):
                            raise GuardianError("cache_process_active_at_boundary")
                        if not lsof_clear(root, self.runner):
                            raise GuardianError("cache_open_handle_at_boundary")
                        root_fd, _ = open_dir_no_follow(root, expected_uid=self.uid, expected_device=self.home.stat().st_dev)
                        try:
                            observed = fingerprint_at(root_fd, row["name"], allow_leaf_symlink=(row["class"] == "uv_cache"))
                            if not same_fingerprint(observed, row):
                                raise GuardianError("cache_identity_changed_at_boundary")
                            operation_id = self._write_operation_record({"phase": "prepared", "kind": kind, "class": row["class"], "logical_bytes": row["logical_bytes"], "fingerprint_sha256": row["tree_sha256"]})
                            deleted = delete_at(root_fd, row["name"], row, allow_leaf_symlink=(row["class"] == "uv_cache"))
                        finally:
                            os.close(root_fd)
                    else:
                        with exclusive_lock(row["lock_path"]):
                            locked_stat = row["lock_path"].lstat()
                            locked_identity = {"device": locked_stat.st_dev, "inode": locked_stat.st_ino, "uid": locked_stat.st_uid, "type": stat.S_IFMT(locked_stat.st_mode)}
                            if locked_identity != row["lock_identity"]:
                                raise GuardianError("contract_lock_identity_changed_at_boundary")
                            authority, _, _ = load_json_regular(row["authority_path"], MAX_CONTRACT_BYTES, self.uid, 0o600)
                            self._validate_live_authority(authority, row)
                            if sha256_bytes(canonical_json(authority)) != row["value"]["authority_sha256"]:
                                raise GuardianError("contract_authority_changed_at_boundary")
                            if not lsof_clear(root / row["value"]["candidate"], self.runner):
                                raise GuardianError("contract_open_handle_at_boundary")
                            root_fd, _ = open_dir_no_follow(root, expected_uid=self.uid, expected_device=self.home.stat().st_dev)
                            try:
                                observed = fingerprint_at(root_fd, row["value"]["candidate"], allow_leaf_symlink=False)
                                if not same_fingerprint(observed, fingerprint):
                                    raise GuardianError("contract_identity_changed_at_boundary")
                                self._claim_contract(row)
                                operation_id = self._write_operation_record({"phase": "prepared", "kind": kind, "class": row["class"], "logical_bytes": fingerprint["logical_bytes"], "fingerprint_sha256": fingerprint["tree_sha256"], "contract_id": row["contract_id"]})
                                deleted = delete_at(root_fd, row["value"]["candidate"], fingerprint, allow_leaf_symlink=False)
                            finally:
                                os.close(root_fd)
                    receipt["logical_deleted_bytes"] += deleted
                    receipt["deleted"].append({"kind": kind, "class": row["class"], "logical_bytes": deleted, "operation_id": operation_id})
                    self._write_operation_record({"phase": "completed", "prepared_operation_id": operation_id, "kind": kind, "class": row["class"], "logical_bytes": deleted})
                    after_candidate = self.sample()
                    if after_candidate["target_reached"]:
                        receipt["stop_reason"] = "target_reached"
                        break
                except PartialDeletion as exc:
                    receipt["logical_deleted_bytes"] += exc.logical_deleted_bytes
                    receipt["deleted"].append({"kind": kind, "class": row["class"], "logical_bytes": exc.logical_deleted_bytes, "partial": True})
                    receipt["blocked"].append({"kind": kind, "class": row["class"], "reason": str(exc)})
                    receipt["stop_reason"] = "partial_delete_safety_stop"
                    break
                except (GuardianError, OSError) as exc:
                    receipt["blocked"].append({"kind": kind, "class": row["class"], "reason": str(exc) if isinstance(exc, GuardianError) else "boundary_operation_failed"})
            after = self.sample()
            receipt["severity_after"] = after["severity"]
            receipt["free_after_bytes"] = after["free_bytes"]
            receipt["apfs_observed_free_delta_bytes"] = max(0, after["free_bytes"] - before["free_bytes"])
            if receipt["stop_reason"] is None:
                if dry_run:
                    receipt["stop_reason"] = "dry_run_complete"
                elif after["target_reached"]:
                    receipt["stop_reason"] = "target_reached"
                elif receipt["logical_deleted_bytes"] >= self.policy["limits"]["max_delete_bytes"]:
                    receipt["stop_reason"] = "transaction_cap"
                else:
                    receipt["stop_reason"] = "safe_candidates_exhausted"
            receipt["unresolved_pressure"] = after["severity"] != "GREEN" and not after["target_reached"]
            receipt["receipt_file"] = self._write_receipt(receipt)
            return receipt


def public_scan(scan):
    result = dict(scan)
    result.pop("_cache_candidates", None)
    result.pop("_contracts", None)
    return result


def write_contract_command(args, policy):
    home = passwd_home()
    root = safe_join(home, CONTRACT_ROOTS[args.class_name])
    candidate = root / args.candidate
    proofs, _, _ = load_json_regular(args.proofs_file, MAX_CONTRACT_BYTES, os.getuid())
    validate_authority(proofs, args.class_name)
    assert_beneath_home_no_symlink(home, root)
    lock_path = root / ".disk-guardian-retention.lock"
    with exclusive_lock(lock_path):
        lock_stat = lock_path.lstat()
        if stat.S_ISLNK(lock_stat.st_mode) or not stat.S_ISREG(lock_stat.st_mode) or lock_stat.st_uid != os.getuid():
            raise GuardianError("contract_lock_invalid")
        os.chmod(lock_path, 0o600)
        lock_identity = {"device": lock_stat.st_dev, "inode": lock_stat.st_ino, "uid": lock_stat.st_uid, "type": stat.S_IFMT(lock_stat.st_mode)}
        now = time.time()
        authority = {
            "schema": AUTHORITY_SCHEMA,
            "class": args.class_name,
            "root": CONTRACT_ROOTS[args.class_name],
            "candidate": args.candidate,
            "proofs": dict(sorted(proofs.items())),
            "active_references": [],
            "updated_at_epoch": now,
        }
        authority_dir = root / ".disk-guardian-authority"
        authority_dir.mkdir(mode=0o700, exist_ok=True)
        authority_stat = authority_dir.lstat()
        if stat.S_ISLNK(authority_stat.st_mode) or not stat.S_ISDIR(authority_stat.st_mode) or authority_stat.st_uid != os.getuid():
            raise GuardianError("authority_directory_invalid")
        os.chmod(authority_dir, 0o700)
        authority_path = authority_dir / (sha256_bytes(args.candidate.encode("utf-8")) + ".json")
        temporary = authority_dir / ("." + authority_path.name + ".candidate")
        fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
        try:
            os.write(fd, canonical_json(authority))
            os.fsync(fd)
        finally:
            os.close(fd)
        os.replace(temporary, authority_path)
        fsync_directory(authority_dir)
        value = make_contract(
            args.class_name, candidate, sha256_bytes(canonical_json(authority)), lock_identity,
            issued_at=now, ttl_seconds=args.ttl_seconds,
            minimum_age_seconds=args.minimum_age_seconds,
        )
    output_dir = safe_join(home, policy["retention_contracts"]["directory"])
    ensure_private_state_directory(home, output_dir, os.getuid())
    output = output_dir / (value["contract_id"] + ".json")
    fd = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
    try:
        os.write(fd, canonical_json(value))
        os.fsync(fd)
    finally:
        os.close(fd)
    fsync_directory(output_dir)
    print(str(output))


def build_parser():
    parser = argparse.ArgumentParser(description="Fail-closed macOS/APFS disk-pressure guardian")
    parser.add_argument("--policy", help="closed JSON policy; defaults to built-in portable policy")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    sub.add_parser("scan")
    sub.add_parser("doctor")
    cleanup = sub.add_parser("cleanup")
    cleanup.add_argument("--dry-run", action="store_true")
    cleanup.add_argument("--scheduled", action="store_true", help="empty stdout when pressure is resolved")
    contract = sub.add_parser("make-contract")
    contract.add_argument("class_name", choices=sorted(CONTRACT_ROOTS), metavar="CLASS")
    contract.add_argument("candidate", help="exact direct-child name under the registered class root")
    contract.add_argument("--ttl-seconds", type=int, default=86400)
    contract.add_argument("--minimum-age-seconds", type=int, default=3600)
    contract.add_argument("--proofs-file", required=True, help="closed JSON object containing the exact class proof booleans")
    sub.add_parser("self-test")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        if args.command == "self-test":
            validate_policy(default_policy())
            sample = parse_diskutil_plist(plistlib.dumps({
                "MountPoint": str(DATA_VOLUME), "FilesystemType": "apfs",
                "APFSContainerFree": 40 * GIB, "APFSContainerSize": 500 * GIB,
            }))
            thresholds = effective_thresholds(default_policy(), sample["size_bytes"])
            if classify_pressure(sample, thresholds) != "ORANGE":
                raise GuardianError("self_test_pressure_failed")
            print("disk-guardian-community self-test: ok")
            return 0
        policy = load_policy(args.policy)
        if args.command == "make-contract":
            write_contract_command(args, policy)
            return 0
        guardian = Guardian(policy)
        if args.command == "status":
            print(json.dumps(guardian.sample(), sort_keys=True))
        elif args.command == "scan":
            print(json.dumps(public_scan(guardian.scan()), sort_keys=True))
        elif args.command == "doctor":
            print(json.dumps(guardian.doctor(), sort_keys=True))
        elif args.command == "cleanup":
            receipt = guardian.cleanup(dry_run=args.dry_run)
            if not (args.scheduled and not receipt.get("unresolved_pressure") and not receipt.get("blocked")):
                print(json.dumps(receipt, sort_keys=True))
            return 2 if receipt.get("unresolved_pressure") and not args.dry_run else 0
        return 0
    except AlreadyRunning:
        return 0
    except GuardianError as exc:
        print(json.dumps({"schema": "disk-guardian-community-error/v1", "error": str(exc)}), file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
