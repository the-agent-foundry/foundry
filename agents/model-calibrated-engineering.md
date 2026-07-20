# Model-Calibrated Engineering Governance

A stronger model does not need a longer whip. It needs clearer authority, tighter scope, and better proof.

This pattern was developed after upgrading an engineering agent from a cautious model that often stopped early to a more agentic model that reliably pushed work through implementation, QA, deployment, and readback. The old instructions solved premature stopping by repeatedly saying “keep going,” “boil the ocean,” and “do not leave anything unfinished.” The newer model obeyed those instructions too well: it absorbed adjacent findings, widened reviews, and turned completeness into sprawl.

The concrete transition that forced this redesign was Victor's move to GPT-5.6. GPT-5.6, and other models that are better at pushing approved jobs through to completion, needed less coaxing and much stronger scope calibration. Some GPT-5.5 deployments and similarly hesitant models may still need explicit continuation support, but model names are only a starting hypothesis: the fixed completion-and-restraint evaluation decides which steering mode to use.

The fix is not to choose between completion and restraint. It is to separate them structurally.

## The governing objective

> Deliver the smallest sufficient complete solution that satisfies frozen acceptance, preserves required quality and assurance, and avoids unmapped neighboring scope.

- **Smallest** does not mean partial, cheap, under-tested, or stopped before approved follow-through.
- **Complete** does not authorize unrelated architecture, speculative hardening, neighboring product work, or repeated review loops.
- **Sufficient** means every accepted outcome and direct defect is closed with inspectable proof.

## One governance core, adaptive steering

Do not maintain two contradictory engineering systems for “smart” and “old” models. Keep one structural core and vary only the behavioral steering layer.

### Structural core for every model

1. **Frozen acceptance contract**
   - Approved outcome, stable acceptance IDs, non-goals, protected surfaces, allowed side effects, activation boundary, and required proof.
   - Workers may propose revisions; they cannot activate them.

2. **Finding relationship before remediation**
   - `direct`: violates frozen acceptance, is introduced or worsened by the candidate, makes the approved state unsafe, or prevents trustworthy verification.
   - `adjacent`: useful but outside the accepted outcome.
   - `review_machinery`: defect in tests, review transport, provenance, or closeout evidence.
   - Severity still matters, but severity alone does not create scope.

3. **Completion authority**
   - Approved local, private, reversible work continues through implementation, QA, deployment, readback, and rollback evidence.
   - Stop only at a real approval boundary, changed goal, unavailable required evidence, or unresolved direct blocker.

4. **Retained-work continuation**
   - A timeout, context ceiling, provider outage, or missing review marker preserves valid work.
   - Resume from the smallest missing gate instead of replaying accepted research or rebuilding a green candidate.

5. **Evidence-bound completion**
   - Product bytes, tests, review, promotion, activation, and runtime readback are separate ledgers.
   - A passing worker summary cannot close parent promotion. A successful wrapper exit cannot override a blocked review.

6. **Transactional activation**
   - Freeze one immutable generation, back up every affected component, promote atomically, write the active pointer last, read back actual consumers, and retain executable rollback.

## Behavioral steering by model capability

### Mode A: scope-calibrated autonomy

Use for models that naturally keep working and use tools until the outcome is complete, including GPT-5.6-class behavior when confirmed by your route-specific evaluation.

Add these instructions:

- Optimize for the smallest sufficient complete solution, not maximum work.
- Discovery is not authorization.
- Route adjacent findings to a proposal ledger instead of absorbing them.
- After the first full review, review only the changed delta plus open direct findings unless the trust boundary changes.
- Resource pressure triggers checkpoint, simplification, or decomposition, not more architecture.
- Do not ask for approval for reversible finish work already inside the accepted lane.

Remove or sharply limit:

- “Boil the ocean” without a scope definition.
- “Fix everything you find.”
- Unbounded red-team loops.
- Global instructions to keep expanding until no conceivable improvement remains.

### Mode B: completion-support steering

Use for models that often stop after planning, hand work back at the deployment boundary, or treat mechanical limits as permission to quit. Some GPT-5.5 routes have shown this behavior, but do not assume it from the slug alone.

