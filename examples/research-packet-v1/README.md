# Research Packet v1 Example

This is a public-safe packet fixture for the analyst researcher pattern. It is synthetic by design: the structure is real, the topic is generic, and the sources are placeholders.

Use this as a shape to copy into your own private workspace. Replace placeholders with real sources only inside your own privacy boundary.

## Packet summary

- **Question:** Can we rely on a documented product feature when community reports describe edge cases?
- **Answer:** The basic workflow appears supported, but the edge-case behavior needs a targeted test before production reliance.
- **Confidence:** likely overall; verified only for the narrower documented-workflow claim.
- **Status:** `fixture_clean`.
- **Artifact map:** source ledger, claim ledger, contradictions, brief, recommendation, handoff, manifest, and errors.

## Required files

- `README.md`: packet index and status.
- `source-ledger.jsonl`: one JSON object per source.
- `claim-ledger.jsonl`: one JSON object per material claim.
- `contradictions.md`: credible disagreements and resolution criteria.
- `brief.md`: decision-useful analyst brief.
- `recommendation.md`: recommendation, risks, alternatives, assumptions, and change triggers.
- `handoff.json`: orchestrator-owned routing metadata.
- `packet_manifest.json`: manifest and validation status.
- `errors.jsonl`: failures and blocked lookups.

## Pickup prompt

> Use this Research Packet v1 fixture as the output contract for a substantive research task. Before researching, define the source plan and privacy ceiling. During research, maintain the source ledger and claim ledger. Before final delivery, validate packet structure, conservative confidence labels, contradictions, and orchestrator-owned handoff routing.
