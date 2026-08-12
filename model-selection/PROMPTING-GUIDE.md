# Prompting guide for agent models

This guide captures portable family-level guidance. It is not a substitute for route-specific evaluation, and it deliberately excludes private system prompts and runtime adapters.

## Universal contract

```text
Goal: <one observable outcome>
Context: <facts, files, and sources the model needs>
Constraints: <scope, authority, privacy, budget, forbidden actions>
Deliverable: <exact output shape, path, and audience>
Verification: <tests, citations, readback, or evidence required before claiming done>
Stop conditions: <what must remain unresolved or needs approval>
```

Do not ask for hidden chain-of-thought. Ask for the conclusion, assumptions, evidence, material uncertainty, and verification result.

## OpenAI reasoning family

Applies to GPT-5.6-class and adjacent reasoning/coding routes.

- Lead with the outcome and completion criteria.
- Keep tool requirements explicit: “write and run” is different from “describe.”
- Separate runtime controls such as reasoning effort, service tier, and context choice from prose instructions.
- Use the most capable tier for genuine ambiguity and long-horizon work, the balanced tier for everyday execution, and the smallest tier for tightly bounded high-volume jobs.
- Avoid repeating generic tool doctrine already enforced by the runtime; duplicate instructions waste context and can conflict.
- Require artifact/test/readback evidence for build work.

**Watch for:** paying flagship rates for simple extraction; treating a lower tier as a drop-in replacement without testing completion; long-context and fast-mode multipliers.

## Claude family

Applies to Fable, Opus, Sonnet, and Haiku routes.

- State the outcome, authority, non-goals, and output size clearly.
- Give capable Claude routes room to execute, but constrain narrow tasks explicitly so they do not broaden into adjacent work.
- For judgment work, separate evidence, assumptions, recommendation, and what would change the recommendation.
- Use adaptive thinking for difficult agentic work when the route supports it; keep reasoning controls in runtime configuration.
- Use Fable only when the capability ceiling matters enough to justify the premium. Use Opus for deep work/review, Sonnet for the mainstream balance, and Haiku for bounded speed.
- Use fresh-context independent verification for long, expensive builds.

**Watch for:** verbosity, scope expansion, redundant self-review loops, and assuming all Claude endpoints share one privacy or feature contract.

## Gemini family

- Specify role, goal, context, constraints, tools, and output schema plainly.
- Use Flash for fast frontier multimodal or grounded work, Pro for deeper multimodal reasoning, and Flash-Lite for volume.
- Configure thinking through runtime controls; do not ask the model to print internal reasoning.
- Pin stable model IDs for production. `latest` aliases can move underneath you.
- Budget search grounding, Maps, cache storage, and agent-loop intermediate tokens separately from base inference.
- Treat free-tier and paid-tier data-use posture as different routes.

**Watch for:** preview drift, hidden grounding/tool economics, and hot-swapping aliases.

## Grok family

- For review, define the adversarial scope, severity rubric, evidence threshold, and final verdict.
- Require concrete, reproducible failure modes. Park speculative or adjacent findings instead of allowing review to expand the product mandate.
- Enable X or web tools when current information matters; base model knowledge is not an automatic live feed.
- For coding routes, bind claims to exact files, commands, tests, and observed outputs.
- Use a cheaper general route for ordinary tool work and the stronger route when critique or reasoning quality clears a measured threshold.

**Watch for:** speculative blockers, separately metered server-side tools, and long-context price doubling.

## Reviewer independence

Do not automatically use the same provider, prompt, and model family for builder and reviewer. Independence is not guaranteed by a different model name, but diversity can expose correlated blind spots. Preserve the exact reviewer contract and require evidence-bound findings either way.

## Prompt maintenance

Re-evaluate prompting guidance when any of these change:

- model generation or reasoning controls;
- provider endpoint or tool surface;
- system prompt or adapter;
- context or output limits;
- fixed evaluation performance;
- model behavior around completion, restraint, citations, or structured output.

Prompt folklore ages even faster than pricing. Treat it accordingly.
