# Model selection for agents

A model is an operating dependency, not a personality choice. The right route for a cron, tool, profile, reviewer, or subagent depends on the work, the route, and the economics, not whichever model won last week's leaderboard.

This package is a practical operating system for choosing models. It combines:

- a maintained public baseline roster;
- a private local overlay for the routes you can actually use;
- opinionated, evidence-labeled workload guidance;
- route-aware cost analysis;
- prompting guidance by model family;
- a selection record you can preserve with every automation;
- a monthly freshness contract.

It is intentionally not a universal ranking. Model catalogs, prices, subscriptions, tools, privacy terms, and behavior change too quickly for that nonsense.

## The hybrid model

Use two layers:

1. **Public baseline:** `public-model-roster.json` and `MODEL-ROSTER.md` describe selected, publicly documented first-party API model candidates. They are not executable routes. Agent Foundry maintains this layer.
2. **Private overlay:** `local-overlay.example.json` is copied outside a public repo and populated with your credentials-present state, contractual rates, quotas, approved data classes, route validation, and measured performance.

The public baseline never proves that a model is enabled, entitled, production-safe, or successful in your environment. The private overlay binds a public candidate to an exact model ID, API mode, endpoint class, endpoint label, geography, service tier, tool surface, structured-output state, privacy variant, billing basis, and fallback. The overlay should never be committed publicly.

## Decision sequence

### 1. Define the job before choosing the model

Record:

- observable outcome;
- input and output shape;
- task volume and schedule;
- autonomy and tool requirements;
- context and modality requirements;
- latency target;
- data sensitivity and residency requirements;
- failure cost;
- verification and fallback requirements.

If the job is still “be smart about this,” you do not have a model-selection problem. You have a specification problem wearing sunglasses.

### 2. Apply hard gates

Reject any route that fails a mandatory requirement:

- unavailable or unentitled in your environment;
- incompatible tool or structured-output surface;
- insufficient context or modality support;
- unacceptable retention, training-use, residency, or privacy posture;
- unacceptable route provenance or fallback behavior;
- unable to meet the completion **and** restraint floors on a fixed evaluation set.

Price does not rescue a route that fails a hard gate.

### 3. Compare utility, not benchmark prestige

For surviving routes, score the workload-specific trade-offs:

| Dimension | Typical question |
|---|---|
| Quality | Does it produce the required answer or artifact? |
| Completion | Does it finish approved work rather than stop at a plan? |
| Restraint | Does it avoid adjacent or unauthorized work? |
| Reliability | How often are retries, repairs, or fallbacks required? |
| Latency | Does p50/p95 latency fit the interaction or schedule? |
| Economics | What is the expected all-in cost per successful outcome? |
| Operability | Are tooling, telemetry, quotas, and error behavior production-usable? |
| Independence | Is it sufficiently different from the builder to serve as a reviewer? |

Weights belong to the job. A cheap classifier and a board-critical research agent should not share one scorecard.

### 4. Estimate all-in cost

Token list price is only one line item:

```text
expected cost per successful outcome =
  model input + model output + cache writes/reads
  + built-in tool calls + retrieval/storage/runtime charges
  + expected retries and fallbacks
  + reviewer/judge model cost
  + operator recovery time
```

Subscription or OAuth access is not “free.” Record the applicable plan, quota, credit multiplier, throttling risk, and marginal accounting model. Keep direct-API list price as a comparison reference only when it is clearly labeled as such.

### 5. Evaluate the exact route

Before live use, follow [`../skills/examples/model-onboarding-skill.md`](../skills/examples/model-onboarding-skill.md). Freeze the route, endpoint, tools, prompt adapter, reasoning controls, fallback, fixtures, rubric, and thresholds. Evaluate the baseline and candidate on the same workload.

### 6. Preserve the decision

Every production cron, tool, or profile should retain a short selection record:

- chosen route and fallback;
- alternatives considered;
- hard-gate evidence;
- workload scores and measured date;
- expected volume and all-in cost;
- approval and validation state;
- re-evaluation trigger.

Use [`examples/selection-record.example.json`](examples/selection-record.example.json) as the starting shape.

## Evidence labels

The roster deliberately separates three kinds of statements:

- **Official:** model identity, public availability, list price, context, retirement, or provider feature claim from an official source.
- **Observed:** behavior measured on a fixed, disclosed evaluation. The public baseline does not claim private observed results.
- **Editorial:** Agent Foundry's opinionated best-fit, weakness, or cost/benefit guidance. Useful judgment, not vendor fact.

Unknown means unknown. Do not let an agent convert an empty field into a confident paragraph.

## Package map

- [`MODEL-ROSTER.md`](MODEL-ROSTER.md): readable public baseline table.
- [`public-model-roster.json`](public-model-roster.json): canonical machine-readable baseline.
- [`model-roster.schema.json`](model-roster.schema.json): roster contract.
- [`local-overlay.example.json`](local-overlay.example.json): private environment overlay template.
- [`local-overlay.schema.json`](local-overlay.schema.json): exact-route overlay contract.
- [`selection-record.schema.json`](selection-record.schema.json): public synthetic-fixture contract for workload-selection evidence; private production records need a separately governed approval/runtime schema.
- [`PROMPTING-GUIDE.md`](PROMPTING-GUIDE.md): family-level prompting guidance.
- [`SPECIALIST-MODELS.md`](SPECIALIST-MODELS.md): image, video, audio, embedding, and other specialist-route appendix.
- [`MAINTENANCE.md`](MAINTENANCE.md): refresh and freshness policy.
- [`examples/`](examples/): synthetic selection records for common agent workloads.
- [`scripts/`](scripts/): deterministic renderer and validator.

## Recommended use in a cron, tool, or profile build

1. Read this guide and the public roster.
2. Load your private overlay from a non-public location and validate it with `python3 model-selection/scripts/validate_roster.py --overlay /private/path/local-overlay.json`.
3. Shortlist only routes that pass hard gates.
4. Estimate all-in cost at expected volume.
5. Run a fixed route-specific evaluation.
6. Select the smallest route that clears the required quality, completion, restraint, and reliability floors.
7. Record the choice and re-evaluation trigger.
8. Activate transactionally with readback and rollback.

## Pickup prompt

> Read `model-selection/README.md`, `MODEL-ROSTER.md`, `PROMPTING-GUIDE.md`, and the model-onboarding skill. Ask me for the job's outcome, volume, autonomy, tools, context, modalities, latency, privacy, failure cost, and budget. Then shortlist routes from the public baseline plus my private overlay. Reject routes that fail hard gates, estimate all-in cost per successful outcome, identify what remains unknown, and propose a fixed evaluation. Do not recommend live activation from public reputation or list price alone.
