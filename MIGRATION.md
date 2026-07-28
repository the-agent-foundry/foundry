# Migration notes

Most Agent Foundry updates are additive. When a release changes folder layout, schemas, required gates, or example contracts in a way that could break existing forks, the migration note lives here and is linked from the GitHub Release.

## Current migration status

No mandatory migration is required for the current additive update batch.

If you use an older engineer-agent configuration, review `agents/model-calibrated-engineering.md` before copying the updated archetype. Preserve frozen acceptance, approval boundaries, evidence gates, and rollback for every model. For models that stop early, add the bounded completion-support module. Do not preserve unbounded “boil the ocean” or “fix everything you find” language when moving to a more agentic model.

If you use an older finance-control pattern, no mandatory migration is required. To adopt the stronger contract, add a digest-bound mission envelope with closed roles, exact entity/book/period/system scope, versioned inputs, safe destinations, and required closeout; concrete action-layer Class A grants; complete Class B preview/impact/rollback/owner/receipt contracts; an explicit absent-capability map for Class C; actionable blocker packets; source provenance plus claim-scoped precedence; operation-key dedupe; timestamped write-time checks and readback methods; rollback/undo bindings; and honest `PARTIAL_VERIFIED` closeout. Keep direct entry non-authorizing. Validate a synthetic copy with `python3 gates/scripts/fixture_smoke.py .` before connecting live tools.

If you maintain a fork:

1. Pull the latest `main`.
2. Review `CHANGELOG.md` for what changed.
3. Copy only the patterns that help your own agent system.
4. Re-run your local sanitization and lint gates before publishing derived material.

## Maintainer standard for future breaking changes

For any major or breaking change, include:

- what changed
- who is affected
- old path or behavior
- new path or behavior
- manual migration steps
- validation command or checklist
- rollback note, if relevant

Breaking changes should also be called out in the GitHub Release under **Breaking changes** and linked back to this file.
