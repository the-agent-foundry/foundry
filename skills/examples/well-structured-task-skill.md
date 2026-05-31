---
name: well-structured-task
description: Writes actionable task-manager items with context, acceptance criteria, ownership, and source links.
version: 1.1
owner: <YOUR_HANDLE>
tags: [productivity, task-management, writing]
tools: [task-manager]
data_sensitivity: internal
approval_required: before_write
---

# Well-Structured Task

A task manager is only as useful as the tasks in it. A one-line task with no context is a future argument with yourself. This skill defines what a good task looks like and enforces it on every write, so the agent produces tasks that are actionable on their own, by anyone, weeks later.

## When to use

Use this whenever the agent creates or updates a task in the task manager: a follow-up from a meeting, a delegated action, a personal reminder with real stakes, or an operating-system improvement that needs an owner.

Do not use it for throwaway personal notes or for items that belong in a document rather than a task list. A two-second reminder does not need a board-meeting brief stapled to it.

## Inputs

- Required: the core action, why it matters, source context, and the intended owner if known.
- Optional: due date, project or section, priority, source links, acceptance criteria from the requester.
- If missing: ask one sharp clarifying question if the action cannot be made useful. If only owner or date is missing, write the task with an explicit open field rather than guessing.

## Procedure

1. Identify the outcome, not the activity.
2. Write a title that states the outcome: `Send signed agreement to partner` beats `agreement stuff`.
3. Add a context block: why this exists, what triggered it, and any background needed to act without re-asking.
4. Add acceptance criteria: a short checklist of what done actually means.
5. Set owner, due date, project, and section when known. Mark unknown fields clearly.
6. Attach or reference the source material: message, doc, call summary, decision note, or ticket.
7. Before writing to the task manager, show the proposed task if approval is required by your operating rules.
8. After writing, return the task title, destination, and link or identifier.

## What good looks like

A task someone could pick up cold, weeks later, and execute without asking a single follow-up question. Specifically:

- The title states a clear outcome.
- The context answers why the task exists in two or three sentences.
- Acceptance criteria make done objective.
- Every reference is linked or named.
- It is placed where it will actually be seen at the right time.
- Missing owner, date, or context is visible, not silently omitted.
- No filler, no restating the title in the body, no corporate padding.

## Output contract

- Primary output: task-manager draft or written task.
- Required fields:
  - Title: outcome-oriented.
  - Context: why this exists and what triggered it.
  - Acceptance criteria: objective checklist.
  - Owner: named role or `unknown`.
  - Due date: date or `unknown`.
  - Source: link, document name, call summary, or message reference.
  - Destination: project, section, or inbox.
  - Open fields: missing items the owner must resolve.
- Required tool capabilities: draft preview, create/update, destination selection, and read-back or stable task identifier.
- Example skeleton:

```md
Title: <outcome>
Context: <why this exists>
Acceptance criteria:
- <done condition>
Owner: <role or unknown>
Due date: <date or unknown>
Source: <safe source reference>
Destination: <project/section>
Open fields: <none or list>
```

## Privacy and approval

- Data allowed: meeting summaries, source messages, internal project notes, and task metadata.
- Data blocked: credentials, raw private transcripts, sensitive personal details not needed for the task, and customer-specific material that does not belong in the task manager.
- Redaction rule: summarize sensitive context instead of pasting raw source text.
- Approval required before: creating or updating tasks in a shared workspace, assigning work to another person, or adding customer-visible language.

## Verification

- Confirm the task was created or updated in the intended project or section.
- Return a link or stable task identifier when the tool provides one.
- Re-read the final task body if the tool supports it.
- If the write fails, report the failure and provide the draft task text for manual copy-paste.

## Maintenance

- Update this skill when reviewers complain tasks are too vague, too bloated, misplaced, missing source links, or missing acceptance criteria.
- Add a Landmine every time a task causes rework because it lacked context.
- Re-review quarterly or whenever the task manager workflow changes.

## Landmines

- **Vague titles**: a title that names a topic instead of an outcome produces a task nobody acts on. Always state the outcome.
- **Context buried or absent**: if the why is missing, the task gets reopened as a question. Always include it.
- **Soft acceptance criteria**: `improve the deck` is not done-able. Make criteria objective.
- **Orphaned tasks**: a task with no project, owner, or due date drifts forever. Flag missing fields rather than silently omitting them.
- **Over-structuring trivial items**: do not bolt a six-part structure onto a two-second reminder. Match the structure to the stakes.
