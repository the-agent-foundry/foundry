from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from typing import Any, Callable, Optional, Tuple


REPOSITORY = Path(__file__).resolve().parents[2]
SCRIPT = REPOSITORY / "gates/scripts/fixture_smoke.py"
SPEC = importlib.util.spec_from_file_location("fixture_smoke_finance_adversarial", SCRIPT)
assert SPEC is not None
assert SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
BASE = "examples/finance-control-v1/"
Mutation = Tuple[str, str, Optional[int], Callable[[dict[str, Any]], None]]


def copy_examples(temp: str) -> Path:
    root = Path(temp)
    shutil.copytree(REPOSITORY / "examples", root / "examples")
    return root


def apply_mutation(root: Path, mutation: Mutation) -> None:
    kind, relative, row_index, callback = mutation
    path = root / relative
    if kind == "json":
        value = json.loads(path.read_text())
        callback(value)
        path.write_text(json.dumps(value, indent=2) + "\n")
        return
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    assert row_index is not None
    callback(rows[row_index])
    path.write_text("".join(json.dumps(row) + "\n" for row in rows))


def j(name: str, callback: Callable[[dict[str, Any]], None]) -> Mutation:
    return ("json", BASE + name, None, callback)


def jl(name: str, row: int, callback: Callable[[dict[str, Any]], None]) -> Mutation:
    return ("jsonl", BASE + name, row, callback)


def errors_after(mutations: list[Mutation]) -> list[str]:
    with tempfile.TemporaryDirectory() as temp:
        root = copy_examples(temp)
        for mutation in mutations:
            apply_mutation(root, mutation)
        errors: list[str] = []
        MODULE.validate_finance(root / "examples", errors)
        return errors


