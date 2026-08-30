import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[2]
FIXTURE = REPOSITORY / "examples/progressive-specification-jigsaw-v1"
SCRIPT = FIXTURE / "validate_fixture.py"
SPEC = importlib.util.spec_from_file_location("validate_progressive_specification_jigsaw", SCRIPT)
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


class ProgressiveSpecificationJigsawTests(unittest.TestCase):
    def test_repository_fixture_passes(self):
        self.assertEqual(MODULE.validate(FIXTURE), [])

    def test_charter_byte_drift_breaks_exact_approval_binding(self):
        with tempfile.TemporaryDirectory() as temp:
            fixture = copy_fixture(temp)
            charter = fixture / "CHARTER.md"
            charter.write_text(charter.read_text(encoding="utf-8") + "\nChanged after approval.\n", encoding="utf-8")
            errors = MODULE.validate(fixture)
            self.assertTrue(any("not exact byte copies" in error for error in errors))
            self.assertTrue(any("frozen synthetic identity" in error for error in errors))

    def test_specification_rewrite_cannot_self_validate_by_updating_receipts(self):
        with tempfile.TemporaryDirectory() as temp:
            fixture = copy_fixture(temp)
            replacement = (fixture / "CHARTER.md").read_text(encoding="utf-8").replace("small internal booking application", "large public marketplace")
            (fixture / "CHARTER.md").write_text(replacement, encoding="utf-8")
            (fixture / "PHASE-0-SPECIFICATION.md").write_text(replacement, encoding="utf-8")
            digest = MODULE.sha256_bytes(replacement.encode("utf-8"))
            digest_chunks = [digest[index:index + 16] for index in range(0, 64, 16)]
            mutate_json(
                fixture / "charter-lock.json",
                lambda value: (
                    value.update(specification_sha256_chunks=digest_chunks, charter_sha256_chunks=digest_chunks),
                    value["owner_approval"].update(approved_specification_sha256_chunks=digest_chunks),
                ),
            )
            errors = MODULE.validate(fixture)
            self.assertTrue(any("frozen synthetic identity" in error for error in errors))

    def test_joint_omission_of_required_lock_field_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            fixture = copy_fixture(temp)
            mutate_json(fixture / "charter-lock.json", lambda value: value.pop("execution_authority"))
            errors = MODULE.validate(fixture)
            self.assertTrue(any("missing keys" in error and "execution_authority" in error for error in errors))

    def test_piece_requires_nonempty_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            fixture = copy_fixture(temp)
            mutate_jsonl(fixture / "decision-pieces.jsonl", 0, lambda value: value.update(evidence=[]))
            errors = MODULE.validate(fixture)
            self.assertTrue(any("evidence must be a unique non-empty string list" in error for error in errors))

    def test_piece_cannot_gain_execution_authority(self):
        with tempfile.TemporaryDirectory() as temp:
            fixture = copy_fixture(temp)
            mutate_jsonl(fixture / "decision-pieces.jsonl", 1, lambda value: value.update(execution_authority=True))
            errors = MODULE.validate(fixture)
            self.assertTrue(any("execution authority widened" in error for error in errors))

    def test_piece_dependencies_must_be_ordered(self):
        with tempfile.TemporaryDirectory() as temp:
            fixture = copy_fixture(temp)
            rows = read_jsonl(fixture / "decision-pieces.jsonl")
            rows[0]["dependencies"] = ["PIECE-INTEGRATION-01"]
            write_jsonl(fixture / "decision-pieces.jsonl", rows)
            errors = MODULE.validate(fixture)
            self.assertTrue(any("dependency is missing or not dependency-ordered" in error for error in errors))

    def test_integration_requires_complete_check_set(self):
        with tempfile.TemporaryDirectory() as temp:
            fixture = copy_fixture(temp)
            mutate_json(fixture / "integration-sweep.json", lambda value: value["checks"].pop())
            errors = MODULE.validate(fixture)
            self.assertTrue(any("required check set drift" in error for error in errors))

    def test_boolean_or_float_generation_cannot_pass_as_integer(self):
        for invalid in (True, 1.0):
            with self.subTest(invalid=invalid), tempfile.TemporaryDirectory() as temp:
                fixture = copy_fixture(temp)
                mutate_json(fixture / "integration-sweep.json", lambda value: value.update(generation=invalid))
                errors = MODULE.validate(fixture)
                self.assertTrue(any("generation must be exact integer 1" in error for error in errors))

    def test_build_cells_must_cover_every_requirement(self):
        with tempfile.TemporaryDirectory() as temp:
            fixture = copy_fixture(temp)
            mutate_json(
                fixture / "BUILD-SPEC.json",
                lambda value: value["cells"][1].update(requirement_ids=["REQ-003"]),
            )
            errors = MODULE.validate(fixture)
            self.assertTrue(any("requirement coverage is incomplete" in error for error in errors))

    def test_build_dependencies_must_be_topological(self):
        with tempfile.TemporaryDirectory() as temp:
            fixture = copy_fixture(temp)
            mutate_json(
                fixture / "BUILD-SPEC.json",
                lambda value: value["cells"][0].update(dependencies=["CELL-SCHEDULE-01"]),
            )
            errors = MODULE.validate(fixture)
            self.assertTrue(any("dependency is missing or not dependency-ordered" in error for error in errors))

    def test_allowed_and_protected_surfaces_cannot_overlap(self):
        with tempfile.TemporaryDirectory() as temp:
            fixture = copy_fixture(temp)
            def overlap(value):
                value["cells"][0]["allowed_surfaces"].append(value["cells"][0]["protected_surfaces"][0])
            mutate_json(fixture / "BUILD-SPEC.json", overlap)
            errors = MODULE.validate(fixture)
            self.assertTrue(any("allowed and protected surfaces overlap" in error for error in errors))

    def test_build_or_handoff_authority_cannot_be_widened(self):
        mutations = (
            ("BUILD-SPEC.json", lambda value: value.update(build_started=True, builder_launch_authorized=True)),
            ("STATUS.json", lambda value: value.update(build_started=True, execution_authority=True)),
            ("final-readiness.json", lambda value: value.update(builder_handoff_authorized=True, execution_authority=True)),
        )
        for filename, mutation in mutations:
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as temp:
                fixture = copy_fixture(temp)
                mutate_json(fixture / filename, mutation)
                errors = MODULE.validate(fixture)
                self.assertTrue(any("authority widened" in error or "build_started must be exact false" in error for error in errors))

    def test_lifecycle_identity_rewrite_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            fixture = copy_fixture(temp)
            for filename in ("PHASE-0-DISCOVERY.json", "charter-lock.json", "integration-sweep.json", "BUILD-SPEC.json", "STATUS.json", "final-readiness.json"):
                mutate_json(fixture / filename, lambda value: value.update(programme_id="different-programme"))
            rows = read_jsonl(fixture / "decision-pieces.jsonl")
            for row in rows:
                row["programme_id"] = "different-programme"
            write_jsonl(fixture / "decision-pieces.jsonl", rows)
            errors = MODULE.validate(fixture)
            self.assertTrue(any("programme identity drift" in error or "stale charter or programme binding" in error for error in errors))

    def test_phase0_requires_adaptive_questions_and_no_charter(self):
        mutations = (
            lambda value: value.update(adaptive_questions=[]),
            lambda value: value.update(adaptive_questions=value["adaptive_questions"] + [dict(value["adaptive_questions"][0])]),
            lambda value: value.update(charter_created_during_conversation=True),
        )
        for mutation in mutations:
            with tempfile.TemporaryDirectory() as temp:
                fixture = copy_fixture(temp)
                mutate_json(fixture / "PHASE-0-DISCOVERY.json", mutation)
                errors = MODULE.validate(fixture)
                self.assertTrue(any("PHASE-0-DISCOVERY" in error for error in errors))

    def test_decision_and_integration_generations_are_content_bound(self):
        with tempfile.TemporaryDirectory() as temp:
            fixture = copy_fixture(temp)
            mutate_jsonl(
                fixture / "decision-pieces.jsonl",
                0,
                lambda value: value.update(
                    decision="Launch an unrelated public marketplace immediately.",
                    evidence=["rewritten evidence that retains the same reusable piece identity"],
                ),
            )
            errors = MODULE.validate(fixture)
            self.assertTrue(any("frozen accepted generation" in error for error in errors))
        with tempfile.TemporaryDirectory() as temp:
            fixture = copy_fixture(temp)
            mutate_json(
                fixture / "integration-sweep.json",
                lambda value: [check.update(evidence="x") for check in value["checks"]],
            )
            errors = MODULE.validate(fixture)
            self.assertTrue(any("frozen accepted generation" in error for error in errors))
            self.assertTrue(any("substantive passing evidence" in error for error in errors))

    def test_cell_requirements_must_be_supported_by_named_pieces(self):
        with tempfile.TemporaryDirectory() as temp:
            fixture = copy_fixture(temp)
            rows = read_jsonl(fixture / "decision-pieces.jsonl")
            rows[0]["requirement_ids"] = ["REQ-004"]
            rows[1]["requirement_ids"] = ["REQ-001", "REQ-002", "REQ-003", "REQ-005"]
            write_jsonl(fixture / "decision-pieces.jsonl", rows)
            errors = MODULE.validate(fixture)
            self.assertTrue(any("not supported by the cell's named pieces" in error for error in errors))

    def test_owner_gate_prose_cannot_widen_authority(self):
        mutations = (
            ("STATUS.json", lambda value: value.update(next_owner_gate="Builder authorized; launch now without approval.")),
            ("final-readiness.json", lambda value: value.update(next_owner_prompt="Implementation started; launch the builder now.")),
        )
        for filename, mutation in mutations:
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as temp:
                fixture = copy_fixture(temp)
                mutate_json(fixture / filename, mutation)
                errors = MODULE.validate(fixture)
                self.assertTrue(any("authority widening" in error for error in errors))

    def test_wrong_container_types_fail_closed_without_crashing(self):
        mutations = (
            ("integration-sweep.json", lambda value: value.update(accepted_piece_ids=True)),
            ("STATUS.json", lambda value: value.update(accepted_piece_ids=True)),
            ("decision-pieces.jsonl", None),
            ("BUILD-SPEC.json", lambda value: value["cells"][0].update(dependencies=True)),
        )
        for filename, mutation in mutations:
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as temp:
                fixture = copy_fixture(temp)
                if filename == "decision-pieces.jsonl":
                    mutate_jsonl(fixture / filename, 0, lambda value: value.update(dependencies=True))
                else:
                    assert mutation is not None
                    mutate_json(fixture / filename, mutation)
                errors = MODULE.validate(fixture)
                self.assertTrue(errors)
                self.assertTrue(any("string list" in error for error in errors))

    def test_duplicate_piece_identity_lists_fail_closed(self):
        for filename in ("integration-sweep.json", "STATUS.json"):
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as temp:
                fixture = copy_fixture(temp)
                mutate_json(fixture / filename, lambda value: value["accepted_piece_ids"].append(value["accepted_piece_ids"][0]))
                errors = MODULE.validate(fixture)
                self.assertTrue(any("unique non-empty string list" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
