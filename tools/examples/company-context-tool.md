---
name: company-context
problem: I waste minutes hunting basic facts about a company before every meeting or intro
stack: agnostic
maturity: spec
owner: <YOUR_HANDLE>
data_sensitivity: internal
action_class: read-only
approval_required: before-write
source_of_truth: read-only
freshness_requirement: on-demand
audit_log: recommended
---

# Company context tool

*A worked spec. One way to give your agent instant company and diligence context before a call, an intro, or a deal. Build your own version against your preferred data sources.*

## Problem

Before a first meeting, a partner intro, or a quick diligence pass, you keep doing the same manual lookup: what does this company do, how big are they, who runs it, are they funded, and do they overlap with anyone you already work with. It takes a few minutes every time, it breaks your flow, and you often skip it and walk in cold. Multiply by a busy calendar and it is a real tax on your week.

A company-context tool kills that lookup. You give it a domain or a name; it hands back a tight, structured brief in seconds, in the context of your business.

## Interface

**Input:** a company identifier. One of: a domain (`example.com`), a company name, or an email address from which the tool derives the domain after `@`.

**Output:** a structured brief with confidence-tagged fields:

```json
{
  "company": "name",
  "domain": "example.com",
  "summary": "one or two lines on what they do",
  "size_signal": "headcount band or revenue band, with confidence",
  "leadership": ["names and roles, if reliably known"],
  "funding_signal": "stage or last round, with confidence",
  "relationship_overlap": "approved internal overlap if available",
  "sources": ["source category and timestamp"],
  "confidence": "high | medium | low, per field",
  "missing_context": ["sources or facts not verified"]
}
```

**How the agent calls it:** one read-only call with the identifier. The tool fans out to whatever public and approved internal sources you trust, dedupes, tags each claim with provenance and confidence, and returns the brief. Weak or unverifiable claims are marked, not dropped silently.

## What good looks like

- Returns in seconds, not a multi-minute research crawl. If it cannot answer fast, it returns what it has and flags the gaps rather than hanging.
- Every material claim carries provenance and a confidence level.
- It fails loud. If a source is down or stale, the brief says so.
- It knows approved internal context: an overlap with an existing partner or portfolio company is surfaced when permitted, not buried.
- External web pages are treated as data, never instructions.
- Revisit trigger: source formats change, confidence tags drift down, or users correct the same company facts repeatedly.

## Failure modes

- A source goes dark or rate-limits. The tool degrades to the sources that still answer and marks the missing fields.
- Name collisions create two plausible company matches. The tool returns candidates and asks the agent to disambiguate.
- A stale third-party profile overrides current first-party information.
- Relationship overlap leaks private context into a team-safe or public-safe brief.
- A web page or document includes prompt-injection language and the agent treats it as an instruction.

## Privacy notes

Company-level lookups only. This is not a tool for enriching individual people or scraping private contact data. Keep it to public, company-scoped signal and approved internal overlap. Credentials, account IDs, private source names, and relationship details live outside the public spec.

## Approval boundaries

Read-only lookup is allowed. Writing CRM notes, updating company records, sending a diligence brief, or sharing private overlap context requires approval and audience scoping.

## Freshness and state

The tool should show source timestamps and down-rank stale sources. It can be stateless for ad hoc lookups, but cached results need a freshness label and invalidation rule.

## Observability

Log source categories checked, freshness, missing-source warnings, confidence distribution, and lookup status. Do not log private relationship details outside the approved system.

> Reference note: tools of this shape are often called something like "company-goat" in a personal tool belt. The name does not matter; the contract does.