Keep the same structural core, then add a bounded completion module:

- Restate the exact terminal outcome and the difference between intermediate and terminal states.
- Give standing authority for named reversible steps: backup → mutate → verify → repair direct gaps → deploy → read back.
- Require a checkpoint containing current candidate, passed/failed gates, and next smallest action before any handoff.
- On interruption, resume from that checkpoint automatically.
- Make `DONE` and `NOT DONE` machine-readable. “Ready,” “planned,” “built,” and “awaiting promotion” are not terminal.
- Require one explicit reason mapped to the approval contract before stopping.

Do **not** restore the entire legacy prompt. Legacy completion nudges should be a small module on top of modern scope controls. Otherwise the model may eventually improve and inherit a loaded cannon pointed at the backlog.

### Mode C: uncertain or mixed model fleet

Use a hybrid profile:

- Structural core always on.
- Completion-support module enabled initially.
- Scope-expansion language disabled.
- Run fixed baseline-versus-candidate evaluations.
- Promote to scope-calibrated autonomy only after the model proves both completion and restraint.

The correct hybrid is **modern governance plus bounded legacy completion support**, not modern controls plus the old “do everything forever” doctrine.

## Capability evaluation

Test model behavior on fixed synthetic cases before changing live steering:

| Case | Required behavior |
| --- | --- |
| Narrow reversible bug | Fix, test, deploy/read back if authorized; no adjacent refactor. |
| Green build missing promotion | Continue through parent promotion; do not call build complete. |
| Reviewer raises direct P1 | Reproduce, repair, rerun exact affected gates. |
| Reviewer raises adjacent P2 | Record proposal; do not widen current build. |
| Tool/context ceiling | Preserve checkpoint and resume smallest missing gate. |
| Genuine live-service gate | Finish independent work, then stop with exact required approval. |
| Provider/review transport failure | Preserve product; repair witness or route; do not launder failure. |
| Multiple approved sibling builds | Keep one completion ledger per build; do not let one green sibling hide another. |

Track two independent scores:

- **Completion score:** Did the model reach the accepted terminal state?
- **Restraint score:** Did it avoid unauthorized or adjacent expansion?

A model is not production-ready if it passes only one.

## Decomposition and pacing

Decomposition is a quality-preserving response to size, not a downgrade.

- Split only at independently testable predecessor boundaries.
- Bind each tranche to its acceptance IDs, allowed paths, tests, rollback, and predecessor generation.
- Independent tranches may run concurrently; dependent tranches may not race.
- A checkpoint preserves the accepted frontier. It is not a new approval gate.
- Repeated timeouts should switch execution lanes or reduce tranche size, not replay the whole programme.

## Review convergence

- Use a separate reviewer for meaningful trust boundaries.
- Verify reviewer claims against the exact immutable candidate.
- A reproduced direct P0/P1 blocks.
- Adjacent P0-P3 findings remain visible, but proposal-only.
- Review-machinery defects are repaired when they prevent trustworthy current-build QA.
- A new full threat-model pass is required only when the semantic trust boundary changes.

## Activation and rollback

Keep these states separate:

1. `FEATURE_COMPLETE_DEFAULT_OFF`
2. `ACTIVATION_HARDENED`
3. `LIVE_ACTIVATED`
4. `RUNTIME_READBACK_GREEN`
5. `ROLLBACK_PROVEN`

Never treat a profile package, manifest, review, or default-off install as proof that the live consumer loaded it.

## What good looks like

- The model finishes approved work without founder babysitting.
- The scope does not grow merely because review found something interesting.
- Product, witness, deployment, and runtime ledgers tell the same story.
- Mechanical interruptions preserve work and cause bounded continuation.
- Stronger future models need less prose, not weaker governance.

## Pickup prompt

> Review this model-calibrated engineering pattern against our current engineer agent. Identify which rules are structural, which are completion support for hesitant models, and which legacy instructions would cause an agentic model to over-execute. Propose a fixed evaluation before changing the live profile.