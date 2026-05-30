# The Approval Gate

Human approval before any external action. This is the pattern that keeps an autonomous agent from doing something irreversible on your behalf before you have seen it.

It is a hard gate. It does not ask the model to be careful. It blocks the action at the boundary and requires an explicit human yes.

## When the gate fires

Any action that leaves the building or changes a source of truth requires approval. Concretely, the agent may draft, analyze, reconcile, summarize, research, and recommend freely. It must stop and ask before it does any of the following:

- Sends an external message on your behalf (email, chat, social, customer or vendor contact).
- Changes a production system, a source-of-truth record, prices, automations, or configuration.
- Spends money or commits you to anything.
- Publishes public content.
- Touches credentials, model routing, or gateway services.

The line is simple: internal and reversible can be autonomous. External or irreversible needs a human.

## How the gate works

1. The agent prepares the action fully: the exact message, the exact record change, the exact spend. No vague "I will email them." It shows the artifact.
2. The agent presents it for approval with enough context to judge: what, to whom, why, and what happens on yes.
3. The gate blocks until an explicitly approved human responds.
4. On approval, the action proceeds and is logged. On rejection or silence, nothing happens.

The gate lives at the action layer, not in the prompt. The model cannot approve its own action by reasoning that it is probably fine.

## Why it has to be a hard gate

Approval-by-good-behavior is policy theater. If the only thing stopping a bad send is an instruction telling the model to be careful, then a clever bit of injected content or a confident hallucination can talk it past the rule. The control has to be structural: the send function itself checks for approval and refuses without it.

## Design checklist

- [ ] The set of actions requiring approval is explicit and enumerated.
- [ ] The agent presents the fully-formed artifact, not a description of intent.
- [ ] The gate blocks at the action layer and fails closed (no approval means no action).
- [ ] Approvals come only from explicitly whitelisted humans.
- [ ] Every approved action is logged with who approved it and when.

> Reference implementation (one way to do this): route every outbound send through a single function that checks an approval flag tied to a whitelisted user, and refuses to execute without it. The model never gets to bypass it because there is no other path to send.
