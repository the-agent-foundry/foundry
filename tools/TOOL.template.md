---
name: <tool-name>
problem: <one line describing the recurring annoyance this tool kills>
stack: agnostic
maturity: spec
owner: <YOUR_HANDLE>
data_sensitivity: <public | internal | private | regulated>
action_class: <read-only | draft-only | internal-write | external-write>
approval_required: <never | before-write | before-external-action | always>
source_of_truth: read-only
freshness_requirement: on-demand
audit_log: recommended
---

# <Tool name>

*One sentence on what this tool does and why it belongs in the tool belt.*

## Problem

What manual loop does this remove? How often does it happen? What does getting it wrong cost?

## Interface

**Input:** describe the input shape. Keep it implementation-neutral.

**Output:** describe the output contract. Include confidence, provenance, and uncertainty where appropriate.

```json
{
  "result": "structured output shape",
  "confidence": "high | medium | low",
  "sources": ["source category, not private source record"],
  "warnings": ["missing context or degraded source notes"]
}
```

**How the agent calls it:** describe when the agent should invoke the tool and what it must do with the result.

## What good looks like

- The tool kills the recurring annoyance without creating a new review burden.
- The output is short, structured, and useful for a decision or next action.
- Every material claim has provenance or an uncertainty label.
- Source outages, stale data, and ambiguity are visible.
- Revisit trigger: describe the signal that says this tool needs tuning.

## Failure modes

- Ambiguous input.
- Stale or missing source data.
- Duplicate or conflicting records.
- Overconfident inference from weak evidence.
- Silent failure that makes the founder believe the task was handled when it was not.

## Privacy notes

State what sensitive data may flow through the tool, the maximum safe audience for output, and what must never be logged, sent, or published.

## Approval boundaries

- Read-only behavior allowed without approval.
- Draft-only behavior allowed without external side effects.
- Writes require explicit approval unless the workflow has been separately promoted and tested.
- External sends, purchases, publishing, source-of-truth changes, and credential operations require hard approval gates.

## Freshness and state

Name the source freshness requirement, dedupe keys, high-water marks, retry state, or reason the tool can be stateless.

## Observability

Describe the audit log, success marker, failure alert, and proof artifact an operator can inspect.

## Reference implementation notes

> Example only: describe categories of sources and implementation choices. Do not include credentials, endpoints, private IDs, or machine paths.
