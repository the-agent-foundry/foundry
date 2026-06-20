---
name: question-storm
description: Generates mode-specific pre-build or pre-research inquiry artifacts before retrieval, spec, synthesis, or proposal promotion.
version: 1.0
owner: <YOUR_HANDLE>
tags: [planning, research, engineering, governance, qa]
tools: [artifact-writer, local-validator, source-reader, test-runner]
data_sensitivity: internal
approval_required: before_write
---

# Question Storm

Question Storm is the thinking gate before the work starts. It turns an ambiguous request into the questions that should change retrieval, design, tests, acceptance criteria, approval boundaries, or the final decision.

The artifact is inquiry, not evidence. It helps the agent decide what to inspect next; it must not become an unsupported claim ledger.

## When to use

Use this before non-trivial research, company intelligence, commercial synthesis, meeting prep, engineering builds, autonomous-loop proposals, or any task where the wrong first question would send the agent down the wrong trail.

Do not use it for trivial lookups, already-specified edits, or ceremonial "what else should we consider" padding that will not change action.

## Inputs

- Required: task summary, intended mode, task class, known constraints, approval boundary, and expected final artifact.
- Optional: privacy ceiling, affected surfaces, suspected protected surfaces, missing fields, prior related artifacts, source-quality requirements, and acceptance criteria.
- If missing: use a compact artifact for moderate ambiguity, a full artifact for complex or protected-surface work, and `skip` only when the task is genuinely trivial.

Recommended modes:

| Mode | Use case | Core question |
|---|---|---|
| `dex` | research, company intelligence, meeting prep, strategy memo | What should we know before advising the founder? |
| `victor_build` | complex build/spec formation | What must be true before we build? |
| `auto_buildroom_proposal` | build candidate or scout result | Is this a bounded build candidate, or repeated noise? |

## Procedure

1. Classify the work as `TRIVIAL`, `MODERATE`, or `COMPLEX`.
2. Pick the mode: `dex`, `victor_build`, `auto_buildroom_proposal`, or a conservative fallback.
3. Resolve depth:
   - `TRIVIAL` -> `skip` unless protected surfaces are present.
   - `MODERATE` -> `compact`.
   - `COMPLEX` or protected-surface work -> `full`.
4. Generate a machine-readable Question Storm artifact with personas, question clusters, assumptions, probe plan, missing evidence, accepted proxies, deferred questions, and revisit triggers.
5. Use the questions to drive retrieval, inspection, test design, source-ledger requirements, or proposal review.
6. Keep answers and evidence in the downstream artifact, not inside the Question Storm artifact.
7. Preserve the artifact or a rendered section when a later reviewer needs to inspect why the work started where it did.

## What good looks like

A useful Question Storm changes the next move. Specifically:

- It produces concrete questions tied to retrieval, probe planning, design, tests, acceptance criteria, decision, risk, source ledgers, claim ledgers, or approval boundaries.
- It filters empty, vague, duplicate, and ceremonial questions.
- It names protected-surface risk early: credentials, tokens, live gateways, cron activation, source-of-truth mutation, external sends, or privacy boundaries.
- It keeps private context out of public artifacts.
- It makes missing evidence visible without pretending the missing evidence is solved.

## Output contract

Primary output: `question_storm` artifact.

Required fields:

```json
{
  "schema_version": "1",
  "artifact_type": "question_storm",
  "task_class": "dex_company_intel | victor_complex_build | auto_buildroom_proposal | other",
  "mode": "dex | victor_build | auto_buildroom_proposal | other",
  "classification": "TRIVIAL | MODERATE | COMPLEX",
  "depth": "skip | compact | full",
  "personas_used": [],
  "questions": [],
  "clusters": [],
  "assumptions": [],
  "retrieval_or_probe_plan": [],
  "missing_evidence": [],
  "accepted_proxies": [],
  "questions_intentionally_deferred": [],
  "revisit_triggers": [],
  "mode_outputs": {}
}
```

Each question must include:

```json
{
  "id": "qs-victor-build-001",
  "persona": "qa_lead",
  "question": "Which live path proves this change works beyond the helper function?",
  "why_it_matters": "Prevents surface-incomplete QA.",
  "affects": ["tests", "acceptance_criteria"],
  "priority": "high",
  "status": "open"
}
```

Required tool capabilities: write local artifacts, inspect relevant source files, run validators or tests, and link the artifact into the downstream packet, spec, or proposal.

## Privacy and approval

- Data allowed: generalized task descriptions, public-safe source categories, synthetic fixtures, mode labels, and approval-boundary metadata.
- Data blocked from public artifacts: private prompts, credentials, raw logs, chat IDs, customer data, private memory, exact local runtime paths, and source-of-truth records.
- Approval required before: using the artifact to trigger live changes, external sends, credential work, source-of-truth writes, or autonomous activation.
- Question Storm cannot approve work. It can only identify what must be checked before approval or build.

## Verification

- Validate the artifact has the required fields and non-empty high-priority questions when depth is `compact` or `full`.
- Confirm every question has a non-empty `affects` list from an allowed set.
- Confirm the downstream artifact preserves source-ledger and claim-ledger boundaries.
- For build handoffs, verify the rendered pre-build inquiry appears before the spec and acceptance criteria.
- For proposal workflows, verify proposal-only fields remain unchanged.

## Maintenance

Update the mode tables when a repeated miss appears: missing protected surface, weak source planning, bad acceptance criteria, or recurring overbuild. Add fixture tests for every mechanical failure.

Retire questions that become ceremonial. A stale question is prompt plaque. Scrape it off.

## Landmines

- **Question-as-evidence laundering**: a generated question is not a source. Keep source and claim ledgers separate.
- **Ceremonial storming**: ten impressive questions that change nothing are worse than one useful blocker.
- **Approval drift**: inquiry can make a proposal sharper, but it cannot approve build, send, publish, or activate.
- **Mode sprawl**: add modes only when the output contract differs. Otherwise use a persona cluster inside an existing mode.
- **Private-context bleed**: public examples should show the artifact shape, not the founder's live paths or internal records.
