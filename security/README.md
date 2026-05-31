# Security patterns

This directory contains sanitized security patterns for agentic operating systems. These are architecture references, not production code and not Darryl's live configuration.

Start here:

- [`tenant-scoped-agent-security.md`](tenant-scoped-agent-security.md) — a detailed first-principles breakdown of how to keep one agent from leaking one client's fleet or machine context to another.
- [`tenant-security-policy.example.yaml`](tenant-security-policy.example.yaml) — machine-readable example policy for tenants, users, resources, capabilities, and egress surfaces.
- [`resource-acl.schema.json`](resource-acl.schema.json) — JSON Schema for tagging resources/artifacts with tenant, classification, provenance, and allowed capabilities.
- [`egress-surface-test-matrix.example.yaml`](egress-surface-test-matrix.example.yaml) — machine-readable acceptance fixtures for cross-tenant leak prevention.

## Pickup prompt

> Review the security/ directory in The Agent Foundry. I operate or plan to operate an agent that can see multiple customers, machines, workspaces, or accounts. Tell me which parts of this tenant-scoped security model we should implement, what policy schema we need, and what tests would prove one customer cannot access another customer's resources. Ask me for missing context before implementation.
