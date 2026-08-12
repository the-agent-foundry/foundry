#!/usr/bin/env python3
import copy
import importlib.util
import json
import os
import plistlib
import stat
import subprocess
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "disk-guardian" / "disk_guardian.py"
SPEC = importlib.util.spec_from_file_location("disk_guardian_community", MODULE_PATH)
dg = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(dg)


class Proc:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def clear_runner(command, **kwargs):
    if command[:2] == ["/usr/bin/pgrep", "-lf"]:
        return Proc(1, "", "")
    if command and command[0] == "/usr/sbin/lsof":
        return Proc(1, b"" if not kwargs.get("text") else "", b"" if not kwargs.get("text") else "")
    raise AssertionError(command)


def fixed_measure(free=20 * dg.GIB, size=500 * dg.GIB):
    return lambda: {
        "measurement_contract": "fixture",
        "free_bytes": free,
        "size_bytes": size,
        "used_percent": round((size - free) / size * 100, 4),
    }


class PolicyTests(unittest.TestCase):
    def test_default_policy_is_closed_and_valid(self):
        self.assertEqual(dg.validate_policy(dg.default_policy())["schema"], dg.POLICY_SCHEMA)

    def test_unknown_policy_key_rejected(self):
        policy = dg.default_policy()
        policy["delete_anything"] = True
        with self.assertRaisesRegex(dg.GuardianError, "policy_unknown_keys"):
            dg.validate_policy(policy)

    def test_boolean_numeric_cap_rejected(self):
        policy = dg.default_policy()
        policy["limits"]["max_delete_bytes"] = True
        with self.assertRaisesRegex(dg.GuardianError, "max_delete_bytes_not_integer"):
            dg.validate_policy(policy)

    def test_bad_threshold_order_rejected(self):
        policy = dg.default_policy()
        policy["thresholds"]["critical_free_percent"] = 30
        with self.assertRaisesRegex(dg.GuardianError, "threshold_percent_order_invalid"):
            dg.validate_policy(policy)

    def test_absolute_state_path_rejected(self):
        policy = dg.default_policy()
        policy["state_directory"] = "/private/place"
        with self.assertRaisesRegex(dg.GuardianError, "policy_state_directory_invalid"):
            dg.validate_policy(policy)

    def test_scheduled_stdout_must_be_empty(self):
        policy = dg.default_policy()
        policy["scheduled_healthy_stdout"] = "all good"
        with self.assertRaisesRegex(dg.GuardianError, "scheduled_healthy_stdout_must_be_empty"):
            dg.validate_policy(policy)


class MeasurementTests(unittest.TestCase):
    def plist(self, free=50 * dg.GIB, size=500 * dg.GIB, mount=str(dg.DATA_VOLUME), fs="apfs"):
        return plistlib.dumps({"MountPoint": mount, "FilesystemType": fs, "APFSContainerFree": free, "APFSContainerSize": size})

    def test_authoritative_apfs_fields(self):
        sample = dg.parse_diskutil_plist(self.plist())
        self.assertEqual(sample["free_bytes"], 50 * dg.GIB)
        self.assertIn("APFSContainerFree", sample["measurement_contract"])

    def test_wrong_mount_rejected(self):
        with self.assertRaisesRegex(dg.GuardianError, "data_volume_mount_invalid"):
            dg.parse_diskutil_plist(self.plist(mount="/"))

    def test_non_apfs_rejected(self):
        with self.assertRaisesRegex(dg.GuardianError, "data_volume_not_apfs"):
            dg.parse_diskutil_plist(self.plist(fs="ext4"))

    def test_pressure_is_size_aware(self):
        policy = dg.default_policy()
        thresholds = dg.effective_thresholds(policy, 1000 * dg.GIB)
        self.assertEqual(thresholds["target"], 200 * dg.GIB)
        sample = {"free_bytes": 60 * dg.GIB}
        self.assertEqual(dg.classify_pressure(sample, thresholds), "RED")

    def test_absolute_overrides_are_honored(self):
        policy = dg.default_policy()
        values = [4, 7, 10, 15, 20]
        for name, value in zip(("critical", "red", "orange", "yellow", "target"), values):
            policy["thresholds"][name + "_free_bytes"] = value * dg.GIB
        policy = dg.validate_policy(policy)
        self.assertEqual(dg.effective_thresholds(policy, 1000 * dg.GIB)["target"], 20 * dg.GIB)


