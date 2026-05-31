# Agents

Specialists beat a generalist.

## Why

Pile too many skills and tools onto one agent and you get confusion. It is like asking one employee to do six different jobs and keep every detail of each straight in their head. It gets messy, and quality slips across the board.

A purpose-built sub-agent does one thing and becomes an expert at it. It loads only the skills and tools relevant to its role, so its context stays clean and focused, and you can go incredibly deep on spec'ing exactly what good looks like for that one job.

We have all used the trick: "you are an expert with ten years of experience in X." It works because it makes the model adopt a focused frame and reach for the right knowledge before answering. A purpose-built sub-agent is a leap forward on the same idea, except it does not vanish when the chat closes. It persists. The expert frame, the skills, the tools, the standards: all of it, every time.

The usual shape is one orchestrator that holds context and delegates, with specialists that execute. The orchestrator is the chief of staff. The specialists are the team.

## How to spec one

1. Read `AGENT-SPEC.schema.md`. That is the canonical role spec.
2. Decide the one job this agent owns. If you cannot say it in a sentence, the scope is too broad.
3. Fill in `AGENTS.template.md` for its operating instructions (what it does, how, its boundaries).
4. Fill in `SOUL.template.md` for its identity and voice (who it is, how it communicates).
5. Give it only the skills and tools its job needs. Resist the urge to make it general.
6. Spec what good looks like for its one job in painful detail.

## What is in this folder

- `AGENT-SPEC.schema.md` : canonical agent role-spec schema. The format archetypes and community agents must match.
- `AGENTS.template.md` : blank operating-instructions template.
- `SOUL.template.md` : blank identity and voice template.
- `archetypes/` : six proven role specs to adapt:
  - `orchestrator.md` : chief of staff, holds context and delegates.
  - `engineer.md` : the deepest archetype in this first pass. It includes classification, research, design gate, red-team, QA, manifest, and approval doctrine.
  - `call-processor.md` : turns call recordings and transcripts into business intelligence.
  - `briefer.md` : research and intel, turns raw signal into something worth reading.
  - `writer.md` : content and copy, trained on what good and what bad sound like.
  - `mechanic.md` : runtime and recovery, fixes the system when it breaks.

## Depth note

The public archetypes are sanitized, not hollow. They intentionally omit private prompts, live paths, credential handling, customer names, and internal logs, but they should preserve the operating pattern well enough for another founder's agent to adapt.

Victor, the engineer archetype, is the first expanded example. The same treatment should be staged for the other specialists, tools, and skills.

## Pickup prompt

> Review this folder and tell me whether we should build a version of it for my company. Ask me for missing context first.
