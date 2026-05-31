---
name: relationship-directory
problem: Relationship context gets stale, duplicated, or buried exactly when I need it
stack: agnostic
maturity: spec
owner: <YOUR_HANDLE>
data_sensitivity: private
action_class: read-only
approval_required: before-write
source_of_truth: writes-with-approval
freshness_requirement: weekly
audit_log: required
---

# Relationship directory tool

*A worked spec for finding and maintaining relationship context without turning private notes into a reckless CRM dump.*

## Problem

A founder's relationship graph is a living asset. Roles change, introductions happen, promises get made, preferences matter, and stale notes quietly rot. The pain shows up before calls, fundraising, hiring, sales, partnerships, and follow-ups.

A relationship-directory tool retrieves relationship context, resolves identities carefully, surfaces open loops, and proposes hygiene updates without auto-merging or oversharing sensitive notes.

## Interface

**Input:** person name, company name, domain, participant list, relationship query, or request such as "what do we know before this intro?" Optional audience: founder-only, team-safe, or public-safe.

**Output:** relationship context packet:

```json
{
  "canonical_record": "safe person or organization label",
  "identity_confidence": "high | medium | low",
  "known_roles": ["role or affiliation with date/confidence"],
  "last_interaction": "date and source category",
  "relationship_summary": "audience-scoped summary",
  "open_loops": ["commitments, intros, follow-ups"],
  "duplicate_candidates": ["possible duplicate records"],
  "suggested_updates": ["updates requiring approval"],
  "sensitive_notes_excluded": true,
  "sources": ["source category and timestamp"]
}
```

**How the agent calls it:** before meetings, introductions, outreach, follow-ups, or directory hygiene. Retrieval is read-only. Merge, update, or share actions require approval.

## What good looks like

- Identity resolution is cautious and confidence-labeled.
- The packet helps the founder act better, not just see contact trivia.
- Private relationship notes stay founder-only unless explicitly downgraded.
- Stale roles and affiliations are labeled with dates.
- Duplicate and conflicting records are surfaced instead of silently merged.
- Revisit trigger: wrong identity matches, stale roles, or private notes appearing in team-safe outputs.

## Failure modes

- Two people with similar names are merged.
- Former titles are treated as current.
- Private notes leak into a team-safe brief or external draft.
- The tool enriches individuals from questionable sources.
- The directory becomes a generic CRM mirror instead of an operating map.

## Privacy notes

Relationship notes are highly sensitive and often personal. Access should be scoped by user, audience, and context. Public examples must use fictional people, organizations, and interactions only. Avoid enrichment that collects private contact data without a clear lawful and ethical basis.

## Approval boundaries

Read-only lookup is allowed inside approved scopes. Updating canonical records, merging duplicates, exporting records, adding private notes, or sharing relationship context requires approval and an audit trail.

## Freshness and state

Track source dates, last verification, duplicate-candidate status, merge decisions, and stale-record flags. A weekly hygiene job can propose updates, but should not mutate records without a promotion gate.

## Observability

Log lookup category, identity confidence, source freshness, duplicate warnings, and any proposed writes. Do not log raw private relationship notes outside the approved store.
