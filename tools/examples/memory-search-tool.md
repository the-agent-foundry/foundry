---
name: memory-search
problem: I know we discussed this before but cannot retrieve the right prior context quickly
stack: agnostic
maturity: spec
owner: <YOUR_HANDLE>
data_sensitivity: private
action_class: read-only
approval_required: before-write
source_of_truth: read-only
freshness_requirement: on-demand
audit_log: required
---

# Memory search tool

*A worked spec for retrieving long-term operating memory with citations, freshness, and confidence instead of vibes.*

## Problem

Founders accumulate decisions, notes, people context, meeting summaries, and lessons learned faster than they can retrieve them. The agent may remember that something exists, but without a retrieval tool it guesses or asks the founder to repeat himself.

A memory-search tool lets the agent query approved memory stores and return source-backed context before answering or acting.

## Interface

**Input:** natural-language query plus optional scope: person, company, project, decision type, date range, memory class, or audience.

**Output:** ranked retrieval results:

```json
{
  "answer": "short answer if the evidence supports one",
  "matches": [
    {
      "title": "memory label",
      "date": "source date",
      "summary": "why this match matters",
      "source_ref": "safe citation or internal reference",
      "confidence": "high | medium | low",
      "freshness": "current | possibly stale | stale"
    }
  ],
  "related_entities": ["people, companies, projects, or decisions"],
  "not_found": false,
  "warnings": ["identity collision, stale result, low source confidence"]
}
```

**How the agent calls it:** before answering context-heavy questions, preparing meetings, drafting follow-ups, or making recommendations that depend on prior decisions. The tool is read-only.

## What good looks like

- Cites memory sources rather than claiming memory as magic.
- Prioritizes precision over recall for high-stakes questions.
- Shows dates and freshness so old context does not override newer facts.
- Returns "not found" when evidence is weak.
- Supports scoped queries so private founder-only memories do not leak into team-safe work.
- Revisit trigger: frequent false positives, stale answers, or identity collisions.

## Failure modes

- Semantic search returns plausible but irrelevant notes.
- Old memories override newer decisions.
- Similar names create identity collisions.
- The agent treats an impression as a verified fact.
- Search logs become a secondary leak of sensitive queries.

## Privacy notes

Memory is often the most sensitive part of an agent system. Access should be scoped by memory class and audience. Public examples must use synthetic records only and should never include real names, relationship notes, transcripts, contact data, or private decisions.

## Approval boundaries

Read-only retrieval is allowed inside approved contexts. Creating, replacing, deleting, exporting, or sharing memory records requires explicit approval or a separately promoted workflow with review gates.

## Freshness and state

The tool should preserve source dates, last-updated timestamps, and supersession relationships where available. If the memory store supports soft deletes or archived notes, those states must be visible.

## Observability

Log query metadata, scopes used, result count, and confidence distribution. Avoid logging raw private query text unless the runtime is approved for sensitive audit logs.
