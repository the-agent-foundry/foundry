import importlib.util
import hashlib
import json
import unittest
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[2]
SCRIPT = REPOSITORY / "gates/scripts/fixture_smoke.py"
SPEC = importlib.util.spec_from_file_location("fixture_smoke_finance", SCRIPT)
assert SPEC is not None
assert SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
FIXTURE = REPOSITORY / "examples/finance-control-v1"


class FinanceFixtureTests(unittest.TestCase):
    def test_finance_fixture_passes_closed_validator(self):
        errors: list[str] = []
        MODULE.validate_finance(REPOSITORY / "examples", errors)
        self.assertEqual(errors, [])

    def test_mixed_mission_closeout_matches_contract(self):
        closeout = json.loads((FIXTURE / "mission-closeout.json").read_text())
        self.assertEqual(closeout["terminal_state"], "PARTIAL_VERIFIED")
        self.assertEqual(
            closeout["counts"],
            {
                "executed_writes": 1,
                "already_satisfied_noops": 1,
                "idempotent_replay_noops": 1,
                "awaiting_class_b_approval": 1,
                "blocked_or_unresolved": 8,
                "external_sends": 0,
                "money_movements": 0,
                "class_c_executions": 0,
            },
        )
        self.assertTrue(closeout["adjacent_class_a_completed"])
        self.assertFalse(closeout["live_system_affected"])

    def test_only_prebound_class_a_write_executed(self):
        mission = json.loads((FIXTURE / "mission-request.json").read_text())
        mutations = MODULE.load_jsonl(FIXTURE / "mutation-ledger.jsonl")
        executed = [row for row in mutations if row["result"] == "executed_write"]
        self.assertEqual(len(executed), 1)
        self.assertEqual(executed[0]["action_id"], mission["write_grant"]["action_id"])
        self.assertEqual(executed[0]["write_grant_id"], mission["write_grant"]["grant_id"])
        self.assertEqual(executed[0]["verification"], "passed")

    def test_class_b_is_pending_and_class_c_is_absent(self):
        profile = json.loads((FIXTURE / "profile.example.json").read_text())
        approvals = MODULE.load_jsonl(FIXTURE / "approval-packets.jsonl")
        actions = MODULE.load_jsonl(FIXTURE / "action-candidates.jsonl")
        self.assertEqual(len(approvals), 1)
        self.assertEqual(approvals[0]["approval_status"], "pending")
        self.assertIsNone(approvals[0]["approval_receipt"])
        self.assertFalse(approvals[0]["executed"])
        class_c = [row for row in actions if row["action_class"] == "C"]
        self.assertEqual(len(class_c), 6)
        self.assertTrue(all(row["status"] == "blocked_capability_absent" for row in class_c))
        self.assertTrue(all(not row["approval_unlockable"] for row in class_c))
        self.assertTrue(all(value == "absent" for value in profile["absent_capabilities"].values()))

    def test_document_instruction_is_non_authorizing_evidence(self):
        evidence = MODULE.load_jsonl(FIXTURE / "evidence-ledger.jsonl")
        injected = next(row for row in evidence if row["evidence_id"] == "ev-injected-note")
        self.assertIn("bypass controls", injected["observed_value"])
        self.assertFalse(injected["instruction_authority"])
        self.assertFalse(injected["verified"])

    def test_undo_rehearsal_restores_predecessor(self):
        undo = json.loads((FIXTURE / "undo-receipt.json").read_text())
        self.assertTrue(undo["rehearsal_executed"])
        self.assertEqual(undo["rehearsal_restored_value"], undo["before_value"])
        self.assertEqual(undo["rehearsal_restored_digest"], undo["before_digest"])
        self.assertEqual(undo["predecessor_readback"], "passed")
        self.assertFalse(undo["live_system_affected"])

    def test_mission_envelope_is_closed_digest_bound_and_destination_safe(self):
        mission = json.loads((FIXTURE / "mission-request.json").read_text())
        envelope = mission["mission_envelope"]
        raw_digest = hashlib.sha256(
            json.dumps(envelope, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        digest = "sha256:" + ":".join(raw_digest[index:index + 2] for index in range(0, 64, 2))
        self.assertEqual(mission["mission_envelope_digest"], digest)
        self.assertEqual(envelope["audience"]["audience_id"], envelope["owner"]["owner_id"])
        self.assertEqual(
            envelope["scope"],
            {
                "entity_id": "synthetic-entity",
                "book_id": "synthetic-book",
                "period_id": "2026-Q2",
                "target_system": "synthetic-ledger",
            },
        )
        self.assertTrue(all(".." not in value and not value.startswith("/") for value in envelope["artifact_destinations"].values()))
        self.assertEqual(envelope["undo_destination"], envelope["artifact_destinations"]["undo_receipt"])
        self.assertEqual(envelope["required_closeout_state"], "PARTIAL_VERIFIED")

    def test_evidence_provenance_and_claim_precedence_are_explicit(self):
        mission = json.loads((FIXTURE / "mission-request.json").read_text())
        evidence = MODULE.load_jsonl(FIXTURE / "evidence-ledger.jsonl")
        actions = MODULE.load_jsonl(FIXTURE / "action-candidates.jsonl")
        authorized = {row["input_id"]: row for row in mission["mission_envelope"]["authorized_inputs"]}
        for row in evidence:
            source = authorized[row["source_input_id"]]
            self.assertEqual(row["source_version"], source["version"])
            self.assertEqual(row["source_digest"], source["digest"])
            self.assertEqual(row["source_as_of"], source["as_of"])
            self.assertTrue(row["pinpoints"])
        executed = next(row for row in actions if row["action_id"] == "act-a-category")
        self.assertEqual(executed["precedence_resolution"]["winning_evidence_id"], "ev-record-001")
        self.assertEqual(executed["precedence_resolution"]["resolution_state"], "verified")

    def test_class_b_packet_has_preview_impact_rollback_owner_and_closed_receipt_contract(self):
        packet = MODULE.load_jsonl(FIXTURE / "approval-packets.jsonl")[0]
        self.assertEqual(len(packet["exact_preview"]), packet["execution_count"])
        self.assertEqual(packet["impact_analysis"]["records_affected"], packet["execution_count"])
        self.assertTrue(packet["impact_analysis"]["reversible"])
        self.assertEqual(packet["rollback_plan"]["predecessor_snapshot_ref"], "before-snapshot.json")
        self.assertEqual(packet["approval_owner"]["role"], "finance_approval_owner")
        self.assertTrue(packet["approval_receipt_contract"]["closed"])
        self.assertIsNone(packet["approval_receipt"])
        self.assertFalse(packet["executed"])

    def test_blocker_packets_are_actionable_and_class_c_never_resumes_execution(self):
        blockers = MODULE.load_jsonl(FIXTURE / "blocker-ledger.jsonl")
        for blocker in blockers:
            self.assertTrue(blocker["reason"])
            self.assertTrue(blocker["evidence_refs"])
            self.assertTrue(blocker["owner_lane"])
            self.assertTrue(blocker["required_human_action"])
            self.assertTrue(blocker["recovery_condition"]["verification_rule"])
        class_c = [row for row in blockers if row["blocker_type"] == "capability_absent"]
        self.assertTrue(all(row["recovery_condition"]["resume_disposition"] == "close_blocker_without_agent_execution" for row in class_c))

    def test_mutation_receipt_binds_timestamp_precondition_readback_and_undo(self):
        mutation = MODULE.load_jsonl(FIXTURE / "mutation-ledger.jsonl")[0]
        undo = json.loads((FIXTURE / "undo-receipt.json").read_text())
        self.assertTrue(mutation["receipt_timestamp"].endswith("Z"))
        self.assertEqual(mutation["write_time_precondition"]["result"], "precondition_matched")
        self.assertEqual(mutation["readback"]["method"], "synthetic_system_of_record_readback")
        self.assertEqual(mutation["rollback_binding"]["undo_receipt_id"], undo["undo_receipt_id"])
        self.assertEqual(mutation["rollback_binding"]["undo_destination"], undo["undo_destination"])


if __name__ == "__main__":
    unittest.main()
