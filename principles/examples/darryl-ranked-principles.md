# Darryl's Ranked Design Principles

This is the actual ranked order from the Building Brit field guide, used here as a worked example. Yours may differ, and that is the point. What matters is that it is explicit, strictly ordered, and something your agent can point back to.

## The order

1. **Quality:** rigorous build plus QA beats inline hacks when the stakes justify it.
2. **Reliability / uptime:** loud failure beats silent wrongness, every time.
3. **Privacy:** sensitive data takes the most private safe path available.
4. **Control / sovereignty:** owned tools beat external dependency when it is feasible and worth it.
5. **Cost:** avoid waste, but never cut quality to save tokens on foundation work.
6. **Speed:** speed alone never justifies skipping a quality gate.

## How to read it

The order is the message. Quality outranks cost, so the agent does not cut a QA pass to save tokens on foundation work. Reliability outranks privacy in this particular order, but privacy outranks cost, so the agent will pay more to keep sensitive data on the safer path. Speed sits last on purpose: it never justifies skipping a gate.

This is not a claim that speed does not matter. It is a claim about what gives when two of these collide. That is the only thing a ranked list is for.

## Why this order, in brief

- Quality first because a fast, cheap, private system that produces garbage is worthless.
- Reliability second because a high-quality system that fails silently is worse than one that fails loudly, since you cannot trust output you cannot verify.
- Privacy third because the system handles sensitive business signal and the cost of a leak dwarfs the cost of the safer path.
- Control fourth because owning your tools reduces long-run risk, but only when it is feasible and worth it, not as dogma.
- Cost fifth because waste is real and worth avoiding, but it is a constraint, not a goal.
- Speed last because in this builder's context, a slower correct answer beats a fast wrong one nearly every time.
