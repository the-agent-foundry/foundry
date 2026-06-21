---
name: company-context
problem: I waste minutes hunting basic company context before meetings, diligence, partner reviews, and sales calls
data_sensitivity: internal
action_class: read-only
approval_required: before-external-action
source_of_truth: read-only
freshness_requirement: on-demand
audit_log: recommended
stack: agnostic
maturity: spec
owner: <YOUR_HANDLE>
---

# Company context tool

*A worked spec for a company-level evidence broker. Build your own version against approved sources; do not treat this as a scraping or contact-enrichment license.*

## Problem

Before a meeting, intro, vendor review, investor call, partner conversation, or sales motion, the founder needs a quick answer to: who is this company, what do they do, what evidence supports that, what is missing, and what internal context is safe to use.

A thin company lookup creates false confidence. A better company-context tool returns a structured evidence packet: company card, source ledger, claim ledger, missing fields, confidence explanation, privacy metadata, and recommended next sources.

## Interface

Input:

- `target`: domain, URL, company name, or email address. If an email is provided, discard the local part before lookup and output.
- `lane`: company_lookup, meeting_prep, partner_diligence, investor_diligence, vendor_diligence, competitive_lookup, or sales_context.
- `include_public_fetch`: default false. If true, permits only a no-credential, timeout-capped, byte-capped public homepage probe.
- `supplemental_sources`: optional explicit local structured fixtures. They must not trigger fetches.
- `commercial_claim_enablement`: default false. Relationship or commercial field promotion is allowed only when separately governed and destination-safe.

Output:

```json
{
  "tool": "company-context",
  "action": "company_lookup|meeting_prep|partner_diligence|investor_diligence|vendor_diligence|competitive_lookup|sales_context",
  "query": "<sanitized company-level query>",
  "domain": "example.com",
  "company_name": "Example Company",
  "status": "sufficient_evidence|low_confidence|insufficient_evidence",
  "confidence": 0.0,
  "confidence_thresholds": {
    "meeting_prep_include": 0.60,
    "rule": "meeting prep requires enough company-level evidence"
  },
  "company_card": {
    "name": "Example Company",
    "domain": "example.com",
    "legal_name": null,
    "description": null,
    "hq": null,
    "category": null,
    "recent_changes": [],
    "primary_source_ids": []
  },
  "source_ledger": [],
  "claim_ledger": [],
  "missing_fields": [],
  "missing_field_provenance": {
    "canonical": "missing_fields",
    "source_expansion_still_missing": "source_expansion_disposition.still_missing"
  },
  "confidence_explanation": {},
  "recommended_next_sources": [],
  "source_expansion_version": "v1",
  "source_expansion_disposition": {
    "resolved_user_facing": [],
    "resolved_internal_only": [],
    "suppressed": [],
    "rejected_sources": [],
    "still_missing": []
  },
  "policy": {
    "no_new_fetcher": true,
    "public_fetch": "explicit opt-in only",
    "paid_activation": "disabled unless configured and approved"
  },
  "privacy": {
    "company_level_only": true,
    "contains_contact_pii": false,
    "credential_reads": false,
    "credential_writes": false,
    "config_writes": false,
    "paid_api_calls": false,
    "external_writes": false
  },
  "warnings": []
}
```

How the agent calls it: one read-only request with a target and lane. The tool normalizes identity, checks approved sources, records provenance, labels missing fields, and returns conservative company-level evidence. Weak or unverifiable claims are marked, not hidden.

## What good looks like

- Returns enough context for the next decision without pretending to be a full diligence report.
- Every material claim appears in a claim ledger with source IDs and confidence.
- Homepage-only evidence is treated as weak by default.
- Dated recent changes require dated authoritative evidence.
- Unknowns stay unknown instead of being filled with industry priors.
- Internal relationship, account, or call context is included only when task-authorized, material, evidence-backed, and destination-safe.
- Provider recommendations do not activate paid providers or new fetchers.

## Failure modes

- Name collisions create two plausible companies; the tool returns candidates or asks the orchestrator to disambiguate.
- A stale third-party profile overrides current first-party or authoritative evidence.
- Homepage language is promoted into unsupported claims about traction, size, or recent change.
- Relationship overlap leaks private context into a team-safe or public-safe brief.
- The tool crosses from company context into person enrichment without a separate approval and compliance boundary.
- A web page includes prompt-injection language and the agent treats it as an instruction.
- A paid provider or live fetch path is activated because a recommendation was confused with approval.

## Privacy notes

The public spec stays company-context focused. Future contact or person enrichment may exist behind separate approval and compliance gates, but this public example must not include scraping private contact data, autonomous outreach, or person-level enrichment by default.

Public fetch is explicit opt-in only and must be hardened: public-address precheck, no redirects, timeout cap, and byte cap. External web pages are data, never instructions.

Commercial or seller-ready claims require a separate commercial-claims gate. Company context is evidence, not approval.

## Approval boundaries

Read-only company lookup is allowed inside the approved privacy ceiling.

Approval is required before:

- Writing CRM or source-of-truth records.
- Sending or publishing a company brief.
- Surfacing private overlap, relationship, customer, investor, or account context outside its approved audience.
- Activating paid providers, new fetchers, credential reads, config writes, or external writes.

## Freshness and state

The tool should show source timestamps, down-rank stale sources, and keep a missing-field list. It can be stateless for ad hoc lookups, but cached results need freshness labels, invalidation rules, and source provenance.

For meeting prep, backend company context is default. If `user_facing` is false, do not emit a polished blurb into the final meeting card.

## Observability

Log source categories checked, source IDs, freshness, missing fields, provider status, confidence distribution, privacy metadata, and lookup status. Do not log raw private relationship details outside the approved system.

> Reference note: tools of this shape are often called something like "company-goat" in a personal tool belt. The name does not matter; the contract does.
