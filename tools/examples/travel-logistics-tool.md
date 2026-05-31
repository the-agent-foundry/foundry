---
name: travel-logistics
problem: Planning and tracking travel eats time and attention I would rather spend elsewhere
stack: agnostic
maturity: spec
owner: <YOUR_HANDLE>
data_sensitivity: private
action_class: draft-only
approval_required: before-external-action
source_of_truth: read-only
freshness_requirement: real-time
audit_log: required
---

# Travel logistics tool

*A worked spec. One way to let your agent handle the friction of travel: options, timing, and the small logistics that otherwise pile up. Build your own version against your preferred providers.*

## Problem

Travel is a stack of small annoyances. Finding workable flights around a meeting, checking what time you actually need to leave, figuring out connection risk, remembering time-zone math, and knowing whether a tight layover is realistic. None of it is hard. All of it is friction, and it interrupts whatever you were actually doing.

A travel-logistics tool absorbs that friction. You describe the trip in plain language; it returns viable options and the logistics already worked out.

## Interface

**Input:** a trip described naturally, or structured fields: origin, destination, must-arrive-by time, preferences, minimum connection buffer, and whether booking is in scope.

**Output:** a small set of ranked, viable options with the logistics resolved:

```json
{
  "options": [
    {
      "summary": "carrier-agnostic description of the itinerary",
      "depart_local": "time in origin local zone",
      "arrive_local": "time in destination local zone",
      "connection_risk": "low | medium | high, with reasoning",
      "leave_home_by": "computed, accounting for airport and buffer",
      "quote_timestamp": "when availability was checked",
      "notes": "anything that would bite you"
    }
  ],
  "timezone_delta": "hours, with direction",
  "confidence": "high | medium | low",
  "sources": ["availability or timing source category"]
}
```

**How the agent calls it:** one draft-only call with the trip description. The tool resolves availability, does the time-zone and leave-by math, scores connection risk, and returns ranked options. Booking, purchasing, cancelling, loyalty-account changes, or messages to travel providers are out of scope unless a separate approval-gated tool handles them.

## What good looks like

- Returns a short list of genuinely viable options, not a raw dump of every fare.
- Ranking reflects constraints: arrive-by time, buffer, preferences, and fatigue cost.
- Leave-by and connection-risk math is conservative.
- Time-zone math is always shown and always right.
- Availability is timestamped and stale quotes are labeled.
- Revisit trigger: leave-by estimates or connection-risk scoring prove wrong in practice.

## Failure modes

- Provider data is unavailable or stale. The tool returns partial results with clear warnings.
- Ambiguous input, such as airport or date, creates expensive risk. The tool asks one clarifying question.
- Fare or seat availability changes after the quote timestamp.
- Travel preferences leak location or absence-from-home details into a shared channel.
- The agent implies booking happened when it only drafted options.

## Privacy notes

Trip parameters and preferences may reveal where you are, when you are away, and who you may be meeting. Keep that data in your own environment. Provider credentials, loyalty numbers, payment information, and booking references never belong in the public spec.

## Approval boundaries

Drafting options is allowed. Booking, purchasing, cancelling, changing seats, using loyalty points, sending itinerary details, or messaging providers requires explicit approval and a hard action gate.

## Freshness and state

Availability and fares require real-time or near-real-time freshness. The tool should include quote timestamps, source freshness, and assumptions for airport buffers. If used for active trip tracking, it needs trip identifiers and alert state in a private store.

## Observability

Log provider/source category checked, quote timestamp, stale/partial availability warnings, connection-risk score, and whether any external action was blocked pending approval.

> Reference note: tools of this shape are sometimes called something like "flight-goat" in a personal tool belt. The name is cosmetic; the contract is the point.
