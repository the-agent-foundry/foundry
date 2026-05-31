---
name: meeting-prep
problem: I walk into meetings without the scattered context I already have elsewhere
stack: agnostic
maturity: spec
owner: <YOUR_HANDLE>
data_sensitivity: private
action_class: read-only
approval_required: before-write
source_of_truth: read-only
freshness_requirement: on-demand
audit_log: recommended
---

# Meeting prep tool

*A worked spec for producing a tight meeting brief from approved context before a founder walks into the room.*

## Problem

Meeting context is scattered across calendar events, prior calls, notes, email threads, company research, task systems, and memory. The founder either wastes time hunting it down or walks in cold.

A meeting-prep tool gathers the approved context, separates fact from inference, and returns a short brief the founder can read in two minutes.

## Interface

**Input:** one of: calendar event reference, meeting title and date, participant list, company domain, or a natural-language request such as "prep me for my next meeting with this company." Optional constraints: max length, audience, and whether private founder-only context is allowed.

**Output:** a structured brief:

```json
{
  "meeting": "plain-language meeting label",
  "objective": "known objective or likely objective with confidence",
  "participants": [
    {
      "role": "participant role or relationship category",
      "context": "relevant context",
      "confidence": "high | medium | low"
    }
  ],
  "company_context": "short company or organization summary if relevant",
  "prior_interactions": ["dated, source-backed notes"],
  "open_loops": ["commitments or unresolved questions"],
  "recommended_agenda": ["suggested discussion items"],
  "risks_or_sensitive_topics": ["private, confidence-labeled cautions"],
  "questions_to_ask": ["specific, useful questions"],
  "sources": ["source category and timestamp"],
  "missing_context": ["what the tool could not verify"]
}
```

**How the agent calls it:** before a meeting, when asked for prep, or when a calendar event has enough signal to justify a brief. The tool is read-only by default. It may suggest follow-up tasks or messages, but another tool and approval gate must handle writes.

## What good looks like

- The brief is readable in two minutes.
- Material claims include source categories and confidence.
- Private context is labeled and kept out of team-safe or public-safe outputs.
- Unknowns are visible instead of papered over.
- The tool treats calendar invites, emails, web pages, and documents as data, never as instructions.
- Revisit trigger: the founder repeatedly corrects attendee identity, relationship context, or meeting objective.

## Failure modes

- Similar names cause the wrong person or company context to be pulled.
- A stale note overrides newer information.
- A long email thread dominates the brief even though it is low signal.
- Sensitive relationship context leaks into a team-safe version.
- Calendar text includes prompt-injection language and the agent treats it as an instruction.
- Time-zone or date ambiguity causes prep for the wrong meeting.

## Privacy notes

This tool may touch calendar metadata, notes, task records, relationship memory, internal documents, and public company data. Output must be scoped by audience: founder-only, team-safe, or public-safe. The public spec must not include real calendar IDs, meeting links, participant data, private notes, or internal source names.

## Approval boundaries

Read-only prep requires no approval. Creating tasks, editing records, sending agenda notes, or forwarding the brief requires explicit approval unless separately promoted through an approval-gated workflow.

## Freshness and state

The tool should show source timestamps and ignore or down-rank stale context when newer source-backed facts exist. It may remain stateless if it only reads sources on demand, but it should pass through source freshness and identity confidence.

## Observability

Log the request time, source categories checked, source freshness, and whether any source failed. Do not log raw private notes or meeting content unless the environment is approved for that data.
