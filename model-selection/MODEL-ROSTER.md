# Public model-candidate roster

**Snapshot:** 2026-09-25

**Review due:** 2026-10-25

**Prices:** USD per 1M tokens unless noted

**Scope:** selected first-party API model candidates for agent-capable language work

> This is a maintained planning baseline, not proof of local availability or a universal leaderboard. These are model candidates, not executable routes. Bind one to an endpoint, API mode, service tier, geography, tools, privacy variant, and fallback in a private overlay before evaluation.

## Fast shortlist

| Workload shape | Starting model candidate | Why |
|---|---|---|
| Hardest long-horizon work | `openai/gpt-6-astra` or `anthropic/claude-fable-5-1` | Editorial high-capability starting points; use only when the job earns the premium |
| Balanced production agent | `openai/gpt-6-sol` or `anthropic/claude-opus-5-5` | Editorial cost-capability starting points |
| Cheap bounded worker | `openai/gpt-6-luna` or `google/gemini-3.5-flash-lite` | Editorial high-volume economics |
| Independent deep review | `anthropic/claude-opus-5-5` or `xai/grok-4.7` | Editorial reviewer candidates; prefer provider diversity from the builder |
| Fast grounded multimodal work | `google/gemini-3.8-flash` | Editorial multimodal starting point; grounding is separately priced |
| Bounded coding specialist | `xai/grok-build-0.1` | Coding-focused route with low published output cost |

These are editorial starting points, not activation decisions.

## Candidate table

| Model candidate | Status | Standard price: in / cached / write / out | Price tier and caveat | Editorial best fit | Editorial weakness |
|---|---|---|---|---|---|
| `openai/gpt-6-astra` | current | $10 / $1 / $12.5 / $50 | Flagship Standard short context; >272k input tokens: 2x input/cache and 1.5x output for full request. | ambiguous high-stakes deliverables; complex agentic work | premium token price; local suitability and entitlement untested |
| `openai/gpt-6-sol` | current | $2 / $0.2 / $2.5 / $10 | Flagship Standard short context; long context, Fast mode and residency can cost more. | everyday coding and writing; balanced agentic work | still requires exact-route evaluation; tool fees and long context can dominate |
| `openai/gpt-6-luna` | current | $0.1 / $0.01 / $0.125 / $0.5 | Flagship Standard short context; long context, Fast mode and residency can cost more. | bounded classification; frequent scoped automations | lower ceiling for ambiguous work; retries and tools can erase savings |
| `openai/gpt-5.6-sol` | current | $4 / $0.4 / $5 / $20 | Cyber models, standard short context; promotional pricing at least through 2026-11-21. >272k input tokens: 2x input, 1.5x output for full request. | complex professional work; large codebase reasoning; high-stakes synthesis | expensive for routine or high-volume tasks; long-context and service-tier multipliers can dominate cost |
| `openai/gpt-5.6-terra` | current | $2 / $0.2 / $2.5 / $12 | Standard short context; >272k input tokens: 2x input and 1.5x output for full request; cache writes 1.25x input. | balanced daily agents; production coding and analysis; moderate-volume professional workflows | not the cheapest route for bounded extraction; still needs workload-specific completion and restraint evaluation |
| `openai/gpt-5.6-luna` | current | $0.2 / $0.02 / $0.25 / $1.2 | Standard short context; >272k input tokens: 2x input and 1.5x output for full request; cache writes 1.25x input. | bounded high-volume workers; classification and extraction; cheap subagents with strong contracts | lower ceiling on ambiguous or long-horizon work; cheap calls become expensive when weak specifications cause retries |
| `anthropic/claude-fable-5-1` | current | $10 / $0.25 / $12.5 / $50 | Five-minute cache write; one-hour write $20. Covered model: confirm retention/ZDR contract before sensitive use. | long-horizon agentic reasoning; complex coding and research | premium cost; HTTP 200 refusal needs explicit handling; covered-model 30-day retention absent special authorization |
| `anthropic/claude-fable-5` | legacy | $10 / $1 / $12.5 / $50 | Legacy, still available. Five-minute cache-write price shown; one-hour writes cost more. | maximum-capability autonomous knowledge work; long-horizon coding; capability-critical research | higher cache read price than Fable 5.1; safety classifiers may return refusals as HTTP 200 and require explicit fallback handling; covered-model 30-day retention absent special authorization |
| `anthropic/claude-opus-5-5` | current | $4 / $0.2 / $5 / $20 | Five-minute cache write; one-hour write $8. Fast and US-only inference cost more. | general-purpose Claude agent; independent deep review | HTTP 200 classifier refusal needs handling; exact-route tool and restraint behavior untested |
| `anthropic/claude-opus-5` | legacy | $5 / $0.5 / $6.25 / $25 | Legacy, still available. Five-minute cache write; fast mode and US-only inference add premiums. | deep reasoning and review; complex agentic coding; independent high-stakes critique | can be verbose or expand narrow tasks without a tight contract; premium cost for routine execution |
| `anthropic/claude-sonnet-5` | current | $2 / $0.2 / $2.5 / $10 | Five-minute cache-write price shown. | everyday production agents; general coding; balanced Claude workloads | not the maximum reasoning tier; route-specific tool and restraint behavior still requires evaluation |
| `anthropic/claude-haiku-4-5-20251001` | current | $1 / $0.1 / $1.25 / $5 | Five-minute cache-write price shown. | fast lightweight agents; repetitive transformations; latency-sensitive bounded work | lower ceiling on hard reasoning; often more expensive than the cheapest cross-provider small models |
| `google/gemini-3.8-flash` | current | $0.75 / $0.075 / n/a / $3.75 | Standard paid promotional rates through 2026-12-31; scheduled $1.50/$0.15/$7.50 from 2027-01-01. Cache storage and grounding separate. | fast multimodal agents; search-grounded and coding workflows | grounding and storage charges require budgeting; free and paid data-use terms differ |
| `google/gemini-3.6-flash` | current | $0.75 / $0.075 / n/a / $3.75 | Previous-generation stable, not shut down. Standard paid promotional rates through 2026-12-31; scheduled $1.50/$0.15/$7.50 from 2027-01-01. Cache storage and grounding separate. | fast frontier multimodal work; search-grounded agents; coding and web workflows | tool and grounding charges can exceed token cost; free and paid tiers have materially different privacy and feature posture |
| `google/gemini-3.1-pro-preview` | preview | $2 / $0.2 / n/a / $12 | Standard prompts up to 200k tokens; longer prompts cost more. Preview routes can change. | deep multimodal reasoning; technical analysis; agentic coding evaluations | preview stability risk; long-context and grounding costs require explicit modeling |
| `google/gemini-3.5-flash-lite` | current | $0.3 / $0.03 / n/a / $2.5 | Standard paid tier; batch/flex rates are lower. | high-volume agentic tasks; translation; simple data processing | lower reasoning ceiling; grounding fees can erase savings for search-heavy tasks |
| `xai/grok-4.7` | current | $2 / $0.5 / n/a / $6 | Standard global short context; prompt >=200k uses $4/$1/$12 for all tokens. Search tools separately billed; US region 1.1x, priority 2x. | independent adversarial review; agentic coding and tools | no realtime knowledge without search tools; review needs evidence and severity contract |
| `xai/grok-4.6` | current | $2 / $0.5 / n/a / $6 | Still listed; standard global short context. Prompt >=200k uses $4/$1/$12 for all tokens; tools separately billed. | agentic coding; independent review with exact artifacts | no realtime knowledge without search tools; not an entitlement or performance claim |
| `xai/grok-4.5` | current | $2 / $0.3 / n/a / $6 | Still listed; short standard global context. Prompts >=200k use $4/$0.60/$12 for all tokens; tools separately metered. | adversarial review; general agentic tools; current X and web research when tools are enabled | real-time knowledge requires separately priced tools; speculative review must be constrained by evidence and severity rules |
| `xai/grok-4.3` | current | $1.25 / $0.2 / n/a / $2.5 | Prompts at or above 200k tokens cost 2x; server-side tools are separately metered. | fast instruction following; tool-calling agents; cost-sensitive xAI workloads | lower ceiling than Grok 4.5 for difficult review; tool costs and long-context tiers need explicit budgeting |
| `xai/grok-build-0.1` | current | $1 / $0.2 / n/a / $2 | Prompts at or above 200k tokens cost 2x. | bounded agentic software engineering; implementation workers; code review with exact artifacts | specialist rather than universal default; requires tests and file-bound verification to prevent invented completion evidence |

