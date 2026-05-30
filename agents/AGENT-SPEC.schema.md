# AGENT-SPEC Schema (Canonical)

This is the format every agent role spec must match: the archetypes in this folder and any agent contributed to the community namespace. The format linter checks the required frontmatter keys and section headings. Keep the shape, fill in real content.

A role spec is framework-agnostic. It describes a role, its boundaries, and what good looks like, not an implementation. Reference concrete stacks only as labeled examples.

## Required frontmatter

A YAML frontmatter block at the top, delimited by `---`. Required keys:

| Key | Meaning |
| --- | --- |
| `role` | The job title in one phrase, e.g. "engineer" or "call processor". |
| `mission` | One line: the single job this agent owns. |
| `reports_to` | Who it reports to, usually the orchestrator, or `founder` for the orchestrator itself. |

Optional but recommended: `skills` (list), `tools` (list), `model_preference` (free text, framework-agnostic note on reasoning needs).

## Required sections

The body must contain these headings:

- **Mission** : the one job, expanded. What this agent is for and, just as important, what it is not for.
- **Scope** : what is in bounds and what is out of bounds. The edges of the role.
- **Skills and tools** : the specific skills and tool kinds this role loads. Keep it lean. A specialist loads only what its job needs.
- **What good looks like** : the concrete quality bar for this role's output. The definition of done.
- **Approval boundaries** : what the agent may do autonomously and what requires human approval. Ties to the approval gate.

## Canonical shape

```
---
role: <role>
mission: <one line: the single job this agent owns>
reports_to: <orchestrator | founder>
skills: [<skill>, <skill>]
tools: [<tool-kind>, <tool-kind>]
---

# <Agent Name or Role>

## Mission
<the one job, expanded, including what this agent is NOT for>

## Scope
<in bounds, out of bounds>

## Skills and tools
<the lean set this role loads>

## What good looks like
<the concrete quality bar for this role>

## Approval boundaries
<what it may do alone, what needs a human>
```

## Notes

- One job per agent. If the mission needs the word "and" more than once, split it.
- Lean context. The whole point of a specialist is a clean, focused context. Do not pile on skills it does not need.
- Pair this with `SOUL.template.md` for identity and voice, and `AGENTS.template.md` for full operating instructions.
