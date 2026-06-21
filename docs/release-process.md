# Release and update-notification process

The Agent Foundry uses GitHub Releases as the public notification channel and `CHANGELOG.md` as the durable update history.

## Reader notification path

Readers who want update notifications should subscribe to releases:

1. Open the repository on GitHub.
2. Click **Watch**.
3. Choose **Custom**.
4. Select **Releases**.
5. Click **Apply**.

RSS/Atom feed:

```text
https://github.com/the-agent-foundry/foundry/releases.atom
```

## Maintainer release standard

Use a GitHub Release for each meaningful upload or update batch. Do not publish a release for tiny typo-only changes unless they affect a published artifact.

Recommended tag format:

```text
YYYY.MM.DD
```

Examples:

- `2026.06.20`
- `2026.06.27`
- `2026.07.04`

If multiple meaningful releases land on the same day, append a short suffix:

- `2026.06.20-2`
- `2026.06.20-security`

## Release body template

```md
## What changed
- Added ...
- Updated ...
- Removed/deprecated ...

## Who should care
- Founders using the repo as an agent-pattern catalog
- Agents reading the repo for build recommendations
- Maintainers of forks or derived private systems

## Action needed
- Pull latest `main`.
- Review `CHANGELOG.md`.
- Check `MIGRATION.md` if this release changes schemas, paths, or gate behavior.

## Breaking changes
- None, or list exact migration steps.

## Safety checks
- Sanitizer passed.
- Format lint passed.
- Secret scan passed or unavailable with reason.
```

## Before publishing

Run the publication checks in `PUBLICATION_CHECKLIST.md`. For release tags or large imports, also run the manual `release-sanitization` workflow when available.

Do not publish a release from an unmerged feature branch unless the release is intentionally a pre-release. Normal release notifications should point at `main`.
