# Engineering Governance v2: Synthetic Fixture

This public-safe fixture demonstrates model-calibrated engineering governance without exposing a private agent, launcher, model route, or runtime.

Pair it with `../../agents/model-calibrated-engineering.md` and `../../agents/archetypes/engineer.md`.

The synthetic job repairs a recurring local report generator. The accepted outcome is narrow: prevent duplicate reports, preserve existing destinations, prove rollback, and deploy the reversible fix. The reviewer also notices an unrelated dashboard styling issue; that finding is retained as adjacent rather than absorbed.

Every approval, deployment, promotion, rollback, and terminal-state value belongs only to this fictional scenario. Every structured artifact declares `synthetic: true` and `authorizing: false`; none can authorize or describe a live action.

## Artifact chain

1. `acceptance-contract.json` freezes outcome, non-goals, protected surfaces, and terminal state.
2. `finding-ledger.json` separates direct, adjacent, and review-machinery findings.
3. `retained-checkpoint.json` shows how valid work survives a mechanical interruption.
4. `parent-followthrough.json` proves that worker-green is not terminal until deployment and readback finish.

## Model adaptation

- A completion-capable model receives the scope-calibrated objective and adjacent-routing rules.
- A hesitant model receives the same structural contract plus a bounded completion-support module.
- Neither model receives authority to widen scope, skip gates, or cross approval boundaries.

## Pickup prompt

> Validate this fixture as a coherent contract chain. Then compare it to our engineer agent: where would it stop too early, and where would it over-expand? Recommend the smallest prompt/runtime change that improves both completion and restraint.
