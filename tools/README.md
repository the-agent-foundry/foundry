# tools/

*The tool belt. Small, purpose-built tools that each remove one recurring annoyance.*

A capable agent is only as useful as the things it can actually do. Skills teach it how to think about a task; tools give it hands. The pattern that pays off: start a tool belt the moment your foundation is stable, and add a tool every time you catch yourself doing the same annoying thing twice.

None of these is a moonshot on its own. Collectively they are the difference between an agent that talks and one that quietly handles the friction of your week.

## What lives here

- **`TOOL-SPEC.schema.md`** is the canonical shape for describing a tool: the problem it kills, the interface it exposes, and what "good" looks like. It is a spec, not code. We publish patterns, not live integrations.
- **`examples/`** holds worked specs you can hand to your own agent and say "build me a version of this for my stack."

These are framework-agnostic on purpose. Whether you are on OpenClaw, Codex, Hermes, or something you rolled yourself, a tool spec describes the contract, not the wiring. Your agent fills in the wiring for your environment.

## A note on what is NOT here

No live credentials. No API keys. No private endpoints. No real internal URLs. A tool spec tells you what to build and how to judge it. The moment you implement it, the secrets live in your own secret store, never in a repo.

## Pickup prompt

Hand this folder to your agent:

> Review this folder and tell me whether we should build a version of it for my company. Read TOOL-SPEC.schema.md and the examples. Then ask me which recurring annoyances in my week are worth turning into a tool, and propose the two highest-value ones to build first. Ask me for missing context before you write any code.