class FilesystemSafetyTests(unittest.TestCase):
    def test_fingerprint_rejects_symlink(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target = root / "outside"
            target.write_text("keep")
            (root / "candidate").symlink_to(target)
            fd = os.open(root, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0))
            try:
                with self.assertRaisesRegex(dg.GuardianError, "tree_symlink_prohibited"):
                    dg.fingerprint_at(fd, "candidate")
            finally:
                os.close(fd)
            self.assertEqual(target.read_text(), "keep")

    def test_uv_leaf_symlink_unlinks_link_not_target(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            outside = root / "outside"
            outside.write_text("keep")
            candidate = root / "candidate"
            candidate.mkdir()
            (candidate / "leaf").symlink_to(outside)
            fd = os.open(root, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0))
            try:
                frozen = dg.fingerprint_at(fd, "candidate", allow_leaf_symlink=True)
                dg.delete_at(fd, "candidate", frozen, allow_leaf_symlink=True)
            finally:
                os.close(fd)
            self.assertEqual(outside.read_text(), "keep")
            self.assertFalse(candidate.exists())

    def test_identity_drift_blocks_delete(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            candidate = root / "candidate"
            candidate.mkdir()
            (candidate / "file").write_text("one")
            fd = os.open(root, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0))
            try:
                frozen = dg.fingerprint_at(fd, "candidate")
                (candidate / "file").write_text("changed")
                with self.assertRaisesRegex(dg.GuardianError, "delete_boundary_identity_changed"):
                    dg.delete_at(fd, "candidate", frozen)
            finally:
                os.close(fd)
            self.assertTrue(candidate.exists())

    def test_nested_node_drift_blocks_delete(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            candidate = root / "candidate"
            (candidate / "nested").mkdir(parents=True)
            leaf = candidate / "nested/file"
            leaf.write_text("one")
            fd = os.open(root, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0))
            try:
                frozen = dg.fingerprint_at(fd, "candidate")
                leaf.write_text("changed")
                with self.assertRaisesRegex(dg.GuardianError, "delete_boundary_identity_changed"):
                    dg.delete_at(fd, "candidate", frozen)
            finally:
                os.close(fd)
            self.assertTrue(candidate.exists())

    def test_same_size_same_mtime_content_rewrite_blocks_delete(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            candidate = root / "candidate"
            candidate.mkdir()
            leaf = candidate / "file"
            leaf.write_text("one")
            fd = os.open(root, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0))
            try:
                frozen = dg.fingerprint_at(fd, "candidate")
                old_mtime = leaf.stat().st_mtime_ns
                leaf.write_text("two")
                os.utime(leaf, ns=(old_mtime, old_mtime))
                with self.assertRaisesRegex(dg.GuardianError, "delete_boundary_identity_changed"):
                    dg.delete_at(fd, "candidate", frozen)
            finally:
                os.close(fd)

    def test_special_file_rejected(self):
        if not hasattr(os, "mkfifo"):
            self.skipTest("mkfifo unavailable")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            os.mkfifo(root / "pipe")
            fd = os.open(root, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0))
            try:
                with self.assertRaisesRegex(dg.GuardianError, "tree_special_file_prohibited"):
                    dg.fingerprint_at(fd, "pipe")
            finally:
                os.close(fd)

    def test_relative_escape_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(dg.GuardianError, "relative_path_invalid"):
                dg.safe_join(Path(td), "../escape")

    def test_symlinked_cache_parent_is_rejected(self):
        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as outside_td:
            home = Path(td)
            outside = Path(outside_td)
            (outside / "uv").mkdir()
            (home / ".cache").symlink_to(outside)
            guardian = dg.Guardian(dg.default_policy(), home=home, measure_fn=fixed_measure(), runner=clear_runner)
            scan = guardian.scan()
            uv_rows = [row for row in scan["cache_classes"] if row["class"] == "uv_cache" and row["root_id"] == ".cache/uv"]
            self.assertEqual(uv_rows[0]["blocker"], "path_component_symlink_prohibited")

    def test_group_writable_policy_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "policy.json"
            path.write_text(json.dumps(dg.default_policy()))
            path.chmod(0o664)
            with self.assertRaisesRegex(dg.GuardianError, "policy_group_or_world_writable"):
                dg.load_policy(path)


