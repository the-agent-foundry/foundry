---
name: progressive-specification-jigsaw
description: Turns ambiguous product goals into an owner-approved, implementation-ready blueprint without starting the build.
version: 1.1
owner: <YOUR_HANDLE>
tags: [specification, architecture, decision-mapping, scope-control, builder-handoff]
tools: [conversation, source-reader, research, artifact-store, validator]
data_sensitivity: internal
approval_required: before_write
---

# Progressive Specification: Jigsaw

Jigsaw resolves product fog before implementation. It is a design conversation first and deterministic lifecycle machinery second. Its terminal boundary is `READY_FOR_BUILDER` plus `BUILD_NOT_STARTED`: the blueprint may be ready while implementation remains unauthorized and untouched.

## When to use

Use Jigsaw when the destination, users, behavior, architecture, interfaces, authority, migration, or acceptance criteria still require consequential decisions. It fits new products, major workflows, agent-system designs, migrations, and cross-component changes where building before agreement would create expensive rework.

Do not use it for a bounded repair whose source owner, interfaces, acceptance test, rollback, and authority are already known. Do not use it as planning theater for routine tasks, or as authority to launch an engineering agent.

## Inputs

Required:

- problem and initiating frustration;
- intended users, operating context, and owner-visible product;
- success criteria and unacceptable failures;
- non-goals and privacy, authority, compatibility, or migration boundaries;
- known sources and assumptions;
- owner identity or role that can approve the specification;
- durable artifact location with access controls appropriate to the source data.

Optional:

- existing system topology and interfaces;
- internal source inspection;
- external research;
- feasibility spikes for genuinely uncertain architecture;
- a known builder handoff schema.

If destination, audience, authority, or unacceptable failure is unclear, remain in the design conversation. Do not silently fill material gaps and call the result approved.

## Procedure

1. **Conduct Phase 0 as a real design conversation**
   - Present a provisional understanding of the problem, intended product, users, and why it matters.
   - Ask one to three adaptive questions at a time whose answers can change a real decision.
   - Pressure-test assumptions, offer material alternatives, and explain the consequence of being wrong.
   - Continue until the owner can explain the destination simply and agrees the proposal makes sense.

2. **Show the complete specification**
   - Produce one plain-English candidate containing the problem, product behavior, users and context, acceptance criteria, owner decisions, delegated freedom, non-goals, authority boundaries, unacceptable failures, risks, amendment triggers, builder handoff shape, recommendation, and material alternatives.
   - Keep the exact candidate bytes in a durable Phase 0 artifact.
   - Ask what is wrong or missing; revise before requesting approval.

3. **Bind the exact approval generation**
   - Preflight the candidate for required sections, substantive acceptance criteria, placeholders, unsafe references, and execution-authority language.
   - Compute an exact digest and present a human-readable readback.
   - Lock only after the owner explicitly approves that exact semantic generation.
   - Copy the approved candidate unchanged into the canonical charter and record equal candidate/charter digests plus an authenticated approval reference.
   - Any material body change requires a new approval generation.

4. **Map decisions autonomously inside the locked envelope**
   - Create bounded pieces such as `owner_decision`, `internal_inspection`, `external_research`, `feasibility_spike`, `bounded_design`, and `integration`.
   - Each piece resolves one decision-changing question and binds the current charter identity, evidence, interfaces, invariants, failure behavior, acceptance, residual uncertainty, and `execution_authority: false`.
   - A feasibility spike is disposable evidence. It needs an accepted design or integration successor before production mapping.
   - Escalate only a decision that would materially change destination, users, authority, unacceptable failure, a major migration/compatibility obligation, or the promised product.

5. **Run an integration sweep**
   - Reconcile producers and consumers, state owners, shared concepts, migration and compatibility, observability, recovery, rollback, acceptance coverage, and stale bindings.
   - Require one current passing sweep over the exact accepted piece generation.
   - Parent/orchestrator synthesis owns integration; worker consensus does not amend the charter.

6. **Create dependency-ordered builder cells**
   - Use the fewest cells that preserve dependencies and verification.
   - Every cell names requirements, accepted pieces, interfaces, responsibilities, non-goals, inputs, outputs, state owner, invariants, failure behavior, allowed and protected surfaces, activation boundary, rollback, readback, and cumulative verification.
   - Keep implementation freedom broad inside the contract; do not prescribe arbitrary file or test-count ceilings.

7. **Validate and stop at the true owner gate**
   - Recompute traceability from requirements through accepted pieces, integration, and builder cells.
   - Reject stale identity, missing evidence, orphan interfaces, authority widening, incomplete failure behavior, and unsupported readiness claims.
   - Produce a concise owner readback: what was designed, how it works, what a builder would create, slices, verification, remaining risks, expected burden, and the exact meaning of done.
   - End with `READY_FOR_BUILDER` and `BUILD_NOT_STARTED`. Ask whether to hand the exact validated blueprint to a builder. Do not launch one.

