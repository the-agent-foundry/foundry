# The Six-Question Design Gate

Before building any non-trivial system, a recurring automation, a persistent feature, or an architecture choice, answer these six questions first. This is a reasoning gate, but treat it like a hard one for anything that will run unattended or persist over time. Skipping it is how you ship clever one-offs that rot.

Use it as a checklist. Write the answers down. If you cannot answer one, you are not ready to build.

## The six questions

### 1. What are we actually trying to accomplish?

State the real underlying need, not the requested implementation. The thing someone asked for is usually a guess at a solution. Find the need underneath it, because the right build often looks nothing like the original request.

- [ ] I have stated the real need in one sentence, without naming a solution.

### 2. What domain concept are we modeling?

Identify the real-world thing, not a lazy proxy for it. If you model the proxy, you ship something that drifts away from reality the moment the proxy and the concept diverge.

- [ ] I have named the real domain concept, and I have not substituted a measurable stand-in for it.

### 3. How does this break when nobody is looking?

Think about new data, volume changes, source drift, upstream behavior changes, and six months of neglect. Systems do not fail at the demo. They fail quietly, later, when the inputs stop looking like the inputs you tested on.

- [ ] I have listed the realistic failure modes and what each one looks like in the wild.

### 4. Are we solving the problem or just this instance?

Decide consciously: a one-off fix, or a reusable system? Both are legitimate. The mistake is building a one-off by accident when you needed a system, or over-engineering a system when a one-off was enough.

- [ ] I have made a conscious, stated choice between one-off and reusable.

### 5. What state does the system need to stay alive?

High-water marks, provenance, dedupe, freshness, retry state, health checks. A system that processes a stream needs to know what it already saw, where data came from, how fresh it is, and whether it is still healthy. Name the state up front or you will bolt it on badly later.

- [ ] I have listed the state the system must track to keep working over time.

### 6. What tradeoffs and proxies are acceptable, and when do we revisit?

Document the shortcuts, the failure modes, the monitoring, and the explicit trigger that says "revisit this." A conscious proxy with a revisit trigger is good engineering. An unconscious one is a landmine.

- [ ] I have documented each tradeoff and the concrete trigger that would make me revisit it.

## Anti-patterns this gate is built to catch

- **Silent degradation:** output goes stale or wrong with no alert.
- **Proxy logic pretending to be domain modeling:** a measurable stand-in quietly replaces the real concept.
- **"It works today" syndrome:** works on the current sample, no plan for tomorrow.
- **One-shot thinking inside recurring products:** a static pile of cleverness with no renewal.
- **Completion theater:** declaring done from explanation instead of proof.
- **Policy theater:** treating a polite instruction as a real safety control.
- **Build-log theater:** logs exist somewhere, but nobody can actually read the system.
- **Private source-of-truth rot:** the data feeding your automations quietly decays.
- **Perfection paralysis:** over-engineering when a conscious proxy was enough.

> In plain English: build the durable system, not the cute patch. Make failure loud. Protect privacy. Keep the cockpit legible. Prove done with artifacts, not vibes.
