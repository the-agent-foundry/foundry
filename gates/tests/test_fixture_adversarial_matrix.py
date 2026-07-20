import copy
import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[2]
SCRIPT = REPOSITORY / "gates/scripts/fixture_smoke.py"
SPEC = importlib.util.spec_from_file_location("fixture_smoke_adversarial", SCRIPT)
assert SPEC is not None
assert SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def copy_examples(temp: str) -> Path:
    root = Path(temp)
    shutil.copytree(REPOSITORY / "examples", root / "examples")
    return root


def mutate_json(root: Path, relative: str, mutation) -> None:
    path = root / relative
    value = json.loads(path.read_text())
    mutation(value)
    path.write_text(json.dumps(value, indent=2) + "\n")


def errors_after(mutations) -> list[str]:
    with tempfile.TemporaryDirectory() as temp:
        root = copy_examples(temp)
        for relative, mutation in mutations:
            mutate_json(root, relative, mutation)
        return MODULE.validate(root)


class FixtureAdversarialMatrixTests(unittest.TestCase):
    def test_engineering_lifecycle_and_finding_mutations_are_rejected(self):
        base = "examples/engineering-governance-v2/"
        cases = {
            "backup_missing": [(base + "parent-followthrough.json", lambda value: value.pop("backup"))],
            "promotion_readback_missing": [(base + "parent-followthrough.json", lambda value: value["promotion"].pop("exact_readback"))],
            "runtime_verification_missing": [(base + "parent-followthrough.json", lambda value: value.pop("runtime_verification"))],
            "rollback_predecessor_readback_missing": [(base + "parent-followthrough.json", lambda value: value["rollback"].pop("predecessor_readback"))],
            "retained_next_action_missing": [(base + "retained-checkpoint.json", lambda value: value.pop("next_smallest_action"))],
            "direct_p1_reopened_without_count_change": [(base + "finding-ledger.json", lambda value: value["findings"][0].update(disposition="open"))],
            "adjacent_finding_absorbed": [(base + "finding-ledger.json", lambda value: value["findings"][1].update(disposition="incorporated"))],
        }
        for name, mutations in cases.items():
            with self.subTest(name=name):
                self.assertTrue(errors_after(mutations))

    def test_exact_route_detail_mutations_are_rejected(self):
        base = "examples/model-onboarding-v1/"

        def rewrite_drift(value):
            changed = {"provider": "attacker-provider", "model": "attacker-model", "endpoint_class": "responses"}
            value["accepted_route"] = copy.deepcopy(changed)
            value["observed_route"] = copy.deepcopy(changed)
            value["drift_detected"] = False

        cases = {
            "accepted_route_details_self_rewritten": [(base + "drift-report.json", rewrite_drift)],
            "route_matrix_candidate_model_missing": [(base + "route-matrix.json", lambda value: value["routes"][1].pop("model"))],
            "consumer_route_detail_rewritten": [(base + "activation-receipt.json", lambda value: value["actual_consumer_route"].update(model="other-model"))],
            "predecessor_route_detail_missing": [(base + "activation-receipt.json", lambda value: value.pop("predecessor_readback_route"))],
        }
        for name, mutations in cases.items():
            with self.subTest(name=name):
                self.assertTrue(errors_after(mutations))

    def test_legal_binding_joint_omissions_are_rejected(self):
        base = "examples/legal-operator-v1/"
        for key in ("run_id", "matter_id", "audience", "mode", "jurisdiction_hypothesis", "as_of"):
            with self.subTest(key=key):
                mutations = [
                    (base + "matter-request.json", lambda value, key=key: value.pop(key)),
                    (base + "matter-handoff.json", lambda value, key=key: value.pop(key)),
                ]
                self.assertTrue(errors_after(mutations))
        for key in ("owner", "deadline"):
            with self.subTest(key=key):
                def remove_handoff(value, key=key):
                    value.pop(key)
                    value["blocked_slice"].pop(key)
                mutations = [
                    (base + "matter-request.json", lambda value, key=key: value.pop(key)),
                    (base + "matter-handoff.json", remove_handoff),
                ]
                self.assertTrue(errors_after(mutations))
        with self.subTest(key="source_currentness"):
            self.assertTrue(errors_after([(base + "matter-handoff.json", lambda value: value["sources"][0].pop("as_of"))]))

    def test_legal_capability_and_safety_schema_mutations_are_rejected(self):
        base = "examples/legal-operator-v1/"
        cases = {
            "external_action_map_missing": [(base + "profile.example.json", lambda value: value.pop("external_actions"))],
            "public_private_reader_added": [(base + "profile.example.json", lambda value: value["modes"]["public_research"]["allowed_tools"].append("matter_scoped_reader"))],
            "private_network_tool_added": [(base + "profile.example.json", lambda value: value["modes"]["private_matter"]["allowed_tools"].append("public_primary_law_research"))],
            "legal_hard_floors_missing": [(base + "eval-matrix.json", lambda value: value.pop("hard_floors"))],
        }
        for name, mutations in cases.items():
            with self.subTest(name=name):
                self.assertTrue(errors_after(mutations))


if __name__ == "__main__":
    unittest.main()