## What good looks like

- The owner recognizes the final product as the one discussed, not a machinery-shaped substitute.
- One exact approved specification becomes the locked charter without prose drift.
- Material owner decisions remain owner-controlled; routine design and recovery continue autonomously.
- Every requirement maps to accepted evidence, interfaces, integration checks, and builder verification.
- Producer/consumer, state ownership, migration, recovery, rollback, and observability seams are explicit.
- Builder cells are dependency-complete, bounded, and implementation-ready without dictating irrelevant mechanics.
- The final state is mechanically proven as blueprint-ready and build-not-started.

## Output contract

Minimum durable artifact chain:

1. `PHASE-0-SPECIFICATION`: complete owner-visible candidate.
2. `CHARTER`: exact copy of the approved candidate.
3. `charter-lock`: candidate/charter digests, approval reference, charter state, and no-execution boundary.
4. `decision-pieces`: typed accepted decisions with evidence and charter binding.
5. `integration-sweep`: exact generation, required seam checks, and pass/fail evidence.
6. `BUILD-SPEC`: dependency-ordered cells with cumulative verification and protected surfaces.
7. `STATUS`: phase, charter state, accepted generation, blockers, next move, and next owner gate.
8. `final-readiness`: exact blueprint digest, `READY_FOR_BUILDER`, `BUILD_NOT_STARTED`, and no builder-launch authority.

Required tool capabilities: conversational refinement, authorized source inspection, bounded research, durable artifact writes, exact hashing, schema/structure validation, and readback. A builder launcher is deliberately absent from this skill's minimum capability set.

See `../../examples/progressive-specification-jigsaw-v1/` for a synthetic fixture and standard-library validator.

## Privacy and approval

- Match artifact access to the highest data class in the specification sources.
- Public examples may contain only synthetic products, generic roles, placeholder approval references, and non-authorizing evidence.
- Never publish private prompts, personal identities, local paths, chat IDs, credentials, customer/vendor data, raw transcripts, production topology, live configuration, or source-of-truth records.
- Owner approval is required before locking the specification. The approval reference must come from an authenticated durable source; model narration is not approval evidence.
- Separate approval is required before handing the blueprint to a builder, starting implementation, changing live systems, sending externally, spending money, changing credentials, or widening routes or audiences.
- Accepted pieces and readiness artifacts always carry `execution_authority: false`.

## Verification

- Confirm the Phase 0 candidate and locked charter are exact byte copies and bind the approved digest.
- Confirm required charter sections are substantive, not placeholders or repeated filler.
- Confirm every accepted piece binds the current charter, contains typed evidence, and grants no execution authority.
- Confirm feasibility spikes cannot map directly into builder cells without an accepted successor.
- Confirm one current passing integration sweep covers producer/consumer parity, state ownership, migration, observability, recovery, rollback, and acceptance.
- Confirm every requirement and accepted production decision reaches at least one dependency-valid builder cell and verification.
- Confirm allowed and protected surfaces do not overlap.
- Confirm final markers are exactly `READY_FOR_BUILDER` and `BUILD_NOT_STARTED`, with build-started and builder-launch authority both false.
- Run deterministic fixture validation and adversarial mutation tests. Treat those checks as structural proof, not proof of design wisdom or authentic human approval.

## Maintenance

Update the skill when a real specification run exposes a missing owner gate, stale-binding failure, interface gap, recovery problem, or blueprint ambiguity. Add the reproduced failure to the validator or adversarial suite when it is mechanically testable.

Review the skill when artifact schemas, approval capture, builder handoff, model behavior, or privacy boundaries change. Keep conversational judgment in the skill and deterministic invariants in validators; do not bury the design process under receipts.

## Landmines

- **Hidden charter generation**: silently inventing the destination and asking for approval defeats the design conversation. Show provisional understanding and ask adaptive questions first.
- **Two competing specifications**: rewriting the approved prose into a second charter creates drift. Copy exact bytes and bind the approval digest.
- **Approval by narration**: a model-written “approved” field is not authenticated owner evidence.
- **Piece bureaucracy**: pieces resolve decisions; they are not miniature build tasks or a reason to fragment simple work.
- **Spike becomes production**: disposable feasibility code cannot enter the build map without an accepted design successor.
- **Green fragments, broken whole**: individually accepted pieces do not prove interface or state-owner coherence. Require an integration sweep.
- **Blueprint equals permission**: readiness never authorizes implementation, deployment, external sends, credentials, or builder launch.
- **Validator theater**: hashes and schemas prove structure and binding, not product taste, owner understanding, or source truth.
- **Arbitrary slicing**: file ceilings and test-count caps can destroy dependency integrity. Slice by coherent state and interface ownership.
- **Endless owner gates**: only material destination/authority changes need escalation; routine mapping, integration, recovery, and validation remain autonomous.
