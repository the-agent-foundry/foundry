#!/usr/bin/env python3
"""Fail-closed validation for Agent Foundry's synthetic operating-pattern fixtures."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


class FixtureError(ValueError):
    pass


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FixtureError(f"{path}: invalid JSON: {exc}") from exc


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise FixtureError(f"{path}: cannot read JSONL: {exc}") from exc
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise FixtureError(f"{path}:{line_number}: invalid JSONL row: {exc}") from exc
        if not isinstance(value, dict):
            raise FixtureError(f"{path}:{line_number}: JSONL row must be an object")
        rows.append(value)
    return rows


def require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def require_synthetic(errors: list[str], label: str, value: dict[str, Any]) -> None:
    require(errors, value.get("synthetic") is True, f"{label}: fixture must declare synthetic true")
    require(errors, value.get("authorizing") is False, f"{label}: fixture must declare authorizing false")


def validate_engineering(examples: Path, errors: list[str]) -> None:
    label = "engineering-governance-v2"
    folder = examples / label
    try:
        acceptance = load_json(folder / "acceptance-contract.json")
        findings = load_json(folder / "finding-ledger.json")
        checkpoint = load_json(folder / "retained-checkpoint.json")
        followthrough = load_json(folder / "parent-followthrough.json")
        artifacts = [acceptance, findings, checkpoint, followthrough]
        for name, artifact in zip(
            ["acceptance-contract", "finding-ledger", "retained-checkpoint", "parent-followthrough"],
            artifacts,
        ):
            require_synthetic(errors, f"{label}/{name}", artifact)

        require(errors, {item.get("contract_id") for item in artifacts} == {"eng-demo-001"}, f"{label}: contract IDs do not match")
        candidate_ids = {findings.get("candidate_id"), checkpoint.get("candidate_id"), followthrough.get("candidate_id")}
        candidate_digests = {findings.get("candidate_digest"), checkpoint.get("candidate_digest"), followthrough.get("candidate_digest")}
        require(errors, len(candidate_ids) == 1 and None not in candidate_ids and all(candidate_ids), f"{label}: candidate IDs do not bind one immutable candidate")
        require(errors, len(candidate_digests) == 1 and None not in candidate_digests and all(candidate_digests), f"{label}: candidate digests do not bind one immutable candidate")
        require(errors, acceptance.get("approval_state") == "synthetic_scenario_approved", f"{label}: approval state must be explicitly synthetic")
        require(errors, acceptance.get("authoritative") is False, f"{label}: public fixture cannot claim authoritative state")
        require(errors, acceptance.get("live_runtime_affected") is False, f"{label}: acceptance fixture cannot claim live runtime effect")

        finding_rows = findings.get("findings", [])
        relationships = {"direct", "adjacent", "review_machinery"}
        require(errors, isinstance(finding_rows, list) and bool(finding_rows), f"{label}: finding ledger is empty")
        require(errors, all(item.get("relationship") in relationships for item in finding_rows), f"{label}: unknown finding relationship")
        direct_closed = {"incorporated", "rejected_with_evidence"}
        machinery_closed = {"machinery_repaired", "rejected_with_evidence"}
        calculated_open_direct = sum(
            1
            for item in finding_rows
            if item.get("relationship") == "direct"
            and item.get("severity") in {"P0", "P1"}
            and item.get("disposition") not in direct_closed
        )
        require(errors, findings.get("open_direct_p0_p1") == calculated_open_direct, f"{label}: open direct P0/P1 count does not match finding dispositions")
        require(errors, calculated_open_direct == 0, f"{label}: direct P0/P1 remains open")
        require(errors, all(item.get("disposition") == "proposal_only" for item in finding_rows if item.get("relationship") == "adjacent"), f"{label}: adjacent finding escaped proposal-only disposition")
        require(errors, all(item.get("disposition") in machinery_closed for item in finding_rows if item.get("relationship") == "review_machinery"), f"{label}: review-machinery finding is not closed")
        require(errors, findings.get("adjacent_activation_authority") is False, f"{label}: adjacent findings cannot authorize activation")

        require(errors, checkpoint.get("work_abandoned") is False, f"{label}: retained checkpoint cannot abandon accepted work")
        require(errors, checkpoint.get("new_approval_required") is False, f"{label}: retained checkpoint cannot manufacture a new approval gate")
        require(errors, bool(checkpoint.get("passed_gates")) and bool(checkpoint.get("open_gates")), f"{label}: retained checkpoint gate inventory is incomplete")
        require(errors, bool(checkpoint.get("next_smallest_action")), f"{label}: retained checkpoint next action is missing")

        backup = followthrough.get("backup", {})
        promotion = followthrough.get("promotion", {})
        runtime = followthrough.get("runtime_verification", {})
        rollback = followthrough.get("rollback", {})
        require(errors, backup.get("state") == "verified" and bool(backup.get("inventory_sha256")), f"{label}: predecessor backup witness is incomplete")
        require(errors, promotion.get("state") == "complete" and promotion.get("exact_readback") is True, f"{label}: promotion/readback witness is incomplete")
        require(errors, runtime.get("dedupe_regression") == "pass" and runtime.get("retry_path") == "pass" and runtime.get("unrelated_destinations_unchanged") is True, f"{label}: runtime verification witness is incomplete")
        require(errors, rollback.get("state") == "exercised" and rollback.get("predecessor_readback") == "pass", f"{label}: rollback/predecessor readback witness is incomplete")
        require(errors, followthrough.get("terminal_state") == "DONE_VERIFIED", f"{label}: parent follow-through is not terminal")
        require(errors, followthrough.get("live_runtime_affected") is False, f"{label}: synthetic follow-through cannot claim live runtime effect")
        require(errors, followthrough.get("external_send") is False, f"{label}: synthetic follow-through cannot claim external send")
        require(errors, followthrough.get("service_restart") is False, f"{label}: synthetic follow-through cannot claim service restart")
    except (FixtureError, KeyError, TypeError, AttributeError) as exc:
        errors.append(f"{label}: malformed contract chain: {exc}")


def validate_onboarding(examples: Path, errors: list[str]) -> None:
    label = "model-onboarding-v1"
    folder = examples / label
    try:
        sources = load_jsonl(folder / "source-ledger.jsonl")
        matrix = load_json(folder / "route-matrix.json")
        manifest = load_json(folder / "eval-manifest.json")
        comparison = load_json(folder / "comparison-report.json")
        activation = load_json(folder / "activation-receipt.json")
        drift = load_json(folder / "drift-report.json")
        for name, artifact in [
            ("route-matrix", matrix),
            ("eval-manifest", manifest),
            ("comparison-report", comparison),
            ("activation-receipt", activation),
            ("drift-report", drift),
        ]:
            require_synthetic(errors, f"{label}/{name}", artifact)
        for index, source in enumerate(sources, 1):
            require_synthetic(errors, f"{label}/source-ledger row {index}", source)

        require(errors, {manifest.get("manifest_id"), comparison.get("manifest_id"), activation.get("manifest_id")} == {"eval-demo-001"}, f"{label}: manifest IDs do not match")
        route_rows = matrix.get("routes", [])
        required_route_keys = {
            "route_id",
            "provider",
            "model",
            "endpoint_class",
            "tools",
            "structured_output",
            "retention_status",
            "retention_source_id",
            "retention_claim_scope",
            "fallback",
        }
        require(errors, isinstance(route_rows, list) and bool(route_rows), f"{label}: route matrix is empty")
        require(errors, all(required_route_keys.issubset(route) for route in route_rows), f"{label}: route-detail schema is incomplete")
        require(errors, all(all(route.get(key) for key in ("route_id", "provider", "model", "endpoint_class")) for route in route_rows), f"{label}: exact route identity contains an empty field")
        route_ids = {item.get("route_id") for item in route_rows}
        route_details = {
            item.get("route_id"): {
                "provider": item.get("provider"),
                "model": item.get("model"),
                "endpoint_class": item.get("endpoint_class"),
                "tools": item.get("tools"),
                "structured_output": item.get("structured_output"),
                "fallback": item.get("fallback"),
            }
            for item in route_rows
        }
        require(errors, route_ids == {manifest.get("baseline_route"), manifest.get("candidate_route")}, f"{label}: route matrix and eval manifest disagree")
        require(errors, set(comparison.get("results", {})) == route_ids, f"{label}: comparison does not cover every evaluated route")

        floors = manifest.get("hard_floors", {})
        required_floor_keys = {
            "privacy_leaks",
            "unauthorized_actions",
            "route_provenance_match",
            "valid_structured_output_rate",
        }
        require(errors, set(floors) == required_floor_keys, f"{label}: hard-floor schema is incomplete or contains unknown keys")
        require(
            errors,
            all(isinstance(floors.get(key), (int, float)) and not isinstance(floors.get(key), bool) for key in required_floor_keys),
            f"{label}: hard-floor values must be numeric and non-Boolean",
        )
        hard_floor_pass = True
        for route_id in sorted(route_ids):
            result = comparison.get("results", {}).get(route_id, {})
            required_result_keys = required_floor_keys | {"quality_score", "completion_score", "restraint_score", "route_provenance_evidence"}
            result_schema_complete = required_result_keys.issubset(result)
            result_types_valid = all(
                isinstance(result.get(key), (int, float)) and not isinstance(result.get(key), bool)
                for key in required_floor_keys | {"quality_score", "completion_score", "restraint_score"}
            )
            require(errors, result_schema_complete, f"{label}: {route_id} result schema is incomplete")
            require(errors, result_types_valid, f"{label}: {route_id} result metrics must be numeric and non-Boolean")
            checks = [
                set(floors) == required_floor_keys,
                result_schema_complete,
                result_types_valid,
                result.get("privacy_leaks") == floors.get("privacy_leaks"),
                result.get("unauthorized_actions") == floors.get("unauthorized_actions"),
                isinstance(result.get("route_provenance_match"), (int, float)) and result.get("route_provenance_match") >= floors.get("route_provenance_match", 1.0),
                isinstance(result.get("valid_structured_output_rate"), (int, float)) and result.get("valid_structured_output_rate") >= floors.get("valid_structured_output_rate", 1.0),
            ]
            hard_floor_pass = hard_floor_pass and all(checks)
            evidence = result.get("route_provenance_evidence", {})
            require(errors, evidence.get("expected_route_id") == route_id, f"{label}: {route_id} provenance expected route is missing or wrong")
            require(errors, evidence.get("observed_route_id") == route_id, f"{label}: {route_id} provenance observed route is missing or wrong")
            require(errors, bool(evidence.get("call_receipt_id")), f"{label}: {route_id} provenance call receipt is missing")
            require(errors, evidence.get("expected_route_detail") == route_details.get(route_id), f"{label}: {route_id} expected route detail is not bound to the route matrix")
            require(errors, evidence.get("observed_route_detail") == route_details.get(route_id), f"{label}: {route_id} observed route detail is not bound to the route matrix")
        require(errors, comparison.get("hard_floors_passed") is hard_floor_pass, f"{label}: hard_floors_passed does not match recomputed results")
        require(errors, hard_floor_pass, f"{label}: recomputed hard floors did not pass")
        require(errors, comparison.get("human_approval_for_live_activation") == "pending", f"{label}: synthetic live approval must remain pending")

        source_ids = {source.get("source_id") for source in sources}
        for route in matrix.get("routes", []):
            require(errors, route.get("retention_status") == "unknown_for_synthetic_route", f"{label}: exact synthetic route retention must remain unknown")
            require(errors, route.get("retention_source_id") in source_ids, f"{label}: route retention source is not in the source ledger")
            require(errors, route.get("retention_claim_scope") == "provider_policy_only_exact_route_unverified", f"{label}: route privacy claim is over-broad")
        require(errors, len(matrix.get("unknowns", [])) == len(route_ids), f"{label}: exact-route privacy unknowns are incomplete")

        require(errors, activation.get("candidate_route") == manifest.get("candidate_route"), f"{label}: activation receipt route mismatch")
        require(errors, bool(manifest.get("candidate_generation")) and activation.get("generation_id") == manifest.get("candidate_generation"), f"{label}: activation generation does not match the candidate generation")
        require(errors, activation.get("state") == "DISPOSABLE_ACTIVATION_REHEARSAL_PASSED", f"{label}: activation receipt is not a disposable rehearsal")
        require(errors, activation.get("inactive_generation_validated") is True, f"{label}: inactive generation was not validated")
        require(errors, activation.get("actual_consumer_readback") == manifest.get("candidate_route"), f"{label}: candidate consumer readback mismatch")
        require(errors, activation.get("actual_consumer_route") == route_details.get(manifest.get("candidate_route")), f"{label}: candidate consumer route detail mismatch")
        require(errors, activation.get("predecessor_backup_verified") is True, f"{label}: predecessor backup was not verified")
        require(errors, activation.get("live_activation") is False, f"{label}: fixture cannot claim live activation")
        require(errors, activation.get("candidate_reactivated") is False, f"{label}: rehearsal must end default-off")
        require(errors, activation.get("rollback_exercised") is True, f"{label}: rollback was not exercised")
        require(errors, activation.get("predecessor_readback_after_rollback") == manifest.get("baseline_route"), f"{label}: predecessor rollback readback mismatch")
        require(errors, activation.get("predecessor_readback_route") == route_details.get(manifest.get("baseline_route")), f"{label}: predecessor rollback route detail mismatch")
        require(errors, activation.get("approval_required_for_live_activation") is True, f"{label}: live activation approval gate is missing")

        require(errors, drift.get("accepted_route_id") == manifest.get("candidate_route"), f"{label}: drift accepted route ID mismatch")
        require(errors, drift.get("accepted_generation") == manifest.get("candidate_generation") == activation.get("generation_id"), f"{label}: drift, manifest, and activation generations do not match")
        require(errors, drift.get("accepted_route") == route_details.get(manifest.get("candidate_route")), f"{label}: drift accepted route detail is not bound to the route matrix")
        route_identity_changed = (
            drift.get("observed_route_id") != drift.get("accepted_route_id")
            or drift.get("observed_route") != drift.get("accepted_route")
        )
        require(errors, drift.get("drift_detected") is route_identity_changed, f"{label}: drift flag does not match route identity")
        require(errors, drift.get("automatic_effect") == "block_new_activation_and_require_re_evaluation", f"{label}: drift does not fail closed")
        require(errors, drift.get("live_route_changed") is False, f"{label}: synthetic drift fixture cannot claim live route mutation")
    except (FixtureError, KeyError, TypeError, AttributeError) as exc:
        errors.append(f"{label}: malformed contract chain: {exc}")


def validate_legal(examples: Path, errors: list[str]) -> None:
    label = "legal-operator-v1"
    folder = examples / label
    try:
        profile = load_json(folder / "profile.example.json")
        request = load_json(folder / "matter-request.json")
        handoff = load_json(folder / "matter-handoff.json")
        matrix = load_json(folder / "eval-matrix.json")
        for name, artifact in [("profile", profile), ("matter-request", request), ("matter-handoff", handoff), ("eval-matrix", matrix)]:
            require_synthetic(errors, f"{label}/{name}", artifact)

        require(errors, profile.get("licensed_counsel") is False, f"{label}: profile cannot claim licensed counsel status")
        public_tools = profile.get("modes", {}).get("public_research", {}).get("allowed_tools", [])
        private_mode = profile.get("modes", {}).get("private_matter", {})
        required_public_tools = {"public_primary_law_research", "public_source_packet_writer"}
        required_private_tools = {"matter_scoped_reader", "matter_scoped_draft_writer", "document_parser", "artifact_hasher"}
        require(errors, set(public_tools) == required_public_tools, f"{label}: public tool inventory is incomplete or crosses into private matter capability")
        require(errors, set(private_mode.get("allowed_tools", [])) == required_private_tools, f"{label}: private tool inventory is incomplete or network-capable")
        require(errors, profile.get("modes", {}).get("public_research", {}).get("confidential_inputs_allowed") is False, f"{label}: public mode permits confidential inputs")
        require(errors, private_mode.get("network_allowed") is False, f"{label}: private mode does not fail closed on network access")
        required_external_actions = {"send", "sign", "file_or_serve", "accept_or_waive", "settle_or_commit", "delete_evidence", "release_hold"}
        external_actions = profile.get("external_actions", {})
        require(errors, set(external_actions) == required_external_actions, f"{label}: external action denial schema is incomplete or contains unknown capabilities")
        require(errors, all(external_actions.get(key) == "absent" for key in required_external_actions), f"{label}: external action capability must remain absent")
        require(errors, profile.get("memory", {}).get("global_memory") == "disabled", f"{label}: global memory must be disabled")
        require(errors, profile.get("memory", {}).get("session_resume") == "disabled", f"{label}: session resume must be disabled")
        require(errors, profile.get("direct_entry", {}).get("usable_matter_authority") is False, f"{label}: direct entry cannot carry matter authority")

        required_bindings = [
            "run_id",
            "matter_id",
            "requester",
            "owner",
            "audience",
            "mode",
            "jurisdiction_hypothesis",
            "as_of",
            "deadline",
            "authorized_inputs",
            "input_hashes",
            "profile_generation",
        ]
        require(errors, set(profile.get("required_run_bindings", [])) == set(required_bindings), f"{label}: profile required-run-binding schema is incomplete or contains unknown keys")
        for key in required_bindings:
            require(errors, key in request and key in handoff, f"{label}: mandatory request/handoff binding is missing for {key}")
            require(errors, request.get(key) == handoff.get(key), f"{label}: request/handoff binding mismatch for {key}")
        nonempty_identity_bindings = ["run_id", "matter_id", "requester", "owner", "audience", "mode", "jurisdiction_hypothesis", "as_of", "deadline", "profile_generation"]
        for key in nonempty_identity_bindings:
            value = request.get(key)
            require(errors, isinstance(value, str) and bool(value.strip()), f"{label}: identity binding must be non-empty for {key}")
        expected_input_hashes = [item.get("sha256") for item in request.get("authorized_inputs", [])]
        require(errors, bool(expected_input_hashes) and request.get("input_hashes") == expected_input_hashes, f"{label}: input-hash binding does not match authorized inputs")
        require(errors, bool(request.get("profile_generation")), f"{label}: profile generation binding is missing")
        require(errors, request.get("external_action_authority") is False, f"{label}: request cannot grant external action authority")
        require(errors, handoff.get("external_action_taken") is False, f"{label}: handoff claims an external action")
        require(errors, handoff.get("gate_state") == "PARTIAL_BLOCKED_SLICE", f"{label}: handoff gate state is missing or wrong")
        require(errors, handoff.get("confidence") in {"verified", "likely", "weak", "contested"}, f"{label}: handoff confidence is invalid")
        require(errors, bool(handoff.get("bottom_line")) and bool(handoff.get("recommended_position")), f"{label}: handoff is disclaimer-first or lacks a recommendation")
        require(errors, bool(handoff.get("completed_unaffected_lanes")), f"{label}: handoff did not finish unaffected lanes")
        blocked = handoff.get("blocked_slice", {})
        require(errors, blocked.get("owner") == request.get("owner"), f"{label}: blocked-slice owner does not match request")
        require(errors, blocked.get("deadline") == request.get("deadline"), f"{label}: blocked-slice deadline does not match request")

        input_versions = {(item.get("artifact_id"), item.get("version")) for item in request.get("authorized_inputs", [])}
        source_versions = {(item.get("artifact_id"), item.get("version")) for item in handoff.get("sources", [])}
        require(errors, bool(source_versions), f"{label}: handoff source ledger is empty")
        require(errors, source_versions.issubset(input_versions), f"{label}: handoff source is not bound to an authorized input version")
        require(errors, all(source.get("synthetic") is True and source.get("pinpoints") and source.get("as_of") for source in handoff.get("sources", [])), f"{label}: source provenance, currentness, or pinpoint is missing")

        require(errors, bool(matrix.get("safety_cases")), f"{label}: safety evaluation cases are missing")
        require(errors, bool(matrix.get("usefulness_cases")), f"{label}: usefulness evaluation cases are missing")
        require(errors, bool(matrix.get("over_conservatism_failures")), f"{label}: over-conservatism evaluation is missing")
        required_legal_floors = {"safety_failures", "cross_matter_leaks", "external_actions", "fabricated_authority", "over_conservatism_failures"}
        legal_floors = matrix.get("hard_floors", {})
        require(errors, set(legal_floors) == required_legal_floors, f"{label}: legal hard-floor schema is incomplete or contains unknown keys")
        require(errors, all(legal_floors.get(key) == 0 and not isinstance(legal_floors.get(key), bool) for key in required_legal_floors), f"{label}: legal hard floors must require numeric zero failures")
    except (FixtureError, KeyError, TypeError, AttributeError) as exc:
        errors.append(f"{label}: malformed contract chain: {exc}")


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    examples = root / "examples"

    for path in sorted(examples.rglob("*.json")):
        try:
            load_json(path)
        except FixtureError as exc:
            errors.append(str(exc))
    for path in sorted(examples.rglob("*.jsonl")):
        try:
            load_jsonl(path)
        except FixtureError as exc:
            errors.append(str(exc))

    validate_engineering(examples, errors)
    validate_onboarding(examples, errors)
    validate_legal(examples, errors)
    return errors


def main(argv: list[str]) -> int:
    root = Path(argv[1] if len(argv) > 1 else ".").resolve()
    errors = validate(root)
    if errors:
        for error in errors:
            print(error)
        print(f"fixture_smoke: FAILED. {len(errors)} error(s).")
        return 1
    print("fixture_smoke: CLEAN. Syntax, synthetic authority, lifecycle, route, rollback, drift, and matter bindings passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
