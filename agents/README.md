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
- `profile-operating-model.md` : how to decide what stays with the orchestrator, what becomes a specialist profile, and what graduates to an autonomous loop.
- `archetypes/` : seven field-tested role specs to adapt:
  - `archetypes/orchestrator.md` : chief of staff, routes work, verifies specialists, and synthesizes decisions.
  - `archetypes/engineer.md` : builds and QAs systems with classification, research, design gate, red-team, QA, manifest, and approval doctrine.
  - `archetypes/call-processor.md` : turns recordings and transcripts into corrected business intelligence, memory, and routed actions.
  - `archetypes/briefer.md` : monitors sources, filters signal, verifies claims, and composes decision-useful briefings.
  - `archetypes/analyst-researcher.md` : produces decision-grade research packets with source ledgers, claim ledgers, contradictions, confidence labels, and orchestrator-owned handoff routing.
  - `archetypes/writer.md` : drafts in founder voice using a voice corpus, anti-slop corpus, recursive revision, and human final approval.
  - `archetypes/mechanic.md` : monitors runtime health, diagnoses outages, and recovers through tested paths.

## Common name mapping

The field guide uses named specialists. In this repo, the generic role names are the portable pattern:

- Brit: orchestrator / chief of staff
- Victor: engineer
- Nora: call processor
- Dex: analyst researcher / briefer
- Ivy: writer
- Greg: mechanic

## Depth note

The public archetypes are sanitized, not hollow. They intentionally omit private prompts, live paths, credential handling, customer names, and internal logs, but they preserve the operating pattern well enough for another founder's agent to adapt.

The first pass expanded the engineer archetype, represented by the sanitized Victor example. Later passes bring the rest of the specialist profiles up to the same public-useful standard, including the research-packet pattern behind a decision-grade analyst.

## Pickup prompt

> Review this folder and tell me whether we should build a version of it for my company. Ask me for missing context first.
