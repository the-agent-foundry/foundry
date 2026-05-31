---
name: call-action-ledger
problem: Decisions and commitments from calls vanish or become vague follow-up noise
stack: agnostic
maturity: spec
owner: <YOUR_HANDLE>
data_sensitivity: private
action_class: draft-only
approval_required: before-write
source_of_truth: writes-with-approval
freshness_requirement: on-demand
audit_log: required
---

# Call action ledger tool

*A worked spec for turning meeting notes or transcripts into decisions, commitments, action candidates, and approval-ready follow-ups.*

## Problem

Calls contain decisions, commitments, objections, risks, and next steps. Those details often stay trapped in transcripts or sloppy notes, then decay into "circle back" mush.

A call-action-ledger tool extracts the operational record: what was decided, who committed to what, what needs approval, and what should be written to memory or a task system.

## Interface

**Input:** transcript, note file, call summary, or meeting notes. Optional context: known attendees, company/project, entity dictionary, and output audience.

**Output:** a structured ledger:

```json
{
  "summary": "concise call summary",
  "decisions": [
    {"decision": "what was decided", "evidence_ref": "timestamp, line range, or short sanitized excerpt appropriate to the output audience", "confidence": "high | medium | low"}
  ],
  "commitments": [
    {"owner": "person or role", "commitment": "specific action", "due": "date if stated", "confidence": "high | medium | low"}
  ],
  "task_candidates": [
    {"title": "task title", "owner": "suggested owner", "context": "why it exists", "approval_needed": true}
  ],
  "memory_candidates": ["durable facts worth storing"],
  "follow_up_draft": "optional draft, never sent directly",
  "uncertainties": ["ambiguous speaker, missing date, unclear owner"],
  "sources": ["source category and timestamp"]
}
```

**How the agent calls it:** after a call, after receiving a transcript, or when asked to extract actions from notes. The tool proposes writes. A task or memory tool performs writes only after policy allows it.

## What good looks like

- Separates "said," "decided," "committed," and "inferred."
- Uses timestamps, line ranges, or minimal sanitized excerpts for decisions and commitments. Raw transcript quotes are excluded by default unless needed for review inside the approved audience scope.
- Labels uncertain speaker attribution, vague owners, and implied deadlines.
- Produces task candidates that are specific enough to execute.
- Does not send follow-ups or write source-of-truth records without approval.
- Revisit trigger: duplicate tasks, hallucinated commitments, or frequent human correction of owners/deadlines.

## Failure modes

- Speaker attribution is wrong or turn-boundary bleed changes meaning.
- Brainstorming is mistaken for a decision.
- A polite suggestion is treated as a commitment.
- Sensitive comments are stored too broadly.
- Duplicate actions are created from repeated transcript imports.
- The tool silently writes to a task manager, CRM, or memory store without approval.

## Privacy notes

Call content may contain confidential, personal, legal, financial, employment, or customer-sensitive information. Raw transcripts should not be copied into public examples or broad logs. Store only the minimum durable facts needed, with provenance and audience scope.

## Approval boundaries

Extraction and drafting are allowed. Task creation, memory updates, CRM updates, external follow-up sends, and broad sharing require approval unless the workflow has been separately promoted with logging, dedupe, and rollback.

## Freshness and state

Track source identity, transcript version, import timestamp, and dedupe keys so the same call does not create duplicate tasks or memories. If transcript completeness is unknown, label the ledger partial.

## Observability

Log the source category, processing status, counts of decisions/actions/memory candidates, and any low-confidence extraction warnings. Keep raw transcript logging disabled unless explicitly approved.
