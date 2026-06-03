---
name: research-packet
description: Creates decision-grade research packets with source ledgers, claim ledgers, contradictions, confidence labels, and orchestrator-owned handoff.
version: 1.0
owner: <YOUR_HANDLE>
tags: [research, analyst, evidence, briefing, handoff]
tools: [web-search, document-reader, source-ledger, packet-validator, sanitizer]
data_sensitivity: confidential
approval_required: before_external_send
---

# Research Packet

A research packet is the audit trail for serious agent research. It keeps the question, sources, claims, contradictions, recommendation, and routing metadata together so the founder can trust the answer without rereading the entire internet.

## When to use

Use this for substantive business, technical, market, competitive, vendor, partner, process-hardening, platform-bug, or community best-practice research.

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

If missing:

- If the question is ambiguous but low risk, proceed with explicit assumptions.
- If privacy ceiling, approval boundary, or external-send intent is unclear, stop and ask the orchestrator.
- If the required research-packet skill or validator is unavailable, emit a blocked status before research begins.

## Procedure

1. **Create the packet**
   - Create a unique packet directory or workspace.
   - Seed required files: `README.md`, `source-ledger.jsonl`, `claim-ledger.jsonl`, `contradictions.md`, `brief.md`, `recommendation.md`, `handoff.json`, `packet_manifest.json`, and `errors.jsonl`.
   - Use atomic writes or a staging directory so a partial packet is never reported as complete.

2. **Write the source plan**
   - Restate the decision, not just the topic.
   - List source classes in priority order.
   - Define what would count as enough evidence and what would force a weak or contested label.

3. **Collect sources**
   - Prefer Tier A: official docs, official repos, releases, standards, filings, vendor notes, regulator material, and direct reproducible test output.
   - Use Tier B: respected practitioners, maintained project docs, and reputable trade or analyst reporting with concrete details.
   - Use Tier C: forums, issue comments, newsletters, and community threads as partial evidence.
   - Treat Tier D: vague social posts, engagement bait, listicles, uncited claims, and AI slop as discovery only.

4. **Build the source ledger**
   - Record one source per line with stable ID, tier, type, locator, author or maintainer when relevant, retrieved date, summary, and use in the answer.
   - Note source incentives, freshness, and limitations when material.

5. **Build the claim ledger**
   - Record each material claim with source IDs, confidence, claim type, assumptions, and contradiction status.
   - Remove unsupported claims or mark them insufficient.

6. **Handle contradictions**
   - Preserve credible disagreements in `contradictions.md`.
   - State what would resolve them: official confirmation, maintainer response, reproducible test, additional data, or time.

7. **Synthesize**
   - Write `brief.md` with answer, context, evidence summary, confidence, and open questions.
   - Write `recommendation.md` with recommended action, alternatives, risks, assumptions, and what would change the recommendation.

8. **Handoff**
   - Write `handoff.json` with route owner, route, triage flag, task type, confidence, artifacts, sources used, errors, and approval needs.
   - Ambiguous or sensitive next steps route back to the orchestrator with `needs_triage: true`.

9. **Validate**
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

Source ledger row skeleton:

```json
{"source_id":"S1","tier":"A","source_type":"official_docs","title":"<title>","locator":"https://example.org/source","retrieved":"<YYYY-MM-DD>","summary":"<why this source matters>","limitations":"<known limits>"}
```

Claim ledger row skeleton:

```json
{"claim_id":"C1","claim":"<material claim>","claim_type":"fact|interpretation|recommendation|unknown","source_ids":["S1"],"confidence":"verified|likely|weak|contested|insufficient","assumptions":[],"contradiction_ids":[]}
```

Handoff skeleton:

```json
{
  "route_owner": "orchestrator",
  "route_version": "research-routing-v1",
  "route": "orchestrator",
  "needs_triage": false,
  "task_type": "market|competitive|technical|vendor|partner|process|strategic|ad_hoc",
  "confidence": "verified|likely|weak|contested|insufficient",
  "artifacts": [],
  "sources_used": [],
  "errors": [],
  "approval_needed": []
}
```

## Privacy and approval

Allowed data depends on the task privacy ceiling. Default to founder-only/private workspace until told otherwise.

Blocked from public artifacts:

- Credentials, private keys, private file paths, hostnames, chat or user IDs, raw logs, private prompts, private memory, customer/vendor specifics, source-of-truth records, internal telemetry, and personal data.

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
- **Missing skill fallback**: if the research-packet skill or validator is missing, stop before research and route to the orchestrator.
- **Half-written packet**: never report a packet complete if required files failed to write.
- **Private context leak**: do not copy private runtime docs into a public repo and hope regexes save you. Generate public-safe material from templates.
- **Routing self-ownership**: the analyst recommends; the orchestrator routes and approves.
