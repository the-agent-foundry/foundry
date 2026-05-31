# TOOL-SPEC schema

*The canonical shape for describing a tool in The Agent Foundry. Copy this structure. A conforming tool spec is a spec, not an implementation: it describes the contract and the quality bar, never live credentials or code that leaks secrets.*

A valid tool spec has a YAML frontmatter block with at least the required keys, and a body that contains at least the required sections. The format linter checks for these.

## Required frontmatter keys

```yaml
---
name: short-tool-name              # required. lowercase, hyphens
problem: one line on what it kills  # required. the recurring annoyance
stack: agnostic                     # optional. agnostic | or name a reference stack
maturity: spec                      # optional. spec | prototype | production
owner: <YOUR_HANDLE>                # optional. who maintains this spec
---
```

## Optional frontmatter keys worth adding

These are not required by the linter, but they make tool specs safer and easier for another agent to implement without wandering into trouble.

```yaml
data_sensitivity: public | internal | private | regulated
action_class: read-only | draft-only | internal-write | external-write
approval_required: never | before-write | before-external-action | always
source_of_truth: none | read-only | writes-with-approval
freshness_requirement: real-time | daily | weekly | on-demand | none
audit_log: required | recommended | not-needed
```

Use these when the tool touches private memory, calendar, email, company data, task systems, money, credentials, publishing, or customer-visible communication.

## Required sections

A conforming tool spec must contain these headings:

### Problem
The recurring annoyance, stated plainly. What do you keep doing by hand? How often? What does getting it wrong cost you? If you cannot describe the pain in two sentences, it is not a tool yet.

### Interface
The contract. What goes in, what comes out, and how the agent calls it. Describe inputs, outputs, and the shape of the response, not the implementation. Keep it stack-agnostic: an agent on any runtime should be able to read this and know what to build.

### What good looks like
The quality bar. How do you know the tool is working versus quietly degrading? Latency budget, accuracy expectations, failure behavior, and the trigger that tells you to revisit it.

### Failure modes
How it breaks when nobody is looking, and what the agent should do when it does.

### Privacy notes
What data flows through, where it must not go, and the maximum audience for the output.

### Approval boundaries
What the tool may do on its own, what it may only draft, and what requires explicit human approval.

### Freshness and state
What sources must be fresh, what high-water marks or dedupe state exist, and how stale inputs are labeled.

### Observability
What gets logged, what should alert, and how an operator can prove the tool ran correctly.

## Optional but encouraged sections

- **Reference implementation** : clearly labeled, e.g. "> Example (one way to do this on stack X): ...". Never required, never the only path.

## Safety rules

A tool spec describes a contract. The moment you implement it, secrets live in your own secret store, never here.

Do not include:

- live credentials, tokens, keys, passwords, or session cookies
- private endpoints, hostnames, database names, bucket names, workspace IDs, calendar IDs, CRM IDs, or chat IDs
- real customer, investor, employee, patient, or vendor records
- personal emails, phone numbers, addresses, or private relationship notes
- raw logs, transcripts, screenshots, inbox exports, or calendar dumps
- private URLs, query strings, filenames, branch names, commit messages, git remotes, document metadata, EXIF/PDF metadata, vector-store IDs, embedding IDs, or other identifiers that reveal private systems, people, companies, or relationships
- exact internal file paths or machine-specific runtime paths

Allowed: synthetic examples, placeholder handles, public-safe source categories, and interface contracts.

If your draft contains a key, a token, a real endpoint, a real path, or source data that belongs to an actual person or company relationship, you are writing an integration, not a spec. Strip it.

## Build-order rule

Tools should usually graduate in this order:

1. **Read-only** : retrieve, summarize, classify, and cite.
2. **Draft-only** : prepare an action packet for a human.
3. **Internal-write** : write to a low-risk internal system with dedupe, logging, and rollback.
4. **External-write** : send, publish, purchase, message, or mutate a customer-visible system only behind a hard approval gate.

The more a tool can affect the outside world, the less you should trust prompt discipline. Put the enforcement in the plumbing.
