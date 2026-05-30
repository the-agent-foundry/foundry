---
name: Submit an artifact
about: Low-friction path (Tier 2). Paste a skill, agent spec, or tool spec to contribute without driving git yourself.
title: "[artifact] <short name>"
labels: ["community-submission"]
---

<!--
SCRUB BEFORE YOU PASTE. Remove all of the following:
  - credentials, API keys, tokens, private keys
  - .env contents and KEY=value secrets
  - real absolute paths (use /path/to/your/vault)
  - real chat IDs, user IDs, long numeric IDs (use <CHAT_ID>)
  - mesh / Tailscale hostnames, internal endpoints, IP addresses
  - email addresses, phone numbers, any PII
  - customer / vendor / partner specifics
A maintainer will run the sanitization gate, but you are responsible for scrubbing first.
-->

## Your handle

<!-- The namespace this lands under: community/<your-handle>/ -->
<YOUR_HANDLE>

## Artifact kind

<!-- One of: skill | agent | tool -->
skill

## Short name

<!-- e.g. weekly-board-pack -->

## The artifact

<!--
Paste your artifact below, ideally already matching the canonical schema:
  - skill: skills/SKILL.schema.md
  - agent: agents/AGENT-SPEC.schema.md
  - tool:  tools/TOOL-SPEC.schema.md
If it is not formatted yet, paste it raw and note that below. A maintainer will format it.
-->

```
<paste here>
```

## Notes for the maintainer

<!-- Anything we should know. Is it pre-formatted? Anything you were unsure how to scrub? -->

## Sign-off

- [ ] I certify this contribution is mine to share and contains no secrets, credentials, or private data.
