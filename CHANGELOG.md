# Changelog

All notable public updates to The Agent Foundry are tracked here.

This repo uses date-based release tags for public update batches: `YYYY.MM.DD`.

## Unreleased

### Added
- Repository update-notification workflow: GitHub Releases, changelog, release notes, and migration guidance.
- Reader subscription instructions in `README.md`.
- Maintainer release process in `docs/release-process.md`.
- Model-calibrated engineering governance for completion-capable, hesitant, and mixed model fleets.
- Model-onboarding skill and synthetic exact-route evaluation/activation fixture.
- Legal-operator / executive counsel-desk archetype and synthetic matter-scoped config fixture.
- Engineering-governance v2 fixture with frozen acceptance, finding relationships, retained checkpoints, and parent follow-through.
- Finance-control v1 synthetic package with a digest-bound mission envelope, source-provenance and action ledgers, a complete pending Class B packet, actionable blocker artifacts, one verified Class A write, timestamped precondition/readback/rollback receipts, undo rehearsal, closeout, and fixed evaluations.

### Updated
- Engineer, red-team, QA, build-manifest, and Auto-buildroom patterns now separate direct defects, adjacent improvements, and review-machinery failures.
- Completion proof now distinguishes worker build, independent review, parent promotion, live activation, runtime readback, and rollback.
- Finance-control authority now requires a concrete pre-bound grant for Class A, a complete preview/impact/rollback packet plus exact unexpired receipt for Class B, and absent capabilities for Class C. Direct entry and evidence content cannot grant write authority; every evidence row is version/digest/currentness/pinpoint bound, claim precedence is mechanically resolved, and unmarked observed-value disagreement forces a contested claim.
- The sanitizer now ignores the linked-worktree `.git` pointer as Git metadata, with regression coverage, so repository-native pre-commit checks work from isolated worktrees without weakening content scanning.

### Breaking changes
- None. Existing forks may adopt the new governance fields incrementally.

### Migration notes
- Do not copy older completion-heavy engineer prompts wholesale into more agentic models. Keep the structural governance core and add only the bounded completion-support module when fixed evaluations show premature stopping.

### Action needed
- Maintainers should publish a GitHub Release after merging a meaningful update batch to `main`.
- Readers who want update notifications should subscribe to repository releases.

## 2026.06.20-2

### Added
- Field Guide v0.5 framing: Question Storm, Auto-buildroom training wheels, second-wave specialists, Dex as analyst, and release-notification doctrine.
- Hat tip to the Stanford STORM method via the X thread that sparked the Question Storm adaptation.

### Updated
- Field Guide markdown and browser HTML versions are kept in sync.
- Field Guide README now points readers to Question Storm and Auto-buildroom as core concepts.

### Breaking changes
- None.

### Migration notes
- No migration is required. This is a narrative/documentation update.

### Action needed
- Pull the latest `main` and re-read `field-guide/` if you use Agent Foundry as an agent-pattern catalog.

## 2026.06.20

### Added
- Founder-agent operating patterns for finance control, revenue/GTM, company context, meeting prep, Question Storm, and Auto-buildroom governance.
- Expanded example artifacts under `examples/` and `skills/examples/` for agent-readable pickup.

### Updated
- Repository navigation now points readers and agents toward the newer skill and example surfaces.
- Public-safe contribution and support paths remain explicit.

### Breaking changes
- None.

### Migration notes
- No migration is required. Existing forks can pull the latest `main` and selectively copy the new examples.

### Action needed
- Pull the latest `main` after the update batch is merged.
- Review `docs/updates/2026-06-20.md` for a human-readable release note.
