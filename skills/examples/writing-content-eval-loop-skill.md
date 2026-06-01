---
name: writing-content-eval-loop
description: Evaluates founder-voice drafts with a versioned rubric, synthetic pass/fail fixtures, deterministic publishability gate, advisory judge checks, and human review for warnings.
version: 1.0
owner: <YOUR_HANDLE>
tags: [writing, evaluation, qa, content, publishing]
tools: [document-reader, content-qa-gate, hash-tool]
data_sensitivity: confidential
approval_required: before_external_send
---

# Writing Content Eval Loop

A writing agent should not rely on taste prompts alone. It needs an executable loop that proves a draft cleared the non-negotiables before a human sees it as publishable.

This skill turns content QA into a repeatable gate: a versioned rubric, synthetic positive and negative fixtures, an expected-results manifest, a compatibility lock, a deterministic final check, advisory judge notes, failure intake, and health telemetry.

## When to use

Use this when a writing agent drafts or revises founder posts, essays, speeches, newsletters, field guides, or other public-facing thought leadership.

Do not use this as an autopublishing permission slip. A pass means the candidate cleared the eval loop. It does not mean the founder approved the point of view, claims, timing, or external send.

## Inputs

- Required: draft or final candidate, audience, channel, content type, source ledger or claim boundaries, and intended use.
- Required eval config: `rubric_version`, `manifest_version`, synthetic fixture manifest, expected pass/fail outcomes, and compatibility lock.
- Required gate inputs: deterministic content QA rules, blocked data classes, warning policy, approval boundary, and final-candidate hash.
- Optional: calibrated judge prompt, prior approved calibration cases, staged failure examples, and human review notes.
- If missing: fail closed on missing rubric, manifest, compatibility lock, source ledger, or approval boundary. Do not guess.

Example compatibility lock:

```yaml
schema_version: "1"
rubric_version: "YYYY-MM-DD.1"
manifest_version: "YYYY-MM-DD.1"
gate_version: "YYYY-MM-DD.1"
compatible_gate_min_version: "YYYY-MM-DD.1"
judge_status: advisory_until_calibrated
```

Example fixture manifest shape:

```yaml
fixtures:
  - case_id: positive-clear-thesis
    fixture_type: positive
    channel: linkedin
    fixture_text: "A short synthetic draft with a clear thesis, sourced claim, and no private facts."
    expected_publishable: true
  - case_id: negative-unsourced-claim
    fixture_type: negative
    channel: linkedin
    fixture_text: "A short synthetic draft that makes a concrete claim with no source."
    expected_publishable: false
```

## Procedure

1. Define the content job: channel, audience, content type, privacy level, and claims that need support.
2. Load the rubric and compatibility lock. Stop if the rubric, manifest, schema, or gate versions do not match.
3. Run the deterministic content QA gate first. Hard failures block publishability.
4. Run the synthetic positive and negative fixture corpus. Compare actual results to the manifest's expected pass/fail outcomes.
5. Evaluate the final candidate with the same gate used for the fixture corpus.
6. Treat warning-only findings as `pass_with_warnings`, not as clean approval. Require a human review note before external use.
7. Run LLM judge checks only as advisory unless calibration evidence exists and the founder has approved activating them as a gate.
8. Record telemetry for the evaluated candidate: candidate hash, rubric version, manifest version, gate version, fixture results, hard failures, warnings, advisory notes, and approval requirement.
9. Mark a final artifact as agent-owned only when matching QA telemetry names the final candidate and shows a non-degraded pass. A non-degraded pass means the required versions matched, telemetry wrote successfully, no bypass flags were used, and required human review notes exist.
10. Intake failures into a staging area. Promote only founder-approved calibration cases with a hash-bound approval record.

## What good looks like

- The draft has a real thesis, source-aware claims, and no obvious machine-writing tells.
- Synthetic positive fixtures pass and synthetic negative fixtures fail.
- The final candidate passes the deterministic gate.
- Warning-only issues are visible and tied to a human review note.
- The judge cannot overrule deterministic failures unless the gate was explicitly redesigned and versioned.
- The final is not called agent-owned without matching QA telemetry. Agent-owned means the agent can prove which candidate it evaluated, which gate version passed, and which final artifact that telemetry belongs to.
- The process is boring from a privacy perspective: no private corpus samples, raw transcripts, real paths, provider details, run IDs, or customer data appear in public artifacts.

