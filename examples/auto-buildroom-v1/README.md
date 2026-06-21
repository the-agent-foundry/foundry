# Auto-buildroom v1 fixture

This is a synthetic, public-safe fixture for governing agent-found build candidates.

It shows the contract chain shape, not a private run record. Replace the placeholders with your own workspace paths, validators, and approval rules before using it in a real system.

## Files

- `idea-contract.json` : proposal-only signal contract with a full Question Storm artifact.
- `intent-review.json` : stale/duplicate/safety filter before approval.
- `main-review.json` : bounded build approval review with hard gates preserved.
- `product-plan.json` : beneficiary, problem, non-goals, acceptance criteria, risk, and expected artifacts.
- `build-plan.json` : allowed/protected surfaces and verification checks.
- `coder-verification.json` : builder receipt with commands and exit-code evidence.
- `qa-verification.json` : independent QA receipt shape.
- `verification-delta.json` : confirmed/drift/regression/missing-evidence state.
- `trust-report.json` : clean/watch/investigate summary.
- `retention-review.json` : recommendation-only retention decision.
- `operator-summary.md` : human-facing status summary.
- `fixtures/` and `check_fixture_health.py` : tiny synthetic proof harness for stale/fresh health behavior.

## Pickup prompt

> Review this Auto-buildroom fixture. Tell me which internal recurring repairs or improvement candidates in my company deserve proposal-only detection first, what approval boundary each would need before build, and which validators would prove a clean closeout. Do not activate a recurring builder.
