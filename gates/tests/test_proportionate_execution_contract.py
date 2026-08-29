import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[2]
FIXTURE = REPOSITORY / "examples/proportionate-execution-contract-v1"
SCRIPT = FIXTURE / "validate_fixture.py"
SPEC = importlib.util.spec_from_file_location("validate_proportionate_execution", SCRIPT)
assert SPEC is not None
assert SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def copy_fixture(temp: str) -> Path:
    target = Path(temp) / "fixture"
    shutil.copytree(FIXTURE, target)
    return target


def mutate_json(path: Path, mutation) -> None:
    value = json.loads(path.read_text(encoding="utf-8"))
    mutation(value)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row, separators=(",", ":")) + "\n" for row in rows), encoding="utf-8")


def mutate_jsonl(path: Path, row_index: int, mutation) -> None:
    rows = read_jsonl(path)
    mutation(rows[row_index])
    write_jsonl(path, rows)


class ProportionateExecutionContractTests(unittest.TestCase):
    def test_repository_fixture_passes(self):
        self.assertEqual(MODULE.validate(FIXTURE), [])

    def test_material_action_requires_accepted_mapping(self):
        with tempfile.TemporaryDirectory() as temp:
            fixture = copy_fixture(temp)
            mutate_jsonl(fixture / "action-ledger.jsonl", 3, lambda row: row.update(mapping=None))
            errors = MODULE.validate(fixture)
            self.assertTrue(any("material action is unmapped" in error for error in errors))

    def test_adjacent_finding_cannot_gain_current_work_authority(self):
        with tempfile.TemporaryDirectory() as temp:
            fixture = copy_fixture(temp)
            mutate_jsonl(
                fixture / "action-ledger.jsonl",
                1,
                lambda row: row.update(material=True, mapping="CLAIM-CONFIG-01", claim_state_before="open", claim_state_after="closed", disposition="executed"),
            )
            errors = MODULE.validate(fixture)
            self.assertTrue(any("adjacent finding gained current-work authority" in error for error in errors))

    def test_any_action_after_first_green_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            fixture = copy_fixture(temp)
            ledger = fixture / "action-ledger.jsonl"
            rows = read_jsonl(ledger)
            extra = dict(rows[1])
            extra.update(ordinal=6, action_id="ACT-ADJACENT-02", description="Another unrelated proposal.")
            rows.append(extra)
            write_jsonl(ledger, rows)
            mutate_json(fixture / "closeout-receipt.json", lambda value: value.update(adjacent_findings_parked=2))
            errors = MODULE.validate(fixture)
            self.assertTrue(any("action ledger continued after first green" in error for error in errors))

    def test_float_ordinal_cannot_bypass_post_green_detection(self):
        with tempfile.TemporaryDirectory() as temp:
            fixture = copy_fixture(temp)
            ledger = fixture / "action-ledger.jsonl"
            rows = read_jsonl(ledger)
            extra = dict(rows[1])
            extra.update(ordinal=6.0, action_id="ACT-ADJACENT-02", description="A float-ordinal proposal after first green.")
            rows.append(extra)
            write_jsonl(ledger, rows)
            mutate_json(fixture / "closeout-receipt.json", lambda value: value.update(adjacent_findings_parked=2))
            errors = MODULE.validate(fixture)
            self.assertTrue(any("ordinals must be exact non-Boolean integers" in error for error in errors))

    def test_boolean_and_float_ordinals_are_rejected_even_when_equal_to_integers(self):
        for row_index, invalid_ordinal in ((0, True), (4, 5.0)):
            with self.subTest(invalid_ordinal=invalid_ordinal), tempfile.TemporaryDirectory() as temp:
                fixture = copy_fixture(temp)
                mutate_jsonl(fixture / "action-ledger.jsonl", row_index, lambda row: row.update(ordinal=invalid_ordinal))
                errors = MODULE.validate(fixture)
                self.assertTrue(any("ordinals must be exact non-Boolean integers" in error for error in errors))

    def test_reported_first_green_must_match_recomputed_lifecycle(self):
        with tempfile.TemporaryDirectory() as temp:
            fixture = copy_fixture(temp)
            mutate_json(fixture / "closeout-receipt.json", lambda value: value.update(first_green_ordinal=999))
            errors = MODULE.validate(fixture)
            self.assertTrue(any("first green does not match recomputed" in error for error in errors))

    def test_duplicate_claim_closure_cannot_leave_gate_unwitnessed(self):
        with tempfile.TemporaryDirectory() as temp:
            fixture = copy_fixture(temp)
            mutate_jsonl(
                fixture / "action-ledger.jsonl",
                4,
                lambda row: row.update(mapping="CLAIM-CONFIG-01", claim_state_before="closed"),
            )
            errors = MODULE.validate(fixture)
            self.assertTrue(any("claim was already closed" in error for error in errors))
            self.assertTrue(any("not every accepted claim or gate was closed" in error for error in errors))

    def test_demoted_mutation_cannot_close_claim(self):
        with tempfile.TemporaryDirectory() as temp:
            fixture = copy_fixture(temp)
            mutate_jsonl(fixture / "action-ledger.jsonl", 3, lambda row: row.update(material=False))
            errors = MODULE.validate(fixture)
            self.assertTrue(any("non-material action changed claim state" in error for error in errors))
            self.assertTrue(any("not every accepted claim or gate was closed" in error for error in errors))

    def test_executed_action_requires_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            fixture = copy_fixture(temp)
            mutate_jsonl(fixture / "action-ledger.jsonl", 3, lambda row: row.update(evidence=""))
            errors = MODULE.validate(fixture)
            self.assertTrue(any("identity, description, or evidence is empty" in error for error in errors))

    def test_closeout_cannot_omit_an_accepted_gate(self):
        with tempfile.TemporaryDirectory() as temp:
            fixture = copy_fixture(temp)
            mutate_json(fixture / "closeout-receipt.json", lambda value: value.update(closed_claim_ids=["CLAIM-CONFIG-01"]))
            errors = MODULE.validate(fixture)
            self.assertTrue(any("closed claims do not exactly match witnessed lifecycle" in error for error in errors))

    def test_changed_surface_must_stay_allowed(self):
        with tempfile.TemporaryDirectory() as temp:
            fixture = copy_fixture(temp)
            mutate_json(fixture / "closeout-receipt.json", lambda value: value["changed_surfaces"].append("scheduler behavior"))
            errors = MODULE.validate(fixture)
            self.assertTrue(any("changed surface escaped allowed scope" in error for error in errors))

    def test_allowed_and_protected_surfaces_cannot_overlap(self):
        with tempfile.TemporaryDirectory() as temp:
            fixture = copy_fixture(temp)
            mutate_json(fixture / "task-contract.json", lambda value: value["allowed_surfaces"].append("scheduler behavior"))
            mutate_json(fixture / "closeout-receipt.json", lambda value: value["changed_surfaces"].append("scheduler behavior"))
            errors = MODULE.validate(fixture)
            self.assertTrue(any("allowed and protected surfaces overlap" in error for error in errors))
            self.assertTrue(any("changed surface overlaps a protected surface" in error for error in errors))

    def test_post_green_action_must_stay_in_closeout_allowlist(self):
        with tempfile.TemporaryDirectory() as temp:
            fixture = copy_fixture(temp)
            mutate_json(fixture / "closeout-receipt.json", lambda value: value["post_green_actions"].append("launch another review"))
            errors = MODULE.validate(fixture)
            self.assertTrue(any("post-green action escaped bounded closeout allowlist" in error for error in errors))

    def test_synthetic_config_witness_must_show_exact_change(self):
        with tempfile.TemporaryDirectory() as temp:
            fixture = copy_fixture(temp)
            mutate_json(fixture / "synthetic-config-after.json", lambda value: value.update(scheduler_mode="hourly"))
            errors = MODULE.validate(fixture)
            self.assertTrue(any("unexpected key changed" in error for error in errors))
            self.assertTrue(any("protected configuration changed" in error for error in errors))

    def test_runtime_enforcement_remains_optional_in_prompt_only_fixture(self):
        with tempfile.TemporaryDirectory() as temp:
            fixture = copy_fixture(temp)
            mutate_json(fixture / "task-contract.json", lambda value: value.update(runtime_enforcement_required=True))
            errors = MODULE.validate(fixture)
            self.assertTrue(any("runtime enforcement must remain optional" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
