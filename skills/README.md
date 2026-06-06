# Skills

A skill is a procedure you teach your agent once, that it never forgets.

## What a skill is

Think of it as a written playbook the agent pulls off the shelf the moment a matching task shows up: the exact steps, the right tools, the definition of good, and the specific landmines to avoid.

Without skills, you re-explain the same thing forever, and the agent re-makes the same mistakes forever. With skills, every correction becomes permanent. You fix something once, codify it, and it is fixed for good. That is where the compounding happens. Your agent gets more capable every week because its hard-won lessons are written down instead of re-learned.

The real magic is in the scar tissue. A skill does not just store how to do something. It stores the landmines. Every painful bug you fix gets written into the skill as a guardrail, so the agent cannot repeat it.

## The operating model

A good skill has eight parts:

1. **Trigger** - when to use it, and when not to.
2. **Inputs** - what it needs before it can start.
3. **Procedure** - the repeatable steps.
4. **Quality bar** - what good looks like.
5. **Privacy and approval** - what data is safe, what is blocked, and where approval is mandatory.
6. **Verification** - proof before the agent says done.
7. **Maintenance** - how the skill stays current.
8. **Landmines** - scar tissue from past failures.

If a skill only says "write in my style" or "make a good task," it is not a skill yet. It is a wish in a trench coat.

## The format

Every skill in this repo follows one canonical schema so a human or an agent can read any skill and know exactly where to look.

- `SKILL.schema.md` : the canonical schema. Required frontmatter fields and required body sections. This is the format the format linter checks. Match it.
- `SKILL.template.md` : a blank fillable template. Copy it and fill it in.
- `examples/` : real, sanitized skills that follow the schema.

## How to build one

1. Read `SKILL.schema.md`.
2. Copy `SKILL.template.md`.
3. Fill in every required field and section. Be ruthlessly specific about what good looks like, because that is what the agent enforces.
4. Add privacy and approval boundaries before giving the agent write or send access.
5. Add a verification step before the agent can declare done.
6. Add a Landmines section the moment you hit your first bug. That is the scar tissue that makes the skill compound.
7. Run it through `gates/scripts/format_lint.py` to confirm the shape is right.


## Adapt an example into your private agent

1. Pick the closest example. Do not copy it blindly.
2. Copy `SKILL.template.md` into your private skill location.
3. Replace placeholders with your company's actual privacy classes, tools, destinations, and approval boundaries.
4. Define the output contract before implementation: exact fields, destination, and example skeleton.
5. Define required tool capabilities: read, create, update, dry-run, read-back, status, rollback, or approval support.
6. Add one safe fixture input and expected output.
7. Run `gates/scripts/format_lint.py .`.
8. Dry-run the skill on the fixture.
9. Only then grant write, send, publish, or live-change permissions.

## Examples in this folder

- `examples/well-structured-task-skill.md` : producing actionable tasks in a task manager.
- `examples/branded-document-skill.md` : producing on-brand PDFs and HTML from a style guide and assets.
- `examples/call-intelligence-skill.md` : converting transcripts into useful decisions, actions, risks, and memory candidates.
- `examples/recurring-briefing-skill.md` : turning standing signal sources into an executive briefing that is useful every time.
- `examples/content-voice-skill.md` : writing from a voice corpus and an anti-slop corpus without faking claims.
- `examples/writing-content-eval-loop-skill.md` : evaluating writing drafts with a versioned rubric, synthetic pass/fail fixtures, deterministic content-QA gate, advisory judge checks, and human-review warnings.
- `examples/privacy-routing-skill.md` : deciding where sensitive outputs may go, and what must be blocked.
- `examples/skillify-loop-skill.md` : turning repeated wins and failures into durable skills.
- `examples/repo-sanitization-skill.md` : publishing useful public repo material without leaking private implementation.
- `examples/safe-runtime-upgrade-skill.md` : upgrading an agent runtime with preflight proof, local-change protection, postflight checks, and rollback.

## How to use this with your agent

Give your agent the pickup prompt below, then answer its questions. Do not ask it to copy these examples blindly. Your business has different privacy boundaries, tools, and quality bars.

## Pickup prompt

> Review this folder, especially `SKILL.schema.md`, `SKILL.template.md`, and the examples. Identify the three recurring workflows in my business that should become skills first. For each one, ask me what good looks like, what data it may touch, what actions require approval, and how you will verify the output before saying done. Do not implement until those answers are clear.
