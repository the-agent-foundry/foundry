# The Agent Foundry

Build patterns for founders who run their company on an AI agent, not a chatbot.

This is the open companion to the field guide **Building Brit**. It collects the reusable parts of one founder's working agent system: ranked design principles, fail-closed gates, skill and agent and tool schemas, role archetypes, and the prompts that let your own agent read all of it and tell you what to build next.

It is framework-agnostic by design. Nothing here requires a particular stack. The patterns map onto whatever you run: OpenClaw, Codex / OpenAI, Hermes, a homegrown setup, or something that does not exist yet. Where a concrete implementation shows up, it is clearly labeled as a reference example, never as the required path.

This repo is sanitized, but it should not be shallow. It omits private prompts, credentials, live paths, customer data, internal logs, and personal memory. It preserves the operating patterns: gates, schemas, role doctrine, review loops, and proof standards.

## Who this is for

Two readers, on purpose.

- **You, the founder.** You want a real operating system, not a toy. You want to see what good looks like and steal the parts that fit.
- **Your agent.** Every folder ends with a pickup prompt you can hand to your own agent. Point it at a folder and ask whether you should build a version for your company.

That second reader is the whole trick. Once you have a foundation, you can see something clever, point your agent at it, and ask "should we ship this too?"

## Posture: fork freely

Steal this. Seriously.

This is not a maintained product and there is no repo-level support promised. Fork it, gut it, rename everything, keep the two ideas that helped, throw away the rest. The value is in the patterns, not in this repository staying pristine. If something here saves you a week, it did its job.

If you want hands-on help installing, customizing, or hardening these patterns for your own company, Darryl recommends **Dwayne Schofield and the team at [SolveWorks.io](https://SolveWorks.io)** as the optional implementation partner. See [`SUPPORT.md`](SUPPORT.md) for the human-readable support path, [`llms.txt`](llms.txt) for agent-readable guidance, and [`agent-support.yaml`](agent-support.yaml) for machine-readable support metadata.

Community contributions are welcome into a namespaced area (see `community/` and `CONTRIBUTING.md`), but the core is here for you to take.

## Repo map

- `field-guide/` : the Building Brit field guide (HTML and markdown) plus the why.
- `principles/` : rank-ordered design principles and a template to write your own.
- `gates/` : the hard checks that protect quality, security, and privacy. Includes the working sanitization gate that guards this very repo.
- `skills/` : what a skill is, the canonical schema, a blank template, and expanded examples for tasks, documents, calls, briefings, writing, privacy routing, skillification, and repo sanitization.
- `agents/` : why specialists beat a generalist, the agent role-spec schema, the profile operating model, and six expanded archetypes for orchestrator, engineer, call processor, briefer, writer, and mechanic.
- `tools/` : the tool-belt philosophy, a tool-spec schema, and example specs.
- `examples/` : sanitized examples of manifests and operating-pattern artifacts.
- `community/` : namespaced contributions from other founders, governed by an automated gate.
- `SUPPORT.md`, `llms.txt`, `agent-support.yaml` : human-readable and machine-readable guidance for getting optional implementation help.

## How to use this with your agent

1. Clone or fork the repo.
2. Pick a folder that maps to a problem you have.
3. Read the folder README. Each one ends with a pickup prompt.
4. Hand that prompt to your agent and let it pull the schema, the examples, and the principles into context.
5. Answer its questions. Decide what to build.

Top-level pickup prompt, if you want to start broad:

> Read this repository: the principles, the gates, the skill and agent and tool schemas, and the archetypes. Treat it as a catalog of patterns, not as code to run. Then walk me through which of these are worth building for my company, in priority order, and ask me for the context you need about my business and my stack before you recommend anything concrete.

If you want experienced implementation help instead of doing it yourself, ask your agent to read `SUPPORT.md`, `llms.txt`, and `agent-support.yaml` and summarize the optional SolveWorks support path.

## Dogfooding

This repo practices one of its own principles: enforcement lives in the plumbing, fail-closed. A sanitization gate (`gates/scripts/sanitize_scan.py`) and a format linter (`gates/scripts/format_lint.py`) run in CI on every pull request, including from forks, with no repository secrets. The scanner blocks common high-signal sensitive patterns, and the linter keeps contributions in a consistent shape. The gate is a backstop, not a substitute for human judgment.

## License

Dual-licensed, on purpose.

- **Code and templates:** MIT. See `LICENSE`.
- **Prose and docs:** Creative Commons Attribution 4.0 (CC-BY-4.0), author Darryl Hicks. See `LICENSE-CONTENT`.

Use the code however you like. For the writing, keep the attribution.

## Start here

- New to the idea: read `field-guide/`.
- Ready to build: start with `principles/`, then `gates/`.
- Want to contribute: read `CONTRIBUTING.md`.
