#!/usr/bin/env python3
"""Render MODEL-ROSTER.md from the canonical public JSON roster."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "public-model-roster.json"
OUTPUT = ROOT / "MODEL-ROSTER.md"


def money(value: object) -> str:
    if value is None:
        return "n/a"
    return f"${value:g}"


def compact(items: list[str]) -> str:
    return "; ".join(items)


def render(data: dict) -> str:
    lines = [
        "# Public model-candidate roster",
        "",
        f"**Snapshot:** {data['as_of']}",
        "",
        f"**Review due:** {data['review_due_at']}",
        "",
        "**Prices:** USD per 1M tokens unless noted",
        "",
        "**Scope:** selected first-party API model candidates for agent-capable language work",
        "",
        "> This is a maintained planning baseline, not proof of local availability or a universal leaderboard. These are model candidates, not executable routes. Bind one to an endpoint, API mode, service tier, geography, tools, privacy variant, and fallback in a private overlay before evaluation.",
        "",
        "## Fast shortlist",
        "",
        "| Workload shape | Starting model candidate | Why |",
        "|---|---|---|",
        "| Hardest long-horizon work | `openai/gpt-6-astra` or `anthropic/claude-fable-5-1` | Editorial high-capability starting points; use only when the job earns the premium |",
        "| Balanced production agent | `openai/gpt-6-sol` or `anthropic/claude-opus-5-5` | Editorial cost-capability starting points |",
        "| Cheap bounded worker | `openai/gpt-6-luna` or `google/gemini-3.5-flash-lite` | Editorial high-volume economics |",
        "| Independent deep review | `anthropic/claude-opus-5-5` or `xai/grok-4.7` | Editorial reviewer candidates; prefer provider diversity from the builder |",
        "| Fast grounded multimodal work | `google/gemini-3.8-flash` | Editorial multimodal starting point; grounding is separately priced |",
        "| Bounded coding specialist | `xai/grok-build-0.1` | Coding-focused route with low published output cost |",
        "",
        "These are editorial starting points, not activation decisions.",
        "",
        "## Candidate table",
        "",
        "| Model candidate | Status | Standard price: in / cached / write / out | Price tier and caveat | Editorial best fit | Editorial weakness |",
        "|---|---|---|---|---|---|",
    ]
    for candidate in data["candidates"]:
        p = candidate["prices"]
        price = " / ".join([money(p["input"]), money(p["cached_input"]), money(p["cache_write"]), money(p["output"])])
        lines.append(
            f"| `{candidate['candidate_id']}` | {candidate['status']} | {price} | {p['notes']} | {compact(candidate['best_fit'])} | {compact(candidate['weaknesses'])} |"
        )
    lines.extend([
        "",
        "## Price and route caveats",
        "",
        "- Prices are standard first-party API list prices for the candidate model. Long context, batch/flex, fast/priority, residency, caching, built-in tools, storage, and managed-agent runtime can change the bill.",
        "- Subscription, OAuth, cloud-marketplace, router, and negotiated-contract routes need separate rows in your private overlay. Do not paste direct-API prices onto them and call it accounting.",
        "- `publicly_documented` does not mean enabled, entitled, validated, or approved in your environment.",
        "- Preview routes can change without the stability expected from generally available routes.",
        "- `legacy` means still available in the cited catalogue, not retired. Google's 3.6 Flash is previous-generation **stable**, and xAI still lists 4.5 and 4.6; none of these statuses proves local entitlement.",
        "- Google Flash 3.8/3.6 paid Standard promotional rates run through 2026-12-31, with higher published rates scheduled from 2027-01-01; OpenAI GPT-5.6 Sol promotional pricing is documented at least through 2026-11-21. Recheck before relying on future bills.",
        "- Suitability guidance is editorial unless an `observed` fixed evaluation is explicitly published.",
        "",
        "## Sources",
        "",
    ])
    for source in data["sources"]:
        lines.append(f"- [{source['publisher']}: {source['source_id']}]({source['url']}) - accessed {source['accessed_at']}")
    lines.extend([
        "",
        "## How to use this roster",
        "",
        "Read [`README.md`](README.md), combine this baseline with a private local overlay, estimate all-in cost, and run the exact-route onboarding/evaluation contract before activation.",
        "",
        "The machine-readable authority for this page is [`public-model-roster.json`](public-model-roster.json). Run `python3 model-selection/scripts/render_roster.py --check` to detect drift.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    rendered = render(data)
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != rendered:
            print("MODEL-ROSTER.md is stale; run render_roster.py")
            return 1
        print("model roster render: CLEAN")
        return 0
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
