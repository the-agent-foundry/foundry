# Contributing to The Agent Foundry

This guide is written for two readers: you, the founder, and your agent. Read your half. Then hand your agent its half.

The core of this repo is fork-freely. You do not need to contribute anything to get value here. But if you have built a skill, an agent spec, or a tool pattern that worked, sharing it back into the `community/` namespace helps the next founder. Contributions are accepted into a namespaced area, governed by an automated gate that fails closed.

Two rules sit above everything else:

1. **Nothing sensitive enters this repo. Ever.** No credentials, API keys, .env contents, real chat or user IDs, mesh or Tailscale hostnames, real absolute filesystem paths, customer or vendor specifics, PII, or raw logs. Use placeholders.
2. **You own your namespace.** Contributions go under `community/<your-handle>/`. The gate is a backstop, not a guarantee. You are responsible for scrubbing your own work before you submit it.

---

## For you (the human)

You have two ways to contribute, depending on whether your agent can drive `gh` or git.

### Tier 1: your agent opens the pull request

If your agent can run git and `gh` (or push to a fork), this is the clean path. You hand it the paste-in prompt below, answer a couple of questions, and it does the rest: reformats your artifact to the canonical schema, runs the sanitization self-check, and opens the PR under your handle.

### Tier 2: the low-friction path

If your agent cannot drive git, open a **Submit an artifact** issue from the issue templates. Paste your skill, agent spec, or tool spec into the template. Scrub it first (the template reminds you what to remove). A maintainer formats it and lands it under your handle. Slower, but no tooling required.

### Picking a handle

Your handle is your namespace. Pick something stable and recognizable: `community/<your-handle>/`. Lowercase, no spaces. You own everything under it.

### The sign-off

Every contribution carries a one-line Developer Certificate of Origin. By submitting, you sign:

> I certify this contribution is mine to share and contains no secrets, credentials, or private data.

That is the whole agreement. No heavyweight CLA.

### How review works

Contributors here are a trusted peer group, not the open internet. Community PRs that pass the automated gate (sanitization scan plus format lint) may auto-merge on green, or get a quick rubber-stamp from two or three maintainers. Community PRs are **squash-merged** so each contribution lands as one clean commit under your namespace.

---

## For your agent

You are helping a founder contribute an artifact to The Agent Foundry. Follow this exactly.

### 1. Read the canonical schemas first

Before reformatting anything, read the schema that matches the artifact kind. Match it precisely. The format linter checks these.

- Skills: `skills/SKILL.schema.md`
- Agents: `agents/AGENT-SPEC.schema.md`
- Tools: `tools/TOOL-SPEC.schema.md`

Also read `principles/README.md` so the artifact respects the founder's ranked principles, and `gates/README.md` so you understand the fail-closed posture.

### 2. Mandatory pre-submit sanitization self-check

This is not optional. Before you stage a single file, scrub the artifact:

- Remove all credentials, API keys, tokens, and private keys.
- Remove `.env` contents and any `KEY=value` secret assignments.
- Replace real absolute paths with placeholders: `/path/to/your/vault`, not a real home path.
- Replace real chat IDs, user IDs, and long numeric IDs with `<CHAT_ID>` or similar.
- Remove mesh and Tailscale hostnames, internal endpoints, and IP addresses.
- Remove email addresses, phone numbers, and any PII.
- Remove customer, vendor, and partner specifics. Generalize the pattern.
- Replace your real handle only where intended; use `<YOUR_HANDLE>` in shared examples.

Then run the repo's own gates against your contribution and fix anything they flag:

```
python3 gates/scripts/sanitize_scan.py community/<YOUR_HANDLE>/
python3 gates/scripts/format_lint.py .
gitleaks detect --source . --no-git --redact  # if installed
```

Both Python gates must exit 0. Gitleaks must also be clean before you submit when installed locally, and it is required in CI. If `sanitize_scan.py` or Gitleaks flags something real, scrub it and re-run. Do not add an allowlist entry to silence a real secret. Allowlist entries are only for synthetic placeholders or reviewed non-text artifacts; they must be narrow, repo-relative, path-specific where applicable, anchored when possible, and documented with a comment explaining why the entry is safe.

Never commit env files, logs, exports, screenshots with private data, PDFs with metadata, archives, database files, local agent profiles, memory dumps, or generated artifacts you have not reviewed.

### 3. The exact git flow (Tier 1)

```
# 1. Fork the repo on GitHub (or use an existing fork).
# 2. Clone your fork and create a branch.
git checkout -b contrib/<YOUR_HANDLE>-<short-name>

# 3. Add files ONLY under your namespace. Never touch the core.
#    Allowed:   community/<YOUR_HANDLE>/skills/<name>.md
#               community/<YOUR_HANDLE>/agents/<name>.md
#               community/<YOUR_HANDLE>/tools/<name>.md
#    Not allowed: edits to principles/, gates/, skills/, agents/, tools/, or
#                 any other contributor's namespace.

# 4. Run the gates locally. Both must exit 0.
python3 gates/scripts/sanitize_scan.py community/<YOUR_HANDLE>/
python3 gates/scripts/format_lint.py .
gitleaks detect --source . --no-git --redact  # if installed

# 5. Commit with the DCO line in the body, then push and open the PR.
git add community/<YOUR_HANDLE>/
git commit -m "community: add <short-name> under <YOUR_HANDLE>"
git push origin contrib/<YOUR_HANDLE>-<short-name>
# 6. Open the PR. Check the DCO box in the PR template.
```

Stay inside `community/<YOUR_HANDLE>/`. A PR that edits the core or another handle's namespace will be sent back.

### 4. Paste-in prompt the founder gives you

A founder can hand you this directly:

> You are contributing to The Agent Foundry. Read the schemas in `skills/`, `agents/`, and `tools/`, plus `principles/README.md`. Reformat my `<artifact>` to match the canonical schema for its kind. Run the mandatory sanitization self-check and scrub anything sensitive: credentials, paths, IDs, hostnames, emails, customer specifics. Then run `gates/scripts/sanitize_scan.py` and `gates/scripts/format_lint.py` and fix anything they flag. When both pass clean, open a pull request that adds the artifact under `community/<MY_HANDLE>/`, with the DCO line in the commit. Ask me for my handle and anything missing before you start.

---

## What the gate checks

Every pull request, including from forks, runs sanitization, format lint, and Gitleaks in CI with no repository secrets:

- `gates/scripts/sanitize_scan.py` : scans for credentials, private keys, secret assignments, credential-bearing connection strings, package auth residue, real home paths, mesh hostnames, emails, phone numbers, long numeric IDs, and risky artifacts. Fails closed on any finding.
- `gates/scripts/format_lint.py` : checks that your artifact carries the required frontmatter keys and section headings for its kind.
- Gitleaks : scans for maintained provider-token patterns in CI with redacted output.

If any required check exits non-zero, the PR cannot merge until you fix it.

## The disclaimer, said plainly

You own your namespace. The automated gate is a backstop, not a guarantee. It catches common, high-signal mistakes. It cannot catch everything. You are responsible for sanitizing your own contribution. If you would not post it publicly with your name on it, do not submit it here.
