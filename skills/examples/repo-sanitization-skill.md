---
name: repo-sanitization
description: Publishes useful public repo material while removing private implementation details and proving the gate is clean.
version: 1.0
owner: <YOUR_HANDLE>
tags: [security, public-repo, sanitization, publishing]
tools: [git, sanitizer, secret-scanner, linter]
data_sensitivity: restricted
approval_required: before_live_change
---

# Repo Sanitization

Public companion repos should be useful enough for another founder's agent to learn from, but boring from an attacker's perspective. This skill preserves transferable operating patterns while removing private implementation details.

## When to use

Use this before publishing agent docs, skills, tool specs, prompts, gates, templates, examples, HTML pages, or community contributions to a public repo.

Do not use it to launder private material into public form when the underlying artifact is not safe to share. Some things should stay private.

## Inputs

- Required: source artifact, intended public audience, allowed detail level, blocked data classes, and repo gate commands.
- Optional: existing sanitizer, secret scanner, publication checklist, review rubric, and example placeholders.
- If missing: stop and define the blocked categories before editing. Sanitization without a boundary is vibes wearing a lab coat.

## Procedure

1. Classify the artifact: principle, gate, skill, tool, agent spec, example, code, or rendered asset.
2. Remove credentials, private IDs, private paths, hostnames, raw logs, private memory, customer specifics, personal data, and internal implementation details from body text, filenames, frontmatter, markdown links, URL query strings, diff context, generated metadata, embedded assets, PDF text layers, and archive members.
3. Preserve the operating doctrine: triggers, quality bars, state, approval boundaries, failure modes, QA protocols, schemas, and examples.
4. Replace private specifics with placeholders that teach the pattern.
5. Run deterministic sanitizer and format/schema lint.
6. Run a maintained secret scanner such as Gitleaks when available.
7. Run content review for hype, slop, unsupported claims, and public credibility.
8. Use a pull request so checks and review are visible before merge.
9. Verify the public link renders correctly if publishing HTML.

## What good looks like

The repo is sanitized but not hollow. Specifically:

- No credentials, private paths, IDs, raw logs, or private data remain.
- The examples are generic but operationally useful.
- The scanner output is redacted and clean.
- The format linter passes.
- The public artifact explains what to build, why it matters, how it fails, and how to verify it.
- A capable founder's agent can adapt the pattern without seeing your private system.

## Output contract

- Primary output: public-release sanitization record.
- Required fields:
  - Files reviewed: changed files and artifact types.
  - Sensitive classes checked: credentials, paths, IDs, logs, prompts, memory, customer data, metadata.
  - Commands run: sanitizer, format lint, secret scanner, content checks, and history scan when applicable.
  - Findings: clean, fixed, or blocked.
  - Manual review notes: context leaks scanners cannot catch.
  - Public rendering check: URL and content type when applicable.
  - Approval status: owner, scope, and timestamp.
- Required tool capabilities: git diff inspection, sanitizer, secret scanner, format lint, rendered-artifact review, and CI status check.
- Example skeleton:

```md
Files reviewed: <list>
Commands run: <list>
Findings: <clean|fixed|blocked>
Manual review: <summary>
Public rendering: <url/status or n/a>
Approval: <owner/scope/date>
```

## Privacy and approval

- Data allowed: public-safe doctrine, synthetic examples, placeholders, schemas, and generalized failure modes.
- Data blocked: credentials, private keys, raw logs, private prompts, exact routing config, chat IDs, customer/vendor specifics, private memory, and source-of-truth data.
- Redaction rule: replace private values with placeholders and remove surrounding context if the context itself reveals too much.
- Approval required before: pushing to a public repo, enabling Pages, publishing rendered artifacts, or accepting external contributions that touch core docs.

## Verification

- Run the repo sanitizer and format linter.
- Run Gitleaks or equivalent with redacted output.
- Run a full-history scan before major public releases or after moving sensitive material.
- Review changed files manually for private context that scanners cannot see. Include filenames, frontmatter, links, rendered assets, generated files, artifact metadata, embedded assets, PDF text layers, and archive members.
- Verify GitHub CI and public rendering after merge.

## Maintenance

- Update scanner patterns when a near-miss appears.
- Add fixture tests for every sanitizer bug.
- Review publication checklist before broad sharing.
- Keep public examples useful as the private system evolves, but never mirror private implementation blindly.

## Landmines

- **Sanitization as shallowing**: deleting all detail makes the repo safe but useless. Preserve process, gates, and examples.
- **Scanner theater**: regexes help, but human review still catches context leaks.
- **Secret in logs**: a scanner that prints the matched secret creates a new leak. Redact output.
- **Broad allowlists**: a wide allowlist turns the gate into decoration. Allowlist narrowly and document why.
- **Rendered artifact drift**: HTML or PDF outputs can differ from markdown source. Review rendered files too.
