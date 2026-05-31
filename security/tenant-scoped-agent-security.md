# Tenant-Scoped Agent Security

*How to keep one agent from leaking another client's fleet.*

This is a sanitized, public architecture note. It is not Darryl's live runtime, not a dump of private policy files, and not a promise that any specific framework implements this out of the box.

## The problem

A single agent may know about many clients, machines, workspaces, repositories, tickets, logs, or credentials. That is useful until Client A asks a normal question and the agent answers using context from Client B.

The failure usually does **not** look like a Hollywood breach. It looks like ordinary helpfulness:

- "Here are all failing machines" when the requester should see only their tenant.
- A summary that includes another client's hostname, alert, ticket, or operator note.
- A tool query that returns mixed-tenant rows and hands them to the model.
- A generated file/report with hidden cross-tenant rows.
- An error message that leaks a private path, secret label, internal machine name, or support note.

The security boundary cannot be "the prompt told the agent to be careful." Prompt instructions are useful for behavior, but they are not an authorization layer. The guard has to live in the plumbing.

## Core mental model

Treat every answer, tool call, retrieval, file, and status update as an authorization problem.

```text
requester + tenant + resource + capability + surface -> decision
```

Where:

- **Requester**: the human, bot, service account, or profile asking.
- **Tenant**: the client/account/workspace that owns the resource.
- **Resource**: machine, repo, ticket, log, document, credential, report, artifact, memory, or conversation.
- **Capability**: read status, read logs, summarize, restart, SSH, mutate config, send file, disclose secret, etc.
- **Surface**: retrieval, tool call, model context, generated artifact, final answer, attachment, error notice, audit log.
- **Decision**: allow, allow with redaction, hold for approval, block, or delivery-fail.

If your system cannot name those fields for a request, it cannot reliably enforce tenant isolation.

## The transferable lesson from Telegram-style routing

Telegram routing work starts with users, chats, topics, content categories, and egress surfaces. A fleet-support agent should use the same pattern with different nouns:

- Telegram requester -> fleet requester
- chat/topic -> tenant/channel/session
- content category -> resource classification
- attachment -> report/log/artifact
- visible send -> answer, file, tool result, status update

The key insight is route-first and surface-aware:

1. Identify who is asking.
2. Identify where the answer will go.
3. Identify what resources/facts were used.
4. Decide whether that exact answer/action is authorized for that exact requester and route.
5. Record safe metadata about the decision.

## Architecture layers

### 1. Ingress authentication: who is asking?

Authenticate the requester before the model sees the request.

Minimum fields:

```yaml
subject:
  id: "user_support_alex"
  type: "human"
  display_name: "Alex Example"
  tenants: ["tenant_alpha"]
  roles: ["support_viewer"]
  auth_source: "telegram_allowlist_or_sso"
```

Do not rely on display names. Use stable platform IDs, SSO subject IDs, or verified account mappings. Display names are labels, not authority.

### 2. Tenant/resource registry: what exists and who owns it?

Every machine/resource needs an ownership record.

```yaml
resource:
  id: "machine_alpha_web_01"
  tenant: "tenant_alpha"
  type: "machine"
  classification: "confidential"
  allowed_capabilities:
    support_viewer: ["read_status", "read_sanitized_logs"]
    support_operator: ["read_status", "read_sanitized_logs", "restart_service"]
    admin: ["*"]
```

Unknown resource should not default to "global." It should hold or fail loudly until ownership is known.

### 3. Retrieval guard: what context may the model see?

The safest place to enforce tenant isolation is before retrieved data enters the model context.

Bad pattern:

```text
retrieve all relevant machine notes -> ask the model to ignore unauthorized ones
```

Good pattern:

```text
resolve requester -> resolve authorized tenant/resource set -> retrieve only matching data -> attach provenance -> model answers
```

Every retrieved memory/document/log chunk should carry provenance:

```yaml
provenance:
  tenant: "tenant_alpha"
  resource_ids: ["machine_alpha_web_01"]
  source_type: "log_excerpt"
  source_id: "log_alpha_web_01_2026_05_31_1200Z"
  classification: "confidential"
```

### 4. Tool guard: what actions may tools take?

Tool calls must enforce policy at dispatch time. The model should not be able to smuggle a cross-tenant action through a clever prompt.

Every tool call should include or derive:

```yaml
tool_request:
  subject_id: "user_support_alex"
  tenant: "tenant_alpha"
  resource_id: "machine_alpha_web_01"
  capability: "read_sanitized_logs"
  reason: "User requested recent error summary"
```

The tool wrapper checks authorization before network/disk/SSH/API access. If a backend query can return mixed-tenant data, filter before the model sees the result and assert that no returned row violates the authorized tenant/resource set.

