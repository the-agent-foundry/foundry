# community/

*Where everyone in the chat shares their own skills, agents, and tools, in the same format we use, in one place.*

This is the part of the repo that grows. The core (principles, gates, skills, agents, tools, the field guide) is curated and fork-freely. This directory is yours to contribute to.

## How it works

Every contributor gets a namespace: `community/<your-handle>/`. Inside it, the same three buckets as the core:

```
community/
  your-handle/
    skills/     your SKILL.md files, matching skills/SKILL.schema.md
    agents/     your agent role specs, matching agents/AGENT-SPEC.schema.md
    tools/      your tool specs, matching tools/TOOL-SPEC.schema.md
  another-handle/
    ...
```

You own your namespace. You cannot overwrite the core or anyone else's namespace, and they cannot touch yours. Attribution is automatic: your handle is right there in the path.

## The gate does the gatekeeping

Every pull request, including from forks, runs two checks automatically before anything merges:

1. **Sanitization scan** (`gates/scripts/sanitize_scan.py`) looks for credentials, keys, real paths, IDs, and PII. Any finding fails the check. Nothing sensitive lands by accident.
2. **Format lint** (`gates/scripts/format_lint.py`) confirms your artifact matches the canonical schema, so everything in the repo has a consistent, agent-readable shape.

If both checks are green, your contribution can land. This is the same principle the field guide preaches: enforcement lives in the plumbing, fail-closed, not in a polite request to be careful.

Community contributions are squash-merged, so the history stays clean and any problem is a single clean revert.

## Important: the gate is a backstop, not a guarantee

The scanner catches the common, high-signal patterns. It is not perfect. **You are responsible for sanitizing your own contribution before you submit it.** Scrub credentials, private data, real paths, and internal identifiers yourself. The gate is your safety net, not your sanitizer.

## How to contribute

See [`CONTRIBUTING.md`](../CONTRIBUTING.md) at the repo root. It is written for two readers: you, and your agent. There are two paths:

- **Tier 1 (technical):** your agent forks, adds files under your namespace, runs the gate locally, and opens a pull request.
- **Tier 2 (low-friction):** open a "Submit an artifact" issue, paste your skill or tool, and it gets formatted and landed for you.

## Pickup prompt

> Read CONTRIBUTING.md and the schemas in skills/, agents/, and tools/. I want to contribute my <skill / agent / tool> to The Agent Foundry. Reformat it to match the canonical schema, run the sanitization self-check and scrub anything sensitive, then prepare it for submission under community/<MY_HANDLE>/. Ask me for my handle and anything missing first.
