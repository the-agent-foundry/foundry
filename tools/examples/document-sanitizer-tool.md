---
name: document-sanitizer
problem: Public docs and repo contributions can accidentally leak secrets or private operating details
stack: agnostic
maturity: spec
owner: <YOUR_HANDLE>
data_sensitivity: private
action_class: draft-only
approval_required: before-external-action
source_of_truth: none
freshness_requirement: on-demand
audit_log: required
---

# Document sanitizer tool

*A worked spec for checking docs, prompts, examples, and diffs before they become public or leave the trust boundary.*

## Problem

Useful public artifacts often start from private operating material. Without a sanitizer, a founder can accidentally leak credentials, private paths, customer names, raw logs, personal data, internal endpoints, or enough surrounding detail to reconstruct something sensitive.

A document-sanitizer tool fails closed, redacts risky content, and produces a reviewable report before publishing or committing.

## Interface

**Input:** explicit document, pasted text, git diff, or allowlisted file set. Folder and artifact-bundle scans require explicit scope, refuse home directories, secret stores, dependency/vendor folders, broad workspace roots, symlinks, nested archives, external URLs, and binary/media metadata unless approved. Optional audience: public repo, investor, customer, internal team, founder-only.

**Output:** sanitization report:

```json
{
  "status": "pass | blocked | needs-human-review",
  "redacted_artifact_ref": "safe output reference if produced",
  "findings": [
    {"severity": "critical | high | medium | low", "category": "secret | credential | endpoint | identifier | path | personal-data | customer-record | raw-source | private-context | implementation-detail | metadata | source-specific", "location": "safe locator", "action": "redacted | requires-review"}
  ],
  "redactions": ["summary of what changed"],
  "residual_risks": ["context that may still need human judgment"]
}
```

**How the agent calls it:** before public sharing, repo commits, external sends, or contribution acceptance. The tool can prepare a sanitized draft, but it does not publish.

## What good looks like

- Conservative by default and fails closed on possible secrets.
- Detects common leak classes without destroying the useful operating pattern.
- Scans content plus surrounding metadata: filenames, links, frontmatter, comments, diff headers, and embedded or generated artifact metadata where applicable.
- Produces a reviewable diff or report, not an opaque rewrite.
- Separates deterministic findings from human-judgment risks.
- Makes false positives easy to review without weakening the gate.
- Revisit trigger: human reviewers find leaks after a pass, or sanitizer strips so much that examples become useless.

## Failure modes

- Unusual secret formats evade detection.
- Over-sanitization removes the useful doctrine and leaves hollow docs.
- Context allows re-identification even after obvious names are removed.
- Filenames, paths, markdown links, URL query strings, frontmatter, comments, document metadata, PDF text layers, git diff context, generated artifacts, or archive members leak sensitive context after visible body text is redacted.
- The agent treats a sanitizer pass as legal, compliance, or security approval.
- Raw sensitive input is retained in logs.

## Privacy notes

This tool may process the most sensitive drafts in the system. Run it inside the trusted environment where possible. Logs should contain finding summaries and safe locators, not raw sensitive content. Public fixtures must use fake secrets and synthetic examples.

## Approval boundaries

The tool may block, redact, and draft safe replacements. Publishing, committing, sending externally, or adding allowlist exceptions requires approval. Allowlist changes are high-risk because they weaken future protection.

## Freshness and state

Sanitization rules should be versioned. Keep a safe audit record of rule version, artifact hash, finding counts, and approval decision. Do not retain raw blocked artifacts unless the storage location is approved for that sensitivity.

## Observability

Log rule version, scan scope, pass/block status, finding counts by severity, and approval outcome. Alert on critical findings in artifacts marked public-bound.
