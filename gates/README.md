# Gates

A gate is a check the system must pass before it proceeds. Some gates are hard. Some are reasoning. Knowing which is which is one of the highest-leverage skills in building an agent.

## Hard gate vs reasoning

Your agent will tell you it fixed something, then do the same thing wrong nine more times. The instinct is to write a rule for every failure. Do that everywhere and the magic drains out: the agent gets compliant, lifeless, and mediocre. You over-constrained it.

The discipline is knowing where each belongs.

- **A hard gate** is for things that must be true every single time, where a wrong answer is unacceptable: a privacy check, a sanitization scan, a QA pass, an approval before something leaves the building. Hard gates live in the plumbing and fail closed. They do not ask the model nicely. They block.
- **Reasoning** is for everything where judgment beats rigid rules: how to phrase a brief, how to prioritize a list, how to rebuild a report from scratch given what it knows you are trying to accomplish.

Tight specs on the bookends, light touch on the middle. Hard gates on the things that must never go wrong. Reasoning on everything else.

## A principle this repo dogfoods

> Enforcement lives in the plumbing, fail-closed.

Do not rely on the model choosing not to do the wrong thing. Put the control at the actual boundary where the action happens. This repository practices it: `scripts/sanitize_scan.py` is a hard gate that blocks any pull request carrying secrets, and it runs in CI with no way for the model to talk its way past it.

## What is in this folder

- `scripts/sanitize_scan.py` : the working sanitization gate that guards this repo. Scans for credentials, keys, real paths, IDs, and PII. Fails closed. This is a hard gate.
- `scripts/format_lint.py` : checks contributed artifacts against the canonical schemas.
- `content-qa-gate.py` : a mechanical anti-slop checker for prose. Run any draft through it before it ships. This is the real script, shipped as-is.
- `six-question-design-gate.md` : six questions to answer before building any non-trivial system. A reasoning gate with teeth.
- `security-egress-gate.md` : the security and egress control pattern for a tool-using agent.
- `approval-gate.md` : the human-approval-before-external-action pattern.

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

> Review this folder and tell me whether we should build a version of it for my company. Ask me for missing context first.
