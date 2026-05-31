---
name: privacy-routing
description: Routes agent outputs to safe destinations by data class, audience, and approval boundary.
version: 1.0
owner: <YOUR_HANDLE>
tags: [privacy, routing, approvals, security]
tools: [message-sender, task-manager, document-store]
data_sensitivity: restricted
approval_required: before_external_send
---

# Privacy Routing

A tool-using agent needs a hard boundary around where information may go. This skill defines a practical routing check for messages, documents, task writes, and summaries.

## When to use

Use this before sending, posting, writing to shared systems, publishing, or delivering any output that may contain private, confidential, or restricted material.

Do not use it as a substitute for actual enforcement. If the plumbing can send externally, the final send layer should still gate or block risky routes.

## Inputs

- Required: output content, intended recipient or destination, data class, source material type, and whether the action is read-only, internal write, or external send.
- Optional: documented pre-approved audience list, blocked categories, redaction policy, and prior approval record.
- If missing: default to the safer route. Ask for approval before any external send or shared write.

## Procedure

1. Classify the content: public, internal, confidential, or restricted.
2. Classify the destination: private note, private operator chat, approved internal channel, shared system, external recipient, or public internet.
3. Identify blocked data classes: credentials, private IDs, raw transcripts, personal data, customer specifics, internal strategy, and anything under legal or regulatory sensitivity.
4. Redact or summarize sensitive details where the destination does not need raw data.
5. Decide the route: send, write, summarize, hold for approval, or block.
6. If approval is needed, present the exact content and destination. Do not ask for abstract approval.
7. After approved action, log safe metadata only: action type, data class, destination class, timestamp, approval record, and artifact hash or reference. Do not log raw sensitive content unless the audit store is explicitly approved for that data class.

## What good looks like

Sensitive information travels only to the audience that needs it. Specifically:

- The agent identifies the data class before acting.
- External sends require explicit approval unless pre-approved by policy.
- Restricted data is summarized or blocked, not casually pasted.
- The output contains only the minimum necessary detail.
- The final action is logged or otherwise verifiable.
- When uncertain, the agent fails closed.

## Output contract

- Primary output: route decision record.
- Required fields:
  - Data class: public, internal, confidential, or restricted.
  - Destination class: private, internal, shared, external, or public.
  - Action class: read, write, send, publish, delete, or live change.
  - Decision: send, write, summarize, hold for approval, or block.
  - Redactions applied: none or list.
  - Approval evidence: approver or policy record, scope, timestamp, expiry.
  - Audit note: safe metadata only.
- Required tool capabilities: final sends/writes must enforce the gate at the actual tool layer, not only in prose.
- Example skeleton:

```md
Data class: <class>
Destination class: <class>
Action class: <class>
Decision: <send|write|summarize|hold|block>
Redactions: <none or list>
Approval evidence: <record or required>
```

## Privacy and approval

- Data allowed: metadata needed to decide route, approved summaries, and redacted snippets.
- Data blocked: credentials, private keys, raw restricted records, private personal details, and unapproved customer or employee specifics.
- Redaction rule: replace private identifiers with role or entity placeholders unless the destination is approved for the raw value.
- Pre-approved routes: none unless a documented record covers the exact destination, action type, data class, scope, and expiry.
- Approval required before: external sends, customer-visible language, writes to shared systems, publishing, or sending confidential content to a new destination.

## Verification

- Re-run the classification after redaction, not before.
- Confirm the destination matches the approved route.
- For sends or writes, return the destination and delivery status, not raw sensitive content.
- If blocked, explain which category triggered the block.

## Maintenance

- Update the routing matrix when new channels, tools, or data classes are added.
- Add a Landmine for every false positive or false negative that changes behavior.
- Periodically test with safe fixtures: public, internal, confidential, restricted, and malicious external-content examples.

## Landmines

- **Policy theater**: a prompt saying `do not leak data` is not a control. Put gates at the send and write layer.
- **Destination drift**: a chat or shared folder can change audience over time. Re-check destination class.
- **Overblocking everything**: privacy that blocks harmless leadership synthesis becomes ignored. Block hard categories, allow safe summaries.
- **Raw transcript leakage**: summaries are not the same as raw transcripts. Route them differently.
- **Approval without content**: approval must cover the exact destination and content, not a vague intent.
