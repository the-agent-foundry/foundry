#!/usr/bin/env python3
"""Validate the public synthetic Progressive Specification — Jigsaw fixture."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
EXPECTED_FIXTURE_ID = "synthetic-jigsaw-v1"
EXPECTED_PROGRAMME_ID = "workshop-booking-planner"
EXPECTED_CHARTER_SHA256 = "".join(("7706c86ca6f479d1", "9bdfeacb7ddf4aa8", "cee2916177efaf51", "92882c660eb5c557"))
EXPECTED_BUILD_SPEC_SHA256 = "".join(("60f94b6c2d3a6384", "c0315990a5cebf6c", "cdeae710536ee170", "4ef91c4faf851c7e"))
EXPECTED_REQUIREMENTS = {"REQ-001", "REQ-002", "REQ-003", "REQ-004", "REQ-005"}
EXPECTED_PIECES = {"PIECE-DATA-01", "PIECE-SCHEDULE-01", "PIECE-INTEGRATION-01"}
EXPECTED_CELLS = {"CELL-DATA-01", "CELL-SCHEDULE-01"}
REQUIRED_INTEGRATION_CHECKS = {
    "producer_consumer_parity",
    "state_owner",
    "migration",
    "observability",
    "recovery",
    "rollback",
    "acceptance_coverage",
}
PRIVATE_MARKERS = ("/Users/", ".hermes/", "Telegram", "Darryl", "Brit", "Victor")

LOCK_KEYS = {
    "schema_version", "fixture_id", "programme_id", "synthetic",
    "specification_path", "charter_path", "specification_sha256_chunks",
    "charter_sha256_chunks", "exact_byte_copy", "owner_approval",
    "charter_state", "execution_authority",
}
APPROVAL_KEYS = {"approval_ref", "approved_specification_sha256_chunks", "approved"}
PIECE_KEYS = {
    "piece_id", "piece_type", "status", "programme_id", "charter_sha256_chunks",
    "question", "decision", "requirement_ids", "dependencies", "evidence",
    "interfaces", "invariants", "failure_behavior", "acceptance",
    "residual_uncertainty", "execution_authority",
}
INTEGRATION_KEYS = {
    "schema_version", "fixture_id", "programme_id", "synthetic",
    "charter_sha256_chunks", "generation", "status", "accepted_piece_ids",
    "checks", "execution_authority",
}
CHECK_KEYS = {"check_id", "status", "evidence"}
BUILD_KEYS = {
    "schema_version", "fixture_id", "programme_id", "synthetic",
    "charter_sha256_chunks", "integration_generation", "build_started",
    "builder_launch_authorized", "terminal_state", "cells",
}
CELL_KEYS = {
    "cell_id", "dependencies", "requirement_ids", "piece_ids", "interfaces",
    "responsibilities", "non_goals", "inputs", "outputs", "state_owner",
    "invariants", "failure_behavior", "allowed_surfaces", "protected_surfaces",
    "activation_boundary", "rollback", "readback", "verification",
}
STATUS_KEYS = {
    "schema_version", "fixture_id", "programme_id", "synthetic", "phase",
    "charter_state", "charter_sha256_chunks", "accepted_piece_ids",
    "integration_status", "readiness_status", "build_state", "build_started",
    "next_owner_gate", "execution_authority",
}
FINAL_KEYS = {
    "schema_version", "fixture_id", "programme_id", "synthetic",
    "charter_sha256_chunks", "build_spec_sha256_chunks", "integration_generation",
    "validation_status", "readiness_status", "build_state", "build_started",
    "builder_handoff_authorized", "execution_authority", "next_owner_prompt",
}


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def join_digest(value: Any) -> str:
    if (
        not isinstance(value, list)
        or len(value) != 4
        or not all(isinstance(chunk, str) and re.fullmatch(r"[0-9a-f]{16}", chunk) for chunk in value)
    ):
        return ""
    return "".join(value)


def exact_bool(value: Any) -> bool:
    return type(value) is bool


def exact_int(value: Any) -> bool:
    return type(value) is int


def nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def nonempty_string_list(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(nonempty_string(item) for item in value)
        and len(value) == len(set(value))
    )


def require_exact_keys(value: Any, expected: set[str], label: str, errors: list[str]) -> bool:
    if not isinstance(value, dict):
        errors.append(f"{label}: expected object")
        return False
    actual = set(value)
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing:
        errors.append(f"{label}: missing keys {missing}")
    if extra:
        errors.append(f"{label}: unexpected keys {extra}")
    return not missing and not extra


def load_json(path: Path, label: str, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{label}: unreadable JSON: {exc}")
        return None


def load_jsonl(path: Path, label: str, errors: list[str]) -> list[Any]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        errors.append(f"{label}: unreadable JSONL: {exc}")
        return []
    rows: list[Any] = []
    for index, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            errors.append(f"{label}:{index}: invalid JSON: {exc}")
    return rows


def check_identity(value: dict[str, Any], label: str, errors: list[str]) -> None:
    if value.get("fixture_id") != EXPECTED_FIXTURE_ID:
        errors.append(f"{label}: fixture identity drift")
    if value.get("programme_id") != EXPECTED_PROGRAMME_ID:
        errors.append(f"{label}: programme identity drift")
    if join_digest(value.get("charter_sha256_chunks")) != EXPECTED_CHARTER_SHA256:
        errors.append(f"{label}: charter identity drift")


def validate(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    required_files = [
        "PHASE-0-SPECIFICATION.md", "CHARTER.md", "charter-lock.json",
        "decision-pieces.jsonl", "integration-sweep.json", "BUILD-SPEC.json",
        "STATUS.json", "final-readiness.json",
    ]
    for filename in required_files:
        if not (root / filename).is_file():
            errors.append(f"missing required artifact: {filename}")
    if errors:
        return errors

    spec_bytes = (root / "PHASE-0-SPECIFICATION.md").read_bytes()
    charter_bytes = (root / "CHARTER.md").read_bytes()
    spec_hash = sha256_bytes(spec_bytes)
    charter_hash = sha256_bytes(charter_bytes)
    if spec_bytes != charter_bytes:
        errors.append("approved specification and charter are not exact byte copies")
    if spec_hash != EXPECTED_CHARTER_SHA256 or charter_hash != EXPECTED_CHARTER_SHA256:
        errors.append("charter content does not match the frozen synthetic identity")
    requirements_in_charter = set(re.findall(rb"REQ-\d{3}", charter_bytes))
    decoded_requirements = {item.decode("ascii") for item in requirements_in_charter}
    if decoded_requirements != EXPECTED_REQUIREMENTS:
        errors.append("charter requirement set drift")

    public_artifacts = required_files + ["README.md"]
    for filename in public_artifacts:
        path = root / filename
        if path.is_file():
            text = path.read_text(encoding="utf-8", errors="replace")
            for marker in PRIVATE_MARKERS:
                if marker in text:
                    errors.append(f"{path.name}: private marker detected: {marker}")

    lock = load_json(root / "charter-lock.json", "charter-lock", errors)
    pieces = load_jsonl(root / "decision-pieces.jsonl", "decision-pieces", errors)
    integration = load_json(root / "integration-sweep.json", "integration-sweep", errors)
    build = load_json(root / "BUILD-SPEC.json", "BUILD-SPEC", errors)
    status = load_json(root / "STATUS.json", "STATUS", errors)
    final = load_json(root / "final-readiness.json", "final-readiness", errors)
    if any(value is None for value in (lock, integration, build, status, final)):
        return errors

    if require_exact_keys(lock, LOCK_KEYS, "charter-lock", errors):
        check_identity(lock, "charter-lock", errors)
        if lock["schema_version"] != "jigsaw-charter-lock.v1":
            errors.append("charter-lock: wrong schema version")
        if lock["synthetic"] is not True or not exact_bool(lock["synthetic"]):
            errors.append("charter-lock: synthetic must be exact true")
        if lock["specification_path"] != "PHASE-0-SPECIFICATION.md" or lock["charter_path"] != "CHARTER.md":
            errors.append("charter-lock: artifact path drift")
        if join_digest(lock["specification_sha256_chunks"]) != spec_hash or join_digest(lock["charter_sha256_chunks"]) != charter_hash:
            errors.append("charter-lock: file digest mismatch")
        if lock["exact_byte_copy"] is not True or not exact_bool(lock["exact_byte_copy"]):
            errors.append("charter-lock: exact_byte_copy must be exact true")
        if lock["charter_state"] != "locked":
            errors.append("charter-lock: charter is not locked")
        if lock["execution_authority"] is not False or not exact_bool(lock["execution_authority"]):
            errors.append("charter-lock: execution authority widened")
        approval = lock["owner_approval"]
        if require_exact_keys(approval, APPROVAL_KEYS, "charter-lock.owner_approval", errors):
            if approval["approval_ref"] != "synthetic-owner-approval-v1":
                errors.append("charter-lock: approval reference drift")
            if join_digest(approval["approved_specification_sha256_chunks"]) != spec_hash:
                errors.append("charter-lock: approval does not bind the exact specification")
            if approval["approved"] is not True or not exact_bool(approval["approved"]):
                errors.append("charter-lock: approved must be exact true")

    piece_by_id: dict[str, dict[str, Any]] = {}
    seen_piece_ids: set[str] = set()
    all_piece_requirements: set[str] = set()
    valid_piece_types = {
        "owner_decision", "internal_inspection", "external_research",
        "feasibility_spike", "bounded_design", "integration",
    }
    for index, piece in enumerate(pieces, 1):
        label = f"decision-pieces row {index}"
        if not require_exact_keys(piece, PIECE_KEYS, label, errors):
            continue
        if piece["programme_id"] != EXPECTED_PROGRAMME_ID or join_digest(piece["charter_sha256_chunks"]) != EXPECTED_CHARTER_SHA256:
            errors.append(f"{label}: stale charter or programme binding")
        piece_id = piece["piece_id"]
        if not nonempty_string(piece_id) or piece_id in seen_piece_ids:
            errors.append(f"{label}: missing or duplicate piece identity")
            continue
        seen_piece_ids.add(piece_id)
        piece_by_id[piece_id] = piece
        if piece["piece_type"] not in valid_piece_types:
            errors.append(f"{label}: unsupported piece type")
        if piece["status"] != "accepted":
            errors.append(f"{label}: piece is not accepted")
        for key in ("question", "decision", "failure_behavior"):
            if not nonempty_string(piece[key]):
                errors.append(f"{label}: {key} is empty")
        for key in ("requirement_ids", "evidence", "interfaces", "invariants", "acceptance", "residual_uncertainty"):
            if not nonempty_string_list(piece[key]):
                errors.append(f"{label}: {key} must be a unique non-empty string list")
        if not isinstance(piece["dependencies"], list) or not all(nonempty_string(item) for item in piece["dependencies"]):
            errors.append(f"{label}: dependencies must be a string list")
        if any(dependency not in seen_piece_ids for dependency in piece["dependencies"]):
            errors.append(f"{label}: dependency is missing or not dependency-ordered")
        requirement_ids = set(piece["requirement_ids"]) if isinstance(piece["requirement_ids"], list) else set()
        if not requirement_ids <= EXPECTED_REQUIREMENTS:
            errors.append(f"{label}: unknown requirement binding")
        all_piece_requirements.update(requirement_ids)
        if piece["execution_authority"] is not False or not exact_bool(piece["execution_authority"]):
            errors.append(f"{label}: execution authority widened")
    if set(piece_by_id) != EXPECTED_PIECES:
        errors.append("decision-pieces: accepted piece identity set drift")
    if all_piece_requirements != EXPECTED_REQUIREMENTS:
        errors.append("decision-pieces: requirement coverage is incomplete")

    if require_exact_keys(integration, INTEGRATION_KEYS, "integration-sweep", errors):
        check_identity(integration, "integration-sweep", errors)
        if integration["schema_version"] != "jigsaw-integration-sweep.v1":
            errors.append("integration-sweep: wrong schema version")
        if integration["synthetic"] is not True or not exact_bool(integration["synthetic"]):
            errors.append("integration-sweep: synthetic must be exact true")
        if not exact_int(integration["generation"]) or integration["generation"] != 1:
            errors.append("integration-sweep: generation must be exact integer 1")
        if integration["status"] != "pass":
            errors.append("integration-sweep: status is not pass")
        if set(integration["accepted_piece_ids"]) != EXPECTED_PIECES:
            errors.append("integration-sweep: accepted piece set drift")
        if integration["execution_authority"] is not False or not exact_bool(integration["execution_authority"]):
            errors.append("integration-sweep: execution authority widened")
        check_ids: set[str] = set()
        checks = integration["checks"]
        if not isinstance(checks, list):
            errors.append("integration-sweep: checks must be a list")
        else:
            for index, check in enumerate(checks, 1):
                label = f"integration-sweep check {index}"
                if not require_exact_keys(check, CHECK_KEYS, label, errors):
                    continue
                if not nonempty_string(check["check_id"]) or check["check_id"] in check_ids:
                    errors.append(f"{label}: missing or duplicate check identity")
                check_ids.add(check["check_id"])
                if check["status"] != "pass" or not nonempty_string(check["evidence"]):
                    errors.append(f"{label}: check lacks passing evidence")
        if check_ids != REQUIRED_INTEGRATION_CHECKS:
            errors.append("integration-sweep: required check set drift")

    build_bytes = (root / "BUILD-SPEC.json").read_bytes()
    build_hash = sha256_bytes(build_bytes)
    if build_hash != EXPECTED_BUILD_SPEC_SHA256:
        errors.append("BUILD-SPEC: content does not match the frozen synthetic identity")
    cell_by_id: dict[str, dict[str, Any]] = {}
    seen_cells: set[str] = set()
    cell_requirements: set[str] = set()
    cell_pieces: set[str] = set()
    if require_exact_keys(build, BUILD_KEYS, "BUILD-SPEC", errors):
        check_identity(build, "BUILD-SPEC", errors)
        if build["schema_version"] != "jigsaw-build-spec.v1":
            errors.append("BUILD-SPEC: wrong schema version")
        if build["synthetic"] is not True or not exact_bool(build["synthetic"]):
            errors.append("BUILD-SPEC: synthetic must be exact true")
        if not exact_int(build["integration_generation"]) or build["integration_generation"] != 1:
            errors.append("BUILD-SPEC: integration generation drift")
        if build["build_started"] is not False or not exact_bool(build["build_started"]):
            errors.append("BUILD-SPEC: build_started must be exact false")
        if build["builder_launch_authorized"] is not False or not exact_bool(build["builder_launch_authorized"]):
            errors.append("BUILD-SPEC: builder launch authority widened")
        if build["terminal_state"] != "BUILD_NOT_STARTED":
            errors.append("BUILD-SPEC: terminal state drift")
        cells = build["cells"]
        if not isinstance(cells, list) or not cells:
            errors.append("BUILD-SPEC: cells must be a non-empty list")
        else:
            for index, cell in enumerate(cells, 1):
                label = f"BUILD-SPEC cell {index}"
                if not require_exact_keys(cell, CELL_KEYS, label, errors):
                    continue
                cell_id = cell["cell_id"]
                if not nonempty_string(cell_id) or cell_id in seen_cells:
                    errors.append(f"{label}: missing or duplicate cell identity")
                    continue
                seen_cells.add(cell_id)
                cell_by_id[cell_id] = cell
                for key in ("requirement_ids", "piece_ids", "interfaces", "responsibilities", "non_goals", "inputs", "outputs", "invariants", "allowed_surfaces", "protected_surfaces", "verification"):
                    if not nonempty_string_list(cell[key]):
                        errors.append(f"{label}: {key} must be a unique non-empty string list")
                for key in ("state_owner", "failure_behavior", "activation_boundary", "rollback", "readback"):
                    if not nonempty_string(cell[key]):
                        errors.append(f"{label}: {key} is empty")
                if not isinstance(cell["dependencies"], list) or not all(nonempty_string(item) for item in cell["dependencies"]):
                    errors.append(f"{label}: dependencies must be a string list")
                if any(dependency not in seen_cells for dependency in cell["dependencies"]):
                    errors.append(f"{label}: dependency is missing or not dependency-ordered")
                requirements = set(cell["requirement_ids"]) if isinstance(cell["requirement_ids"], list) else set()
                pieces_for_cell = set(cell["piece_ids"]) if isinstance(cell["piece_ids"], list) else set()
                if not requirements <= EXPECTED_REQUIREMENTS:
                    errors.append(f"{label}: unknown requirement binding")
                if not pieces_for_cell <= EXPECTED_PIECES:
                    errors.append(f"{label}: unknown piece binding")
                cell_requirements.update(requirements)
                cell_pieces.update(pieces_for_cell)
                allowed = set(cell["allowed_surfaces"]) if isinstance(cell["allowed_surfaces"], list) else set()
                protected = set(cell["protected_surfaces"]) if isinstance(cell["protected_surfaces"], list) else set()
                if allowed & protected:
                    errors.append(f"{label}: allowed and protected surfaces overlap")
                if "no live activation" not in cell["activation_boundary"].lower():
                    errors.append(f"{label}: activation boundary does not remain inactive")
    if set(cell_by_id) != EXPECTED_CELLS:
        errors.append("BUILD-SPEC: builder cell identity set drift")
    if cell_requirements != EXPECTED_REQUIREMENTS:
        errors.append("BUILD-SPEC: requirement coverage is incomplete")
    if cell_pieces != EXPECTED_PIECES:
        errors.append("BUILD-SPEC: accepted piece coverage is incomplete")

    if require_exact_keys(status, STATUS_KEYS, "STATUS", errors):
        check_identity(status, "STATUS", errors)
        if status["schema_version"] != "jigsaw-status.v1":
            errors.append("STATUS: wrong schema version")
        if status["synthetic"] is not True or not exact_bool(status["synthetic"]):
            errors.append("STATUS: synthetic must be exact true")
        if not exact_int(status["phase"]) or status["phase"] != 4:
            errors.append("STATUS: phase must be exact integer 4")
        if status["charter_state"] != "locked" or status["integration_status"] != "pass":
            errors.append("STATUS: lifecycle is not locked and integrated")
        if set(status["accepted_piece_ids"]) != EXPECTED_PIECES:
            errors.append("STATUS: accepted piece set drift")
        if status["readiness_status"] != "READY_FOR_BUILDER" or status["build_state"] != "BUILD_NOT_STARTED":
            errors.append("STATUS: terminal markers drift")
        if status["build_started"] is not False or not exact_bool(status["build_started"]):
            errors.append("STATUS: build_started must be exact false")
        if status["execution_authority"] is not False or not exact_bool(status["execution_authority"]):
            errors.append("STATUS: execution authority widened")
        if not nonempty_string(status["next_owner_gate"]):
            errors.append("STATUS: next owner gate is empty")

    if require_exact_keys(final, FINAL_KEYS, "final-readiness", errors):
        check_identity(final, "final-readiness", errors)
        if final["schema_version"] != "jigsaw-final-readiness.v1":
            errors.append("final-readiness: wrong schema version")
        if final["synthetic"] is not True or not exact_bool(final["synthetic"]):
            errors.append("final-readiness: synthetic must be exact true")
        if join_digest(final["build_spec_sha256_chunks"]) != build_hash:
            errors.append("final-readiness: build spec digest mismatch")
        if not exact_int(final["integration_generation"]) or final["integration_generation"] != 1:
            errors.append("final-readiness: integration generation drift")
        if final["validation_status"] != "pass":
            errors.append("final-readiness: validation status is not pass")
        if final["readiness_status"] != "READY_FOR_BUILDER" or final["build_state"] != "BUILD_NOT_STARTED":
            errors.append("final-readiness: terminal markers drift")
        if final["build_started"] is not False or not exact_bool(final["build_started"]):
            errors.append("final-readiness: build_started must be exact false")
        if final["builder_handoff_authorized"] is not False or not exact_bool(final["builder_handoff_authorized"]):
            errors.append("final-readiness: builder handoff authority widened")
        if final["execution_authority"] is not False or not exact_bool(final["execution_authority"]):
            errors.append("final-readiness: execution authority widened")
        if not nonempty_string(final["next_owner_prompt"]):
            errors.append("final-readiness: next owner prompt is empty")

    return errors


def main() -> int:
    errors = validate(ROOT)
    if errors:
        print("progressive_specification_jigsaw: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("progressive_specification_jigsaw: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
