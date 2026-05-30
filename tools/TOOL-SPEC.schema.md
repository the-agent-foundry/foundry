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

## Required sections

A conforming tool spec must contain these headings:

### Problem
The recurring annoyance, stated plainly. What do you keep doing by hand? How often? What does getting it wrong cost you? If you cannot describe the pain in two sentences, it is not a tool yet.

### Interface
The contract. What goes in, what comes out, and how the agent calls it. Describe inputs, outputs, and the shape of the response, not the implementation. Keep it stack-agnostic: an agent on any runtime should be able to read this and know what to build.

### What good looks like
The quality bar. How do you know the tool is working versus quietly degrading? Latency budget, accuracy expectations, failure behavior (fail loud, never silent), and the trigger that tells you to revisit it.

## Optional but encouraged sections

- **Failure modes** : how it breaks when nobody is looking, and what the agent should do when it does.
- **Privacy notes** : what data flows through, and where it must not go.
- **Reference implementation** : clearly labeled, e.g. "> Example (one way to do this on stack X): ...". Never required, never the only path.

## The rule

A tool spec describes a contract. The moment you implement it, secrets live in your own secret store, never here. If your draft contains a key, a token, a real endpoint, or a real path, you are writing an integration, not a spec. Strip it.