### 5. Model context guard: what facts were assembled?

Before the final prompt is built, validate the assembled context bundle.

Required invariant:

> Every context item visible to the model must be authorized for the requester, route, and requested task.

If a context item lacks tenant/resource provenance, either classify it, redact it, or hold. Unprovenanceable context becomes a leak vector.

### 6. Artifact guard: what files/reports were generated?

Generated files are egress too. A clean message caption does not make a dirty attachment safe.

For every generated artifact, write a sidecar record:

```yaml
artifact:
  path: "reports/tenant_alpha/status-summary.md"
  sha256: "example_only_not_a_real_hash"
  tenant_scope: ["tenant_alpha"]
  resources: ["machine_alpha_web_01", "machine_alpha_worker_02"]
  classification: "confidential"
  generated_from:
    - source_id: "log_alpha_web_01_2026_05_31_1200Z"
      tenant: "tenant_alpha"
  allowed_recipients: ["tenant_alpha:support_viewer", "tenant_alpha:support_operator"]
```

Final delivery should inspect the artifact sidecar. If the sidecar is missing, stale, or broader than the recipient's authority, hold instead of sending.

### 7. Egress guard: what can be sent back?

Final answers, edits, status messages, error notices, attachments, and retry fallbacks are all egress surfaces.

The final answer should be checked against:

- requester authority
- destination/route trust level
- tenant scope of retrieved context
- tenant scope of tool results
- tenant scope of attached artifacts
- hard-denial categories such as secrets, raw credentials, private keys, cross-tenant resource names, private notes, and unapproved logs

This is the part teams often miss. They guard the tool call, then leak in the helpful final summary.

### 8. Receipts and audits: what happened?

Audit logs should record decision metadata, not raw sensitive payloads.

Good audit record:

```yaml
decision:
  id: "decision_2026_05_31_001"
  subject_id: "user_support_alex"
  tenant_scope: ["tenant_alpha"]
  resource_scope: ["machine_alpha_web_01"]
  capability: "read_sanitized_logs"
  surface: "final_answer"
  decision: "allow"
  reason_codes: ["subject_tenant_match", "resource_acl_allows_capability", "no_cross_tenant_context"]
  payload_hash: "example_only"
```

Bad audit record:

```text
Full prompt, raw logs, raw credentials, private machine names, and whole final answer dumped into a shared log.
```

## Policy decision pseudocode

```python
def authorize(subject, tenant, resource, capability, surface, context_items=None, artifacts=None):
    if subject is None or not subject.authenticated:
        return block("unknown_subject")

    if tenant not in subject.tenants:
        return block("subject_not_in_tenant")

    # Broad/list requests must first resolve the authorized resource set. Do not
    # let "all machines" mean "all machines the backend knows about".
    if resource is None and requires_resource_scope(capability):
        authorized_resources = resolve_authorized_resources(subject, tenant, capability)
        if not authorized_resources:
            return hold("no_authorized_resource_scope")

    if resource and resource.tenant != tenant:
        return block("resource_tenant_mismatch")

    if resource and not resource.allows(subject.roles, capability):
        return block("capability_denied")

    for item in context_items or []:
        if item.tenant != tenant:
            return block("cross_tenant_context")
        if not item.provenance:
            return hold("missing_context_provenance")

    for artifact in artifacts or []:
        if tenant not in artifact.tenant_scope:
            return block("cross_tenant_artifact")
        if artifact.classification_requires_approval and not artifact.approval:
            return hold("artifact_requires_approval")

    if surface in {"final_answer", "attachment", "error_notice"}:
        if contains_secret_or_cross_tenant_identifier():
            return block("egress_sensitive_content")

    return allow("authorized")
```

## Egress surface matrix

A real system should test every surface that can show a user information.

| Surface | Risk | Required guard |
|---|---|---|
| Retrieval/RAG context | Model sees unauthorized facts before answer | Pre-model tenant/resource filter |
| Tool call | Model triggers unauthorized machine action | Tool-dispatch authorization |
| Tool result | Backend returns mixed-tenant rows | Post-result assertion before model context |
| Final answer | Summary leaks another client | Final egress check |
| Attachment/report | File includes hidden cross-tenant data | Artifact sidecar + content/metadata check |
| Status/progress update | "Checking machine_beta" leaks target | Safe status templates scoped to tenant |
| Error notice | Stack/path/resource leak | Scrubbed operational notice |
| Retry/fallback path | Bypasses normal guard | Same guard at every send path |
| Admin/debug mode | Permanent god-mode leaks | Explicit, scoped, expiring override with audit |

## Acceptance test matrix

At minimum, build fixtures that prove:

