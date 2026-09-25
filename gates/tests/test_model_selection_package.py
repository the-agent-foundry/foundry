#!/usr/bin/env python3
"""Adversarial mutations for the public model-selection package."""
from __future__ import annotations

import copy
import datetime as dt
import importlib.util
import json
import math
import shutil
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PACKAGE = REPO / "model-selection"
MODULE_PATH = PACKAGE / "scripts/validate_roster.py"
SPEC = importlib.util.spec_from_file_location("validate_roster", MODULE_PATH)
VALIDATOR = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(VALIDATOR)


class ModelSelectionPackageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name) / "model-selection"
        shutil.copytree(PACKAGE, self.root)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def mutate_json(self, relative: str, mutator) -> None:
        path = self.root / relative
        data = json.loads(path.read_text(encoding="utf-8"))
        mutator(data)
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    def assert_error(self, expected: str, today: dt.date | None = None) -> None:
        errors = VALIDATOR.validate_package(self.root, today=today or dt.date(2026, 9, 25))
        self.assertTrue(any(expected in error for error in errors), errors)

    def test_canonical_package_passes(self) -> None:
        self.assertEqual([], VALIDATOR.validate_package(self.root, today=dt.date(2026, 9, 25)))

    def test_official_refresh_prices_and_predecessors(self) -> None:
        roster = json.loads((self.root / "public-model-roster.json").read_text())
        self.assertEqual(("2026.09.25", "2026-09-25", "2026-10-25"),
                         (roster["roster_version"], roster["as_of"], roster["review_due_at"]))
        rows = {row["candidate_id"]: row for row in roster["candidates"]}
        expected = {
            "openai/gpt-6-astra": (10, 1, 12.5, 50, "current"),
            "openai/gpt-6-sol": (2, .2, 2.5, 10, "current"),
            "openai/gpt-6-luna": (.1, .01, .125, .5, "current"),
            "openai/gpt-5.6-sol": (4, .4, 5, 20, "current"),
            "anthropic/claude-fable-5-1": (10, .25, 12.5, 50, "current"),
            "anthropic/claude-fable-5": (10, 1, 12.5, 50, "legacy"),
            "anthropic/claude-opus-5-5": (4, .2, 5, 20, "current"),
            "anthropic/claude-opus-5": (5, .5, 6.25, 25, "legacy"),
            "google/gemini-3.8-flash": (.75, .075, None, 3.75, "current"),
            "google/gemini-3.6-flash": (.75, .075, None, 3.75, "current"),
            "xai/grok-4.7": (2, .5, None, 6, "current"),
            "xai/grok-4.6": (2, .5, None, 6, "current"),
            "xai/grok-4.5": (2, .3, None, 6, "current"),
        }
        for candidate_id, fact in expected.items():
            with self.subTest(candidate_id=candidate_id):
                row = rows[candidate_id]
                p = row["prices"]
                self.assertEqual(fact, (p["input"], p["cached_input"], p["cache_write"], p["output"], row["status"]))
                self.assertEqual({"identity_and_price": "official", "suitability": "editorial"}, row["evidence"])
        self.assertEqual(len(rows), len(roster["candidates"]))

    def test_rendered_prices_tier_and_editorial_parity(self) -> None:
        text = (self.root / "MODEL-ROSTER.md").read_text()
        self.assertIn("`google/gemini-3.8-flash` | current | $0.75 / $0.075 / n/a / $3.75", text)
        self.assertIn("Standard paid promotional rates through 2026-12-31", text)
        self.assertIn("`anthropic/claude-fable-5` | legacy", text)
        self.assertIn("These are editorial starting points, not activation decisions.", text)
        self.assertIn("`xai/grok-4.5` | current", text)

    def test_duplicate_candidate_fails(self) -> None:
        self.mutate_json("public-model-roster.json", lambda d: d["candidates"].append(copy.deepcopy(d["candidates"][0])))
        self.assert_error("candidate IDs must be unique")

    def test_unknown_source_binding_fails(self) -> None:
        self.mutate_json("public-model-roster.json", lambda d: d["candidates"][0].update({"source_ids": ["not-a-source"]}))
        self.assert_error("source binding invalid")

    def test_observed_claim_without_observed_state_fails(self) -> None:
        def mutate(data):
            data["candidates"][0]["evidence"]["suitability"] = "observed"
            data["candidates"][0]["validation_state"] = "not_validated_by_agent_foundry"
        self.mutate_json("public-model-roster.json", mutate)
        self.assert_error("observed suitability requires observed validation_state")

    def test_schema_enum_failure_is_enforced(self) -> None:
        self.mutate_json("public-model-roster.json", lambda d: d["candidates"][0].update({"status": "imaginary"}))
        self.assert_error("is not in enum")

    def test_schema_type_failure_is_enforced(self) -> None:
        self.mutate_json("public-model-roster.json", lambda d: d["candidates"][0].update({"best_fit": "not-an-array"}))
        self.assert_error("expected type 'array'")

    def test_unknown_property_fails(self) -> None:
        self.mutate_json("public-model-roster.json", lambda d: d["candidates"][0].update({"secret_extra": "nope"}))
        self.assert_error("unknown property 'secret_extra'")

    def test_anthropic_api_identity_fails(self) -> None:
        def mutate(data):
            row = next(row for row in data["candidates"] if row["model"] == "claude-haiku-4-5-20251001")
            row.update({"candidate_id": "anthropic/claude-haiku-4.5", "model": "claude-haiku-4.5"})
        self.mutate_json("public-model-roster.json", mutate)
        self.assert_error("undocumented Anthropic API model ID")

    def test_private_path_fails(self) -> None:
        path = self.root / "README.md"
        path.write_text(path.read_text() + "\n/Users/example/private\n")
        self.assert_error("forbidden marker: /Users/")

    def test_overlay_credentials_fails(self) -> None:
        self.mutate_json("local-overlay.example.json", lambda d: d["routes"][0].update({"credential_present": True}))
        self.assert_error("example overlay cannot claim credentials")

    def test_overlay_missing_exact_route_field_fails(self) -> None:
        self.mutate_json("local-overlay.example.json", lambda d: d["routes"][0].pop("api_mode"))
        self.assert_error("missing required property 'api_mode'")

    def test_live_authority_fails(self) -> None:
        self.mutate_json("examples/selection-record.example.json", lambda d: d.update({"authorizing": True}))
        self.assert_error("expected const False")

    def test_stale_window_over_31_days_fails(self) -> None:
        self.mutate_json("public-model-roster.json", lambda d: d.update({"review_due_at": "2026-10-27"}))
        self.assert_error("review window must be 31 days or less")

    def test_overdue_roster_fails(self) -> None:
        self.assert_error("roster is overdue", today=dt.date(2026, 10, 26))

    def test_stale_source_fails(self) -> None:
        self.mutate_json("public-model-roster.json", lambda d: d["sources"][0].update({"accessed_at": "2026-06-01"}))
        self.assert_error("stale source accessed_at")

    def test_empty_weakness_fails_schema(self) -> None:
        self.mutate_json("public-model-roster.json", lambda d: d["candidates"][0].update({"weaknesses": []}))
        self.assert_error("fewer than minItems")

    def test_chosen_candidate_below_threshold_fails(self) -> None:
        self.mutate_json("examples/selection-record.example.json", lambda d: d["candidates"][0].update({"quality_score": 0.4}))
        self.assert_error("chosen candidate fails quality_score_min")

    def test_chosen_candidate_failed_gate_fails(self) -> None:
        self.mutate_json("examples/selection-record.example.json", lambda d: d["candidates"][0]["hard_gates"].update({"approved_data_posture": False}))
        self.assert_error("chosen candidate must pass every hard gate")

    def test_selection_duplicate_route_id_fails(self) -> None:
        self.mutate_json("examples/selection-record.example.json", lambda d: d["candidates"][1].update({"route_id": d["candidates"][0]["route_id"]}))
        self.assert_error("selection candidate route IDs must be unique")

    def test_selection_unlisted_fallback_fails(self) -> None:
        self.mutate_json("examples/selection-record.example.json", lambda d: d["decision"].update({"fallback_route_id": "provider/unlisted"}))
        self.assert_error("selection fallback must reference a distinct listed candidate")

    def test_fallback_below_threshold_fails(self) -> None:
        self.mutate_json("examples/selection-record.example.json", lambda d: d["candidates"][2].update({"completion_score": 0.1}))
        self.assert_error("fallback candidate fails completion_score_min")

    def test_overlay_duplicate_route_id_fails(self) -> None:
        self.mutate_json("local-overlay.example.json", lambda d: d["routes"].append(copy.deepcopy(d["routes"][0])))
        self.assert_error("overlay route IDs must be unique")

    def test_overlay_enabled_without_entitlement_fails(self) -> None:
        self.mutate_json("local-overlay.example.json", lambda d: d["routes"][0].update({"enabled_state": "enabled"}))
        self.assert_error("enabled route requires credentials and entitlement")

    def test_overlay_passed_without_enabled_fails(self) -> None:
        self.mutate_json("local-overlay.example.json", lambda d: d["routes"][0].update({"runtime_validation_state": "passed"}))
        self.assert_error("passed runtime validation requires enabled route")

    def test_passed_route_requires_complete_evidence(self) -> None:
        def mutate(data: dict) -> None:
            data["routes"][0].update({"credential_present": True, "entitlement_state": "entitled", "enabled_state": "enabled", "runtime_validation_state": "passed"})
        self.mutate_json("local-overlay.example.json", mutate)
        self.assert_error("passed runtime validation requires approvals, workloads, and complete measurements")

    def test_enabled_route_requires_ready_fallback(self) -> None:
        def mutate(data: dict) -> None:
            primary = data["routes"][0]
            fallback = copy.deepcopy(primary)
            fallback["route_id"] = "openai/gpt-5.6-terra/responses/global/fallback"
            primary.update({"credential_present": True, "entitlement_state": "entitled", "enabled_state": "enabled", "fallback_route_id": fallback["route_id"]})
            data["routes"].append(fallback)
        self.mutate_json("local-overlay.example.json", mutate)
        self.assert_error("enabled route fallback must be credentialed, entitled, enabled, and runtime-passed")

    def test_bundled_overlay_notice_must_remain_example_only(self) -> None:
        self.mutate_json("local-overlay.example.json", lambda d: d.update({"notice": "PRIVATE ROUTE OVERLAY"}))
        self.assert_error("bundled overlay notice must begin EXAMPLE ONLY")

    def test_cross_provider_source_binding_fails(self) -> None:
        self.mutate_json("public-model-roster.json", lambda d: d["candidates"][0].update({"source_ids": ["xai-pricing"]}))
        self.assert_error("source publisher does not match candidate provider")

    def test_mixed_provider_source_binding_fails(self) -> None:
        self.mutate_json("public-model-roster.json", lambda d: d["candidates"][0].update({"source_ids": ["openai-pricing", "xai-pricing"]}))
        self.assert_error("source publisher does not match candidate provider")

    def test_future_roster_date_fails(self) -> None:
        def mutate(data: dict) -> None:
            data["as_of"] = "2026-09-26"
            data["review_due_at"] = "2026-10-25"
        self.mutate_json("public-model-roster.json", mutate)
        self.assert_error("roster as_of cannot be in the future")

    def test_future_source_date_fails(self) -> None:
        self.mutate_json("public-model-roster.json", lambda d: d["sources"][0].update({"accessed_at": "2026-09-26"}))
        self.assert_error("source accessed_at cannot be in the future")

    def test_specialist_snapshot_drift_fails(self) -> None:
        path = self.root / "SPECIALIST-MODELS.md"
        path.write_text(path.read_text().replace("**Snapshot date:** 2026-08-11.", "**Snapshot date:** 2026-09-26."))
        self.assert_error("specialist snapshot date must appear exactly once and not follow roster as_of")

    def test_specialist_snapshot_invalid_calendar_date_fails(self) -> None:
        path = self.root / "SPECIALIST-MODELS.md"
        path.write_text(path.read_text().replace("**Snapshot date:** 2026-08-11.", "**Snapshot date:** 2026-02-31."))
        self.assert_error("specialist snapshot date must appear exactly once and not follow roster as_of")

    def test_specialist_snapshot_duplicate_fails(self) -> None:
        path = self.root / "SPECIALIST-MODELS.md"
        path.write_text(path.read_text() + "\n**Snapshot date:** 2026-08-11.\n")
        self.assert_error("specialist snapshot date must appear exactly once and not follow roster as_of")

    def test_non_finite_number_fails(self) -> None:
        self.mutate_json("examples/selection-record.example.json", lambda d: d["candidates"][0].update({"quality_score": math.nan}))
        self.assert_error("non-finite JSON number")

    def test_external_overlay_candidate_mismatch_fails(self) -> None:
        overlay = json.loads((self.root / "local-overlay.example.json").read_text())
        overlay["routes"][0].update({"provider": "xAI", "model_id": "grok-4.5"})
        path = self.root / "private-overlay.json"
        path.write_text(json.dumps(overlay))
        errors = VALIDATOR.validate_package(self.root, today=dt.date(2026, 9, 25), overlay_path=path)
        self.assertTrue(any("exact route provider/model must match public candidate" in error for error in errors), errors)

    def test_external_overlay_duplicate_id_fails(self) -> None:
        overlay = json.loads((self.root / "local-overlay.example.json").read_text())
        duplicate = copy.deepcopy(overlay["routes"][0])
        duplicate["endpoint_label"] = "second endpoint"
        overlay["routes"].append(duplicate)
        path = self.root / "private-overlay.json"
        path.write_text(json.dumps(overlay))
        errors = VALIDATOR.validate_package(self.root, today=dt.date(2026, 9, 25), overlay_path=path)
        self.assertTrue(any("overlay route IDs must be unique" in error for error in errors), errors)

    def test_external_overlay_accepts_private_notice(self) -> None:
        overlay = json.loads((self.root / "local-overlay.example.json").read_text())
        overlay["notice"] = "PRIVATE EXACT-ROUTE OVERLAY"
        path = self.root / "private-overlay.json"
        path.write_text(json.dumps(overlay))
        self.assertEqual([], VALIDATOR.validate_package(self.root, today=dt.date(2026, 9, 25), overlay_path=path))


if __name__ == "__main__":
    unittest.main()