## Price and route caveats

- Prices are standard first-party API list prices for the candidate model. Long context, batch/flex, fast/priority, residency, caching, built-in tools, storage, and managed-agent runtime can change the bill.
- Subscription, OAuth, cloud-marketplace, router, and negotiated-contract routes need separate rows in your private overlay. Do not paste direct-API prices onto them and call it accounting.
- `publicly_documented` does not mean enabled, entitled, validated, or approved in your environment.
- Preview routes can change without the stability expected from generally available routes.
- `legacy` means still available in the cited catalogue, not retired. Google's 3.6 Flash is previous-generation **stable**, and xAI still lists 4.5 and 4.6; none of these statuses proves local entitlement.
- Google Flash 3.8/3.6 paid Standard promotional rates run through 2026-12-31, with higher published rates scheduled from 2027-01-01; OpenAI GPT-5.6 Sol promotional pricing is documented at least through 2026-11-21. Recheck before relying on future bills.
- Suitability guidance is editorial unless an `observed` fixed evaluation is explicitly published.

## Sources

- [OpenAI: openai-pricing](https://developers.openai.com/api/docs/pricing) - accessed 2026-09-25
- [OpenAI: openai-selection](https://developers.openai.com/api/docs/guides/model-selection) - accessed 2026-09-25
- [Anthropic: anthropic-pricing](https://platform.claude.com/docs/en/about-claude/pricing.md) - accessed 2026-09-25
- [Anthropic: anthropic-models](https://platform.claude.com/docs/en/models/overview.md) - accessed 2026-09-25
- [Anthropic: anthropic-refusals](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback) - accessed 2026-09-25
- [Anthropic: anthropic-retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention) - accessed 2026-09-25
- [Google: gemini-pricing](https://ai.google.dev/gemini-api/docs/pricing) - accessed 2026-09-25
- [Google: gemini-models](https://ai.google.dev/gemini-api/docs/models) - accessed 2026-09-25
- [xAI: xai-pricing](https://docs.x.ai/developers/pricing) - accessed 2026-09-25
- [xAI: xai-models](https://docs.x.ai/developers/models) - accessed 2026-09-25

## How to use this roster

Read [`README.md`](README.md), combine this baseline with a private local overlay, estimate all-in cost, and run the exact-route onboarding/evaluation contract before activation.

The machine-readable authority for this page is [`public-model-roster.json`](public-model-roster.json). Run `python3 model-selection/scripts/render_roster.py --check` to detect drift.
