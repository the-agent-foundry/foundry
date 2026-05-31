# Gates

A gate is a check the system must pass before it proceeds. Some gates are hard. Some are reasoning. Knowing which is which is one of the highest-leverage skills in building an agent.

## Hard gate vs reasoning

Your agent will tell you it fixed something, then do the same thing wrong nine more times. The instinct is to write a rule for every failure. Do that everywhere and the magic drains out: the agent gets compliant, lifeless, and mediocre. You over-constrained it.

The discipline is knowing where each belongs.

- **A hard gate** is for things that must be true every single time, where a wrong answer is unacceptable: a privacy check, a sanitization scan, a QA pass, an approval before something leaves the building. Hard gates live in the plumbing and fail closed. They do not ask the model nicely. They block.
- **A reasoning gate** is for everything where judgment beats rigid rules: the six-question design gate, red-team severity triage, what to backlog, how to rebuild a report from scratch, or when a conscious proxy is acceptable.

Tight specs on the bookends, light touch on the middle. Hard gates on the things that must never go wrong. Reasoning on everything else.

## A principle this repo dogfoods

> Enforcement lives in the plumbing, fail-closed.

Do not rely on the model choosing not to do the wrong thing. Put the control at the actual boundary where the action happens. This repository practices it: `gates/scripts/sanitize_scan.py` is a hard gate that blocks common high-signal sensitive patterns in pull requests, and it runs in CI with no way for the model to talk its way past it.

## What is in this folder

- `scripts/sanitize_scan.py` : the working sanitization gate that guards this repo. Scans for credentials, keys, real paths, IDs, and PII-like patterns. Fails closed on high-signal findings. This is a hard gate.
- `scripts/format_lint.py` : checks contributed artifacts against the canonical schemas.
- `content-qa-gate.py` : a mechanical anti-slop checker for prose. Run any draft through it before it ships. This is the real script, shipped as-is.
- `six-question-design-gate.md` : six questions to answer before building any non-trivial system. A reasoning gate with teeth.
- `research-gate.md` : when to research external issues before building, and the source ledger the agent must return.
- `red-team-gate.md` : the pre-build and post-build adversarial review protocol, including P0/P1/P2/P3 severity and disposition rules.
- `qa-gate.md` : the proof standard for declaring work done, including surface inventory and evidence requirements.
- `build-manifest.schema.md` : the audit-record schema for meaningful builds.
- `security-egress-gate.md` : the security and egress control pattern for a tool-using agent.
- `approval-gate.md` : the human-approval-before-external-action pattern.

## How the engineering gates fit together

For serious builds, use this sequence:

1. Six-question design gate: are we solving the real problem?
2. Research gate: if external systems are involved, who else hit this and how did they fix it?
3. Red-team gate: kill bad specs before implementation.
4. Build in a safe workspace.
5. QA gate: prove the artifact works across live surfaces.
6. Build manifest: record what changed and what evidence proves it.
7. Approval gate: only then merge, activate, publish, or perform any gated action.

## Using the scripts

```
# Sanitization gate: exits non-zero on any finding.
python3 gates/scripts/sanitize_scan.py .

# Format linter: exits non-zero on any schema violation.
python3 gates/scripts/format_lint.py .

# Anti-slop content gate: run a draft through it.
python3 gates/content-qa-gate.py path/to/draft.md
```

## Pickup prompt

> Review this folder and tell me whether we should build a version of it for my company. Ask me for missing context first. For any non-trivial build workflow, pay special attention to the design gate, red-team gate, QA gate, and build manifest.
