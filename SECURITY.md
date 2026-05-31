# Security policy

The Agent Foundry is a public, fork-freely repo. That only works if secrets and private operating details never enter the repo in the first place.

## Supported scope

Report security issues for this repository's docs, schemas, gates, templates, workflows, and contribution process.

This repo is not intended to contain live integrations, credentials, private endpoints, production code, customer records, or private agent memory.

## Reporting a leak or vulnerability

Use GitHub's private vulnerability reporting or security advisory flow for this repository when available. If it is unavailable, do not post sensitive details publicly; contact the maintainers through the private security contact listed on the repository/profile. If no private contact is listed, open a public issue containing only "private security contact requested" and no secret, exploit, customer, path, log, screenshot, or vulnerability details.

Do not open a public issue or pull request containing:

- credentials, tokens, API keys, passwords, private keys, session cookies, or seed phrases
- customer, employee, investor, patient, vendor, or private relationship data
- raw logs, transcripts, screenshots, exports, calendars, inbox material, or private memory
- internal endpoints, mesh hostnames, workspace IDs, chat IDs, database names, or private file paths

## If a secret is exposed

Assume it is compromised. Response order:

1. **Revoke or rotate first.** Do not wait for a cleanup PR.
2. **Remove second.** Delete the public exposure and open a cleanup PR if needed.
3. **Investigate third.** Check Git history, forks, Actions logs, releases, Pages output, generated artifacts, and old clones.
4. **Document last.** Record what leaked, when it was revoked, and what gate should prevent recurrence.

History cleanup is not enough. If a live credential touched a public repo, treat it as exposed even if Git history is later rewritten.

## Maintainer expectations

Before public releases or broad sharing, maintainers should run:

```bash
python3 gates/scripts/sanitize_scan.py .
python3 gates/scripts/format_lint.py .
gitleaks detect --source . --redact
```

For release tags or large imports, run the manual `release-sanitization` GitHub Actions workflow. It runs current-tree Foundry sanitization and full-history Gitleaks provider-token scanning. Maintainers must still review history and diffs for privacy/context leaks that Gitleaks does not model.

## Tooling posture

The repo uses layered protection:

- GitHub secret scanning and push protection where available.
- Foundry-specific sanitizer for privacy/context risks provider scanners miss.
- Gitleaks for maintained provider-token patterns.
- Human publication checklist for artifacts, screenshots, PDFs, archives, Git history, and business-sensitive context.

Automated gates are backstops, not guarantees. Human judgment still owns the final public-release decision.
