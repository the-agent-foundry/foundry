# Profile Operating Model

This is the public operating model for specialist profiles: how a founder moves from one general assistant to a small team of focused agents without turning the system into a maze.

The goal is not more agents. The goal is cleaner context, sharper quality bars, and less repeated explanation.

## The four levels

1. **Prototype bench**
   - New, ambiguous, strategic, sensitive, or unproven workflows stay with the orchestrator.
   - The orchestrator learns what good looks like before creating a specialist.

2. **Specialist profile**
   - A repeated domain gets a named owner: engineer, call processor, briefer, writer, mechanic, or another focused role.
   - The profile has its own mission, tools, skills, approval boundaries, and quality bar.

3. **Orchestrated work**
   - Cross-domain requests are decomposed by the orchestrator and routed to specialists.
   - The orchestrator owns final synthesis and verifies claims before reporting done.

4. **Autonomous loop**
   - Recurring workflows run on schedule or trigger only after inputs, owner, QA, privacy ceiling, approval boundary, activation owner, state, and failure behavior are clear.

## Promotion gate

Promote a workflow into a specialist profile only when these are true:

- The task recurs.
- The input and output shape are predictable.
- The quality bar can be written down.
- The role benefits from a focused context.
- Tool access can be scoped narrowly.
- Privacy and approval boundaries are clear.
- Failure behavior is loud and recoverable.
- A human can inspect the output and understand what happened.

Do not create a profile because the name sounds cool. That is how you get an org chart made of fog.

## Profile spec checklist

Every specialist profile needs:

- Mission: one job in one sentence.
- Scope: in bounds and out of bounds.
- Skills: procedures it loads every time.
- Tools: the smallest set needed to do the job.
- Inputs: sources it reads.
- Outputs: artifacts it produces.
- Quality bar: what good looks like.
- State: what it tracks over time.
- Gates: approval, privacy, QA, red-team, or research as needed.
- Handoff contract: what the orchestrator must provide.
- Closeout contract: what evidence it returns.

## Handoff contract

A good specialist handoff includes:

- Real goal.
- Context and relevant history.
- Inputs and file/source paths, if any.
- Constraints and non-goals.
- Privacy ceiling: founder-only, team-safe, public-safe, or external-ready.
- Allowed side effects.
- Required gates.
- Acceptance criteria.
- Desired artifact format.

If the handoff is vague, the output will be vague. Garbage in, polished garbage out.

## Closeout contract

A specialist closeout should include:

- What was done.
- What artifact was created.
- What evidence proves it.
- What failed and how it was fixed.
- What remains uncertain.
- What needs approval, if anything.
- What should be codified for next time.

For meaningful work, use the build manifest pattern or a domain-specific equivalent.

## Privacy posture

Public examples should preserve the pattern, not the private implementation.

Do publish:

- Role specs.
- Quality bars.
- Gate logic.
- Handoff templates.
- Sanitized examples.
- Failure modes and anti-patterns.

Do not publish:

- Live prompts.
- Private memory.
- Credentials or auth config.
- Chat IDs or private routing.
- Customer, employee, investor, vendor, or personal data.
- Raw logs or transcripts.
- Internal paths tied to a real machine.

## Pickup prompt

> Review this operating model and our current assistant setup. Which workflows should stay with the orchestrator, which deserve specialist profiles, and which are ready for autonomous loops? Ask me for missing context before recommending implementation.
