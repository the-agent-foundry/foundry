#!/usr/bin/env python3
"""Validate the public synthetic Progressive Specification: Jigsaw fixture."""

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
EXPECTED_PHASE0_SHA256 = "".join(("64c6fb6bc0447cd2", "0be0fba1c9769e8b", "c14d1b2db29739ed", "29e9ca9806f0a753"))
EXPECTED_CHARTER_SHA256 = "".join(("7706c86ca6f479d1", "9bdfeacb7ddf4aa8", "cee2916177efaf51", "92882c660eb5c557"))
EXPECTED_DECISION_PIECES_SHA256 = "".join(("bc42631061e6c8a6", "3c28a7a519b9c138", "4c3f248ca61cb050", "b5996a3be3aac808"))
EXPECTED_INTEGRATION_SWEEP_SHA256 = "".join(("2452758891af743b", "d4d67c3830bb2f71", "dcf15f324e364cbc", "954eeb618ef3a043"))
EXPECTED_BUILD_SPEC_SHA256 = "".join(("595d38c5c575a6d6", "8d2058e680ea1658", "0f64d80a786d7a62", "0b38b9a95b9556c8"))
EXPECTED_STATUS_SHA256 = "".join(("12f4d89b6042ec6b", "7640aa555c0e600e", "d8eb5d62c596b705", "1f6e0b85bff599d2"))
EXPECTED_NEXT_OWNER_GATE = "Authorize handoff of the exact validated blueprint to a builder."
EXPECTED_NEXT_OWNER_PROMPT = "Specification is complete and validated. Build has not started. Send this exact blueprint to a builder?"
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
PHASE0_KEYS = {
    "schema_version", "fixture_id", "programme_id", "synthetic", "phase0_state",
    "provisional_understanding", "adaptive_questions", "owner_correction_summary",
    "charter_created_during_conversation", "execution_authority",
}
QUESTION_KEYS = {"question", "decision_impact", "consequence_of_error"}