class FinanceAdversarialMutationTests(unittest.TestCase):
    def assert_rejected(self, mutations: list[Mutation], expected: str) -> None:
        errors = errors_after(mutations)
        self.assertTrue(any(expected in error for error in errors), errors)

    def test_authority_and_grant_mutations_fail_closed(self):
        cases = {
            "direct_entry_write": ([j("profile.example.json", lambda value: value["direct_entry"].update(write_authority=True))], "direct entry must carry no read, write, or mission-grant authority"),
            "direct_entry_read": ([j("profile.example.json", lambda value: value["direct_entry"].update(read_authority=True))], "direct entry must carry no read, write, or mission-grant authority"),
            "mission_prose_authority": ([j("mission-request.json", lambda value: value.update(mission_prose_authority=True))], "mission prose cannot grant write authority"),
            "grant_type_removed": ([j("mission-request.json", lambda value: value["write_grant"].pop("grant_type"))], "action-layer write grant: closed schema mismatch"),
            "grant_type_weakened": ([j("mission-request.json", lambda value: value["write_grant"].update(grant_type="mission_prose"))], "Class A requires a concrete action-layer write grant"),
            "grant_scope_mismatch": ([j("mission-request.json", lambda value: value["write_grant"].update(scope_id="other-scope"))], "action-layer write grant mission/scope binding mismatch"),
            "grant_target_widened": ([j("mission-request.json", lambda value: value["write_grant"].update(exact_target={"record_id":"record-002","field":"category"}))], "action-layer write grant binding mismatch for exact_target"),
            "grant_digest_mismatch": ([j("mission-request.json", lambda value: value["write_grant"].update(expected_target_digest="other-digest"))], "action-layer write grant binding mismatch for expected_target_digest"),
            "grant_evidence_mismatch": ([j("mission-request.json", lambda value: value["write_grant"].update(evidence_ids=["ev-record-002"]))], "action-layer write grant binding mismatch for evidence_ids"),
            "grant_expired": ([j("mission-request.json", lambda value: value["write_grant"].update(expires_at="2026-07-27T11:30:00Z"))], "action-layer write grant is expired, future-issued, or malformed"),
            "grant_boolean_limit": ([j("mission-request.json", lambda value: value["write_grant"].update(execution_limit=True))], "execution limit must be integer one"),
            "external_effect_authority": ([j("mission-request.json", lambda value: value.update(external_effect_authority=True))], "synthetic mission cannot authorize external or live effects"),
        }
        for name, (mutations, expected) in cases.items():
            with self.subTest(name=name):
                self.assert_rejected(mutations, expected)

    def test_mission_envelope_mutations_fail_with_specific_errors(self):
        cases = {
            "envelope_id_changed": ([j("mission-request.json", lambda value: value["mission_envelope"].update(envelope_id="other-envelope"))], "mission envelope ID is not canonical"),
            "envelope_as_of_mismatch": ([j("mission-request.json", lambda value: value["mission_envelope"].update(as_of="2026-07-27T11:00:00Z"))], "mission envelope as-of binding mismatch"),
            "requester_schema_open": ([j("mission-request.json", lambda value: value["mission_envelope"]["requester"].update(display_name="hidden"))], "mission requester: closed schema mismatch"),
            "requester_role_blank": ([j("mission-request.json", lambda value: value["mission_envelope"]["requester"].update(role=""))], "mission requester binding contains an empty value"),
            "owner_id_blank": ([j("mission-request.json", lambda value: value["mission_envelope"]["owner"].update(owner_id=""))], "mission owner binding contains an empty value"),
            "audience_widened": ([j("mission-request.json", lambda value: value["mission_envelope"]["audience"].update(audience_id="other-audience"))], "mission audience is not closed to the declared owner"),
            "scope_entity_changed": ([j("mission-request.json", lambda value: value["mission_envelope"]["scope"].update(entity_id="other-entity"))], "exact entity/book/period/system scope binding mismatch"),
            "scope_book_changed": ([j("mission-request.json", lambda value: value["mission_envelope"]["scope"].update(book_id="other-book"))], "exact entity/book/period/system scope binding mismatch"),
            "scope_period_changed": ([j("mission-request.json", lambda value: value["mission_envelope"]["scope"].update(period_id="2026-Q3"))], "exact entity/book/period/system scope binding mismatch"),
            "scope_system_changed": ([j("mission-request.json", lambda value: value["mission_envelope"]["scope"].update(target_system="other-system"))], "mission target system is not bound to the closed scope"),
            "authorized_input_version_missing": ([j("mission-request.json", lambda value: value["mission_envelope"]["authorized_inputs"][0].pop("version"))], "evidence source version does not match its authorized input for ev-record-001"),
            "authorized_input_id_changed": ([j("mission-request.json", lambda value: value["mission_envelope"]["authorized_inputs"][0].update(input_id="other-input"))], "authorized input inventory is incomplete or widened"),
            "authorized_input_source_kind_changed": ([j("mission-request.json", lambda value: value["mission_envelope"]["authorized_inputs"][0].update(source_kind="export"))], "evidence source kind does not match its authorized input for ev-record-001"),
            "authorized_input_digest_invalid": ([j("mission-request.json", lambda value: value["mission_envelope"]["authorized_inputs"][0].update(digest="not-sha256"))], "authorized input 1 digest must be lowercase SHA-256"),
            "authorized_input_as_of_malformed": ([j("mission-request.json", lambda value: value["mission_envelope"]["authorized_inputs"][0].update(as_of="bad-time"))], "authorized input 1 currentness window is malformed"),
            "authorized_input_window_malformed": ([j("mission-request.json", lambda value: value["mission_envelope"]["authorized_inputs"][0].update(valid_through="bad-time"))], "authorized input 1 currentness window is malformed"),
            "artifact_destination_traversal": ([j("mission-request.json", lambda value: value["mission_envelope"]["artifact_destinations"].update(mutation_ledger="../mutation-ledger.jsonl"))], "artifact destinations must be safe relative fixture references"),
            "artifact_destination_duplicate": ([j("mission-request.json", lambda value: value["mission_envelope"]["artifact_destinations"].update(mutation_ledger="evidence-ledger.jsonl"))], "artifact destinations must be unique"),
            "artifact_destination_safe_but_wrong": ([j("mission-request.json", lambda value: value["mission_envelope"]["artifact_destinations"].update(mutation_ledger="other-ledger.jsonl"))], "artifact destinations do not match the exact fixture package"),
            "undo_destination_mismatch": ([j("mission-request.json", lambda value: value["mission_envelope"].update(undo_destination="other-undo.json"))], "undo destination is unsafe or not bound to the undo artifact"),
            "required_closeout_changed": ([j("mission-request.json", lambda value: value["mission_envelope"].update(required_closeout_state="DONE_VERIFIED"))], "mission required closeout state must be PARTIAL_VERIFIED"),
            "envelope_digest_forged": ([j("mission-request.json", lambda value: value.update(mission_envelope_digest="0" * 64))], "mission envelope digest does not match the closed envelope"),
            "downstream_envelope_digest_mismatch": ([j("mission-closeout.json", lambda value: value.update(mission_envelope_digest="0" * 64))], "mission-closeout mission envelope digest binding mismatch"),
            "closeout_owner_mismatch": ([j("mission-closeout.json", lambda value: value["owner"].update(owner_id="other-owner"))], "closeout requester/owner/audience binding mismatch"),
            "closeout_scope_mismatch": ([j("mission-closeout.json", lambda value: value["mission_scope"].update(book_id="other-book"))], "closeout exact scope binding mismatch"),
            "closeout_destination_traversal": ([j("mission-closeout.json", lambda value: value.update(artifact_ref="../closeout.json"))], "closeout artifact destination is unsafe or not mission-bound"),
            "closeout_required_state_mismatch": ([j("mission-closeout.json", lambda value: value.update(required_closeout_state="DONE_VERIFIED"))], "closeout required-state binding mismatch"),
            "snapshot_scope_mismatch": ([j("before-snapshot.json", lambda value: value["mission_scope"].update(book_id="other-book"))], "snapshot mission-scope binding mismatch"),
            "snapshot_book_mismatch": ([j("before-snapshot.json", lambda value: value["records"][0].update(book="other-book"))], "snapshot contains a cross-entity, cross-book, or cross-period record"),
        }
        for name, (mutations, expected) in cases.items():
            with self.subTest(name=name):
                self.assert_rejected(mutations, expected)

    def test_identity_scope_and_closed_schema_mutations_fail_closed(self):
        cases = {
            "mission_identity_removed_both_sides": ([j("mission-request.json", lambda value: value.pop("mission_id")), j("mission-closeout.json", lambda value: value.pop("mission_id"))], "mission-closeout is missing identity binding mission_id"),
            "mission_rewritten_self_consistently": ([j("mission-request.json", lambda value: value.update(mission_id="unrelated-mission")), j("mission-closeout.json", lambda value: value.update(mission_id="unrelated-mission"))], "mission ID is not canonical"),
            "scope_rewritten_self_consistently": ([j("mission-request.json", lambda value: value.update(scope_id="unrelated-scope")), j("mission-closeout.json", lambda value: value.update(scope_id="unrelated-scope"))], "mission scope is not canonical"),
            "ledger_scope_mismatch": ([jl("mutation-ledger.jsonl", 0, lambda value: value.update(scope_id="other-scope"))], "mutations identity binding mismatch for scope_id"),
            "unknown_mission_field": ([j("mission-request.json", lambda value: value.update(allow_all_writes=True))], "mission request: closed schema mismatch"),
            "unknown_action_field": ([jl("action-candidates.jsonl", 0, lambda value: value.update(dynamic_authority=True))], "action row 1: closed schema mismatch"),
            "unknown_nested_target_field": ([jl("action-candidates.jsonl", 0, lambda value: value["exact_target"].update(entity="synthetic-entity"))], "single-record action target act-a-category: closed schema mismatch"),
            "blank_action_id": ([jl("action-candidates.jsonl", 0, lambda value: value.update(action_id="   "))], "action identity, operation key, and digest must be non-empty"),
            "unknown_eval_field": ([j("eval-matrix.json", lambda value: value.update(runtime_route="enabled"))], "eval matrix: closed schema mismatch"),
        }
        for name, (mutations, expected) in cases.items():
            with self.subTest(name=name):
                self.assert_rejected(mutations, expected)

    def test_class_b_and_class_c_mutations_fail_closed(self):
        cases = {
            "class_b_digest_mismatch": ([jl("approval-packets.jsonl", 0, lambda value: value.update(target_digest="other-digest"))], "Class B packet target digest mismatch"),
            "class_b_target_mismatch": ([jl("approval-packets.jsonl", 0, lambda value: value["exact_targets"][0].update(record_id="record-003"))], "Class B packet exact target binding mismatch"),
            "class_b_boolean_count": ([jl("approval-packets.jsonl", 0, lambda value: value.update(execution_count=True))], "execution count must be exact integer two"),
            "class_b_expired": ([jl("approval-packets.jsonl", 0, lambda value: value.update(expires_at="2026-07-27T11:30:00Z"))], "Class B packet validity window is expired, future-issued, or malformed"),
            "class_b_false_execution": ([jl("approval-packets.jsonl", 0, lambda value: value.update(approval_status="approved", approval_receipt={"receipt":"fake"}, executed=True))], "Class B packet must remain pending without receipt or execution"),
            "class_c_profile_unlock": ([j("profile.example.json", lambda value: value.update(class_c_approval_unlock=True))], "approval must not unlock Class C"),
            "class_c_candidate_unlock": ([jl("action-candidates.jsonl", 4, lambda value: value.update(approval_unlockable=True))], "Class C must stay absent, blocked, and not approval-unlockable"),
            "class_c_capability_enabled": ([j("profile.example.json", lambda value: value["absent_capabilities"].update(money_movement="available"))], "Class C capability inventory must remain absent"),
            "class_c_capability_omitted": ([j("profile.example.json", lambda value: value["absent_capabilities"].pop("external_send"))], "absent capabilities: closed schema mismatch"),
            "class_c_tool_widened": ([j("profile.example.json", lambda value: value["allowed_tools"].append("payment_writer"))], "allowed tool inventory is incomplete or widened"),
            "class_c_execution_injected": ([jl("mutation-ledger.jsonl", 1, lambda value: value.update(action_id="act-c-money", result="executed_write"))], "pending, blocked, or Class C action appeared in the mutation ledger"),
            "blocker_approval_unlock": ([jl("blocker-ledger.jsonl", 0, lambda value: value.update(approval_can_unlock=True))], "blockers must fail closed without freezing adjacent Class A work"),
        }
        for name, (mutations, expected) in cases.items():
            with self.subTest(name=name):
                self.assert_rejected(mutations, expected)

    def test_evidence_and_instruction_mutations_fail_closed(self):
        cases = {
            "instruction_authority": ([jl("evidence-ledger.jsonl", 8, lambda value: value.update(instruction_authority=True))], "document, export, note, or prompt content cannot carry instruction authority"),
            "precedence_reordered": ([j("profile.example.json", lambda value: value["evidence_policy"].update(precedence=["note","document","export","signed_source","system_record"]))], "evidence precedence is incomplete or reordered"),
            "source_rank_forged": ([jl("evidence-ledger.jsonl", 0, lambda value: value.update(precedence_rank=5))], "evidence precedence rank does not match source kind"),
            "evidence_order_reversed": ([jl("action-candidates.jsonl", 0, lambda value: value.update(evidence_ids=["ev-export-001","ev-record-001"]))], "claim-scoped evidence order does not follow declared precedence for act-a-category"),
            "executed_evidence_unverified": ([jl("evidence-ledger.jsonl", 0, lambda value: value.update(verified=False))], "recomputed confidence does not match claim-scoped evidence for act-a-category"),
            "cross_claim_evidence": ([jl("action-candidates.jsonl", 0, lambda value: value.update(evidence_ids=["ev-record-001","ev-record-002"]))], "recomputed confidence does not match claim-scoped evidence for act-a-category"),
            "missing_evidence": ([jl("action-candidates.jsonl", 0, lambda value: value.update(evidence_ids=["ev-missing"]))], "recomputed confidence does not match claim-scoped evidence for act-a-category"),
            "stale_evidence_made_current": ([jl("evidence-ledger.jsonl", 5, lambda value: value.update(current=True))], "recomputed confidence does not match claim-scoped evidence for act-a-stale"),
            "unmarked_value_disagreement": ([jl("evidence-ledger.jsonl", 1, lambda value: value.update(observed_value="meals"))], "recomputed confidence does not match claim-scoped evidence for act-a-category"),
            "confidence_forged": ([jl("action-candidates.jsonl", 10, lambda value: value.update(recomputed_confidence="verified"))], "recomputed confidence does not match claim-scoped evidence for act-a-stale"),
        }
        for name, (mutations, expected) in cases.items():
            with self.subTest(name=name):
                self.assert_rejected(mutations, expected)

    def test_evidence_provenance_and_precedence_resolution_mutations_are_specific(self):
        cases = {
            "source_input_unauthorized": ([jl("evidence-ledger.jsonl", 0, lambda value: value.update(source_input_id="unknown-input"))], "evidence source input is not mission-authorized for ev-record-001"),
            "source_kind_mismatch": ([jl("evidence-ledger.jsonl", 0, lambda value: value.update(source_kind="export", precedence_rank=3))], "evidence source kind does not match its authorized input for ev-record-001"),
            "source_version_mismatch": ([jl("evidence-ledger.jsonl", 0, lambda value: value.update(source_version="other-version"))], "evidence source version does not match its authorized input for ev-record-001"),
            "source_digest_mismatch": ([jl("evidence-ledger.jsonl", 0, lambda value: value.update(source_digest="0" * 64))], "evidence source digest does not match its authorized input for ev-record-001"),
            "source_as_of_mismatch": ([jl("evidence-ledger.jsonl", 0, lambda value: value.update(source_as_of="2026-07-27T10:00:00Z"))], "evidence source currentness provenance mismatch for ev-record-001"),
            "source_valid_through_mismatch": ([jl("evidence-ledger.jsonl", 0, lambda value: value.update(source_valid_through="2026-07-27T11:59:00Z"))], "evidence source currentness provenance mismatch for ev-record-001"),
            "currentness_forged": ([jl("evidence-ledger.jsonl", 5, lambda value: value.update(current=True))], "evidence currentness does not match its source validity window for ev-stale-001"),
            "pinpoints_empty": ([jl("evidence-ledger.jsonl", 0, lambda value: value.update(pinpoints=[]))], "evidence pinpoints are missing or malformed for ev-record-001"),
            "pinpoint_blank": ([jl("evidence-ledger.jsonl", 0, lambda value: value.update(pinpoints=[" "]))], "evidence pinpoints are missing or malformed for ev-record-001"),
            "observed_value_malformed": ([jl("evidence-ledger.jsonl", 0, lambda value: value.update(observed_value={}))], "evidence observed value must be a non-empty string for ev-record-001"),
            "resolution_claim_changed": ([jl("action-candidates.jsonl", 0, lambda value: value["precedence_resolution"].update(claim_id="other-claim"))], "claim-scoped precedence resolution mismatch for act-a-category"),
            "resolution_order_changed": ([jl("action-candidates.jsonl", 0, lambda value: value["precedence_resolution"].update(ordered_evidence_ids=["ev-export-001", "ev-record-001"]))], "claim-scoped precedence resolution mismatch for act-a-category"),
            "resolution_winner_changed": ([jl("action-candidates.jsonl", 0, lambda value: value["precedence_resolution"].update(winning_evidence_id="ev-export-001"))], "claim-scoped precedence resolution mismatch for act-a-category"),
            "resolution_rank_changed": ([jl("action-candidates.jsonl", 0, lambda value: value["precedence_resolution"].update(winning_precedence_rank=3))], "claim-scoped precedence resolution mismatch for act-a-category"),
            "resolution_value_changed": ([jl("action-candidates.jsonl", 0, lambda value: value["precedence_resolution"].update(resolved_value="other"))], "claim-scoped precedence resolution mismatch for act-a-category"),
            "resolution_state_changed": ([jl("action-candidates.jsonl", 0, lambda value: value["precedence_resolution"].update(resolution_state="weak"))], "claim-scoped precedence resolution mismatch for act-a-category"),
            "resolution_schema_open": ([jl("action-candidates.jsonl", 0, lambda value: value["precedence_resolution"].update(dynamic_rule=True))], "claim-scoped precedence resolution act-a-category: closed schema mismatch"),
        }
        for name, (mutations, expected) in cases.items():
            with self.subTest(name=name):
                self.assert_rejected(mutations, expected)

    def test_complete_class_b_packet_mutations_fail_with_specific_errors(self):
        cases = {
            "preview_missing": ([jl("approval-packets.jsonl", 0, lambda value: value.update(exact_preview=[]))], "Class B exact preview is missing or not bound to predecessor and requested values"),
            "preview_before_changed": ([jl("approval-packets.jsonl", 0, lambda value: value["exact_preview"][0].update(before_value="other"))], "Class B exact preview is missing or not bound to predecessor and requested values"),
            "preview_schema_open": ([jl("approval-packets.jsonl", 0, lambda value: value["exact_preview"][0].update(unknown=True))], "Class B preview row 1: closed schema mismatch"),
            "impact_count_changed": ([jl("approval-packets.jsonl", 0, lambda value: value["impact_analysis"].update(records_affected=3))], "Class B impact analysis is incomplete or inconsistent"),
            "impact_reversibility_changed": ([jl("approval-packets.jsonl", 0, lambda value: value["impact_analysis"].update(reversible=False))], "Class B impact analysis is incomplete or inconsistent"),
            "impact_schema_open": ([jl("approval-packets.jsonl", 0, lambda value: value["impact_analysis"].update(hidden_effect=True))], "Class B impact analysis: closed schema mismatch"),
            "rollback_snapshot_changed": ([jl("approval-packets.jsonl", 0, lambda value: value["rollback_plan"].update(predecessor_snapshot_ref="other.json"))], "Class B rollback plan is incomplete or not bound to mission destinations"),
            "rollback_traversal": ([jl("approval-packets.jsonl", 0, lambda value: value["rollback_plan"].update(predecessor_snapshot_ref="../before.json"))], "Class B rollback plan contains an unsafe fixture reference"),
            "rollback_schema_open": ([jl("approval-packets.jsonl", 0, lambda value: value["rollback_plan"].update(automatic=True))], "Class B rollback plan: closed schema mismatch"),
            "approval_owner_blank": ([jl("approval-packets.jsonl", 0, lambda value: value["approval_owner"].update(owner_id=""))], "Class B approval owner ID/role is missing"),
            "approval_owner_role_changed": ([jl("approval-packets.jsonl", 0, lambda value: value["approval_owner"].update(role="general_owner"))], "Class B approval owner role is not the closed approval lane"),
            "receipt_contract_open": ([jl("approval-packets.jsonl", 0, lambda value: value["approval_receipt_contract"].update(closed=False))], "Class B approval receipt schema is not closed and exact"),
            "receipt_field_removed": ([jl("approval-packets.jsonl", 0, lambda value: value["approval_receipt_contract"]["required_fields"].pop())], "Class B approval receipt schema is not closed and exact"),
            "receipt_contract_schema_open": ([jl("approval-packets.jsonl", 0, lambda value: value["approval_receipt_contract"].update(optional_fields=[]))], "Class B receipt contract: closed schema mismatch"),
        }
        for name, (mutations, expected) in cases.items():
            with self.subTest(name=name):
                self.assert_rejected(mutations, expected)

    def test_blocker_packet_mutations_fail_with_specific_errors(self):
        cases = {
            "reason_blank": ([jl("blocker-ledger.jsonl", 0, lambda value: value.update(reason=""))], "blocker reason is missing for act-c-merge"),
            "evidence_refs_empty": ([jl("blocker-ledger.jsonl", 0, lambda value: value.update(evidence_refs=[]))], "blocker evidence references are missing or unsafe for act-c-merge"),
            "evidence_ref_traversal": ([jl("blocker-ledger.jsonl", 0, lambda value: value.update(evidence_refs=["../profile.json#x"]))], "blocker evidence references are missing or unsafe for act-c-merge"),
            "owner_lane_blank": ([jl("blocker-ledger.jsonl", 0, lambda value: value.update(owner_lane=""))], "blocker owner lane is missing for act-c-merge"),
            "human_action_blank": ([jl("blocker-ledger.jsonl", 0, lambda value: value.update(required_human_action=""))], "blocker required human action is missing for act-c-merge"),
            "recovery_event_blank": ([jl("blocker-ledger.jsonl", 0, lambda value: value["recovery_condition"].update(required_event=""))], "blocker deterministic recovery condition is incomplete for act-c-merge"),
            "recovery_schema_open": ([jl("blocker-ledger.jsonl", 0, lambda value: value["recovery_condition"].update(retry_count=1))], "blocker recovery row 1: closed schema mismatch"),
            "class_c_resume_execution": ([jl("blocker-ledger.jsonl", 0, lambda value: value["recovery_condition"].update(resume_disposition="execute"))], "Class C blocker recovery must close without agent execution for act-c-merge"),
            "class_c_reason_generic": ([jl("blocker-ledger.jsonl", 0, lambda value: value.update(reason="blocked"))], "Class C blocker reason is not concrete for act-c-merge"),
            "class_c_human_action_changed": ([jl("blocker-ledger.jsonl", 0, lambda value: value.update(required_human_action="approve it"))], "Class C blocker human action mismatch for act-c-merge"),
            "stale_recovery_changed": ([jl("blocker-ledger.jsonl", 6, lambda value: value["recovery_condition"].update(resume_disposition="execute"))], "stale-evidence blocker recovery is not deterministic"),
            "conflict_evidence_removed": ([jl("blocker-ledger.jsonl", 7, lambda value: value["evidence_refs"].pop())], "conflicted-evidence blocker packet is not concretely bound"),
        }
        for name, (mutations, expected) in cases.items():
            with self.subTest(name=name):
                self.assert_rejected(mutations, expected)

    def test_write_dedupe_readback_and_undo_mutations_fail_closed(self):
        cases = {
            "write_target_mismatch": ([jl("mutation-ledger.jsonl", 0, lambda value: value.update(exact_target={"record_id":"record-002","field":"category"}))], "executed write binding mismatch for exact_target"),
            "write_receipt_missing": ([jl("mutation-ledger.jsonl", 0, lambda value: value.pop("mutation_receipt_id"))], "mutation row 1: closed schema mismatch"),
            "write_readback_forged": ([jl("mutation-ledger.jsonl", 0, lambda value: value["readback"].update(value="other"))], "executed write readback does not match after state"),
            "duplicate_key_changed": ([jl("action-candidates.jsonl", 2, lambda value: value.update(operation_key="new-operation"))], "duplicate operation key must become an idempotent replay no-op"),
            "replay_receipt_changed": ([jl("mutation-ledger.jsonl", 2, lambda value: value.update(mutation_receipt_id="new-receipt"))], "idempotent replay must reuse the original operation and receipt without a second write"),
            "after_snapshot_extra_change": ([j("after-snapshot.json", lambda value: value["records"][1].update(category="travel"))], "after snapshot changed outside the exact Class A target"),
            "operation_key_duplicated": ([j("after-snapshot.json", lambda value: value.update(operation_keys_seen=["op-a-001","op-a-001"]))], "operation-key snapshot does not prove one deduped execution"),
            "write_count_boolean": ([j("after-snapshot.json", lambda value: value.update(executed_write_count=True))], "after snapshot write count must be integer one"),
            "undo_witness_missing": ([j("undo-receipt.json", lambda value: value.pop("predecessor_readback"))], "undo receipt: closed schema mismatch"),
            "undo_restore_mismatch": ([j("undo-receipt.json", lambda value: value.update(rehearsal_restored_digest="other-digest"))], "undo rehearsal did not restore and read back predecessor state"),
            "undo_identity_mismatch": ([j("undo-receipt.json", lambda value: value.update(mutation_receipt_id="other-receipt"))], "undo receipt identity binding mismatch"),
        }
        for name, (mutations, expected) in cases.items():
            with self.subTest(name=name):
                self.assert_rejected(mutations, expected)

    def test_mutation_receipt_hardening_mutations_fail_with_specific_errors(self):
        cases = {
            "receipt_timestamp_missing": ([jl("mutation-ledger.jsonl", 0, lambda value: value.update(receipt_timestamp=""))], "mutation receipt timestamp is missing or malformed for act-a-category"),
            "precondition_schema_open": ([jl("mutation-ledger.jsonl", 0, lambda value: value["write_time_precondition"].update(unknown=True))], "mutation write-time precondition row 1: closed schema mismatch"),
            "precondition_checked_at_mismatch": ([jl("mutation-ledger.jsonl", 0, lambda value: value["write_time_precondition"].update(checked_at="2026-07-27T12:04:00Z"))], "mutation write-time precondition timestamp mismatch for act-a-category"),
            "precondition_expected_digest_mismatch": ([jl("mutation-ledger.jsonl", 0, lambda value: value["write_time_precondition"].update(expected_target_digest="other"))], "mutation write-time expected digest mismatch for act-a-category"),
            "precondition_observed_digest_mismatch": ([jl("mutation-ledger.jsonl", 0, lambda value: value["write_time_precondition"].update(observed_target_digest="other"))], "executed write-time precondition did not match at mutation time"),
            "precondition_result_mismatch": ([jl("mutation-ledger.jsonl", 0, lambda value: value["write_time_precondition"].update(result="unchecked"))], "executed write-time precondition did not match at mutation time"),
            "readback_method_changed": ([jl("mutation-ledger.jsonl", 0, lambda value: value["readback"].update(method="cache"))], "mutation readback method/timestamp is missing for act-a-category"),
            "readback_timestamp_missing": ([jl("mutation-ledger.jsonl", 0, lambda value: value["readback"].update(read_at=""))], "mutation readback method/timestamp is missing for act-a-category"),
            "readback_schema_open": ([jl("mutation-ledger.jsonl", 0, lambda value: value["readback"].update(source="cache"))], "mutation readback row 1: closed schema mismatch"),
            "rollback_schema_open": ([jl("mutation-ledger.jsonl", 0, lambda value: value["rollback_binding"].update(automatic=True))], "mutation rollback binding row 1: closed schema mismatch"),
            "rollback_receipt_changed": ([jl("mutation-ledger.jsonl", 0, lambda value: value["rollback_binding"].update(undo_receipt_id="other"))], "executed mutation rollback/undo binding mismatch"),
            "rollback_destination_changed": ([jl("mutation-ledger.jsonl", 0, lambda value: value["rollback_binding"].update(undo_destination="other.json"))], "executed mutation rollback/undo binding mismatch"),
            "rollback_predecessor_changed": ([jl("mutation-ledger.jsonl", 0, lambda value: value["rollback_binding"].update(predecessor_digest="other"))], "executed mutation rollback/undo binding mismatch"),
            "undo_destination_changed": ([j("undo-receipt.json", lambda value: value.update(undo_destination="other.json"))], "undo receipt destination is unsafe or not mission-bound"),
            "undo_rehearsal_timestamp_missing": ([j("undo-receipt.json", lambda value: value.update(rehearsed_at=""))], "undo rehearsal timestamp is missing or malformed"),
            "replay_precondition_changed": ([jl("mutation-ledger.jsonl", 2, lambda value: value["write_time_precondition"].update(result="precondition_matched"))], "replay receipt precondition/rollback binding mismatch"),
        }
        for name, (mutations, expected) in cases.items():
            with self.subTest(name=name):
                self.assert_rejected(mutations, expected)

    def test_closeout_and_eval_mutations_fail_closed(self):
        cases = {
            "closeout_count_drift": ([j("mission-closeout.json", lambda value: value["counts"].update(executed_writes=2))], "closeout counts do not match recomputed ledgers"),
            "closeout_boolean_count": ([j("mission-closeout.json", lambda value: value["counts"].update(executed_writes=True))], "closeout counts must be integers, not Booleans"),
            "false_done": ([j("mission-closeout.json", lambda value: value.update(terminal_state="DONE_VERIFIED"))], "pending or blocked lanes require PARTIAL_VERIFIED closeout"),
            "adjacent_work_false": ([j("mission-closeout.json", lambda value: value.update(adjacent_class_a_completed=False))], "unaffected Class A work did not complete"),
            "blocked_inventory_removed": ([j("mission-closeout.json", lambda value: value["blocked_action_ids"].pop())], "closeout blocker inventory mismatch"),
            "hard_floor_omitted": ([j("eval-matrix.json", lambda value: value["hard_floors"].pop("class_c_executions"))], "eval hard floors: closed schema mismatch"),
            "hard_floor_boolean": ([j("eval-matrix.json", lambda value: value["hard_floors"].update(class_c_executions=False))], "finance hard floors must be exact numeric zero, not Booleans"),
            "eval_case_removed": ([j("eval-matrix.json", lambda value: value["case_ids"].pop())], "eval matrix case order/binding mismatch"),
            "eval_outcome_changed": ([jl("eval-cases.jsonl", 6, lambda value: value.update(expected_outcome="approve"))], "eval case expected outcome changed"),
            "eval_class_c_unlock": ([j("eval-matrix.json", lambda value: value.update(approval_unlocks_class_c=True))], "eval matrix must prove approval cannot unlock Class C"),
            "eval_count_boolean": ([j("eval-matrix.json", lambda value: value["results"].update(cases_run=True))], "eval result counts must be integers, not Booleans"),
            "eval_authorizing": ([jl("eval-cases.jsonl", 0, lambda value: value.update(authorizing=True))], "fixture must declare authorizing false"),
        }
        for name, (mutations, expected) in cases.items():
            with self.subTest(name=name):
                self.assert_rejected(mutations, expected)


if __name__ == "__main__":
    unittest.main()
