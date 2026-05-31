---
name: task-manager-write
problem: Follow-ups die because tasks are captured inconsistently or never land in the system of record
stack: agnostic
maturity: spec
owner: <YOUR_HANDLE>
data_sensitivity: internal
action_class: internal-write
approval_required: before-write
source_of_truth: writes-with-approval
freshness_requirement: on-demand
audit_log: required
---

# Task manager write tool

*A worked spec for giving an agent narrow, approval-safe write access to a task system without letting it spray vague tasks everywhere.*

## Problem

Meetings, calls, and messages produce follow-ups. If the agent can only talk, those follow-ups stay in chat. If it can write recklessly, it creates duplicates, assigns the wrong owner, or pollutes the task system with vague junk.

A task-manager-write tool turns approved action candidates into clean, deduped tasks with provenance.

## Interface

**Input:** proposed task object:

```json
{
  "title": "specific task title",
  "owner": "person or role",
  "due_date": "date or null",
  "priority": "low | normal | high | urgent",
  "project_or_list": "destination category",
  "context": "why this task exists",
  "source": "call, note, message, or manual request category",
  "confirmation_mode": "require-human-approval | auto-only-for-preapproved-policy-id"
}
```

**Output:** write result:

```json
{
  "status": "created | updated | duplicate_found | blocked | failed",
  "task_ref": "safe reference or link if allowed",
  "normalized_fields": {},
  "duplicate_candidates": [],
  "approval_required": true,
  "warnings": []
}
```

**How the agent calls it:** after a human asks for a task or after another tool proposes action candidates. The write tool must check approval policy, approval artifact or preapproved policy ID, destination allowlist, owner, duplicate state, required fields, and rollback/update strategy before writing. The model may not decide that policy allows a write; the write layer must verify it.

## What good looks like

- Tasks are specific, owned, and actionable.
- Repeated calls do not create duplicates.
- The task includes source context without dumping sensitive raw content.
- Ambiguous owner, destination, or deadline blocks the write or asks for approval.
- Permission failures are loud.
- Revisit trigger: duplicate tasks, wrong destinations, or human cleanup after agent-created tasks.

## Failure modes

- Duplicate tasks from repeated call ingestion.
- Wrong owner or project assignment.
- Sensitive meeting content appears in a broadly visible task title.
- The agent writes based on an unconfirmed inference.
- API failure is hidden and the founder believes the task exists.

## Privacy notes

Task systems are often visible to teams. Keep sensitive context out of titles and broadly visible descriptions. Store only enough provenance to explain the task. Credentials and workspace identifiers belong in a secret store, not a public spec.

## Approval boundaries

Default to approval before write. Auto-create is acceptable only under a named, preapproved policy with allowlisted destination/project/owner, sensitivity checks for title and description, idempotency/dedupe keys, rollback/delete path, audit logging, and monitoring. Block customer-visible, external, ambiguous, or sensitive-content tasks unless a human approves.

## Freshness and state

Use dedupe keys from source identifier, normalized title, owner, and date. Track write status, retry state, and destination mapping. If the destination mapping is stale, block rather than guessing.

## Observability

Log proposed write, approval state, duplicate check result, final status, and safe task reference. Do not log raw sensitive source content.
