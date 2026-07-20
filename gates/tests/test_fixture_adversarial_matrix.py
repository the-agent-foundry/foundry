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
    def assert_rejected(self, mutations, expected: str) -> None:
        errors = errors_after(mutations)
        self.assertTrue(any(expected in error for error in errors), errors)

    def test_engineering_lifecycle_identity_and_finding_mutations_are_rejected(self):
        base = "examples/engineering-governance-v2/"
        cases = {
            "backup_missing": ([(base + "parent-followthrough.json", lambda value: value.pop("backup"))], "predecessor backup witness is incomplete"),
            "promotion_readback_missing": ([(base + "parent-followthrough.json", lambda value: value["promotion"].pop("exact_readback"))], "promotion/readback witness is incomplete"),
            "runtime_verification_missing": ([(base + "parent-followthrough.json", lambda value: value.pop("runtime_verification"))], "runtime verification witness is incomplete"),
            "rollback_predecessor_readback_missing": ([(base + "parent-followthrough.json", lambda value: value["rollback"].pop("predecessor_readback"))], "rollback/predecessor readback witness is incomplete"),
            "retained_next_action_missing": ([(base + "retained-checkpoint.json", lambda value: value.pop("next_smallest_action"))], "retained checkpoint next action is missing"),
            "direct_p1_reopened_without_count_change": ([(base + "finding-ledger.json", lambda value: value["findings"][0].update(disposition="open"))], "open direct P0/P1 count does not match"),
            "adjacent_finding_absorbed": ([(base + "finding-ledger.json", lambda value: value["findings"][1].update(disposition="incorporated"))], "adjacent finding escaped proposal-only"),
            "followthrough_candidate_mismatch": ([(base + "parent-followthrough.json", lambda value: value.update(candidate_id="other-candidate"))], "candidate IDs do not bind one immutable candidate"),
            "checkpoint_candidate_mismatch": ([(base + "retained-checkpoint.json", lambda value: value.update(candidate_id="other-candidate"))], "candidate IDs do not bind one immutable candidate"),
            "candidate_digest_missing": ([(base + "finding-ledger.json", lambda value: value.pop("candidate_digest"))], "candidate digests do not bind one immutable candidate"),
        }
        for name, (mutations, expected) in cases.items():
            with self.subTest(name=name):
                self.assert_rejected(mutations, expected)

    def test_exact_route_lifecycle_and_generation_mutations_are_rejected(self):
        base = "examples/model-onboarding-v1/"

        def rewrite_drift(value):
            changed = {
                "provider": "attacker-provider",
                "model": "attacker-model",
                "endpoint_class": "responses",
                "tools": ["none"],
                "structured_output": True,
                "fallback": None,
            }
            value["accepted_route"] = copy.deepcopy(changed)
            value["observed_route"] = copy.deepcopy(changed)
            value["drift_detected"] = False

        cases = {
            "accepted_route_details_self_rewritten": ([(base + "drift-report.json", rewrite_drift)], "drift accepted route detail is not bound"),
            "route_matrix_candidate_model_missing": ([(base + "route-matrix.json", lambda value: value["routes"][1].pop("model"))], "route-detail schema is incomplete"),
            "consumer_route_detail_rewritten": ([(base + "activation-receipt.json", lambda value: value["actual_consumer_route"].update(model="other-model"))], "candidate consumer route detail mismatch"),
            "predecessor_route_detail_missing": ([(base + "activation-receipt.json", lambda value: value.pop("predecessor_readback_route"))], "predecessor rollback route detail mismatch"),
            "route_tools_widened": ([(base + "route-matrix.json", lambda value: value["routes"][1]["tools"].append("send"))], "expected route detail is not bound"),
            "structured_output_disabled": ([(base + "route-matrix.json", lambda value: value["routes"][1].update(structured_output=False))], "expected route detail is not bound"),
            "fallback_rerouted": ([(base + "route-matrix.json", lambda value: value["routes"][1].update(fallback="baseline-route"))], "expected route detail is not bound"),
            "drift_generation_mismatch": ([(base + "drift-report.json", lambda value: value.update(accepted_generation="other-generation"))], "drift, manifest, and activation generations do not match"),
            "activation_generation_mismatch": ([(base + "activation-receipt.json", lambda value: value.update(generation_id="other-generation"))], "activation generation does not match"),
            "inactive_validation_false": ([(base + "activation-receipt.json", lambda value: value.update(inactive_generation_validated=False))], "inactive generation was not validated"),
            "predecessor_backup_false": ([(base + "activation-receipt.json", lambda value: value.update(predecessor_backup_verified=False))], "predecessor backup was not verified"),
            "candidate_reactivated": ([(base + "activation-receipt.json", lambda value: value.update(candidate_reactivated=True))], "rehearsal must end default-off"),
            "rollback_not_exercised": ([(base + "activation-receipt.json", lambda value: value.update(rollback_exercised=False))], "rollback was not exercised"),
            "provenance_receipt_missing": ([(base + "comparison-report.json", lambda value: value["results"]["candidate-route"]["route_provenance_evidence"].pop("call_receipt_id"))], "provenance call receipt is missing"),
            "privacy_scope_overclaim": ([(base + "route-matrix.json", lambda value: value["routes"][0].update(retention_claim_scope="exact_route_verified"))], "route privacy claim is over-broad"),
        }
        for name, (mutations, expected) in cases.items():
            with self.subTest(name=name):
                self.assert_rejected(mutations, expected)

    def test_legal_binding_joint_omissions_are_rejected(self):
        base = "examples/legal-operator-v1/"
        ordinary = ("run_id", "matter_id", "requester", "audience", "mode", "jurisdiction_hypothesis", "as_of", "authorized_inputs", "input_hashes", "profile_generation")
        for key in ordinary:
            with self.subTest(key=key):
                mutations = [
                    (base + "matter-request.json", lambda value, key=key: value.pop(key)),
                    (base + "matter-handoff.json", lambda value, key=key: value.pop(key)),
                ]
                self.assert_rejected(mutations, f"mandatory request/handoff binding is missing for {key}")
        for key in ("owner", "deadline"):
            with self.subTest(key=key):
                def remove_handoff(value, key=key):
                    value.pop(key)
                    value["blocked_slice"].pop(key)
                mutations = [
                    (base + "matter-request.json", lambda value, key=key: value.pop(key)),
                    (base + "matter-handoff.json", remove_handoff),
                ]
                self.assert_rejected(mutations, f"mandatory request/handoff binding is missing for {key}")
        with self.subTest(key="source_currentness"):
            self.assert_rejected([(base + "matter-handoff.json", lambda value: value["sources"][0].pop("as_of"))], "source provenance, currentness, or pinpoint is missing")
        with self.subTest(key="input_hash_inventory"):
            self.assert_rejected([(base + "matter-request.json", lambda value: value.update(input_hashes=["wrong-hash"])), (base + "matter-handoff.json", lambda value: value.update(input_hashes=["wrong-hash"]))], "input-hash binding does not match authorized inputs")

    def test_legal_identity_bindings_reject_blank_and_whitespace(self):
        base = "examples/legal-operator-v1/"
        keys = ("run_id", "matter_id", "requester", "owner", "audience", "mode", "jurisdiction_hypothesis", "as_of", "deadline", "profile_generation")
        for key in keys:
            for bad_value in ("", " \t "):
                with self.subTest(key=key, bad_value=repr(bad_value)):
                    def mutate_handoff(value, key=key, bad_value=bad_value):
                        value[key] = bad_value
                        if key in {"owner", "deadline"}:
                            value["blocked_slice"][key] = bad_value

                    mutations = [
                        (base + "matter-request.json", lambda value, key=key, bad_value=bad_value: value.update({key: bad_value})),
                        (base + "matter-handoff.json", mutate_handoff),
                    ]
                    self.assert_rejected(mutations, f"identity binding must be non-empty for {key}")

    def test_legal_profile_binding_contract_mutations_are_rejected(self):
        base = "examples/legal-operator-v1/"
        for key in ("matter_id", "profile_generation"):
            with self.subTest(key=key):
                self.assert_rejected(
                    [(base + "profile.example.json", lambda value, key=key: value["required_run_bindings"].remove(key))],
                    "profile required-run-binding schema is incomplete",
                )
        self.assert_rejected(
            [(base + "matter-handoff.json", lambda value: value.update(profile_generation="other-generation"))],
            "request/handoff binding mismatch for profile_generation",
        )

    def test_legal_capability_and_safety_schema_mutations_are_rejected(self):
        base = "examples/legal-operator-v1/"
        cases = {
            "external_action_map_missing": ([(base + "profile.example.json", lambda value: value.pop("external_actions"))], "external action denial schema is incomplete"),
            "public_private_reader_added": ([(base + "profile.example.json", lambda value: value["modes"]["public_research"]["allowed_tools"].append("matter_scoped_reader"))], "public tool inventory is incomplete"),
            "private_network_tool_added": ([(base + "profile.example.json", lambda value: value["modes"]["private_matter"]["allowed_tools"].append("public_primary_law_research"))], "private tool inventory is incomplete"),
            "private_network_enabled": ([(base + "profile.example.json", lambda value: value["modes"]["private_matter"].update(network_allowed=True))], "private mode does not fail closed"),
            "external_send_enabled": ([(base + "profile.example.json", lambda value: value["external_actions"].update(send="available"))], "external action capability must remain absent"),
            "legal_hard_floors_missing": ([(base + "eval-matrix.json", lambda value: value.pop("hard_floors"))], "legal hard-floor schema is incomplete"),
        }
        for name, (mutations, expected) in cases.items():
            with self.subTest(name=name):
                self.assert_rejected(mutations, expected)


if __name__ == "__main__":
    unittest.main()
