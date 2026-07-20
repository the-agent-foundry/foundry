# Legal Operator v1: Synthetic Fixture

This fixture packages a safe starting point for an internal legal operator / executive counsel desk. It is AI software, not licensed counsel and not an external-action agent.

Pair it with `../../agents/archetypes/legal-operator.md`, the sanitized Gideon operating pattern.

## Files

- `profile.example.json`: generic role, modes, tools, and approval boundaries in a standard-library-parseable format.
- `matter-request.json`: synthetic one-matter request with hashed inputs.
- `matter-handoff.json`: synthetic useful output with an exact unresolved gate.
- `eval-matrix.json`: safety and over-conservatism cases that must both pass.

## Safety posture

- One run, one matter, one audience.
- Direct entry has no matter authority.
- Public research receives sanitized abstractions only.
- Private mode has no network tools.
- External communication, filing, signing, commitment, evidence deletion, and hold release are absent.
- The profile still answers first, recommends a position, and finishes unaffected lanes.
- The handoff preserves run, matter, input version, jurisdiction, as-of date, audience, owner/deadline, source pinpoints, confidence, and gate state.

## Pickup prompt

> Adapt this fixture to our legal workflow. Ask for jurisdictions, matter classes, approved sources, playbooks, privacy terms, document systems, and approval owners. Keep public and private modes separate, and do not connect real matters until the evaluation matrix passes.