class EvidenceTests(unittest.TestCase):
    def test_active_uv_process_blocks_class(self):
        rows = dg.parse_process_inventory("123 /usr/local/bin/uv pip install thing\n")
        self.assertFalse(dg.class_process_clear("uv_cache", rows))

    def test_prompt_word_does_not_block_unrelated_python(self):
        rows = dg.parse_process_inventory("123 /usr/bin/python3 worker.py discuss uv cache\n")
        self.assertTrue(dg.class_process_clear("uv_cache", rows))

    def test_env_wrapped_uv_blocks_class(self):
        rows = dg.parse_process_inventory("123 /usr/bin/env UV_CACHE_DIR=/tmp/cache uv sync\n")
        self.assertFalse(dg.class_process_clear("uv_cache", rows))

    def test_node_npm_cli_blocks_class(self):
        rows = dg.parse_process_inventory("123 /usr/local/bin/node /opt/npm/bin/npm-cli.js install\n")
        self.assertFalse(dg.class_process_clear("npm_cache", rows))

    def test_versioned_pip_executable_blocks_class(self):
        rows = dg.parse_process_inventory("123 /usr/local/bin/pip3.12 install package\n")
        self.assertFalse(dg.class_process_clear("pip_cache", rows))

    def test_shell_wrapped_uv_blocks_class(self):
        rows = dg.parse_process_inventory("123 /bin/bash -c 'uv sync'\n")
        self.assertFalse(dg.class_process_clear("uv_cache", rows))

    def test_homebrew_ruby_entrypoint_blocks_class(self):
        rows = dg.parse_process_inventory("123 /usr/bin/ruby /opt/homebrew/Library/Homebrew/brew.rb update\n")
        self.assertFalse(dg.class_process_clear("homebrew_download_cache", rows))

    def test_malformed_process_inventory_fails_closed(self):
        with self.assertRaisesRegex(dg.GuardianError, "process_inventory_malformed"):
            dg.parse_process_inventory("not a process row")

    def test_lsof_warning_fails_closed(self):
        def runner(command, **kwargs):
            return Proc(1, b"", b"warning")
        with self.assertRaisesRegex(dg.GuardianError, "lsof_evidence_unavailable"):
            dg.lsof_clear("/tmp/example", runner)