## Output contract

- Primary output: publishability report plus the evaluated candidate or a pointer to it.
- Required fields:
  - `eval_status`: `pass`, `fail`, or `pass_with_warnings`
  - `content_type` and `channel`
  - `rubric_version`
  - `manifest_version`
  - `gate_version`
  - `compatibility_lock_status`
  - `fixture_results`
  - `deterministic_hard_failures`
  - `warnings_requiring_human_review`
  - `human_review_note_required`
  - `llm_judge_status`: `inactive`, `advisory`, or `calibrated_gate`
  - `llm_judge_advisory_findings`
  - `final_candidate_hash`: `<sha256-placeholder>`
  - `agent_owned_final`: `true` or `false`
  - `approval_required_before_external_send`: `true` or `false`
- Required tool capabilities: read approved draft inputs, run deterministic content QA, hash candidates, compare fixture results to a manifest, write safe metadata telemetry, and block external posting without approval.

Example skeleton:

```yaml
eval_status: pass_with_warnings
content_type: founder_post
channel: linkedin
rubric_version: "YYYY-MM-DD.1"
manifest_version: "YYYY-MM-DD.1"
gate_version: "YYYY-MM-DD.1"
compatibility_lock_status: pass
fixture_results:
  positive_passed: 4
  positive_failed: 0
  negative_passed: 0
  negative_failed: 4
deterministic_hard_failures: []
warnings_requiring_human_review:
  - "warning-only tone issue reviewed by founder"
human_review_note_required: true
llm_judge_status: advisory
llm_judge_advisory_findings:
  - "Opening is clear; ending may need sharper founder judgment."
final_candidate_hash: "<sha256-placeholder>"
agent_owned_final: false
approval_required_before_external_send: true
```

## Privacy and approval

- Data allowed: synthetic fixture text, sanitized examples, approved source notes, public sources, private drafts intended for this workflow, and safe metadata.
- Data blocked from public repos: private paths, private voice corpus samples, raw transcript excerpts, customer stories, personal data, provider routing, credentials, run IDs, final-content archives, raw telemetry records, and private prompts.
- Redaction rule: public fixtures should use synthetic examples or placeholders. Do not use real founder writing samples as public negative or positive cases.
- Approval required before: publishing externally, using private source material in a public draft, activating an LLM judge as a hard gate, promoting a staged failure into an approved calibration case, or marking a final artifact as agent-owned.

## Verification

- Run the deterministic gate against the final candidate and record the exit result.
- Run the synthetic fixture corpus and verify actual results match expected manifest outcomes.
- Verify the compatibility lock matches rubric, manifest, schema, and gate versions.
- Verify warning-only output cannot become externally usable without a human review note.
- Verify an LLM judge is labeled advisory unless a calibration report and approval exist.
- Verify failure intake separates staged failures from approved calibration cases.
- Verify public artifacts contain no private paths, real corpus samples, customer data, provider routing, credentials, run IDs, raw telemetry, or final-content archives.

## Maintenance

- Version the rubric whenever the quality bar, channel, content type, or warning policy changes.
- Update the manifest when synthetic fixtures are added, retired, or reclassified.
- Keep positive and negative fixtures synthetic or sanitized.
- Stage recurring failures first. Promote them into calibration only after founder approval and a matching content hash.
- Periodically run a health check: stale fixture versions, missing compatibility lock, degraded telemetry, warning bypasses, and finals without matching QA records.
- Retire judge checks that drift from human taste or produce unexplained disagreements.

## Landmines

- **Prompt-only quality control**: telling the agent to avoid bad writing is not a gate.
- **Judge theater**: an LLM judge is useful evidence, not authority, until calibrated against approved cases.
- **Warning laundering**: warnings that disappear from the final handoff become silent quality debt.
- **Corpus leakage**: real voice samples and private failures can leak sensitive facts even when they look harmless.
- **Telemetry as content**: public repos may show telemetry field names and schemas, not raw records.
- **Hash mysticism**: a hash proves integrity of a candidate, not quality or approval.
- **Agent-owned fiction**: a final is not agent-owned just because the filename says so. Require matching QA telemetry.
