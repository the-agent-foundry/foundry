import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "fixture_smoke.py"
SPEC = importlib.util.spec_from_file_location("fixture_smoke", SCRIPT)
assert SPEC is not None
assert SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
REPOSITORY = Path(__file__).resolve().parents[2]


def copy_repository_examples(temp: str) -> Path:
    root = Path(temp)
    shutil.copytree(REPOSITORY / "examples", root / "examples")
    return root


def mutate_json(path: Path, mutation) -> None:
    value = json.loads(path.read_text())
    mutation(value)
    path.write_text(json.dumps(value, indent=2) + "\n")


class FixtureSmokeTests(unittest.TestCase):
    def test_repository_fixtures_pass(self):
        self.assertEqual(MODULE.validate(REPOSITORY), [])

    def test_invalid_json_is_reported(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            examples = root / "examples"
            (examples / "engineering-governance-v2").mkdir(parents=True)
            (examples / "engineering-governance-v2" / "acceptance-contract.json").write_text("{")
            errors = MODULE.validate(root)
            self.assertTrue(any("invalid JSON" in error for error in errors))

    def test_engineering_fixture_must_be_synthetic(self):
        with tempfile.TemporaryDirectory() as temp:
            root = copy_repository_examples(temp)
            path = root / "examples/engineering-governance-v2/acceptance-contract.json"
            mutate_json(path, lambda value: value.update(synthetic=False))
            self.assertTrue(any("synthetic true" in error for error in MODULE.validate(root)))

    def test_engineering_fixture_cannot_claim_authority(self):
        with tempfile.TemporaryDirectory() as temp:
            root = copy_repository_examples(temp)
            path = root / "examples/engineering-governance-v2/acceptance-contract.json"
            mutate_json(path, lambda value: value.update(authoritative=True))
            self.assertTrue(any("cannot claim authoritative state" in error for error in MODULE.validate(root)))

    def test_model_route_matrix_cannot_authorize_activation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = copy_repository_examples(temp)
            path = root / "examples/model-onboarding-v1/route-matrix.json"
            mutate_json(path, lambda value: value.update(authorizing=True))
            self.assertTrue(any("authorizing false" in error for error in MODULE.validate(root)))

    def test_model_hard_floor_metric_cannot_be_omitted(self):
        with tempfile.TemporaryDirectory() as temp:
            root = copy_repository_examples(temp)
            path = root / "examples/model-onboarding-v1/comparison-report.json"
            mutate_json(path, lambda value: value["results"]["candidate-route"].pop("route_provenance_match"))
            errors = MODULE.validate(root)
            self.assertTrue(any("recomputed hard floors did not pass" in error for error in errors))

    def test_every_model_hard_floor_and_result_metric_is_required(self):
        keys = ["privacy_leaks", "unauthorized_actions", "route_provenance_match", "valid_structured_output_rate"]
        for key in keys:
            with self.subTest(kind="floor", key=key), tempfile.TemporaryDirectory() as temp:
                root = copy_repository_examples(temp)
                path = root / "examples/model-onboarding-v1/eval-manifest.json"
                mutate_json(path, lambda value, key=key: value["hard_floors"].pop(key))
                self.assertTrue(any("hard-floor schema is incomplete" in error for error in MODULE.validate(root)))
            with self.subTest(kind="result", key=key), tempfile.TemporaryDirectory() as temp:
                root = copy_repository_examples(temp)
                path = root / "examples/model-onboarding-v1/comparison-report.json"
                mutate_json(path, lambda value, key=key: value["results"]["baseline-route"].pop(key))
                self.assertTrue(any("result schema is incomplete" in error for error in MODULE.validate(root)))

    def test_hard_floor_cannot_false_pass_when_omitted_everywhere(self):
        with tempfile.TemporaryDirectory() as temp:
            root = copy_repository_examples(temp)
            manifest = root / "examples/model-onboarding-v1/eval-manifest.json"
            comparison = root / "examples/model-onboarding-v1/comparison-report.json"
            mutate_json(manifest, lambda value: value["hard_floors"].pop("privacy_leaks"))
            mutate_json(comparison, lambda value: [result.pop("privacy_leaks") for result in value["results"].values()])
            errors = MODULE.validate(root)
            self.assertTrue(any("hard-floor schema is incomplete" in error for error in errors))
            self.assertTrue(any("recomputed hard floors did not pass" in error for error in errors))

    def test_hard_floor_metrics_cannot_be_boolean(self):
        with tempfile.TemporaryDirectory() as temp:
            root = copy_repository_examples(temp)
            path = root / "examples/model-onboarding-v1/eval-manifest.json"
            mutate_json(path, lambda value: value["hard_floors"].update(route_provenance_match=True))
            self.assertTrue(any("numeric and non-Boolean" in error for error in MODULE.validate(root)))

    def test_activation_readback_must_match_candidate(self):
        with tempfile.TemporaryDirectory() as temp:
            root = copy_repository_examples(temp)
            path = root / "examples/model-onboarding-v1/activation-receipt.json"
            mutate_json(path, lambda value: value.update(actual_consumer_readback="wrong-route"))
            self.assertTrue(any("candidate consumer readback mismatch" in error for error in MODULE.validate(root)))

    def test_rollback_requires_predecessor_readback(self):
        with tempfile.TemporaryDirectory() as temp:
            root = copy_repository_examples(temp)
            path = root / "examples/model-onboarding-v1/activation-receipt.json"
            mutate_json(path, lambda value: value.pop("predecessor_readback_after_rollback"))
            self.assertTrue(any("predecessor rollback readback mismatch" in error for error in MODULE.validate(root)))

    def test_route_id_only_drift_cannot_false_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            root = copy_repository_examples(temp)
            path = root / "examples/model-onboarding-v1/drift-report.json"

            def mutate(value):
                value["observed_route"] = value["accepted_route"].copy()
                value["observed_route_id"] = "candidate-route-revision-x"
                value["drift_detected"] = False

            mutate_json(path, mutate)
            self.assertTrue(any("drift flag does not match" in error for error in MODULE.validate(root)))

    def test_route_privacy_claim_must_remain_exact_route_unknown(self):
        with tempfile.TemporaryDirectory() as temp:
            root = copy_repository_examples(temp)
            path = root / "examples/model-onboarding-v1/route-matrix.json"
            mutate_json(path, lambda value: value["routes"][0].update(retention_status="officially_verified"))
            self.assertTrue(any("retention must remain unknown" in error for error in MODULE.validate(root)))

    def test_drift_flag_must_match_route_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            root = copy_repository_examples(temp)
            path = root / "examples/model-onboarding-v1/drift-report.json"
            mutate_json(path, lambda value: value.update(drift_detected=False))
            self.assertTrue(any("drift flag does not match" in error for error in MODULE.validate(root)))

    def test_public_legal_mode_cannot_expose_private_writer(self):
        with tempfile.TemporaryDirectory() as temp:
            root = copy_repository_examples(temp)
            path = root / "examples/legal-operator-v1/profile.example.json"
            mutate_json(path, lambda value: value["modes"]["public_research"]["allowed_tools"].append("matter_scoped_draft_writer"))
            self.assertTrue(any("public mode exposes a private matter writer" in error for error in MODULE.validate(root)))

    def test_legal_request_cannot_grant_external_authority(self):
        with tempfile.TemporaryDirectory() as temp:
            root = copy_repository_examples(temp)
            path = root / "examples/legal-operator-v1/matter-request.json"
            mutate_json(path, lambda value: value.update(external_action_authority=True))
            self.assertTrue(any("cannot grant external action authority" in error for error in MODULE.validate(root)))

    def test_legal_handoff_must_preserve_matter_bindings(self):
        with tempfile.TemporaryDirectory() as temp:
            root = copy_repository_examples(temp)
            path = root / "examples/legal-operator-v1/matter-handoff.json"
            mutate_json(path, lambda value: value.update(audience="different-audience"))
            self.assertTrue(any("binding mismatch for audience" in error for error in MODULE.validate(root)))

    def test_legal_source_must_match_authorized_input_version(self):
        with tempfile.TemporaryDirectory() as temp:
            root = copy_repository_examples(temp)
            path = root / "examples/legal-operator-v1/matter-handoff.json"
            mutate_json(path, lambda value: value["sources"][0].update(version=2))
            self.assertTrue(any("source is not bound to an authorized input version" in error for error in MODULE.validate(root)))


if __name__ == "__main__":
    unittest.main()
