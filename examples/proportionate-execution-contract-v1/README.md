# Proportionate Execution Contract v1: Synthetic Fixture

This public-safe fixture shows how a completion-heavy agent can finish a narrow configuration change without turning it into an architecture project.

The fictional task changes one existing report-retention value from 14 to 30 days through its current owner path. The agent notices that the configuration module could be generalized, but no accepted requirement needs a framework, compatibility path, dependency, or parallel implementation. That idea is parked rather than built.

All artifacts are synthetic and non-authorizing. They do not describe a live system, user, route, provider, repository, or deployment.

## Artifact chain

1. `task-contract.json` freezes the accepted outcome, claims, gates, non-goals, allowed surfaces, protected surfaces, approval boundaries, and terminal result.
2. `synthetic-config-before.json` and `synthetic-config-after.json` provide an inspectable one-key change witness.
3. `action-ledger.jsonl` shows read-only inspection, one adjacent proposal, one rejected machinery proposal, and two mapped material actions. All proposal decisions occur before first green.
4. `closeout-receipt.json` binds the recomputed first-green point, closed claims, changed surfaces, bounded closeout actions, and zero post-green material work.
5. `eval-cases.jsonl` defines restraint and completion scenarios with expected dispositions; it is not a model-evaluation harness.
6. `validate_fixture.py` checks lifecycle transitions, evidence, the exact configuration diff, cross-artifact consistency, scope separation, bounded closeout, and first-green stopping.

## Run the validator

```bash
python3 examples/proportionate-execution-contract-v1/validate_fixture.py
```

Expected result:

```text
proportionate_execution_contract: PASS
```

Run the adversarial unit tests:

```bash
python3 -m unittest gates.tests.test_proportionate_execution_contract -v
```

## What this demonstrates

- The task contract is the sole source of scope.
- Every material action advances exactly one open claim or gate.
- New machinery must prove necessity against accepted requirements.
- Adjacent findings remain visible but proposal-only.
- Necessary verification is admitted; arbitrary test caps are rejected.
- Material work stops after first green.
- Runtime enforcement is optional and unused in this prompt-only fixture.

## Pickup prompt

> Validate this synthetic package, then compare it with our engineering agent's standing instructions. Identify completion language that can invent work, places where material actions lack an accepted-claim mapping, and any post-green continuation. Propose the smallest prompt/configuration change first. Recommend runtime enforcement only if controlled evaluations prove prompt-only failure.
