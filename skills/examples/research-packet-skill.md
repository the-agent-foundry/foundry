---
name: research-packet
description: Creates decision-grade research packets with source ledgers, claim ledgers, contradictions, confidence labels, human-facing companions, and orchestrator-owned handoff.
version: 1.1
owner: <YOUR_HANDLE>
tags: [research, analyst, evidence, briefing, handoff]
tools: [web-search, document-reader, source-ledger, packet-validator, sanitizer]
data_sensitivity: confidential
approval_required: before_external_send
---

# Research Packet

A research packet is the audit trail for serious agent research. It keeps the question, sources, claims, contradictions, recommendation, human-facing companion, and routing metadata together so the founder can trust the answer without rereading the entire internet.

## When to use

Use this for substantive business, technical, market, competitive, vendor, partner, process-hardening, platform-bug, company-context, meeting-prep, or community best-practice research.

Do not use it for trivial lookups, pure drafting, meeting transcript cleanup, or anything where the answer is already provided and no external or historical evidence is needed.

## Inputs

Required:

- Research question and decision needed.
- Audience and privacy ceiling: founder-only, team-safe, public-safe, or external-ready.
- Source boundaries: allowed sources, blocked sources, freshness requirement, and whether social/community discourse is in scope.
- Output format and deadline.
- Orchestrator handoff route.

Optional:

- Known context, prior assumptions, watchlists, vendors, competitors, issue links, candidate sources, and local tests to run.
- Existing evidence packets, such as company or account context packets.
- Task-authorized internal context fixtures with source IDs and destination-safety metadata.
- Requested human-deliverable format: html, markdown, pdf, or text.

If missing:

- If the question is ambiguous but low risk, proceed with explicit assumptions.
- If privacy ceiling, approval boundary, or external-send intent is unclear, stop and ask the orchestrator.
- If the required research-packet skill or validator is unavailable, emit a blocked status before research begins.

## Procedure

1. **Create the packet**
   - Preflight the packet root for creatability, writability, free space or quota, and collision-resistant directory creation.
   - Create a unique packet directory or workspace.
   - Seed required files: `README.md`, `source-ledger.jsonl`, `claim-ledger.jsonl`, `contradictions.md`, `brief.md`, `recommendation.md`, `handoff.json`, `packet_manifest.json`, and `errors.jsonl`.
   - Use atomic writes or a staging directory so a partial packet is never reported as complete.
   - Emergency fallback packets may preserve failure metadata, but they are non-durable and must not be reported as complete.

2. **Write the source plan**
   - Restate the decision, not just the topic.
   - List source classes in priority order.
   - Define what would count as enough evidence and what would force a weak or contested label.

3. **Collect sources**
   - Prefer Tier A: official docs, official repos, releases, standards, filings, vendor notes, regulator material, authoritative records, and direct reproducible test output.
   - Use Tier B: respected practitioners, maintained project docs, and reputable trade or analyst reporting with concrete details.
   - Use Tier C: forums, issue comments, newsletters, and community threads as partial evidence.
   - Treat Tier D: vague social posts, engagement bait, listicles, uncited claims, and AI slop as discovery only.
   - Homepage or marketing-site-only evidence is weak by default; dated recent changes require dated authoritative evidence.

4. **Build the source ledger**
   - Record one source per line with stable ID, tier, type, locator, author or maintainer when relevant, retrieved date, summary, limitations, destination safety, and use in the answer.
   - Note source incentives, freshness, and limitations when material.

5. **Build the claim ledger**
   - Record each material claim with source IDs, confidence, claim type, assumptions, contradiction status, and destination.
   - Remove unsupported claims or mark them insufficient.
   - Unknown fields stay unknown; do not fill gaps from industry priors or polished homepage language.

6. **Handle contradictions**
   - Preserve credible disagreements in `contradictions.md`.
   - State what would resolve them: official confirmation, maintainer response, reproducible test, additional data, or time.

7. **Synthesize**
   - Write `brief.md` with answer, context, evidence summary, confidence, and open questions.
   - Write `recommendation.md` with recommended action, alternatives, risks, assumptions, and what would change the recommendation.

8. **Create the human-facing companion when needed**
   - For founder or chat-facing research, render a browser-openable `brief.html` or equivalent companion artifact.
   - Record `human_deliverable_format` and `html_path` or equivalent path in `handoff.json`.
   - If rendering fails, record the failure in `errors.jsonl` and do not claim the human deliverable is complete.

9. **Handoff**
   - Write `handoff.json` with route owner, route, triage flag, task type, confidence, human-deliverable metadata, artifacts, sources used, errors, and approval needs.
   - Ambiguous or sensitive next steps route back to the orchestrator with `needs_triage: true`.

10. **Validate**
   - Validate required files exist.
   - Validate JSON and JSONL parse.
   - Validate every material claim references at least one source or is marked insufficient.
   - Validate confidence labels follow the source rubric.
   - Run sanitizer before any public or team-safe artifact leaves the private workspace.

## What good looks like

- The packet can be audited without rerunning the research.
- The first paragraph answers the question.
- The source ledger shows what was checked and why it matters.
- The claim ledger prevents unsupported assertions from slipping into polished prose.
- Contradictions are visible, not buried.
- Confidence is conservative.
- The recommendation is practical and names what would change it.
- The human-facing companion is separate from the machine audit surface.
- The orchestrator owns routing and approval decisions.