class GuardianCacheTests(unittest.TestCase):
    def make_home(self, td):
        home = Path(td)
        (home / ".cache/uv").mkdir(parents=True)
        (home / ".cache/uv/pkg").mkdir()
        (home / ".cache/uv/pkg/data").write_bytes(b"x" * 4096)
        return home

    def test_doctor_reports_material_relief(self):
        with tempfile.TemporaryDirectory() as td:
            home = self.make_home(td)
            guardian = dg.Guardian(dg.default_policy(), home=home, measure_fn=fixed_measure(74 * dg.GIB), runner=clear_runner)
            doctor = guardian.doctor()
            self.assertEqual(doctor["verdict"], "actionable")
            self.assertGreater(doctor["proven_eligible_bytes"], 0)

    def test_cache_cleanup_deletes_exact_child_and_receipts(self):
        with tempfile.TemporaryDirectory() as td:
            home = self.make_home(td)
            guardian = dg.Guardian(dg.default_policy(), home=home, measure_fn=fixed_measure(), runner=clear_runner)
            receipt = guardian.cleanup()
            self.assertFalse((home / ".cache/uv/pkg").exists())
            self.assertGreaterEqual(receipt["logical_deleted_bytes"], 4096)
            self.assertEqual(receipt["stop_reason"], "safe_candidates_exhausted")
            self.assertTrue((home / ".disk-guardian/receipts" / receipt["receipt_file"]).is_file())

    def test_dry_run_has_teeth_but_no_mutation(self):
        with tempfile.TemporaryDirectory() as td:
            home = self.make_home(td)
            guardian = dg.Guardian(dg.default_policy(), home=home, measure_fn=fixed_measure(), runner=clear_runner)
            receipt = guardian.cleanup(dry_run=True)
            self.assertTrue((home / ".cache/uv/pkg/data").exists())
            self.assertTrue(any(row["dry_run"] for row in receipt["deleted"]))

    def test_dry_run_accounts_transaction_cap(self):
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            root = home / ".cache/uv"
            for name in ("a", "b"):
                (root / name).mkdir(parents=True)
                (root / name / "data").write_bytes(b"x" * 600)
            policy = dg.default_policy()
            policy["limits"]["max_candidate_bytes"] = 1024
            guardian = dg.Guardian(policy, home=home, measure_fn=fixed_measure(), runner=clear_runner)
            guardian.policy["limits"]["max_delete_bytes"] = 1024
            receipt = guardian.cleanup(dry_run=True)
            self.assertLessEqual(receipt["planned_logical_bytes"], 1024)
            self.assertEqual(len(receipt["deleted"]), 1)

    def test_doctor_honors_transaction_cap(self):
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            root = home / ".cache/uv"
            for name in ("a", "b"):
                (root / name).mkdir(parents=True)
                (root / name / "data").write_bytes(b"x" * 600)
            policy = dg.default_policy()
            policy["limits"]["max_candidate_bytes"] = 1024
            guardian = dg.Guardian(policy, home=home, measure_fn=fixed_measure(99 * dg.GIB), runner=clear_runner)
            guardian.policy["limits"]["max_delete_bytes"] = 1024
            doctor = guardian.doctor()
            self.assertLessEqual(doctor["proven_eligible_bytes"], 1024)

    def test_transaction_cap_blocks_oversize_candidate(self):
        with tempfile.TemporaryDirectory() as td:
            home = self.make_home(td)
            policy = dg.default_policy()
            policy["limits"]["max_delete_bytes"] = dg.GIB
            policy["limits"]["max_candidate_bytes"] = 1024
            guardian = dg.Guardian(policy, home=home, measure_fn=fixed_measure(), runner=clear_runner)
            receipt = guardian.cleanup()
            self.assertTrue((home / ".cache/uv/pkg").exists())
            self.assertIn("candidate_over_remaining_cap", {row["reason"] for row in receipt["blocked"]})

    def test_high_watermark_stops_following_candidates(self):
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            root = home / ".cache/uv"
            (root / "a").mkdir(parents=True)
            (root / "a/file").write_text("a")
            time.sleep(0.002)
            (root / "b").mkdir()
            (root / "b/file").write_text("b")
            samples = iter((20 * dg.GIB, 120 * dg.GIB, 120 * dg.GIB))
            def measure():
                free = next(samples)
                return fixed_measure(free)()
            guardian = dg.Guardian(dg.default_policy(), home=home, measure_fn=measure, runner=clear_runner)
            receipt = guardian.cleanup()
            self.assertEqual(receipt["stop_reason"], "target_reached")
            self.assertEqual(len(receipt["deleted"]), 1)
            self.assertEqual(sum(int(path.exists()) for path in (root / "a", root / "b")), 1)

    def test_healthy_cleanup_does_not_touch_cache(self):
        with tempfile.TemporaryDirectory() as td:
            home = self.make_home(td)
            guardian = dg.Guardian(dg.default_policy(), home=home, measure_fn=fixed_measure(120 * dg.GIB), runner=clear_runner)
            receipt = guardian.cleanup()
            self.assertEqual(receipt["stop_reason"], "pressure_resolved")
            self.assertTrue((home / ".cache/uv/pkg").exists())


