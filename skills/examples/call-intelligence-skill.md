---
name: call-intelligence
description: Converts call transcripts and notes into decisions, actions, risks, relationship signal, and memory candidates.
version: 1.0
owner: <YOUR_HANDLE>
tags: [calls, meetings, actions, memory]
tools: [transcript-reader, task-manager, memory-system]
data_sensitivity: confidential
approval_required: before_write
---

# Call Intelligence

Calls are one of the highest-value sources of business signal. This skill turns transcripts and notes into useful operating material without pretending every sentence is equally important.

## When to use

Use this for sales calls, investor calls, customer calls, leadership meetings, vendor conversations, hiring loops, and in-person meeting transcripts.

Do not use it for casual conversations, recordings captured without consent where consent is required, or transcripts that include sensitive personal content unrelated to the business purpose.

## Inputs

- Required: transcript or notes, date, meeting title, known attendees, and the business context for why the call matters.
- Optional: source summary, source action items, account or relationship context, known name corrections, and prior related calls.
- If missing: label unknown attendees or uncertain claims clearly. Do not invent names, titles, or decisions.

## Procedure

1. Normalize the transcript: clean obvious transcription artifacts and apply known name/entity corrections.
2. Separate confirmed facts from likely interpretations and uncertain items.
3. Identify decisions made, open questions, commitments, objections, risks, and next actions.
4. Extract relationship signal only when it affects future action. Do not turn gossip into memory.
5. Create task drafts for real commitments using the task skill shape.
6. Create memory candidates only for durable facts: preferences, roles, commitments, recurring context, or relationship history.
7. Produce a final summary with sections for outcome, decisions, actions, risks, relationship notes, and follow-up questions.
8. Ask for approval before writing tasks or memory unless a documented pre-approval record covers the exact destination, action type, data class, scope, and expiry.

## What good looks like

A call summary that changes what the operator does next. Specifically:

- Decisions are explicit and attributed.
- Actions have owners, dates, source context, and acceptance criteria when possible.
- Risks and objections are separated from generic conversation.
- Uncertainty is labeled.
- Names and entities are corrected or marked unknown.
- Memory candidates are durable, not temporary task progress.
- The final output is concise enough to read and complete enough to act on.

## Output contract

- Primary output: final call intelligence summary plus optional task and memory candidates.
- Required sections:
  - Outcome: what changed because of the call.
  - Decisions: decision, owner, source evidence, confidence.
  - Actions: owner, due date, source, acceptance criteria.
  - Risks and objections: issue, severity, next step.
  - Relationship notes: durable signal only, with reason.
  - Follow-up questions: unresolved items.
  - Memory candidates: durable fact, reason to save, confidence.
- Required tool capabilities: transcript read, candidate/draft task creation, candidate/draft memory creation, approval before save.
- Example skeleton:

```md
Outcome: <summary>
Decisions:
- <decision> | evidence: <source> | confidence: <confirmed|likely|uncertain>
Actions:
- Owner: <role> | Due: <date or unknown> | Done when: <criteria>
Memory candidates:
- <fact> | durability reason: <reason> | confidence: <label>
```

## Privacy and approval

- Data allowed: transcript text, meeting metadata, business context, and prior relevant summaries.
- Data blocked: credentials, private personal details unrelated to the business purpose, raw transcripts in broad channels, and sensitive employee/customer content outside approved destinations.
- Redaction rule: for public examples, replace people, companies, dates, metrics, and deal details with placeholders.
- Approval required before: writing tasks, saving memory, sending a summary to attendees, or adding sensitive relationship notes to a shared system.

## Verification

- Check each action against the transcript or source notes.
- Label each insight as confirmed, likely, or uncertain.
- Re-read the final summary for unsupported claims.
- If writing tasks or memory, return links or stable identifiers and confirm the destination.

## Maintenance

- Update entity corrections when the same name or company is mis-transcribed twice.
- Add a Landmine when a summary causes wrong follow-up, missed action, or over-shared context.
- Review memory-write criteria when the memory system starts filling with stale task state.

## Landmines

- **Speaker attribution bleed**: transcripts often assign the tail of one speaker's sentence to the next speaker. Review turn boundaries before extracting intent.
- **Action inflation**: not every suggestion is a commitment. Only create tasks for real commitments or clearly requested follow-ups.
- **Memory pollution**: saving temporary call details as permanent memory creates future noise. Save durable facts only.
- **False certainty**: a polished summary can hide weak evidence. Label uncertainty directly.
- **Oversharing raw transcripts**: summaries can be routed broadly; raw transcripts usually should not be.