## Output contract

Primary output: a research packet directory or attached archive.

Required files:

- `README.md`: question, answer, confidence, packet status, and artifact map.
- `source-ledger.jsonl`: one JSON object per source.
- `claim-ledger.jsonl`: one JSON object per material claim.
- `contradictions.md`: conflicts, uncertainty, and resolution criteria.
- `brief.md`: final analyst brief.
- `recommendation.md`: recommended action, risks, alternatives, assumptions, and change triggers.
- `handoff.json`: orchestrator-owned routing metadata.
- `packet_manifest.json`: file list, status, validator version, and checksums if available.
- `errors.jsonl`: research, source, write, validation, or tool errors.

Conditional files:

- `brief.html`: required when the packet is intended for founder or chat-facing delivery unless explicitly requested as text-only or markdown-only.

Source ledger row skeleton:

```json
{"source_id":"S1","tier":"A|B|C|D","source_type":"official_docs|official_record|public_web|practitioner_writeup|internal_context_fixture|community_thread|direct_test|other","title":"<title>","locator":"<url, document ref, or fixture ref>","retrieved":"<YYYY-MM-DD or RFC3339>","summary":"<why this source matters>","limitations":"<known limits>","destination_safety":"audit_only|internal_only|team_safe|public_safe"}
```

Claim ledger row skeleton:

```json
{"claim_id":"C1","claim":"<material claim>","claim_type":"fact|interpretation|recommendation|hypothesis|unknown","source_ids":["S1"],"confidence":"verified|likely|weak|contested|insufficient","assumptions":[],"contradiction_ids":[],"destination":"audit_only|human_brief_allowed|public_safe"}
```

Handoff skeleton:

```json
{
  "route_owner": "orchestrator",
  "route_version": "research-routing-v1",
  "last_reviewed": "<YYYY-MM-DD>",
  "review_cadence": "quarterly_or_on_role_change",
  "route": "orchestrator",
  "needs_triage": false,
  "task_type": "business_market_competitive|technical_bug_community|best_practice_hardening|tool_vendor_evaluation|strategic_brief|meeting_prep|partner_analysis|ad_hoc",
  "confidence": "verified|likely|weak|contested|insufficient",
  "human_deliverable_format": "html|markdown|pdf|text",
  "html_path": "<path or null>",
  "artifacts": [],
  "sources_used": [],
  "errors": [],
  "approval_needed": []
}
```

Manifest skeleton:

```json
{
  "version": "research_packet_v1",
  "created_at": "<RFC3339 timestamp>",
  "slug": "<packet slug>",
  "task_type": "<task type>",
  "durable": true,
  "status": "created|complete|failed|fixture_clean",
  "packet_dir": "<packet directory or relative fixture path>",
  "files": [],
  "checksums": {},
  "errors": []
}
```

## Privacy and approval

Allowed data depends on the task privacy ceiling. Default to founder-only/private workspace until told otherwise.

Blocked from public artifacts:

- Credentials, private keys, private file paths, hostnames, chat or user IDs, raw logs, private prompts, private memory, customer/vendor specifics, source-of-truth records, internal telemetry, and personal data.

Public artifacts must be generated from public-safe templates, not copied from private runtime docs and regex-sanitized afterward. Before public publication or PR:

- Remove private paths, chat IDs, credentials, customer or account names, raw logs, raw transcripts, memory, source-of-truth records, and internal routing details.
- Run the local sanitizer and available secret scanners.
- Include scanner provenance without raw secret findings.

Approval required before:

- Publishing, pushing, or opening a public PR.
- Sending externally.
- Using restricted/private context in a team-safe or public artifact.
- Contacting sources or subjects.
- Making source-of-truth writes, automation changes, live system changes, or credential changes.

## Verification

Before claiming done:

- Required packet files exist.
- JSON and JSONL files parse.
- Every material claim has source IDs or is marked insufficient.
- Confidence labels obey the source-tier rubric.
- Contradictions are recorded or explicitly absent.
- Handoff route owner is the orchestrator.
- Human-facing companion exists when required and is recorded in handoff metadata.
- Public or team-safe artifacts pass sanitizer and secret scanning when available.
- Any failed source lookup, test, or write is recorded in `errors.jsonl` rather than quietly omitted.

## Maintenance

- Add validator tests for every packet failure that escapes review.
- Tighten source tiers when weak sources get over-promoted.
- Update the handoff schema when routing or approval boundaries change.
- Keep examples synthetic and public-safe.
- Review recurring packets for source drift and stale watchlists.

## Landmines

- **Pretty brief, weak ledger**: prose can hide garbage evidence. The ledger is the truth source.
- **Social proof inflation**: many people repeating the same unsourced claim is still weak evidence.
- **Homepage confidence inflation**: a polished homepage can identify a company; it usually cannot prove recent changes, traction, or diligence-grade facts.
- **Missing skill fallback**: if the research-packet skill or validator is missing, stop before research and route to the orchestrator.
- **Half-written packet**: never report a packet complete if required files failed to write.
- **Private context leak**: do not copy private runtime docs into a public repo and hope regexes save you. Generate public-safe material from templates.
- **Routing self-ownership**: the analyst recommends; the orchestrator routes and approves.