LOCK_KEYS = {
    "schema_version", "fixture_id", "programme_id", "synthetic",
    "phase0_discovery_path", "phase0_discovery_sha256_chunks",
    "specification_path", "charter_path", "specification_sha256_chunks",
    "charter_sha256_chunks", "exact_byte_copy", "owner_approval",
    "charter_state", "charter_created_during_conversation", "execution_authority",
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
    "charter_sha256_chunks", "decision_pieces_sha256_chunks", "generation",
    "status", "accepted_piece_ids", "checks", "execution_authority",
}
CHECK_KEYS = {"check_id", "status", "evidence"}
BUILD_KEYS = {
    "schema_version", "fixture_id", "programme_id", "synthetic",
    "charter_sha256_chunks", "decision_pieces_sha256_chunks",
    "integration_sweep_sha256_chunks", "integration_generation",
    "build_started", "builder_launch_authorized", "terminal_state", "cells",
}
CELL_KEYS = {
    "cell_id", "dependencies", "requirement_ids", "piece_ids", "interfaces",
    "responsibilities", "non_goals", "inputs", "outputs", "state_owner",
    "invariants", "failure_behavior", "allowed_surfaces", "protected_surfaces",
    "activation_boundary", "rollback", "readback", "verification",
}
STATUS_KEYS = {
    "schema_version", "fixture_id", "programme_id", "synthetic", "phase",
    "charter_state", "charter_sha256_chunks", "decision_pieces_sha256_chunks",
    "integration_sweep_sha256_chunks", "build_spec_sha256_chunks", "accepted_piece_ids",
    "integration_status", "readiness_status", "build_state", "build_started",
    "next_owner_gate", "execution_authority",
}
FINAL_KEYS = {
    "schema_version", "fixture_id", "programme_id", "synthetic",
    "charter_sha256_chunks", "decision_pieces_sha256_chunks",
    "integration_sweep_sha256_chunks", "build_spec_sha256_chunks",
    "status_sha256_chunks", "integration_generation",
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


def string_list(value: Any, *, allow_empty: bool = False) -> bool:
    return (
        isinstance(value, list)
        and (allow_empty or bool(value))
        and all(nonempty_string(item) for item in value)
        and len(value) == len(set(value))
    )


def unique_string_set(value: Any, *, allow_empty: bool = False) -> set[str] | None:
    if not string_list(value, allow_empty=allow_empty):
        return None
    return set(value)


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
        "PHASE-0-DISCOVERY.json", "PHASE-0-SPECIFICATION.md", "CHARTER.md",
        "charter-lock.json", "decision-pieces.jsonl", "integration-sweep.json",
        "BUILD-SPEC.json", "STATUS.json", "final-readiness.json",
    ]
    for filename in required_files:
        if not (root / filename).is_file():
            errors.append(f"missing required artifact: {filename}")
    if errors:
        return errors

    discovery_bytes = (root / "PHASE-0-DISCOVERY.json").read_bytes()
    spec_bytes = (root / "PHASE-0-SPECIFICATION.md").read_bytes()
    charter_bytes = (root / "CHARTER.md").read_bytes()
    pieces_bytes = (root / "decision-pieces.jsonl").read_bytes()
    integration_bytes = (root / "integration-sweep.json").read_bytes()
    build_bytes = (root / "BUILD-SPEC.json").read_bytes()
    status_bytes = (root / "STATUS.json").read_bytes()
    discovery_hash = sha256_bytes(discovery_bytes)
    spec_hash = sha256_bytes(spec_bytes)
    charter_hash = sha256_bytes(charter_bytes)
    pieces_hash = sha256_bytes(pieces_bytes)
    integration_hash = sha256_bytes(integration_bytes)
    build_hash = sha256_bytes(build_bytes)
    status_hash = sha256_bytes(status_bytes)
    if discovery_hash != EXPECTED_PHASE0_SHA256:
        errors.append("PHASE-0-DISCOVERY: content does not match the frozen synthetic identity")
    if spec_bytes != charter_bytes:
        errors.append("approved specification and charter are not exact byte copies")
    if spec_hash != EXPECTED_CHARTER_SHA256 or charter_hash != EXPECTED_CHARTER_SHA256:
        errors.append("charter content does not match the frozen synthetic identity")
    if pieces_hash != EXPECTED_DECISION_PIECES_SHA256:
        errors.append("decision-pieces: content does not match the frozen accepted generation")
    if integration_hash != EXPECTED_INTEGRATION_SWEEP_SHA256:
        errors.append("integration-sweep: content does not match the frozen accepted generation")
    if build_hash != EXPECTED_BUILD_SPEC_SHA256:
        errors.append("BUILD-SPEC: content does not match the frozen synthetic identity")
    if status_hash != EXPECTED_STATUS_SHA256:
        errors.append("STATUS: content does not match the frozen synthetic identity")
    requirements_in_charter = set(re.findall(rb"REQ-\d{3}", charter_bytes))
    decoded_requirements = {item.decode("ascii") for item in requirements_in_charter}
    if decoded_requirements != EXPECTED_REQUIREMENTS:
        errors.append("charter requirement set drift")

    discovery = load_json(root / "PHASE-0-DISCOVERY.json", "PHASE-0-DISCOVERY", errors)
    lock = load_json(root / "charter-lock.json", "charter-lock", errors)
    pieces = load_jsonl(root / "decision-pieces.jsonl", "decision-pieces", errors)
    integration = load_json(root / "integration-sweep.json", "integration-sweep", errors)
    build = load_json(root / "BUILD-SPEC.json", "BUILD-SPEC", errors)
    status = load_json(root / "STATUS.json", "STATUS", errors)
    final = load_json(root / "final-readiness.json", "final-readiness", errors)
    if any(value is None for value in (discovery, lock, integration, build, status, final)):
        return errors

    if require_exact_keys(discovery, PHASE0_KEYS, "PHASE-0-DISCOVERY", errors):
        if discovery["schema_version"] != "jigsaw-phase0-discovery.v1":
            errors.append("PHASE-0-DISCOVERY: wrong schema version")
        if discovery["fixture_id"] != EXPECTED_FIXTURE_ID or discovery["programme_id"] != EXPECTED_PROGRAMME_ID:
            errors.append("PHASE-0-DISCOVERY: identity drift")
        if discovery["synthetic"] is not True or not exact_bool(discovery["synthetic"]):
            errors.append("PHASE-0-DISCOVERY: synthetic must be exact true")
        if discovery["phase0_state"] != "candidate_ready_for_owner_review":
            errors.append("PHASE-0-DISCOVERY: phase state drift")
        if not nonempty_string(discovery["provisional_understanding"]):
            errors.append("PHASE-0-DISCOVERY: provisional understanding is empty")
        if not nonempty_string(discovery["owner_correction_summary"]):
            errors.append("PHASE-0-DISCOVERY: owner correction summary is empty")
        questions = discovery["adaptive_questions"]
        if not isinstance(questions, list) or not 1 <= len(questions) <= 3:
            errors.append("PHASE-0-DISCOVERY: adaptive questions must contain one to three rows")
        else:
            seen_questions: set[str] = set()
            for index, question in enumerate(questions, 1):
                label = f"PHASE-0-DISCOVERY question {index}"
                if not require_exact_keys(question, QUESTION_KEYS, label, errors):
                    continue
                for key in ("question", "decision_impact", "consequence_of_error"):
                    if not nonempty_string(question[key]) or len(question[key].strip()) < 20:
                        errors.append(f"{label}: {key} is not substantive")
                question_text = question["question"]
                if nonempty_string(question_text):
                    if question_text in seen_questions:
                        errors.append(f"{label}: duplicate adaptive question")
                    seen_questions.add(question_text)
        if discovery["charter_created_during_conversation"] is not False or not exact_bool(discovery["charter_created_during_conversation"]):
            errors.append("PHASE-0-DISCOVERY: charter was created during conversation")
        if discovery["execution_authority"] is not False or not exact_bool(discovery["execution_authority"]):
            errors.append("PHASE-0-DISCOVERY: execution authority widened")

    if require_exact_keys(lock, LOCK_KEYS, "charter-lock", errors):
        check_identity(lock, "charter-lock", errors)
        if lock["schema_version"] != "jigsaw-charter-lock.v1":
            errors.append("charter-lock: wrong schema version")
        if lock["synthetic"] is not True or not exact_bool(lock["synthetic"]):
            errors.append("charter-lock: synthetic must be exact true")
        if lock["phase0_discovery_path"] != "PHASE-0-DISCOVERY.json":
            errors.append("charter-lock: Phase 0 discovery path drift")
        if join_digest(lock["phase0_discovery_sha256_chunks"]) != discovery_hash:
            errors.append("charter-lock: Phase 0 discovery digest mismatch")
        if lock["specification_path"] != "PHASE-0-SPECIFICATION.md" or lock["charter_path"] != "CHARTER.md":
            errors.append("charter-lock: artifact path drift")
        if join_digest(lock["specification_sha256_chunks"]) != spec_hash or join_digest(lock["charter_sha256_chunks"]) != charter_hash:
            errors.append("charter-lock: file digest mismatch")
        if lock["exact_byte_copy"] is not True or not exact_bool(lock["exact_byte_copy"]):
            errors.append("charter-lock: exact_byte_copy must be exact true")
        if lock["charter_state"] != "locked":
            errors.append("charter-lock: charter is not locked")
        if lock["charter_created_during_conversation"] is not False or not exact_bool(lock["charter_created_during_conversation"]):
            errors.append("charter-lock: charter was created during conversation")
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
        if not nonempty_string(piece["piece_type"]) or piece["piece_type"] not in valid_piece_types:
            errors.append(f"{label}: unsupported piece type")
        if piece["status"] != "accepted":
            errors.append(f"{label}: piece is not accepted")
        for key in ("question", "decision", "failure_behavior"):
            if not nonempty_string(piece[key]):
                errors.append(f"{label}: {key} is empty")
        for key in ("requirement_ids", "evidence", "interfaces", "invariants", "acceptance", "residual_uncertainty"):
            if not nonempty_string_list(piece[key]):
                errors.append(f"{label}: {key} must be a unique non-empty string list")
        dependencies = piece["dependencies"]
        if not string_list(dependencies, allow_empty=True):
            errors.append(f"{label}: dependencies must be a unique string list")
        elif any(dependency not in seen_piece_ids for dependency in dependencies):
            errors.append(f"{label}: dependency is missing or not dependency-ordered")
        requirement_ids = unique_string_set(piece["requirement_ids"])
        if requirement_ids is None:
            requirement_ids = set()
        elif not requirement_ids <= EXPECTED_REQUIREMENTS:
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
        if join_digest(integration["decision_pieces_sha256_chunks"]) != pieces_hash:
            errors.append("integration-sweep: decision-piece generation digest mismatch")
        if not exact_int(integration["generation"]) or integration["generation"] != 1:
            errors.append("integration-sweep: generation must be exact integer 1")
        if integration["status"] != "pass":
            errors.append("integration-sweep: status is not pass")
        accepted_piece_ids = unique_string_set(integration["accepted_piece_ids"])
        if accepted_piece_ids is None:
            errors.append("integration-sweep: accepted_piece_ids must be a unique non-empty string list")
        elif accepted_piece_ids != EXPECTED_PIECES:
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
                check_id = check["check_id"]
                if not nonempty_string(check_id):
                    errors.append(f"{label}: missing check identity")
                elif check_id in check_ids:
                    errors.append(f"{label}: duplicate check identity")
                else:
                    check_ids.add(check_id)
                if check["status"] != "pass" or not nonempty_string(check["evidence"]) or len(check["evidence"].strip()) < 20:
                    errors.append(f"{label}: check lacks substantive passing evidence")
        if check_ids != REQUIRED_INTEGRATION_CHECKS:
            errors.append("integration-sweep: required check set drift")

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
        if join_digest(build["decision_pieces_sha256_chunks"]) != pieces_hash:
            errors.append("BUILD-SPEC: decision-piece generation digest mismatch")
        if join_digest(build["integration_sweep_sha256_chunks"]) != integration_hash:
            errors.append("BUILD-SPEC: integration-sweep generation digest mismatch")
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
                dependencies = cell["dependencies"]
                if not string_list(dependencies, allow_empty=True):
                    errors.append(f"{label}: dependencies must be a unique string list")
                elif any(dependency not in seen_cells for dependency in dependencies):
                    errors.append(f"{label}: dependency is missing or not dependency-ordered")
                requirements = unique_string_set(cell["requirement_ids"])
                pieces_for_cell = unique_string_set(cell["piece_ids"])
                if requirements is None:
                    requirements = set()
                elif not requirements <= EXPECTED_REQUIREMENTS:
                    errors.append(f"{label}: unknown requirement binding")
                if pieces_for_cell is None:
                    pieces_for_cell = set()
                elif not pieces_for_cell <= EXPECTED_PIECES:
                    errors.append(f"{label}: unknown piece binding")
                supported_requirements: set[str] = set()
                for piece_id in pieces_for_cell:
                    piece = piece_by_id.get(piece_id)
                    if piece is not None:
                        piece_requirements = unique_string_set(piece.get("requirement_ids"))
                        if piece_requirements is not None:
                            supported_requirements.update(piece_requirements)
                if not requirements <= supported_requirements:
                    errors.append(f"{label}: requirement is not supported by the cell's named pieces")
                cell_requirements.update(requirements)
                cell_pieces.update(pieces_for_cell)
                allowed = set(cell["allowed_surfaces"]) if isinstance(cell["allowed_surfaces"], list) else set()
                protected = set(cell["protected_surfaces"]) if isinstance(cell["protected_surfaces"], list) else set()
                if allowed & protected:
                    errors.append(f"{label}: allowed and protected surfaces overlap")
                activation_boundary = cell["activation_boundary"]
                if nonempty_string(activation_boundary) and "no live activation" not in activation_boundary.lower():
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
        if join_digest(status["decision_pieces_sha256_chunks"]) != pieces_hash:
            errors.append("STATUS: decision-piece generation digest mismatch")
        if join_digest(status["integration_sweep_sha256_chunks"]) != integration_hash:
            errors.append("STATUS: integration-sweep generation digest mismatch")
        if join_digest(status["build_spec_sha256_chunks"]) != build_hash:
            errors.append("STATUS: build-spec generation digest mismatch")
        if not exact_int(status["phase"]) or status["phase"] != 4:
            errors.append("STATUS: phase must be exact integer 4")
        if status["charter_state"] != "locked" or status["integration_status"] != "pass":
            errors.append("STATUS: lifecycle is not locked and integrated")
        status_piece_ids = unique_string_set(status["accepted_piece_ids"])
        if status_piece_ids is None:
            errors.append("STATUS: accepted_piece_ids must be a unique non-empty string list")
        elif status_piece_ids != EXPECTED_PIECES:
            errors.append("STATUS: accepted piece set drift")
        if status["readiness_status"] != "READY_FOR_BUILDER" or status["build_state"] != "BUILD_NOT_STARTED":
            errors.append("STATUS: terminal markers drift")
        if status["build_started"] is not False or not exact_bool(status["build_started"]):
            errors.append("STATUS: build_started must be exact false")
        if status["execution_authority"] is not False or not exact_bool(status["execution_authority"]):
            errors.append("STATUS: execution authority widened")
        if status["next_owner_gate"] != EXPECTED_NEXT_OWNER_GATE:
            errors.append("STATUS: next owner gate drift or authority widening")

    if require_exact_keys(final, FINAL_KEYS, "final-readiness", errors):
        check_identity(final, "final-readiness", errors)
        if final["schema_version"] != "jigsaw-final-readiness.v1":
            errors.append("final-readiness: wrong schema version")
        if final["synthetic"] is not True or not exact_bool(final["synthetic"]):
            errors.append("final-readiness: synthetic must be exact true")
        if join_digest(final["decision_pieces_sha256_chunks"]) != pieces_hash:
            errors.append("final-readiness: decision-piece generation digest mismatch")
        if join_digest(final["integration_sweep_sha256_chunks"]) != integration_hash:
            errors.append("final-readiness: integration-sweep generation digest mismatch")
        if join_digest(final["build_spec_sha256_chunks"]) != build_hash:
            errors.append("final-readiness: build spec digest mismatch")
        if join_digest(final["status_sha256_chunks"]) != status_hash:
            errors.append("final-readiness: status digest mismatch")
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
        if final["next_owner_prompt"] != EXPECTED_NEXT_OWNER_PROMPT:
            errors.append("final-readiness: next owner prompt drift or authority widening")

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
