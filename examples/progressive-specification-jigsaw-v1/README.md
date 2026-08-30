# Progressive Specification: Jigsaw v1 Synthetic Fixture

This public-safe package shows how an agent can turn an ambiguous product request into an owner-approved, implementation-ready blueprint without silently starting the build.

The fictional product is an internal workshop booking application. Every artifact is synthetic and non-authorizing. The package contains no live system, private prompt, user identity, runtime route, credential, customer record, or implementation authority.

## Artifact chain

1. `PHASE-0-SPECIFICATION.md` is the complete plain-English candidate the owner reviews.
2. `CHARTER.md` is an exact byte copy of the approved candidate, not a second rewritten specification.
3. `charter-lock.json` binds the synthetic approval reference, candidate digest, charter digest, exact-copy state, and no-execution boundary.
4. `decision-pieces.jsonl` resolves bounded data, schedule, and integration questions against the locked charter.
5. `integration-sweep.json` proves producer/consumer parity, state ownership, recovery, rollback, observability, and acceptance coverage over one accepted generation.
6. `BUILD-SPEC.json` turns accepted decisions into dependency-ordered builder cells with requirements, interfaces, invariants, failure behavior, allowed/protected surfaces, verification, rollback, and readback.
7. `STATUS.json` records the compact lifecycle state and next genuine owner gate.
8. `final-readiness.json` binds the exact blueprint and ends at `READY_FOR_BUILDER` plus `BUILD_NOT_STARTED` with no builder-launch authority.
9. `validate_fixture.py` recomputes cross-artifact identity, lifecycle, traceability, dependency, terminal-state, and authority checks.

## Run the validator

```bash
python3 examples/progressive-specification-jigsaw-v1/validate_fixture.py
```

Expected result:

```text
progressive_specification_jigsaw: PASS
```

Run adversarial tests:

```bash
python3 -m unittest gates.tests.test_progressive_specification_jigsaw -v
```

## What this demonstrates

- Phase 0 is a design conversation, not a hidden charter generator.
- The owner approves one complete specification generation.
- The locked charter is an exact copy of what the owner reviewed.
- Decision mapping, integration, and blueprint creation continue autonomously inside the approved envelope.
- Every requirement reaches at least one accepted decision piece and one dependency-ordered builder cell.
- Readiness does not grant implementation, deployment, external-send, or builder-launch authority.
- The terminal boundary is mechanically distinct from build completion.

## Trust boundary

The validator proves that this fixture is internally consistent and matches the repository's frozen synthetic identity. In a real system, an approval reference still needs an authenticated, durable source; a self-reported approval string is not proof of human authorization. Keep approval capture separate from model narration.

## Pickup prompt

> Review this synthetic Jigsaw package and adapt the operating contract, not the fictional product, to our environment. First conduct a conversational specification phase and show me the complete plain-English candidate. Do not lock a charter until I approve that exact generation. After approval, map decisions, run an integration sweep, and prepare dependency-ordered builder cells autonomously. Stop at `READY_FOR_BUILDER` and `BUILD_NOT_STARTED`; ask before handing the blueprint to a builder or starting implementation.
