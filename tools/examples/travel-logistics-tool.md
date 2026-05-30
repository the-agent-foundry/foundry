---
name: travel-logistics
problem: Planning and tracking travel eats time and attention I would rather spend elsewhere
stack: agnostic
maturity: spec
owner: <YOUR_HANDLE>
---

# Travel logistics tool

*A worked spec. One way to let your agent handle the friction of travel: options, timing, and the small logistics that otherwise pile up. Build your own version against your preferred providers.*

## Problem

Travel is a stack of small annoyances. Finding workable flights around a meeting, checking what time you actually need to leave, figuring out the connection risk, remembering the time-zone math, knowing whether a tight layover is realistic. None of it is hard. All of it is friction, and it interrupts whatever you were actually doing. The cost is attention, repeated every time you travel.

A travel-logistics tool absorbs that friction. You describe the trip in plain language; it returns viable options and the logistics already worked out.

## Interface

**Input:** a trip described naturally, or structured fields. For example: origin, destination, must-arrive-by time, preferences (nonstop, cabin, preferred carrier, minimum connection buffer).

**Output:** a small set of ranked, viable options with the logistics resolved:

```
{
  "options": [
    {
      "summary": "carrier-agnostic description of the itinerary",
      "depart_local": "time in origin local zone",
      "arrive_local": "time in destination local zone",
      "connection_risk": "low | medium | high, with reasoning",
      "leave_home_by": "computed, accounting for airport and buffer",
      "notes": "anything that would bite you (tight layover, overnight, etc.)"
    }
  ],
  "timezone_delta": "hours, with direction",
  "confidence": "high | medium | low",
  "sources": ["where availability/timing came from"]
}
```

**How the agent calls it:** one call with the trip description. The tool resolves availability, does the time-zone and leave-by math, scores connection risk, and returns options ranked by how well they fit the constraints.

## What good looks like

- Returns a short list of genuinely viable options, not a raw dump of every fare. Ranking reflects the stated constraints (arrive-by time, buffer, preferences).
- The leave-by and connection-risk math is correct and conservative. A tight layover is flagged honestly, not optimistically.
- Time-zone math is always shown and always right. This is the single most common manual error it should eliminate.
- It fails loud. If availability cannot be retrieved, it says so and returns what it can, rather than presenting stale or invented options.
- Revisit trigger: if leave-by estimates start being wrong in practice, the airport-buffer assumptions need re-tuning.

## Failure modes

- A provider is unavailable. The tool returns partial results with a clear note, never a fabricated itinerary.
- Ambiguous input (which airport, which date). The tool asks one clarifying question rather than guessing on something expensive to get wrong.

## Privacy notes

Trip parameters and preferences may be sensitive (where you are, when you are away). Keep that data in your own environment. Provider credentials live in your secret store, never in the spec.

> Reference note: tools of this shape are sometimes called something like "flight-goat" in a personal tool belt. The name is cosmetic; the contract is the point.
