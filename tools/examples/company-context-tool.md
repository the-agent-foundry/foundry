---
name: company-context
problem: I waste minutes hunting basic facts about a company before every meeting or intro
stack: agnostic
maturity: spec
owner: <YOUR_HANDLE>
---

# Company context tool

*A worked spec. One way to give your agent instant company and diligence context before a call, an intro, or a deal. Build your own version against your preferred data sources.*

## Problem

Before a first meeting, a partner intro, or a quick diligence pass, you keep doing the same manual lookup: what does this company do, how big are they, who runs it, are they funded, do they overlap with anyone you already work with. It takes a few minutes every time, it breaks your flow, and you often skip it and walk in cold. Multiply by a busy calendar and it is a real tax on your week.

A company-context tool kills that lookup. You give it a domain or a name; it hands back a tight, structured brief in seconds, in the context of your business.

## Interface

**Input:** a company identifier. One of: a domain (`example.com`), a company name, or an email address (the tool derives the domain from the local-part's domain).

**Output:** a structured brief with confidence-tagged fields. A reasonable shape:

```
{
  "company": "name",
  "domain": "example.com",
  "summary": "one or two lines on what they do",
  "size_signal": "headcount band or revenue band, with confidence",
  "leadership": ["names and roles, if reliably known"],
  "funding_signal": "stage / last round, with confidence",
  "overlap": "any known relationship to my existing partners or portfolio",
  "sources": ["where each claim came from"],
  "confidence": "high | medium | low, per field"
}
```

**How the agent calls it:** one function call with the identifier. The tool fans out to whatever sources you trust, dedupes, tags each claim with provenance and confidence, and returns the brief. Weak or unverifiable claims are marked, not dropped silently.

## What good looks like

- Returns in seconds, not a multi-minute research crawl. If it cannot answer fast, it returns what it has and flags the gaps rather than hanging.
- Every claim carries provenance and a confidence level. No confident-sounding guesses presented as fact.
- It fails loud. If a source is down or returns nothing, the brief says so. It never fabricates a plausible-looking answer.
- It knows your context: an overlap with an existing partner is surfaced, not buried.
- Revisit trigger: when a data source changes its shape or starts returning stale results, the confidence tags should drift, which is your signal to re-tune.

## Failure modes

- A source goes dark or rate-limits. The tool degrades to the sources that still answer and marks the missing fields, rather than returning nothing or inventing values.
- Name collisions (two companies, same name). The tool returns the candidates and asks the agent to disambiguate rather than guessing.

## Privacy notes

Company-level lookups only. This is not a tool for enriching individual people or scraping private contact data. Keep it to public, company-scoped signal. Whatever sources you wire in, their credentials live in your secret store, never in the spec.

> Reference note: tools of this shape are often called something like "company-goat" in a personal tool belt. The name does not matter; the contract does.