1. Client A can read Client A machine status.
2. Client A cannot read Client B machine status.
3. Client A cannot ask for "all machines" and receive Client B resources.
4. Client A cannot receive a generated report containing Client B rows.
5. A mixed-tenant backend response is blocked before model context assembly.
6. A missing resource ACL holds loudly instead of defaulting to allow.
7. A final answer that mentions unauthorized machine names is blocked or redacted.
8. Error messages do not leak private paths, tokens, hostnames, or cross-tenant IDs.
9. Admin override requires explicit scope, expiry, actor, and reason.
10. Audit records contain hashes and reason codes, not raw sensitive payloads.

See [`egress-surface-test-matrix.example.yaml`](egress-surface-test-matrix.example.yaml) for a machine-readable starting point.

## Telegram bot/security notes

Telegram is often the transport layer for these systems, but Telegram chat allowlists are not enough. Transport authorization says who can talk to the bot. Tenant authorization says what the bot may reveal or do.

Public best-practice notes:

- Treat bot tokens as production secrets. Never paste them into issues, logs, prompts, screenshots, or public repos.
- Use one active delivery mode per bot. Telegram's Bot API notes that `getUpdates` will not work while an outgoing webhook is set; operationally, avoid running multiple pollers/webhooks for the same token.
- If using webhooks, use Telegram's `secret_token` / `X-Telegram-Bot-Api-Secret-Token` verification header and verify it before processing updates.
- When moving a bot between servers, use the Bot API lifecycle methods intentionally (`deleteWebhook`, `logOut`, `close`) rather than letting two runtimes fight over the same token.
- Scope users/chats/topics as transport controls, but do not confuse them with data authorization.
- Group topics are routes, not security principals. A topic ID does not prove the requester may see a machine.
- Redact logs. Telegram update payloads can include usernames, display names, message text, attachments, and metadata.
- Build retry/fallback sends through the same egress guard. Emergency fallbacks are exactly where accidental leaks happen.

Useful public references:

- Telegram Bot API: https://core.telegram.org/bots/api
- Telegram Bots FAQ: https://core.telegram.org/bots/faq
- OWASP LLM Prompt Injection Prevention Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html
- OWASP LLM01 Prompt Injection: https://genai.owasp.org/llmrisk/llm01-prompt-injection/

## Common bad patterns

### Prompt-only firewall

> "The system prompt says never reveal Client B."

Useful instruction. Not a boundary. Enforce before retrieval, before tool dispatch, before final answer, and before attachment delivery.

### Global admin context by default

The agent runs with god-mode and promises to self-filter. That is convenient until a prompt injection or summary bug turns god-mode into a leak.

### Mixed-tenant retrieval then redaction

If unauthorized facts enter context, you are relying on the model to forget them. Filter before context assembly.

### Tool success treated as answer safety

A tool call can be authorized but the final answer can still leak. Guard both.

### Attachments as an afterthought

Generated files are often worse than chat text: more rows, more metadata, less scrutiny. Treat every file as an egress event.

### Silent blocks

A silent block creates operational confusion and people route around the system. Prefer a safe receipt: "I can't provide that from this route; ask from an authorized account or narrow the resource." Do not include the private details in the receipt.

## Design Principles Check

### Real goal
Help builders operate one useful agent across multiple customers/resources without leaking one tenant's machine context to another.

### Domain concept
Tenant-scoped authorization over agent memory, retrieval, tools, artifacts, and egress. This is not merely Telegram access control.

### Unattended breakage
New tenants, machines, routes, tools, file formats, and fallback paths appear over time. If they do not enter the registry and test matrix, they can silently bypass the policy or get blocked in ways operators route around.

### Instance vs problem
This solves the class: "one agent, many tenants/resources." The examples use fake machines and fake tenants so the pattern can be adapted safely.

### Required state
Tenant registry, subject registry, resource ACLs, provenance on context/tool results/artifacts, egress decision logs, and recurring tests over all visible surfaces.

### Tradeoffs / proxies
Classification and secret detection are proxies. They should supplement deterministic tenant/resource authorization, not replace it.

### Decision hierarchy call
Privacy and reliability drive the design. A privacy guard that silently breaks useful operations will be bypassed; a reliable agent that leaks cross-tenant data is unacceptable. The answer is deterministic gates plus clear receipts and tests.

## Pickup prompt

> I operate an agent that can access multiple clients, machines, or workspaces. Read this tenant-scoped security model plus the example YAML/schema files. Build me a proposed authorization design for my stack: subject registry, tenant/resource ACLs, retrieval filtering, tool dispatch guards, artifact sidecars, egress checks, audit records, and an acceptance test matrix. Ask for missing context before implementation. Do not rely on prompt instructions as the security boundary.
