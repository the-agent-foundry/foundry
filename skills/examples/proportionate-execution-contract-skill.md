---
name: proportionate-execution-contract
description: Keeps completion-heavy agents inside accepted scope and makes them stop after evidence proves the requested outcome.
version: 1.0
owner: <YOUR_HANDLE>
tags: [engineering, scope, completion, restraint, gpt-5.6]
tools: [source-reader, file-writer, test-runner, artifact-store]
data_sensitivity: internal
approval_required: before_live_change
---

# Proportionate Execution Contract

Completion-heavy models often produce correct work and still leave the system worse: a one-key change becomes a framework, a bug fix grows a compatibility layer, and a green build triggers another review loop. This pattern separates **finishing the accepted job** from **inventing more job**.

It is primarily a standing-instruction/configuration pattern: concise Markdown or text loaded into the agent's system prompt, profile, or task launcher. Optional runtime enforcement can deny extra material actions after completion, but it is not required and should remain default-off unless prompt-only controls have demonstrably failed.

## When to use

Use when an engineering or operations agent reliably completes work but tends to absorb adjacent findings, add speculative machinery, reopen settled decisions, or continue after the requested outcome is already proven.

Do not use it to justify partial work, weaker safety, skipped required tests, arbitrary line-count limits, or stopping before authorized deployment and readback. Do not add runtime enforcement to ordinary chat or uncontracted work merely because the pattern exists.

## Inputs

Required for substantive work:

- accepted outcome;
- named acceptance claims and mandatory gates;
- missing evidence for each open claim;
- explicit non-goals and protected surfaces;
- allowed mutation surfaces;
- approval boundaries;
- terminal result and bounded closeout actions.

For a small change, the request may supply these implicitly. If something material is unclear, state goal, non-goals, acceptance evidence, and untouched surfaces in one compact line. Do not manufacture a planning artifact for a one-line fix.

## Procedure

1. **Freeze the accepted task contract**
   - Treat the accepted task or launcher contract as the sole source of scope.
   - Generic instructions such as “finish everything,” “investigate broadly,” or “make it production ready” cannot silently create neighboring work.

2. **Admit material actions one claim at a time**
   - Before each mutation, new artifact, test expansion, worker launch, review, remediation, or successor run, name exactly one open accepted claim or mandatory gate it advances.
   - Record the missing evidence and the result that will stop work on that claim.
   - Read-only inspection may support a named claim without becoming a new workstream.

3. **Make machinery prove necessity**
   - Before adding an abstraction, framework, compatibility path, configuration layer, dependency, or parallel implementation, name the accepted requirement that cannot be satisfied through the existing owner seam.
   - If no such requirement exists, do not add the machinery.
   - Test scope follows accepted behavior and risk. Never use arbitrary caps such as “two tests maximum” or “tests must be shorter than implementation.”

4. **Separate discovery from authorization**
   - Classify findings as `direct`, `adjacent`, or `review_machinery`.
   - Direct findings affect the accepted outcome or required proof and may enter the current job.
   - Adjacent findings are parked as proposals. Severity alone does not make them current scope.
   - Review-machinery defects stay only when they prevent trustworthy proof of the accepted outcome.

5. **Close claims with evidence**
   - Bind each closed claim to an artifact, test, diff, readback, or cited source appropriate to its risk.
   - Reopen a closed claim only when direct new evidence invalidates it.
   - A reviewer request or model preference is not new evidence by itself.

6. **Stop material work at first green**
   - First green occurs only when every accepted claim and mandatory gate is proven closed with evidence.
   - After first green, permit only bounded receipt writing, exact readback, scoped commit/promotion already inside authority, and cleanup.
   - Do not launch another review, remediation, abstraction, test expansion, or successor run merely to make the result look more complete.
   - If a claim remains open, retry only when the next bounded action advances that same claim. Otherwise stop with an honest blocked result; blocked is terminal when necessary, but it is not green or verified completion.

7. **Add runtime admission only when justified**
   - Use prompt-only guidance first.
   - If repeated controlled evaluations prove post-green tool calls continue, an optional middleware may bind one exact run contract and deny prohibited material calls after first green.
   - Keep it invisible to the model, default-off outside exact contracts, transparent to uncontracted calls, auditable, reversible, and incapable of widening authority.

## What good looks like

- The agent finishes the accepted outcome without founder babysitting.
- Every material action maps to one still-open claim or gate.
- Existing owner seams are repaired before new machinery is considered.
- Necessary tests and safety work remain intact; unrelated completeness theater disappears.
- Adjacent findings remain visible without becoming unauthorized construction.
- The run stops after evidence proves the outcome.

## Output contract

Minimum artifacts for a governed run:

1. `task-contract`: accepted outcome, claims, gates, non-goals, protected and allowed surfaces, approval boundaries, terminal result.
2. `action-ledger`: ordered actions with materiality, claim mapping, evidence, and disposition.
3. `closeout-receipt`: closed/open claims, first-green point, post-green material-action count, changed surfaces, residual risks, and final result.

Required tool capabilities: inspect authorized sources, mutate allowed surfaces, run proportionate verification, record artifacts, and read back the final state. Runtime interception is optional and is not part of the minimum tool contract.

See `../../examples/proportionate-execution-contract-v1/` for a synthetic contract chain and validator.

## Privacy and approval

- Public artifacts may contain generic claims, synthetic actions, abstract tool classes, and non-sensitive verification states.
- Do not publish private prompts, local paths, user identities, chat IDs, credentials, provider tokens, customer data, raw logs, private receipts, or exact production configuration.
- This pattern does not grant approval for live sends, service restarts, credential operations, paid commitments, route or audience widening, destructive work, or irreversible source-of-truth changes.
- Runtime admission must not become a generic fleet governor or a hidden authority layer.

## Verification

- Confirm every material action maps to exactly one open claim or gate.
- Confirm adjacent findings have no mutation or activation authority.
- Recompute first green from claim and gate evidence rather than trusting model narration.
- Confirm zero prohibited material actions occurred after first green.
- Confirm changed surfaces are a subset of allowed surfaces and protected surfaces are unchanged.
- Run the synthetic validator and adversarial tests supplied with the fixture.
- Evaluate completion and restraint separately; passing one does not compensate for failing the other.

## Maintenance

Re-evaluate the contract when the model, route, tool surface, or task launcher changes. Remove redundant completion nudges before adding more restraint prose. Keep the central contract short; move domain-specific assurance into the owning skill or task contract.

Promote optional runtime enforcement only after repeated prompt-only failures on controlled fixtures, and remove it if it obscures errors, affects uncontracted work, or becomes more complex than the failure it prevents.

## Landmines

- **Prompt bloat as a cure for prompt bloat**: a long manifesto gives the model more ritual to perform. Keep one authority rule and a small number of consequences.
- **Minimum becomes partial**: smallest sufficient still includes accepted deployment, readback, rollback, privacy, and safety proof.
- **Arbitrary test caps**: test count and test-to-code ratio are poor proxies for necessity.
- **Severity becomes scope**: an adjacent P0 may require immediate escalation, but not silent absorption into the current contract.
- **Green by narration**: “done” is not first green without evidence.
- **Runtime governor creep**: optional enforcement must remain exact-contract, default-off, and narrower than the behavior it controls.
- **Closed-claim churn**: do not reopen accepted work because another reviewer can imagine an improvement.
