#!/usr/bin/env python3
"""Validate the synthetic proportionate-execution contract chain."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


TASK_KEYS = {
    "schema_version",
    "contract_id",
    "accepted_outcome",
    "claims",
    "non_goals",
    "allowed_surfaces",
    "protected_surfaces",
    "approval_boundaries",
    "terminal_result",
    "bounded_closeout_actions",
    "runtime_enforcement_required",
    "synthetic",
    "authorizing",
}
CLAIM_KEYS = {"id", "kind", "state", "requirement", "acceptance_evidence"}
ACTION_KEYS = {
    "ordinal",
    "action_id",
    "kind",
    "description",
    "material",
    "mapping",
    "claim_state_before",
    "claim_state_after",
    "disposition",
    "evidence",
    "synthetic",
    "authorizing",
}
CLOSEOUT_KEYS = {
    "schema_version",
    "contract_id",
    "result",
    "closed_claim_ids",
    "open_claims",
    "first_green_ordinal",
    "post_green_material_actions",
    "post_green_actions",
    "adjacent_findings_parked",
    "rejected_unnecessary_machinery",
    "changed_surfaces",
    "protected_surfaces_unchanged",
    "runtime_enforcement_used",
    "residual_risks",
    "external_send",
    "service_restart",
    "live_activation",
    "synthetic",
    "authorizing",
}
EVAL_KEYS = {
    "case_id",
    "scenario",
    "expected_disposition",
    "rationale",
    "synthetic",
    "authorizing",
}
CONFIG_KEYS = {
    "report_retention_days",
    "notification_destination",
    "scheduler_mode",
    "credential_handling",
    "synthetic",
    "authorizing",
}
EXPECTED_CHANGED_CONFIG_KEYS = {"report_retention_days"}
EXPECTED_EVAL_DISPOSITIONS = {
    "reject_unnecessary_machinery",
    "admit_required_verification",
    "admit_direct_repair",
    "park_and_escalate_adjacent",
    "stop_material_work",
    "retry_same_claim_boundedly",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path.name}:{number}: row must be an object")
        rows.append(value)
    return rows


def require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def closed_schema(errors: list[str], label: str, value: Any, keys: set[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{label}: must be an object")
        return
    require(errors, set(value) == keys, f"{label}: closed schema mismatch")


def synthetic_non_authorizing(errors: list[str], label: str, value: dict[str, Any]) -> None:
    require(errors, value.get("synthetic") is True, f"{label}: synthetic must be true")
    require(errors, value.get("authorizing") is False, f"{label}: authorizing must be false")


def nonempty_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value)


def nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate(folder: Path) -> list[str]:
    errors: list[str] = []
    try:
        task = load_json(folder / "task-contract.json")
        actions = load_jsonl(folder / "action-ledger.jsonl")
        closeout = load_json(folder / "closeout-receipt.json")
        evals = load_jsonl(folder / "eval-cases.jsonl")
        config_before = load_json(folder / "synthetic-config-before.json")
        config_after = load_json(folder / "synthetic-config-after.json")
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return [f"fixture load failed: {exc}"]

    for label, value, keys in (
        ("task", task, TASK_KEYS),
        ("closeout", closeout, CLOSEOUT_KEYS),
        ("config before", config_before, CONFIG_KEYS),
        ("config after", config_after, CONFIG_KEYS),
    ):
        closed_schema(errors, label, value, keys)
        if isinstance(value, dict):
            synthetic_non_authorizing(errors, label, value)

    contract_id = task.get("contract_id")
    require(errors, nonempty_string(contract_id), "task: contract_id must be non-empty")
    require(errors, closeout.get("contract_id") == contract_id, "closeout: contract_id mismatch")
    require(errors, nonempty_string(task.get("accepted_outcome")), "task: accepted_outcome must be non-empty")
    require(errors, task.get("terminal_result") == "DONE_VERIFIED", "task: terminal result must be DONE_VERIFIED")
    require(errors, task.get("runtime_enforcement_required") is False, "task: runtime enforcement must remain optional")
    for key in ("non_goals", "allowed_surfaces", "protected_surfaces", "approval_boundaries", "bounded_closeout_actions"):
        require(errors, nonempty_list(task.get(key)), f"task: {key} must be a non-empty list")

    allowed_surfaces = task.get("allowed_surfaces", [])
    protected_surfaces = task.get("protected_surfaces", [])
    if isinstance(allowed_surfaces, list) and isinstance(protected_surfaces, list):
        require(errors, not set(allowed_surfaces) & set(protected_surfaces), "task: allowed and protected surfaces overlap")

    claims = task.get("claims")
    require(errors, nonempty_list(claims), "task: claims must be a non-empty list")
    claims = claims if isinstance(claims, list) else []
    claim_ids: list[str] = []
    for index, claim in enumerate(claims, 1):
        closed_schema(errors, f"claim {index}", claim, CLAIM_KEYS)
        if isinstance(claim, dict):
            claim_id = claim.get("id")
            if isinstance(claim_id, str):
                claim_ids.append(claim_id)
            require(errors, claim.get("kind") in {"accepted_claim", "mandatory_gate"}, f"claim {index}: invalid kind")
            require(errors, claim.get("state") == "open", f"claim {index}: initial state must be open")
            require(errors, all(nonempty_string(claim.get(key)) for key in ("id", "requirement", "acceptance_evidence")), f"claim {index}: identity or evidence is empty")
    require(errors, len(claim_ids) == len(set(claim_ids)) and len(claim_ids) == len(claims), "task: claim IDs must be unique and non-empty")
    claim_id_set = set(claim_ids)

    require(errors, bool(actions), "actions: ledger must not be empty")
    ordinals = [row.get("ordinal") for row in actions]
    require(
        errors,
        all(isinstance(ordinal, int) and not isinstance(ordinal, bool) for ordinal in ordinals),
        "actions: ordinals must be exact non-Boolean integers",
    )
    require(errors, ordinals == list(range(1, len(actions) + 1)), "actions: ordinals must be contiguous")
    action_ids: list[str] = []
    claim_state = {claim_id: "open" for claim_id in claim_ids}
    claim_close_ordinal: dict[str, int] = {}
    material_rows: list[dict[str, Any]] = []

    for index, row in enumerate(actions, 1):
        closed_schema(errors, f"action {index}", row, ACTION_KEYS)
        synthetic_non_authorizing(errors, f"action {index}", row)
        action_id = row.get("action_id")
        if isinstance(action_id, str):
            action_ids.append(action_id)
        require(errors, all(nonempty_string(row.get(key)) for key in ("action_id", "description", "evidence")), f"action {index}: identity, description, or evidence is empty")
        require(errors, isinstance(row.get("material"), bool), f"action {index}: material must be Boolean")

        mapping = row.get("mapping")
        valid_mapping = mapping in claim_id_set
        if mapping is not None:
            require(errors, valid_mapping, f"action {index}: mapping is not an accepted claim or gate")

        if row.get("kind") in {"finding", "proposed_machinery"}:
            require(errors, mapping is None and row.get("claim_state_before") is None and row.get("claim_state_after") is None, f"action {index}: proposal-only row carries claim authority")

        if valid_mapping:
            current_state = claim_state[mapping]
            require(errors, row.get("claim_state_before") == current_state, f"action {index}: claim lifecycle before-state mismatch")

        if row.get("material") is True:
            material_rows.append(row)
            require(errors, valid_mapping, f"action {index}: material action is unmapped")
            require(errors, row.get("disposition") == "executed", f"action {index}: material action disposition must be executed")
            require(errors, row.get("claim_state_after") == "closed", f"action {index}: material action must close one open claim")
            if valid_mapping:
                require(errors, claim_state[mapping] == "open", f"action {index}: claim was already closed")
                if claim_state[mapping] == "open" and row.get("claim_state_after") == "closed":
                    claim_state[mapping] = "closed"
                    claim_close_ordinal[mapping] = row["ordinal"]
        elif valid_mapping:
            require(errors, row.get("claim_state_after") == claim_state[mapping], f"action {index}: non-material action changed claim state")

        if row.get("kind") == "finding":
            require(errors, row.get("material") is False and row.get("disposition") == "proposal_only", f"action {index}: adjacent finding gained current-work authority")
        if row.get("kind") == "proposed_machinery":
            require(errors, row.get("material") is False and row.get("disposition") == "rejected_before_execution", f"action {index}: unnecessary machinery was admitted")

    require(errors, len(action_ids) == len(set(action_ids)) and len(action_ids) == len(actions), "actions: action IDs must be unique and non-empty")
    recomputed_closed_claims = {claim_id for claim_id, state in claim_state.items() if state == "closed"}
    require(errors, recomputed_closed_claims == claim_id_set, "actions: not every accepted claim or gate was closed by evidence")
    recomputed_first_green = max(claim_close_ordinal.values()) if recomputed_closed_claims == claim_id_set and claim_close_ordinal else None

    first_green = closeout.get("first_green_ordinal")
    require(errors, isinstance(first_green, int) and not isinstance(first_green, bool), "closeout: first_green_ordinal must be an integer")
    require(errors, first_green == recomputed_first_green, "closeout: first green does not match recomputed claim lifecycle")
    post_green_rows = [row for row in actions if isinstance(first_green, int) and isinstance(row.get("ordinal"), int) and row["ordinal"] > first_green]
    require(errors, not post_green_rows, "closeout: action ledger continued after first green")
    recomputed_post_green_material = sum(1 for row in post_green_rows if row.get("material") is True)
    require(errors, closeout.get("post_green_material_actions") == recomputed_post_green_material, "closeout: post-green material-action count mismatch")
    require(errors, recomputed_post_green_material == 0, "closeout: material work continued after first green")

    closed_claim_ids = closeout.get("closed_claim_ids")
    require(errors, isinstance(closed_claim_ids, list) and set(closed_claim_ids) == recomputed_closed_claims and len(closed_claim_ids) == len(recomputed_closed_claims), "closeout: closed claims do not exactly match witnessed lifecycle")
    require(errors, closeout.get("open_claims") == [], "closeout: open claims remain")
    require(errors, closeout.get("result") == task.get("terminal_result"), "closeout: result does not match task terminal result")

    changed_surfaces = closeout.get("changed_surfaces")
    require(errors, nonempty_list(changed_surfaces), "closeout: changed surfaces must be non-empty")
    if isinstance(changed_surfaces, list) and isinstance(allowed_surfaces, list) and isinstance(protected_surfaces, list):
        require(errors, set(changed_surfaces).issubset(set(allowed_surfaces)), "closeout: changed surface escaped allowed scope")
        require(errors, not set(changed_surfaces) & set(protected_surfaces), "closeout: changed surface overlaps a protected surface")

    post_green_actions = closeout.get("post_green_actions")
    bounded_closeout_actions = task.get("bounded_closeout_actions")
    require(errors, nonempty_list(post_green_actions), "closeout: post-green actions must be a non-empty list")
    if isinstance(post_green_actions, list) and isinstance(bounded_closeout_actions, list):
        require(errors, set(post_green_actions).issubset(set(bounded_closeout_actions)), "closeout: post-green action escaped bounded closeout allowlist")
    require(errors, closeout.get("protected_surfaces_unchanged") is True, "closeout: protected surfaces are not proven unchanged")
    require(errors, closeout.get("runtime_enforcement_used") is False, "closeout: prompt-only fixture cannot claim runtime enforcement")
    require(errors, closeout.get("external_send") is False and closeout.get("service_restart") is False and closeout.get("live_activation") is False, "closeout: synthetic fixture claims a live side effect")
    require(errors, closeout.get("adjacent_findings_parked") == sum(1 for row in actions if row.get("disposition") == "proposal_only"), "closeout: adjacent count mismatch")
    require(errors, closeout.get("rejected_unnecessary_machinery") == sum(1 for row in actions if row.get("disposition") == "rejected_before_execution"), "closeout: rejected-machinery count mismatch")

    changed_config_keys = {key for key in CONFIG_KEYS if config_before.get(key) != config_after.get(key)}
    require(errors, config_before.get("report_retention_days") == 14, "config witness: before retention must be 14 days")
    require(errors, config_after.get("report_retention_days") == 30, "config witness: after retention must be 30 days")
    require(errors, changed_config_keys == EXPECTED_CHANGED_CONFIG_KEYS, "config witness: unexpected key changed or required key did not change")
    protected_config_keys = CONFIG_KEYS - EXPECTED_CHANGED_CONFIG_KEYS
    require(errors, all(config_before.get(key) == config_after.get(key) for key in protected_config_keys), "config witness: protected configuration changed")

    require(errors, bool(evals), "evals: cases must not be empty")
    eval_ids: list[str] = []
    dispositions: set[str] = set()
    for index, row in enumerate(evals, 1):
        closed_schema(errors, f"eval {index}", row, EVAL_KEYS)
        synthetic_non_authorizing(errors, f"eval {index}", row)
        case_id = row.get("case_id")
        disposition = row.get("expected_disposition")
        if isinstance(case_id, str):
            eval_ids.append(case_id)
        if isinstance(disposition, str):
            dispositions.add(disposition)
        require(errors, all(nonempty_string(row.get(key)) for key in ("case_id", "scenario", "expected_disposition", "rationale")), f"eval {index}: required text is empty")
    require(errors, len(eval_ids) == len(set(eval_ids)) and len(eval_ids) == len(evals), "evals: case IDs must be unique and non-empty")
    require(errors, dispositions == EXPECTED_EVAL_DISPOSITIONS, "evals: completion/restraint disposition coverage is incomplete")

    return errors


def main() -> int:
    folder = Path(__file__).resolve().parent
    errors = validate(folder)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("proportionate_execution_contract: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
