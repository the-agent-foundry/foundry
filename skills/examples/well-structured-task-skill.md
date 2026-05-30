---
name: well-structured-task
description: Writes genuinely well-structured, actionable tasks in a task manager, with full context and acceptance criteria, every time.
version: 1.0
owner: <YOUR_HANDLE>
tags: [productivity, task-management, writing]
tools: [task-manager]
---

# Well-Structured Task

A task manager is only as useful as the tasks in it. A one-line task with no context is a future argument with yourself. This skill defines what a good task looks like and enforces it on every write, so the agent produces tasks that are actionable on their own, by anyone, weeks later.

## When to use

Use this whenever the agent creates or updates a task in the task manager: a follow-up from a meeting, a delegated action, a personal reminder with real stakes.

Do not use it for throwaway personal notes or for items that belong in a doc rather than a task list. A grocery-list item does not need acceptance criteria.

## Inputs

- Required: the core action (what needs to happen) and enough context to make it actionable.
- Optional: an owner, a due date, a project or section, links to source material.
- If missing: if the action is unclear or the context is too thin to write a useful task, ask one sharp clarifying question rather than writing a vague task.

## Procedure

1. Write a **title** that states the outcome, not the activity. "Send signed MSA to the partner" beats "MSA stuff."
2. Add a **context** block: why this exists, what triggered it, and any background needed to act without re-asking.
3. Add **acceptance criteria**: a short checklist of what done actually means. This is what turns a wish into a task.
4. Set **owner** and **due date** if known. If unknown, flag them as open rather than guessing.
5. Attach **links** to the source: the message, the doc, the call summary that spawned it. Never make the reader hunt.
6. Place it in the right **project or section** so it is findable later.
7. Keep the body tight. Structure beats volume.

## What good looks like

A task someone could pick up cold, weeks later, and execute without asking a single follow-up question. Specifically:

- The title states a clear outcome.
- The context answers "why am I looking at this" in two or three sentences.
- Acceptance criteria make "done" objective, not a matter of opinion.
- Every reference is linked, nothing requires a hunt.
- It is placed where it will actually be seen at the right time.
- No filler, no restating the title in the body, no corporate padding.

## Landmines

- **Vague titles**: a title that names a topic instead of an outcome produces a task nobody acts on. Always state the outcome.
- **Context buried or absent**: if the "why" is missing, the task gets reopened as a question. Always include it.
- **Soft acceptance criteria**: "improve the deck" is not done-able. Make criteria objective.
- **Orphaned tasks**: a task with no project, owner, or due date drifts forever. Flag missing fields rather than silently omitting them.
- **Over-structuring trivial items**: do not bolt acceptance criteria onto a two-second reminder. Match the structure to the stakes.
