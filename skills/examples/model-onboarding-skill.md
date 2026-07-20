---
name: model-onboarding
description: Evaluates and activates a new model route against fixed capability, safety, privacy, completion, restraint, and rollback contracts before live use.
version: 1.0
owner: <YOUR_HANDLE>
tags: [models, evaluation, routing, privacy, activation, drift]
tools: [official-doc-reader, route-probe, fixture-runner, evaluator, config-reader, activation-controller]
data_sensitivity: internal
approval_required: before_live_change
---

# Model Onboarding

A model name in a config file is not an onboarding. This skill proves that the exact route can perform the intended work, obey the authority boundary, and survive activation and rollback.

## When to use

Use when adding, replacing, upgrading, or materially rerouting a model/provider for an orchestrator, specialist, evaluator, or unattended workflow.

Do not use benchmark reputation as a substitute for route-specific proof. The same model can behave differently across providers, endpoints, tool surfaces, system prompts, reasoning modes, and retention policies.

## Inputs

Required:

- target role and real workloads;
- baseline route and candidate route;
- official model/provider documentation;
- endpoint, tool, context, structured-output, privacy, retention, pricing, and rate-limit facts;
- fixed positive and negative evaluation corpus;
- acceptance thresholds and hard safety floors;
- activation boundary, rollback, and drift-monitoring plan.

If any material route fact is unknown, label it unknown. Do not fill gaps from model memory.

## Procedure

1. **Build an official-source ledger**
   - Record source URL, publisher, date, accessed date, claim, exact quote where useful, confidence, and affected decision.
   - Separate model capability from provider/endpoint behavior.

2. **Inventory the exact route**
   - Provider, model, endpoint/API mode, reasoning controls, context/output limits, tools, structured output, streaming, data retention, training use, residency, zero-data-retention eligibility, pricing, rate limits, and fallback behavior.
   - Record unknowns explicitly.

3. **Freeze baseline and candidate**
   - Bind exact configuration, prompts/adapters, tool inventory, fixture manifest, evaluator version, and acceptance thresholds.
   - Prevent the candidate from changing the benchmark or rubric.

4. **Evaluate useful capability**
   - Role-specific task quality.
   - Tool use and structured-output compatibility.
   - Long-context and source-grounding behavior where relevant.
   - Completion behavior: does it finish approved work?
   - Restraint behavior: does it avoid adjacent or unauthorized work?

5. **Evaluate safety and authority**
   - Privacy and prompt-injection cases.
   - External-action and approval denial cases.
   - Unsupported-claim and abstention cases.
   - Route/session provenance.
   - No fallback to an unapproved provider or model.

6. **Compare baseline versus candidate**
   - Use the same fixed corpus and scoring contract.
   - Report wins, regressions, invalid cases, and confidence.
   - Hard safety/privacy floors override average quality.

7. **Apply in an inactive generation**
   - Build the complete config/prompt/adapter generation default-off.
   - Validate actual runtime parsing and route projection.
   - Run production-shaped disposable canaries.

8. **Activate transactionally**
   - Require explicit approval if live activation is gated.
   - Back up the complete predecessor.
   - Promote one immutable generation.
   - Write the active pointer last.
   - Read back the actual consumer route, model, tools, and behavior.

9. **Prove rollback**
   - Restore the complete predecessor and verify it.
   - Reinstall/reactivate the candidate only after rollback passes when the intended final state is candidate-active.

10. **Monitor drift**
   - Watch provider/model identity, endpoint behavior, tool compatibility, latency/cost, invalid-output classes, safety floors, and quality regressions.
   - Re-evaluate on meaningful model, provider, prompt-adapter, tool, or policy change.

## What good looks like

- Official claims are source-ledgered and route-specific.
- Baseline and candidate use the same frozen corpus.
- Completion and restraint are both scored.
- Privacy and authority floors are non-negotiable.
- Runtime-applied proof exists; a config diff is not enough.
- Activation and rollback are complete-generation transactions.
- Drift monitoring can identify when the route no longer matches the accepted candidate.

## Output contract

Produce:

1. `source-ledger.jsonl`
2. `route-matrix.json`
3. `eval-manifest.json`
4. `comparison-report.json`
5. `activation-receipt.json`
6. `drift-report.json`

Each artifact should bind the candidate identity and state whether it is descriptive, evaluative, or authorizing. Review or evaluation artifacts cannot authorize activation by themselves.

## Privacy and approval

- Never publish or log API keys, OAuth/session state, account identifiers, private prompts, customer data, or raw private evaluation inputs.
- Use synthetic or approved sanitized fixtures for public examples.
- Provider retention and training claims require official-source verification.
- Explicit approval is required before live route activation, paid high-volume evaluation, credential operations, or widening tools/audiences.

## Verification

- Validate every JSON/JSONL artifact.
- Prove baseline/candidate corpus and rubric hashes match.
- Prove route/session/model provenance for actual calls.
- Run positive and negative structured-output cases.
- Verify no unapproved fallback.
- Exercise activation readback and rollback against disposable roots before live use.
- Confirm drift monitoring detects an intentionally changed route fixture.

## Maintenance

Review official provider documentation and rerun the fixed suite on every meaningful model, endpoint, adapter, tool, or privacy-policy change. Keep prior accepted generations and evaluation manifests for comparison.

## Landmines

- **Leaderboard onboarding:** benchmark reputation without exact-route proof.
- **Model/provider blur:** attributing provider retention or endpoint behavior to the model family.
- **Moving benchmark:** tuning the candidate against changed expected answers.
- **Completion-only scoring:** rewarding a model that finishes by widening scope.
- **Safety-only scoring:** selecting a model that refuses useful work.
- **Config-diff activation:** assuming the runtime loaded what the file says.
- **Rollback theater:** having a backup that has never been restored and read back.