class ContractTests(unittest.TestCase):
    def setup_candidate(self, td, class_name="worktree"):
        home = Path(td).resolve()
        root = home / dg.CONTRACT_ROOTS[class_name]
        root.mkdir(parents=True)
        lock = root / ".disk-guardian-retention.lock"
        lock.write_text("")
        lock.chmod(0o600)
        candidate = root / "old-candidate"
        candidate.mkdir()
        (candidate / "artifact").write_bytes(b"x" * 2048)
        old = time.time() - 7200
        os.utime(candidate / "artifact", (old, old))
        os.utime(candidate, (old, old))
        positive = dg.CONTRACT_PROOFS[class_name]["true"]
        negative = dg.CONTRACT_PROOFS[class_name]["false"]
        proofs = {name: True for name in positive}
        proofs.update({name: False for name in negative})
        authority = {
            "schema": dg.AUTHORITY_SCHEMA, "class": class_name,
            "root": dg.CONTRACT_ROOTS[class_name], "candidate": candidate.name,
            "proofs": proofs, "active_references": [], "updated_at_epoch": time.time(),
        }
        authority_dir = root / ".disk-guardian-authority"
        authority_dir.mkdir(); authority_dir.chmod(0o700)
        authority_path = authority_dir / (dg.sha256_bytes(candidate.name.encode()) + ".json")
        authority_path.write_bytes(dg.canonical_json(authority)); authority_path.chmod(0o600)
        lock_stat = lock.lstat()
        lock_identity = {"device": lock_stat.st_dev, "inode": lock_stat.st_ino, "uid": lock_stat.st_uid, "type": stat.S_IFMT(lock_stat.st_mode)}
        contract = dg.make_contract(class_name, candidate, dg.sha256_bytes(dg.canonical_json(authority)), lock_identity, issued_at=time.time(), minimum_age_seconds=3600)
        contract_dir = home / ".hermes/state/disk-guardian-community/contracts"
        contract_dir.mkdir(parents=True)
        contract_dir.chmod(0o700)
        path = contract_dir / (contract["contract_id"] + ".json")
        path.write_bytes(dg.canonical_json(contract))
        path.chmod(0o600)
        return home, candidate, path, contract

    def test_complete_contract_executes(self):
        with tempfile.TemporaryDirectory() as td:
            home, candidate, _, _ = self.setup_candidate(td)
            guardian = dg.Guardian(dg.default_policy(), home=home, measure_fn=fixed_measure(), runner=clear_runner)
            receipt = guardian.cleanup()
            self.assertFalse(candidate.exists())
            self.assertTrue(any(row["kind"] == "contract" for row in receipt["deleted"]))

    def test_active_reference_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            home, candidate, path, contract = self.setup_candidate(td)
            authority_path = candidate.parent / ".disk-guardian-authority" / (dg.sha256_bytes(candidate.name.encode()) + ".json")
            authority = json.loads(authority_path.read_text())
            authority["active_references"] = ["current"]
            authority_path.write_bytes(dg.canonical_json(authority)); authority_path.chmod(0o600)
            guardian = dg.Guardian(dg.default_policy(), home=home, measure_fn=fixed_measure(), runner=clear_runner)
            scan = guardian.scan()
            self.assertTrue(candidate.exists())
            self.assertIn("contract_active_references", {row.get("blocker") for row in scan["retention_contracts"]})

    def test_non_finite_contract_times_block(self):
        with tempfile.TemporaryDirectory() as td:
            home, candidate, path, contract = self.setup_candidate(td)
            contract["expires_at_epoch"] = float("nan")
            contract["contract_id"] = dg.contract_identifier(contract)
            path.unlink(); path = path.parent / (contract["contract_id"] + ".json")
            path.write_bytes(dg.canonical_json(contract)); path.chmod(0o600)
            guardian = dg.Guardian(dg.default_policy(), home=home, measure_fn=fixed_measure(), runner=clear_runner)
            self.assertIn("contract_time_invalid", {row.get("blocker") for row in guardian.scan()["retention_contracts"]})

    def test_stale_authority_hash_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            home, candidate, _, _ = self.setup_candidate(td)
            authority_path = candidate.parent / ".disk-guardian-authority" / (dg.sha256_bytes(candidate.name.encode()) + ".json")
            authority = json.loads(authority_path.read_text())
            authority["updated_at_epoch"] += 1
            authority_path.write_bytes(dg.canonical_json(authority)); authority_path.chmod(0o600)
            guardian = dg.Guardian(dg.default_policy(), home=home, measure_fn=fixed_measure(), runner=clear_runner)
            self.assertIn("contract_authority_changed", {row.get("blocker") for row in guardian.scan()["retention_contracts"]})

    def test_replaced_lock_identity_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            home, candidate, _, _ = self.setup_candidate(td)
            lock = candidate.parent / ".disk-guardian-retention.lock"
            lock.unlink(); lock.write_text(""); lock.chmod(0o600)
            guardian = dg.Guardian(dg.default_policy(), home=home, measure_fn=fixed_measure(), runner=clear_runner)
            self.assertIn("contract_lock_identity_changed", {row.get("blocker") for row in guardian.scan()["retention_contracts"]})

    def test_missing_proof_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            home, candidate, path, contract = self.setup_candidate(td)
            authority_path = candidate.parent / ".disk-guardian-authority" / (dg.sha256_bytes(candidate.name.encode()) + ".json")
            authority = json.loads(authority_path.read_text())
            authority["proofs"].pop("clean")
            authority_path.write_bytes(dg.canonical_json(authority)); authority_path.chmod(0o600)
            guardian = dg.Guardian(dg.default_policy(), home=home, measure_fn=fixed_measure(), runner=clear_runner)
            self.assertIn("contract_proofs_invalid", {row.get("blocker") for row in guardian.scan()["retention_contracts"]})
            self.assertTrue(candidate.exists())

    def test_identity_rewrite_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            home, candidate, _, _ = self.setup_candidate(td)
            (candidate / "artifact").write_bytes(b"changed")
            guardian = dg.Guardian(dg.default_policy(), home=home, measure_fn=fixed_measure(), runner=clear_runner)
            self.assertIn("contract_identity_changed", {row.get("blocker") for row in guardian.scan()["retention_contracts"]})

    def test_old_root_with_young_nested_file_blocks_contract(self):
        with tempfile.TemporaryDirectory() as td:
            home, candidate, path, contract = self.setup_candidate(td)
            nested = candidate / "fresh"
            nested.write_text("new")
            fresh = time.time()
            os.utime(nested, (fresh, fresh))
            os.utime(candidate, (time.time() - 7200, time.time() - 7200))
            root_fd, _ = dg.open_dir_no_follow(candidate.parent, expected_uid=os.getuid())
            try:
                identity = dg.fingerprint_at(root_fd, candidate.name)
            finally:
                os.close(root_fd)
            identity.pop("name"); identity.pop("_inventory")
            contract["identity"] = identity
            contract["contract_id"] = dg.contract_identifier(contract)
            path.unlink(); path = path.parent / (contract["contract_id"] + ".json")
            path.write_bytes(dg.canonical_json(contract)); path.chmod(0o600)
            guardian = dg.Guardian(dg.default_policy(), home=home, measure_fn=fixed_measure(), runner=clear_runner)
            self.assertIn("contract_candidate_too_young", {row.get("blocker") for row in guardian.scan()["retention_contracts"]})

    def test_replay_claim_blocks_second_execution(self):
        with tempfile.TemporaryDirectory() as td:
            home, candidate, _, contract = self.setup_candidate(td)
            claim_dir = home / ".disk-guardian/claims"
            claim_dir.mkdir(parents=True)
            (claim_dir / (contract["contract_id"] + ".json")).write_text("{}")
            guardian = dg.Guardian(dg.default_policy(), home=home, measure_fn=fixed_measure(), runner=clear_runner)
            self.assertIn("contract_already_claimed", {row.get("blocker") for row in guardian.scan()["retention_contracts"]})
            self.assertTrue(candidate.exists())

    def test_uncontracted_worktree_never_deleted(self):
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            candidate = home / ".hermes/worktrees/uncontracted"
            candidate.mkdir(parents=True)
            (candidate / "source").write_text("keep")
            guardian = dg.Guardian(dg.default_policy(), home=home, measure_fn=fixed_measure(), runner=clear_runner)
            guardian.cleanup()
            self.assertEqual((candidate / "source").read_text(), "keep")


class PublicHygieneTests(unittest.TestCase):
    def test_no_private_bindings_in_package(self):
        forbidden = ("/Users/", "com.revaly", "telegram:", "openclaw", "Arq", "llm-billing", "dashboard-30m")
        for path in (ROOT / "disk-guardian").rglob("*"):
            if path.is_file() and path.suffix in {".py", ".md", ".json", ".sh", ".plist"}:
                text = path.read_text(errors="replace")
                for token in forbidden:
                    self.assertNotIn(token, text, f"{token} in {path}")

    def test_no_snapshot_delete_command(self):
        text = MODULE_PATH.read_text()
        self.assertNotIn("deletelocalsnapshots", text)
        self.assertNotIn("tmutil", text)


if __name__ == "__main__":
    unittest.main()
