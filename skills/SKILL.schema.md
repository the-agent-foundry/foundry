# SKILL Schema (Canonical)

This is the format every skill in the repo must match. The format linter (`gates/scripts/format_lint.py`) checks that the required frontmatter keys and the required section headings are present. Keep the shape, fill in real content.

A skill is framework-agnostic. It describes a procedure, not an implementation. Where you reference a concrete tool or stack, label it as an example, never as the required path.

## Required frontmatter

A YAML frontmatter block at the very top, delimited by `---`. These keys are required:

| Key | Meaning |
| --- | --- |
| `name` | Short, specific skill name. Lowercase-with-hyphens is fine. |
| `description` | One line: what this skill does and when it fires. |
| `version` | Semantic-ish version string, e.g. `1.0`. Bump it when you change behavior. |
| `owner` | Who owns this skill. Use a handle or role, never a real email. |

Optional but recommended keys: `tags` (list), `tools` (list of tool kinds it uses), `last_reviewed` (date).

## Required sections

The body must contain these headings (any heading level):

- **When to use** : the trigger. What kind of task makes the agent reach for this skill, and when it should NOT.
- **Inputs** : what the skill needs to start. Required inputs, optional inputs, and what to do if something is missing.
- **Procedure** : the actual steps, in order. Be specific enough that the agent does it the same way every time.
- **What good looks like** : the definition of done. The quality bar. This is the most important section, because it is what the agent enforces. Be concrete.
- **Landmines** : the scar tissue. Known failure modes, bugs you already hit, and the guardrail for each. Grow this section every time the skill bites you.

## Canonical shape

```
---
name: <skill-name>
description: <one line: what it does and when it fires>
version: <1.0>
owner: <handle-or-role>
tags: [<tag>, <tag>]
tools: [<tool-kind>, <tool-kind>]
---

# <Skill Name>

## When to use
<trigger conditions, and when NOT to use this>

## Inputs
<required inputs, optional inputs, behavior when something is missing>

## Procedure
1. <step>
2. <step>
3. <step>

## What good looks like
<the concrete definition of done and the quality bar the agent enforces>

## Landmines
- <known failure mode>: <the guardrail>
```

## Notes

- Keep it portable. The skill should make sense whether the founder runs OpenClaw, Codex, Hermes, or something homegrown.
- The `What good looks like` section is where the value lives. A vague quality bar produces vague output. Specify it like you are briefing a sharp but inexperienced new hire.
