# tools/

*The tool belt. Small, purpose-built tools that each remove one recurring annoyance.*

A capable agent is only as useful as the things it can actually do. Skills teach it how to think about a task; tools give it hands. The pattern that pays off: start a tool belt the moment your foundation is stable, and add a tool every time you catch yourself doing the same annoying thing twice.

None of these is a moonshot on its own. Collectively they are the difference between an agent that talks and one that quietly handles the friction of your week.

## What lives here

- **`TOOL-SPEC.schema.md`** is the canonical shape for describing a tool: the problem it kills, the interface it exposes, the approval boundary, and what "good" looks like. It is a spec, not code. We publish patterns, not live integrations.
- **`TOOL.template.md`** is the copyable blank spec.
- **`examples/`** holds worked specs you can hand to your own agent and say "build me a version of this for my stack."

These are framework-agnostic on purpose. Whether you are on OpenClaw, Codex, Hermes, or something you rolled yourself, a tool spec describes the contract, not the wiring. Your agent fills in the wiring for your environment.

## Recommended first tool belt

Build tools in the order that makes your agent more useful without making it reckless.

1. **Know before the meeting** : `company-context` and `meeting-prep`.
2. **Capture after the meeting** : `call-action-ledger`.
3. **Remember the relationship** : `relationship-directory` and `memory-search`.
4. **See what changed** : `recurring-briefing`.
5. **Act safely** : `task-manager-write` before anything external.
6. **Publish safely** : `document-sanitizer` before public docs, repo contributions, or shared prompts.
7. **Handle recurring friction** : travel, procurement, reporting, data cleanup, and other repeat annoyances.

## Build-order rule

Start with the least dangerous version that still creates value.

1. **Read-only:** retrieve, summarize, classify, cite.
2. **Draft-only:** prepare a message, task, update, or approval packet.
3. **Internal-write:** mutate an internal system only with dedupe, logging, and rollback.
4. **External-write:** send, publish, buy, message, or change a customer-visible system only behind an approval gate.

If the tool touches money, credentials, legal/compliance material, customer-visible systems, source-of-truth records, or external communication, prompt discipline is not enough. Use the hard gates in `../gates/`.

## Tool handoff contract

A good tool spec should let another agent answer these before writing code:

- What recurring annoyance does this kill?
- What is the input contract?
- What is the output contract?
- What is the source of truth?
- What can the tool do without approval?
- What must be drafted only?
- What must never happen without explicit approval?
- How does the tool fail loudly?
- What proof shows it worked?
- What private data must stay out of logs, prompts, and shared output?

## Related gates

- `../gates/security-egress-gate.md` : sensitive data and send/write boundaries.
- `../gates/approval-gate.md` : human approval before risky side effects.
- `../gates/qa-gate.md` : proof artifacts and completion standards.
- `../gates/research-gate.md` : check upstream patterns before building custom integrations.
- `../gates/build-manifest.schema.md` : document the build, tests, approvals, and residual risks.

## A note on what is NOT here

No live credentials. No API keys. No private endpoints. No real internal URLs. No private calendar IDs, CRM IDs, chat IDs, or workspace names. A tool spec tells you what to build and how to judge it. The moment you implement it, the secrets live in your own secret store, never in a repo.

## Pickup prompt

Hand this folder to your agent:

> Review this folder and tell me whether we should build a version of this tool belt for my company. Read TOOL-SPEC.schema.md, TOOL.template.md, and the examples. Classify each candidate tool by value, risk, data sensitivity, approval boundary, and build complexity. Then recommend the first two tools to build, starting read-only unless there is a compelling reason to do otherwise. Ask me for missing context before writing code.
