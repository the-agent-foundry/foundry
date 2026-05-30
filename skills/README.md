# Skills

A skill is a procedure you teach your agent once, that it never forgets.

## What a skill is

Think of it as a written playbook the agent pulls off the shelf the moment a matching task shows up: the exact steps, the right tools, the definition of good, and the specific landmines to avoid.

Without skills, you re-explain the same thing forever, and the agent re-makes the same mistakes forever. With skills, every correction becomes permanent. You fix something once, codify it, and it is fixed for good. That is where the compounding happens. Your agent gets more capable every week because its hard-won lessons are written down instead of re-learned.

The real magic is in the scar tissue. A skill does not just store how to do something. It stores the landmines. Every painful bug you fix gets written into the skill as a guardrail, so the agent cannot repeat it.

## The format

Every skill in this repo follows one canonical schema so a human or an agent can read any skill and know exactly where to look.

- `SKILL.schema.md` : the canonical schema. Required frontmatter fields and required body sections. This is the format the format linter checks. Match it.
- `SKILL.template.md` : a blank fillable template. Copy it and fill it in.
- `examples/` : real, sanitized skills that follow the schema.

## How to build one

1. Read `SKILL.schema.md`.
2. Copy `SKILL.template.md`.
3. Fill in every required field and section. Be ruthlessly specific about what good looks like, because that is what the agent enforces.
4. Add a Landmines section the moment you hit your first bug. That is the scar tissue that makes the skill compound.
5. Run it through `gates/scripts/format_lint.py` to confirm the shape is right.

## Examples in this folder

- `examples/well-structured-task-skill.md` : producing genuinely well-structured, actionable tasks in a task manager.
- `examples/branded-document-skill.md` : producing on-brand PDFs and HTML from a style guide and assets.

## Pickup prompt

> Review this folder and tell me whether we should build a version of it for my company. Ask me for missing context first.
