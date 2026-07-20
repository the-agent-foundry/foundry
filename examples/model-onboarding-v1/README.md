# Model Onboarding v1: Synthetic Fixture

This fixture shows the minimum public artifact chain for evaluating and activating a model route. It contains no real provider account, credentials, private prompts, live route, or private evaluation data.

Pair it with `../../skills/examples/model-onboarding-skill.md`.

## Scenario

A company is comparing its accepted baseline model route with a candidate route for an internal engineering agent. The candidate must improve task completion without increasing unauthorized scope or weakening privacy.

## Files

- `source-ledger.jsonl`: synthetic official-source records.
- `route-matrix.json`: baseline/candidate route facts and unknowns.
- `eval-manifest.json`: frozen corpus, rubric, floors, and hashes.
- `comparison-report.json`: completion, restraint, quality, and safety comparison.
- `activation-receipt.json`: synthetic inactive-generation activation/readback/rollback proof.
- `drift-report.json`: demonstrates detection of a changed route identity.

All IDs and hashes are illustrative. Replace them with generated values in a private implementation.

Provider-level privacy policy does not prove exact-route eligibility. Both synthetic routes intentionally keep retention eligibility unknown, so private activation remains blocked until exact account and endpoint conditions are independently verified.

## Pickup prompt

> Review this model-onboarding fixture against our current model-switch process. Identify missing route facts, private test data, approval boundaries, and runtime readback. Do not recommend activation from benchmark reputation alone.
