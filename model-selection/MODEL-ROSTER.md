# Public model-candidate roster

**Snapshot:** 2026-08-11

**Review due:** 2026-09-11

**Prices:** USD per 1M tokens unless noted

**Scope:** selected first-party API model candidates for agent-capable language work

> This is a maintained planning baseline, not proof of local availability or a universal leaderboard. These are model candidates, not executable routes. Bind one to an endpoint, API mode, service tier, geography, tools, privacy variant, and fallback in a private overlay before evaluation.

## Fast shortlist

| Workload shape | Starting model candidate | Why |
|---|---|---|
| Hardest long-horizon work | `openai/gpt-5.6-sol` or `anthropic/claude-fable-5` | Highest capability; use only when the job earns the premium |
| Balanced production agent | `openai/gpt-5.6-terra` or `anthropic/claude-sonnet-5` | Strong cost-capability balance |
| Cheap bounded worker | `openai/gpt-5.6-luna` or `google/gemini-3.5-flash-lite` | High-volume economics |
| Independent deep review | `anthropic/claude-opus-5` or `xai/grok-4.5` | Strong judgment or adversarial posture; prefer provider diversity from the builder |
| Fast grounded multimodal work | `google/gemini-3.6-flash` | Native grounding and multimodal strength |
| Bounded coding specialist | `xai/grok-build-0.1` | Coding-focused route with low published output cost |

These are editorial starting points, not activation decisions.

## Candidate table

| Model candidate | Status | Standard price: in / cached / write / out | Editorial best fit | Main caveat |
|---|---|---|---|---|
| `openai/gpt-5.6-sol` | current | $5 / $0.5 / $6.25 / $30 | hardest long-horizon agentic work; large codebase reasoning; high-stakes synthesis | expensive for routine or high-volume tasks; long-context and service-tier multipliers can dominate cost |
| `openai/gpt-5.6-terra` | current | $2 / $0.2 / $2.5 / $12 | balanced daily agents; production coding and analysis; moderate-volume professional workflows | not the cheapest route for bounded extraction; still needs workload-specific completion and restraint evaluation |
| `openai/gpt-5.6-luna` | current | $0.2 / $0.02 / $0.25 / $1.2 | bounded high-volume workers; classification and extraction; cheap subagents with strong contracts | lower ceiling on ambiguous or long-horizon work; cheap calls become expensive when weak specifications cause retries |
| `anthropic/claude-fable-5` | current | $10 / $1 / $12.5 / $50 | maximum-capability autonomous knowledge work; long-horizon coding; capability-critical research | highest list price in the main Claude roster; safety classifiers may return refusals as HTTP 200 and require explicit fallback handling; 30-day data retention; not available under zero data retention |
| `anthropic/claude-opus-5` | current | $5 / $0.5 / $6.25 / $25 | deep reasoning and review; complex agentic coding; independent high-stakes critique | can be verbose or expand narrow tasks without a tight contract; premium cost for routine execution |
| `anthropic/claude-sonnet-5` | current | $2 / $0.2 / $2.5 / $10 | everyday production agents; general coding; balanced Claude workloads | not the maximum reasoning tier; route-specific tool and restraint behavior still requires evaluation |
| `anthropic/claude-haiku-4-5-20251001` | current | $1 / $0.1 / $1.25 / $5 | fast lightweight agents; repetitive transformations; latency-sensitive bounded work | lower ceiling on hard reasoning; often more expensive than the cheapest cross-provider small models |
| `google/gemini-3.6-flash` | current | $1.5 / $0.15 / n/a / $7.5 | fast frontier multimodal work; search-grounded agents; coding and web workflows | tool and grounding charges can exceed token cost; free and paid tiers have materially different privacy and feature posture |
| `google/gemini-3.1-pro-preview` | preview | $2 / $0.2 / n/a / $12 | deep multimodal reasoning; technical analysis; agentic coding evaluations | preview stability risk; long-context and grounding costs require explicit modeling |
| `google/gemini-3.5-flash-lite` | current | $0.3 / $0.03 / n/a / $2.5 | high-volume agentic tasks; translation; simple data processing | lower reasoning ceiling; grounding fees can erase savings for search-heavy tasks |
| `xai/grok-4.5` | current | $2 / $0.3 / n/a / $6 | adversarial review; general agentic tools; current X and web research when tools are enabled | real-time knowledge requires separately priced tools; speculative review must be constrained by evidence and severity rules |
| `xai/grok-4.3` | current | $1.25 / $0.2 / n/a / $2.5 | fast instruction following; tool-calling agents; cost-sensitive xAI workloads | lower ceiling than Grok 4.5 for difficult review; tool costs and long-context tiers need explicit budgeting |
| `xai/grok-build-0.1` | current | $1 / $0.2 / n/a / $2 | bounded agentic software engineering; implementation workers; code review with exact artifacts | specialist rather than universal default; requires tests and file-bound verification to prevent invented completion evidence |

## Price and route caveats

- Prices are standard first-party API list prices for the candidate model. Long context, batch/flex, fast/priority, residency, caching, built-in tools, storage, and managed-agent runtime can change the bill.
- Subscription, OAuth, cloud-marketplace, router, and negotiated-contract routes need separate rows in your private overlay. Do not paste direct-API prices onto them and call it accounting.
- `publicly_documented` does not mean enabled, entitled, validated, or approved in your environment.
- Preview routes can change without the stability expected from generally available routes.
- Suitability guidance is editorial unless an `observed` fixed evaluation is explicitly published.

## Sources

- [OpenAI: openai-pricing](https://developers.openai.com/api/docs/pricing) - accessed 2026-08-11
- [OpenAI: openai-selection](https://developers.openai.com/api/docs/guides/model-selection) - accessed 2026-08-11
- [Anthropic: anthropic-pricing](https://platform.claude.com/docs/en/about-claude/pricing.md) - accessed 2026-08-11
- [Anthropic: anthropic-models](https://platform.claude.com/docs/en/about-claude/models/overview.md) - accessed 2026-08-11
- [Anthropic: anthropic-refusals](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback) - accessed 2026-08-11
- [Anthropic: anthropic-retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention) - accessed 2026-08-11
- [Google: gemini-pricing](https://ai.google.dev/gemini-api/docs/pricing) - accessed 2026-08-11
- [Google: gemini-models](https://ai.google.dev/gemini-api/docs/models) - accessed 2026-08-11
- [xAI: xai-pricing](https://docs.x.ai/developers/pricing) - accessed 2026-08-11
- [xAI: xai-models](https://docs.x.ai/developers/models) - accessed 2026-08-11

## How to use this roster

Read [`README.md`](README.md), combine this baseline with a private local overlay, estimate all-in cost, and run the exact-route onboarding/evaluation contract before activation.

The machine-readable authority for this page is [`public-model-roster.json`](public-model-roster.json). Run `python3 model-selection/scripts/render_roster.py --check` to detect drift.
