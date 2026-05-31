# The Red-Team Gate

A red-team gate is an adversarial review before the system pays the cost of building the wrong thing. It is not a vibe check. It is a structured attempt to find the flaw that will bite later.

Use this gate for MODERATE and COMPLEX work: persistent workflows, unattended automations, security or privacy surfaces, production-like tools, model/provider changes, recurring products, and anything where a bad spec creates expensive cleanup.

## The core distinction

There are two different red-team moments:

1. **Pre-build spec red-team:** pressure-test the plan before implementation. This is the high-leverage gate.
2. **Post-build QA red-team:** inspect the finished artifact, tests, and proof. This is useful, but it is not a substitute for pre-build review.

If you only red-team after building, you are using the reviewer as a demolition crew instead of an architect.

## Severity levels

Classify every finding by mission risk:

- **P0 hard block:** plausible data leak, credential exposure, destructive action, wrong live target, source-of-truth corruption, bypassed approval gate, or unrecoverable failure.
- **P1 block before activation:** likely production failure on a core path, missing required state, broken live surface, or recurring workflow that will silently go wrong.
- **P2 backlog or canary:** useful hardening, bounded edge case, coverage gap, or failure mode with workaround, rollback, or low blast radius.
- **P3 ignore or document:** theoretical concern, proof-style preference, scope expansion, or reviewer misunderstanding with no concrete path to mission failure.

P0/P1 must be resolved before build or activation. P2/P3 require a disposition, not obedience.

## Required inputs

Before red-team starts, provide:

- Problem statement and real goal.
- Classification: TRIVIAL, MODERATE, or COMPLEX.
- Design gate answers for MODERATE or COMPLEX work.
- Proposed spec and acceptance criteria.
- Constraints and non-goals.
- Approval boundaries and allowed side effects.
- Surface inventory: ingress, egress, side effects, scheduled jobs, state, external APIs, user-visible outputs.
- Research ledger when the problem involves external platforms, providers, SDKs, models, APIs, dependencies, or public error signatures.

Missing inputs are not a reason to improvise. They are a red-team finding.

## Reviewer prompt

Use this prompt with a separate model, separate agent, or separate context:

```text
You are the adversarial reviewer for this agent-system build.

Your job is to find the flaw that will matter later, not to be polite.

Review the spec below before implementation. Classify every finding as P0, P1, P2, or P3 using these definitions:
- P0: plausible leak, credential exposure, destructive action, wrong live target, source-of-truth corruption, approval-gate bypass, or unrecoverable failure.
- P1: likely production failure on a core path, missing required state, broken live surface, or recurring workflow that silently goes wrong.
- P2: bounded hardening, coverage gap, or edge case that can be canaried, backlogged, or mitigated.
- P3: theoretical critique, style preference, scope expansion, or concern with no concrete mission-failure path.

Focus on:
1. Is this solving the real domain problem or a proxy?
2. How does it fail after six months of neglect?
3. What state is missing?
4. What live surfaces are absent from QA?
5. Which safety controls are policy theater rather than real enforcement?
6. What would make this silently wrong?
7. What approval gate could be bypassed?
8. What should be mandatory before build or activation?

Return:
- Verdict: approve | approve-with-changes | block
- Findings: severity, title, evidence, consequence, required fix
- Mandatory fixes before build: list only P0/P1
- Backlog/canary items: list P2
- Ignored/not blocking: list P3 with rationale
```

## Disposition ledger

The builder must respond to every finding in a structured ledger:

```yaml
red_team_disposition:
  verdict_received: block
  findings:
    - id: RT-001
      severity: P1
      title: Missing state for recurring workflow
      disposition: incorporated
      rationale: Added high-water mark and freshness check to the spec.
    - id: RT-002
      severity: P2
      title: Add broader regression coverage
      disposition: backlogged
      rationale: Bounded edge case, acceptance path covered, add after first canary.
```

Rules:

- P0/P1 cannot be waved away by the same builder without founder/orchestrator approval.
- P2/P3 can be accepted, backlogged, canaried, or rejected with rationale.
- Do not parse free-form prose as the authority for a hard gate. Use structured fields. Prose is advisory.
- If the reviewer makes a factual claim, verify it. Reviewers hallucinate too.

## The one-loop rule

After a block, do at most one remediation loop unless the next review surfaces a new concrete P0/P1.

The goal is not to win an argument with the reviewer. The goal is to ship the right thing safely. Infinite red-team recursion is its own failure mode.

## Common failure modes this catches

- Pre-build spec review skipped and replaced with post-build criticism.
- Reviewer treats a completed build as if it were still a spec and blocks on sequencing rather than substance.
- The builder uses its own closeout report as proof.
- Red-team findings are accepted blindly without severity triage.
- P2/P3 turns into architecture sprawl.
- A prompt instruction is mistaken for a real boundary control.
- Activation happens before review, especially for unattended scheduled jobs.

## Passing the gate

The red-team gate passes when:

- Pre-build review happened when required.
- Every P0/P1 has an incorporated fix or explicit founder/orchestrator override.
- Every P2/P3 has a documented disposition.
- The final spec reflects the accepted findings.
- The build manifest links the review and disposition ledger.
