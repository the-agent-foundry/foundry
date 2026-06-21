# Migration notes

Most Agent Foundry updates are additive. When a release changes folder layout, schemas, required gates, or example contracts in a way that could break existing forks, the migration note lives here and is linked from the GitHub Release.

## Current migration status

No migration is required for the `2026.06.20` update batch.

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
