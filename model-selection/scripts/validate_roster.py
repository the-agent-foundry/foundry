#!/usr/bin/env python3
"""Deterministic standard-library validation for the public model-selection package."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
ROSTER_PATH = ROOT / "public-model-roster.json"
SCHEMAS = {
    "public-model-roster.json": "model-roster.schema.json",
    "local-overlay.example.json": "local-overlay.schema.json",
    "examples/selection-record.example.json": "selection-record.schema.json",
}
REQUIRED_FILES = [
    ROOT / "README.md",
    ROOT / "MODEL-ROSTER.md",
    ROOT / "PROMPTING-GUIDE.md",
    ROOT / "SPECIALIST-MODELS.md",
    ROOT / "MAINTENANCE.md",
    *[ROOT / path for path in SCHEMAS],
    *[ROOT / path for path in SCHEMAS.values()],
]


def resolve_ref(schema: dict, root_schema: dict) -> dict:
    ref = schema.get("$ref")
    if not ref:
        return schema
    if not ref.startswith("#/"):
        raise ValueError(f"unsupported external schema ref: {ref}")
    node: object = root_schema
    for part in ref[2:].split("/"):
        node = node[part.replace("~1", "/").replace("~0", "~")]  # type: ignore[index]
    return node  # type: ignore[return-value]


def type_matches(value: object, expected: str) -> bool:
    return {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "number": isinstance(value, (int, float)) and not isinstance(value, bool),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "boolean": isinstance(value, bool),
        "null": value is None,
    }[expected]


def schema_errors(value: object, schema: dict, root_schema: dict, path: str = "$") -> list[str]:
    errors: list[str] = []
    schema = resolve_ref(schema, root_schema)
    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: expected const {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: value {value!r} is not in enum")

    expected = schema.get("type")
    if expected is not None:
        options = expected if isinstance(expected, list) else [expected]
        if not any(type_matches(value, option) for option in options):
            return errors + [f"{path}: expected type {expected!r}"]

    if isinstance(value, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                errors.append(f"{path}: missing required property {key!r}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for key in value:
                if key not in properties:
                    errors.append(f"{path}: unknown property {key!r}")
        for key, child in value.items():
            if key in properties:
                errors.extend(schema_errors(child, properties[key], root_schema, f"{path}.{key}"))

    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{path}: fewer than minItems")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errors.append(f"{path}: more than maxItems")
        if schema.get("uniqueItems"):
            encoded = [json.dumps(item, sort_keys=True) for item in value]
            if len(encoded) != len(set(encoded)):
                errors.append(f"{path}: items are not unique")
        if "items" in schema:
            for index, item in enumerate(value):
                errors.extend(schema_errors(item, schema["items"], root_schema, f"{path}[{index}]"))

    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            errors.append(f"{path}: shorter than minLength")
        if "pattern" in schema and re.search(schema["pattern"], value) is None:
            errors.append(f"{path}: does not match pattern {schema['pattern']!r}")
        if schema.get("format") == "date":
            try:
                dt.date.fromisoformat(value)
            except ValueError:
                errors.append(f"{path}: invalid ISO date")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if not math.isfinite(value):
            errors.append(f"{path}: number must be finite")
            return errors
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path}: below minimum")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"{path}: above maximum")
    return errors


def load_json(path: Path) -> dict:
    def reject_constant(value: str) -> None:
        raise ValueError(f"non-finite JSON number: {value}")
    return json.loads(path.read_text(encoding="utf-8"), parse_constant=reject_constant)


def validate_overlay_document(overlay: dict, roster: dict) -> list[str]:
    errors: list[str] = []
    overlay_routes = overlay.get("routes", [])
    overlay_ids = [route.get("route_id") for route in overlay_routes]
    route_map = {route.get("route_id"): route for route in overlay_routes}
    candidate_map = {candidate.get("candidate_id"): candidate for candidate in roster.get("candidates", [])}
    if len(overlay_ids) != len(set(overlay_ids)):
        errors.append("overlay route IDs must be unique")
    for route in overlay_routes:
        route_id = route.get("route_id")
        fallback_id = route.get("fallback_route_id")
        public_candidate = candidate_map.get(route.get("public_candidate_id"))
        if not public_candidate:
            errors.append(f"{route_id}: public_candidate_id must reference a listed public candidate")
        else:
            if route.get("provider") != public_candidate.get("provider") or route.get("model_id") != public_candidate.get("model"):
                errors.append(f"{route_id}: exact route provider/model must match public candidate")
        if fallback_id is not None and (fallback_id not in overlay_ids or fallback_id == route_id):
            errors.append(f"{route_id}: overlay fallback must reference a distinct listed route")
        if route.get("enabled_state") == "enabled" and not (route.get("credential_present") and route.get("entitlement_state") == "entitled"):
            errors.append(f"{route_id}: enabled route requires credentials and entitlement")
        if route.get("runtime_validation_state") == "passed" and route.get("enabled_state") != "enabled":
            errors.append(f"{route_id}: passed runtime validation requires enabled route")
        if route.get("runtime_validation_state") == "passed":
            measured = route.get("measured", {})
            required_measurements = ["evaluated_at", "quality_score", "completion_score", "restraint_score", "p50_latency_ms", "p95_latency_ms", "successful_outcome_rate", "estimated_cost_per_successful_outcome_usd"]
            if not route.get("approved_data_classes") or not route.get("allowed_workloads") or any(measured.get(field) is None for field in required_measurements):
                errors.append(f"{route_id}: passed runtime validation requires approvals, workloads, and complete measurements")
        if fallback_id is not None and route.get("enabled_state") == "enabled":
            fallback = route_map.get(fallback_id)
            if fallback and not (
                fallback.get("credential_present")
                and fallback.get("entitlement_state") == "entitled"
                and fallback.get("enabled_state") == "enabled"
                and fallback.get("runtime_validation_state") == "passed"
            ):
                errors.append(f"{route_id}: enabled route fallback must be credentialed, entitled, enabled, and runtime-passed")
    return errors


def validate_package(root: Path = ROOT, today: dt.date | None = None, overlay_path: Path | None = None) -> list[str]:
    errors: list[str] = []
    if today is None:
        today = dt.datetime.now(dt.timezone.utc).date() if root == ROOT else dt.date.fromisoformat(load_json(root / "public-model-roster.json")["as_of"])
    for path in REQUIRED_FILES:
        relative = path.relative_to(ROOT)
        candidate = root / relative
        if not candidate.exists():
            errors.append(f"missing package file: {relative}")
    if errors:
        return errors

    documents: dict[str, dict] = {}
    for document_path, schema_path in SCHEMAS.items():
        try:
            document = load_json(root / document_path)
            schema = load_json(root / schema_path)
        except ValueError as exc:
            errors.append(f"{document_path}: {exc}")
            continue
        documents[document_path] = document
        errors.extend(f"{document_path}: {error}" for error in schema_errors(document, schema, schema))

    if not all(path in documents for path in SCHEMAS):
        return errors

    roster = documents["public-model-roster.json"]
    bundled_overlay = documents["local-overlay.example.json"]
    try:
        overlay = load_json(overlay_path) if overlay_path else bundled_overlay
    except ValueError as exc:
        return errors + [f"external overlay: {exc}"]
    if overlay_path:
        overlay_schema = load_json(root / "local-overlay.schema.json")
        errors.extend(f"external overlay: {error}" for error in schema_errors(overlay, overlay_schema, overlay_schema))
    example = documents["examples/selection-record.example.json"]
    try:
        as_of = dt.date.fromisoformat(roster["as_of"])
        due = dt.date.fromisoformat(roster["review_due_at"])
        if as_of > today:
            errors.append("roster as_of cannot be in the future")
        if due <= as_of:
            errors.append("review_due_at must follow as_of")
        if (due - as_of).days > 31:
            errors.append("review window must be 31 days or less")
        if today > due:
            errors.append(f"roster is overdue: review_due_at {due.isoformat()} is before {today.isoformat()}")
    except (KeyError, ValueError, TypeError):
        errors.append("as_of and review_due_at must be ISO dates")
        as_of = None

    sources = roster.get("sources", [])
    specialist_text = (root / "SPECIALIST-MODELS.md").read_text(encoding="utf-8")
    specialist_dates = re.findall(r"^\*\*Snapshot date:\*\* (\d{4}-\d{2}-\d{2})\.", specialist_text, flags=re.MULTILINE)
    # The separately priced specialist appendix is a dated historical snapshot;
    # do not silently redate it when the language roster is refreshed.
    try:
        specialist_date = dt.date.fromisoformat(specialist_dates[0]) if len(specialist_dates) == 1 else None
    except ValueError:
        specialist_date = None
    if not as_of or specialist_date is None or specialist_date > as_of:
        errors.append("specialist snapshot date must appear exactly once and not follow roster as_of")
    source_ids = {source.get("source_id") for source in sources}
    if len(source_ids) != len(sources) or None in source_ids:
        errors.append("source IDs must be unique and non-null")
    for source in sources:
        url = source.get("url", "")
        if urlparse(url).scheme != "https" or not urlparse(url).netloc:
            errors.append(f"invalid official source URL: {url}")
        try:
            accessed = dt.date.fromisoformat(source.get("accessed_at", ""))
            if as_of and (as_of - accessed).days > 31:
                errors.append(f"stale source accessed_at: {source.get('source_id')}")
            if as_of and accessed > as_of:
                errors.append(f"source accessed after roster as_of: {source.get('source_id')}")
            if accessed > today:
                errors.append(f"source accessed_at cannot be in the future: {source.get('source_id')}")
        except ValueError:
            pass  # schema already reports malformed dates

    candidates = roster.get("candidates", [])
    candidate_ids = [candidate.get("candidate_id") for candidate in candidates]
    if len(candidate_ids) != len(set(candidate_ids)):
        errors.append("candidate IDs must be unique")
    known_anthropic_ids = {"claude-fable-5-1", "claude-fable-5", "claude-opus-5-5", "claude-opus-5", "claude-sonnet-5", "claude-haiku-4-5-20251001"}
    for candidate in candidates:
        candidate_id = candidate.get("candidate_id", "<missing>")
        expected_id = f"{str(candidate.get('provider', '')).lower()}/{candidate.get('model', '')}"
        if candidate_id != expected_id:
            errors.append(f"{candidate_id}: candidate_id must equal normalized provider/model")
        if not set(candidate.get("source_ids", [])).issubset(source_ids):
            errors.append(f"{candidate_id}: source binding invalid")
        bound_sources = [source for source in sources if source.get("source_id") in candidate.get("source_ids", [])]
        if not bound_sources or any(source.get("publisher") != candidate.get("provider") for source in bound_sources):
            errors.append(f"{candidate_id}: source publisher does not match candidate provider")
        bound_claims = " ".join(" ".join(source.get("claims", [])) for source in bound_sources).lower()
        if "price" not in bound_claims or not any(term in bound_claims for term in ("model", "catalogue", "catalog")):
            errors.append(f"{candidate_id}: sources must cover both model identity and price")
        if candidate.get("evidence", {}).get("suitability") == "observed" and candidate.get("validation_state") != "observed":
            errors.append(f"{candidate_id}: observed suitability requires observed validation_state")
        if candidate.get("provider") == "Anthropic" and candidate.get("model") not in known_anthropic_ids:
            errors.append(f"{candidate_id}: undocumented Anthropic API model ID")

    if any(route.get("credential_present") for route in bundled_overlay.get("routes", [])):
        errors.append("example overlay cannot claim credentials")
    if not str(bundled_overlay.get("notice", "")).startswith("EXAMPLE ONLY"):
        errors.append("bundled overlay notice must begin EXAMPLE ONLY")
    errors.extend(validate_overlay_document(overlay, roster))

    thresholds = example.get("thresholds", {})
    selection_candidates = example.get("candidates", [])
    selection_ids = [candidate.get("route_id") for candidate in selection_candidates]
    if len(selection_ids) != len(set(selection_ids)):
        errors.append("selection candidate route IDs must be unique")
    candidate_map = {candidate.get("route_id"): candidate for candidate in selection_candidates}
    chosen_id = example.get("decision", {}).get("chosen_route_id")
    fallback_id = example.get("decision", {}).get("fallback_route_id")
    chosen = candidate_map.get(chosen_id)
    fallback = candidate_map.get(fallback_id)
    if not chosen:
        errors.append("selection decision must choose a listed candidate")
    if not fallback or fallback_id == chosen_id:
        errors.append("selection fallback must reference a distinct listed candidate")
    score_pairs = [
        ("quality_score", "quality_score_min", lambda actual, floor: actual >= floor),
        ("completion_score", "completion_score_min", lambda actual, floor: actual >= floor),
        ("restraint_score", "restraint_score_min", lambda actual, floor: actual >= floor),
        ("successful_outcome_rate", "successful_outcome_rate_min", lambda actual, floor: actual >= floor),
        ("p95_latency_seconds", "p95_latency_seconds_max", lambda actual, ceiling: actual <= ceiling),
    ]
    if chosen:
        if not all(chosen.get("hard_gates", {}).values()):
            errors.append("chosen candidate must pass every hard gate")
        for score, threshold, predicate in score_pairs:
            if not predicate(chosen[score], thresholds[threshold]):
                errors.append(f"chosen candidate fails {threshold}")
    if fallback:
        if not all(fallback.get("hard_gates", {}).values()):
            errors.append("fallback candidate must pass every hard gate")
        for score, threshold, predicate in score_pairs:
            if not predicate(fallback[score], thresholds[threshold]):
                errors.append(f"fallback candidate fails {threshold}")

    public_paths = [root / path.relative_to(ROOT) for path in REQUIRED_FILES]
    public_text = "\n".join(path.read_text(encoding="utf-8") for path in public_paths if path.suffix in {".md", ".json"})
    for marker in ["/Users/", "/home/", "credential_present\": true", "live_activation\": true", "@gmail.com"]:
        if marker in public_text:
            errors.append(f"public package contains forbidden marker: {marker}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--today", help="Deterministic ISO date for freshness testing; defaults to current UTC date")
    parser.add_argument("--overlay", type=Path, help="Validate a private exact-route overlay without modifying it")
    args = parser.parse_args()
    today = dt.date.fromisoformat(args.today) if args.today else None
    errors = validate_package(today=today, overlay_path=args.overlay)
    if errors:
        for error in errors:
            print(error)
        print(f"model roster validation: FAILED ({len(errors)} error(s))")
        return 1
    roster = load_json(ROSTER_PATH)
    print(f"model roster validation: CLEAN ({len(roster['candidates'])} candidates, {len(roster['sources'])} official sources)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
