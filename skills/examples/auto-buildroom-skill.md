---
name: auto-buildroom
description: Governs autonomous build candidates from signal to proposal, approval, bounded build, QA, trust, and retention without allowing self-approval.
version: 1.0
owner: <YOUR_HANDLE>
tags: [autonomy, governance, engineering, qa, retention]
tools: [artifact-store, scheduler, validator, code-runner, test-runner, source-reader]
data_sensitivity: confidential
approval_required: before_live_change
---

# Auto-buildroom

Auto-buildroom is the governance layer for agent-found work. It turns signals into candidate proposals, filters noise, requires human or orchestrator approval for bounded work, hands builds to an engineer, verifies independently, and records trust state.

It is not an unattended builder. The point is to make autonomy legible and bounded, not to let an agent cosplay as a product manager with a shell prompt.

## When to use

Use this when an agent repeatedly notices a possible internal improvement, repair, automation, skill, tool, or recurring-system hardening candidate and the work might be worth building.

Do not use it for one-off tasks, external outreach, customer-visible sends, credential work, source-of-truth mutations, live service changes, or broad "go improve the system" prompts.

## Inputs

- Required: source signal, proposed beneficiary, suspected problem, evidence that the signal is current, proposed scope, protected surfaces, approval boundary, and verification idea.
- Required before build: approved intent review, bounded product plan, bounded build plan, allowed paths or surfaces, protected paths or surfaces, stop conditions, QA plan, and rollback or retention decision path.
- Optional: duplicate proposal registry, prior trust reports, scheduler state, health artifacts, and Question Storm artifact.
- If missing: keep the item proposal-only, mark missing evidence, and do not create executable build authority.

## Procedure

1. **Detect signal**
   - Collect deterministic metadata: failing checks, stale artifacts, repeated user corrections, broken fixtures, unresolved TODOs, noisy recurring jobs, or repeated manual repairs.
   - Treat social proof or repeated wording as weak signal unless backed by current local evidence.

2. **Run Proposal Storm**
   - Use the Question Storm pattern in `auto_buildroom_proposal` mode.
   - Ask why now, who benefits, what scope is bounded, what protected surfaces exist, what proof is required, and whether the signal is stale or duplicate.

3. **Write an idea contract**
   - Mark `proposal_only: true`.
   - Mark `approval_state: proposed`.
   - Record source signal, missing evidence, out-of-scope items, proposed risk band, and verification ideas.
   - Never include authority verbs such as approved, scheduled, launched, or activated unless the matching approval artifact exists.

4. **Intent review**
   - Reject stale, duplicate, vague, unsafe, or low-value proposals.
   - Escalate anything involving credentials, external sends, live services, source-of-truth records, or destructive changes.

5. **Approval and planning**
   - An authorized reviewer may approve exactly one bounded candidate or an explicit batch.
   - Product plan defines beneficiary, problem, non-goals, acceptance criteria, risk band, expected artifacts, and protected surfaces.
   - Build plan defines allowed paths, protected paths, steps, verification commands, stop conditions, and rollback or recovery.

6. **Engineer handoff**
   - The engineer receives bounded work only: no vague "improve the system" scopes.
   - The handoff includes idea contract, reviews, product plan, build plan, allowed surfaces, protected surfaces, verification commands, and stop conditions.

7. **Independent QA**
   - QA reads the contract chain and changed artifacts.
   - QA reruns deterministic checks where feasible.
   - Coder self-report is evidence to inspect, not proof to trust.

8. **Trust and retention**
   - Verification delta labels evidence as confirmed, drift, regression, or missing evidence.
   - Trust report labels the job clean, watch, or investigate.
   - Retention recommends keep, improve, park, or prune. Retention is recommendation-only and performs no deletion or move.

9. **Operator summary**
   - Surface current status, trust counts, active/completed/watch/investigate jobs, and real human-needed decisions.
   - Do not pad the summary with permission requests for reversible local work the agent should finish.

## What good looks like

- Every build candidate has a contract chain from signal to closeout.
- Proposal-only artifacts cannot approve themselves.
- Bounded plans name allowed and protected surfaces before implementation.
- QA is independent from the builder's narrative.
- Trust state compresses uncertainty without hiding it.
- Retention recommendations never delete, archive, or move by themselves.
- The operator sees only real decisions, not governance confetti.

## Output contract

Primary output: contract chain for one buildroom job.

Minimum artifacts:

1. `idea-contract`
2. `intent-review`
3. `main-review` or equivalent approval review
4. `product-plan`
5. `build-plan`
6. `coder-verification`
7. `qa-verification`
8. `verification-delta`
9. `trust-report`
10. `retention-review`
11. `operator-summary`

Idea contract skeleton:

```json
{
  "schema_version": "1",
  "artifact_type": "idea-contract",
  "job_id": "br-YYYYMMDD-HHMMSS-short-slug",
  "created_by_role": "scout",
  "proposal_only": true,
  "approval_state": "proposed",
  "title": "Short bounded candidate title",
  "source_signals": [],
  "question_storm": {},
  "who_benefits": "operator or team",
  "why_now": "current evidence",
  "proposed_scope": [],
  "protected_surfaces": [],
  "verification_ideas": [],
  "out_of_scope": []
}
```

Required tool capabilities: local artifact writes, validators, file diffs, deterministic tests, scheduler/status reads when recurring jobs are involved, and read-back of created artifacts.

## Privacy and approval

- Data allowed: local metadata, synthetic examples, generalized failure modes, sanitized paths, contract fields, trust states, and verification status.
- Data blocked from public artifacts: credentials, private prompts, raw logs, private memory, chat IDs, customer data, exact runtime paths, source-of-truth records, and live scheduler internals.
- Approval required before: live gateway or service changes, credential movement, external/customer-visible sends, source-of-truth mutation, destructive action, enabled recurring activation, high-volume scraping, or widening delivery routes.
- A proposal scout may propose. It may not approve, build, activate, send, delete, or mutate protected sources.

## Verification

- Validate every artifact against its schema or required field set.
- Prove `proposal_only`, `approval_state`, and `created_by_role` cannot be mutated by Proposal Storm.
- Check duplicate/stale state before promoting a proposal.
- Run planned verification commands and record exit codes or failure evidence.
- Independently inspect the final diff or artifact before trust is marked clean.
- Confirm no live external send, credential movement, service restart, source-of-truth mutation, destructive action, or unattended activation occurred unless separately approved and recorded.

## Maintenance

Review trust reports and parked proposals weekly. Close stale proposals with an explicit rejection or park decision instead of letting them rot into zombie reminders.

Promote the autonomy level only after multiple useful clean cycles: high-signal proposals, disciplined approval, bounded build, independent QA, accurate trust state, and no gate bypass.

## Landmines

- **Repeated signal is not approval**: frequency can justify review, not execution.
- **Dreamer self-approval**: the same agent that detects a signal cannot approve its own build authority.
- **Broad build scopes**: "improve the system" is not a build plan; it is a grenade with a status bar.
- **QA by self-report**: the builder's summary is not independent proof.
- **Retention side effects**: `prune` means recommendation, not deletion.
- **Quiet autonomy creep**: a scheduled scout is not permission for scheduled building.
