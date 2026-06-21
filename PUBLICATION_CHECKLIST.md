# Publication checklist

Use this before broad sharing, release tags, community imports, or turning private operating material into public examples.

## 1. Source and history

- [ ] The public repo was built from a clean public-safe tree, not a casual private-to-public visibility flip.
- [ ] Current tree scan is clean: `python3 gates/scripts/sanitize_scan.py .`.
- [ ] Format lint is clean: `python3 gates/scripts/format_lint.py .`.
- [ ] Gitleaks current-tree scan is clean: `gitleaks detect --source . --no-git --redact`.
- [ ] Full-history provider-token scan is clean before major release: run the manual `release-sanitization` workflow or `gitleaks detect --source . --redact` locally. Separately review history and diffs for privacy/context leaks such as paths, emails, customer names, screenshots, transcripts, and IDs.
- [ ] If any real credential ever touched GitHub, it was revoked/rotated before cleanup was treated as complete.

## 2. GitHub protections

- [ ] GitHub secret scanning is enabled.
- [ ] GitHub push protection is enabled where available.
- [ ] Required branch checks include sanitization, format lint, and Gitleaks.
- [ ] Security alerts are monitored by maintainers.
- [ ] Public issues/PRs are not used to report live secrets.

## 3. Files and generated artifacts

- [ ] No file or directory names contain customer names, emails, phone numbers, handles, chat IDs, workspace IDs, private project names, or other sensitive identifiers.
- [ ] No `.env` files, local profiles, credentials, keys, certs, shell history, notebooks, local databases, or raw exports are present.
- [ ] No logs, transcripts, inbox exports, calendar dumps, task exports, call recordings, or memory dumps are present.
- [ ] No archives are present unless explicitly reviewed and allowlisted.
- [ ] No PDFs, screenshots, images, audio, video, office docs, or binary artifacts are present unless metadata and visible content were reviewed.
- [ ] Lockfiles and package configs do not contain private registry URLs, auth residue, internal paths, or local machine names.
- [ ] Generated HTML/docs do not contain hidden comments, source maps, copied private text, or local paths.

## 4. Content and context

- [ ] No real customer, vendor, partner, investor, employee, patient, or private relationship details appear.
- [ ] No internal architecture, private endpoint names, workspace IDs, chat IDs, CRM IDs, calendar IDs, database names, vector-store names, trace IDs, or profile paths appear.
- [ ] Examples use placeholders or synthetic data.
- [ ] Sanitization did not strip the artifact hollow. The transferable operating pattern still remains.
- [ ] Public-safe, team-safe, and founder-only context are not mixed.

## 5. Review

- [ ] A human reviewed the diff, not just scanner output.
- [ ] Any allowlist entry is narrow, repo-relative, path-specific where applicable, commented, and justified.
- [ ] CI logs do not expose raw matched values.
- [ ] If history was rewritten, maintainers recloned before further work.

## 6. Release and notification

- [ ] `CHANGELOG.md` includes the meaningful update batch.
- [ ] `MIGRATION.md` says either "no migration required" or gives concrete steps for breaking changes.
- [ ] The GitHub Release body includes what changed, who should care, action needed, breaking changes, and safety checks.
- [ ] The release tag uses the date-based format `YYYY.MM.DD` unless this is a deliberate pre-release or hotfix suffix.
- [ ] The release targets `main` after merge; feature-branch releases are marked pre-release.
- [ ] README subscription instructions still point readers to GitHub Releases and the releases Atom feed.
