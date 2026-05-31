---
name: recurring-briefing
problem: I repeatedly ask what changed, what needs attention, and what I am missing
stack: agnostic
maturity: spec
owner: <YOUR_HANDLE>
data_sensitivity: private
action_class: read-only
approval_required: before-external-action
source_of_truth: read-only
freshness_requirement: daily
audit_log: required
---

# Recurring briefing tool

*A worked spec for a daily or weekly operating brief that ranks signal instead of dumping source noise.*

## Problem

A founder's day has too many moving parts: calendar, tasks, meetings, follow-ups, metrics, travel, inbox items, relationship loops, and external watchlists. The recurring question is not "show me everything." It is "what changed, what matters, and where do I need to act?"

A recurring-briefing tool turns approved sources into a short ranked brief on a cadence or on demand.

## Interface

**Input:** briefing type, cadence, lookback window, source categories, delivery audience, and optional focus areas.

**Output:** ranked operating brief:

```json
{
  "brief_type": "daily | weekly | custom",
  "period": "lookback window",
  "top_items": [
    {"item": "what matters", "why_it_matters": "reason", "recommended_action": "next step", "confidence": "high | medium | low"}
  ],
  "decisions_needed": ["specific decisions"],
  "blocked_or_stale_loops": ["open loops needing attention"],
  "upcoming_prep": ["meetings or events needing prep"],
  "source_health": [
    {"source": "source category", "freshness": "fresh | stale | unavailable"}
  ],
  "omitted_noise": "brief note on what was intentionally not included"
}
```

**How the agent calls it:** on a schedule or when asked for a brief. The tool reads approved sources, ranks items, and returns a brief. Generation is separate from delivery. Scheduled delivery requires an explicit destination allowlist, audience label, delivery policy, and cadence approval.

## What good looks like

- Ranked signal, not a firehose.
- Each surfaced item explains why it matters.
- Stale items do not repeat forever unless still actionable.
- Source outages and freshness are visible.
- The brief fits the delivery channel and audience.
- Revisit trigger: the founder stops reading it, repeatedly asks for missing sections, or consistently ignores noisy sections.

## Failure modes

- Source failure hides behind a polished brief.
- Low-confidence signals are framed as urgent.
- Recurring items become wallpaper.
- The brief includes private detail in a shared channel.
- The cadence continues after the underlying need disappears.

## Privacy notes

Briefings can aggregate sensitive calendar, task, relationship, financial, customer, and personal context. Delivery route matters. A founder-only brief can include different material than a team-safe brief. Public specs should describe source categories only.

## Approval boundaries

Generating a brief is allowed. Delivery defaults to local/private display or draft-only. Scheduled delivery is allowed only to an explicit founder-owned recipient or channel allowlist with prior approval, audience label, safe-content policy, expiry/pause behavior, and audit log. Forwarding, posting to shared channels, sending external updates, or mutating source systems requires per-action approval.

## Freshness and state

Track the last run, lookback window, source freshness, items already surfaced, ignored items, and stale loops. Without state, recurring briefings either miss changes or repeat noise.

## Observability

Log run time, source health, item counts, omitted-source warnings, delivery policy, delivery status, and whether the brief was empty by design or empty because sources failed. Do not log raw private content.
