# Example: Victor-Style Build Manifest

This is a sanitized example. It shows the shape of a serious engineering closeout without exposing private config, internal paths, customer data, credentials, or raw logs.

```yaml
manifest_version: 1
build_id: public-docs-victor-system-001
date: 2026-05-30
owner: engineer-agent
classification: MODERATE
status: complete

summary: >
  Expanded the public engineer archetype from a lightweight role description into a reusable engineering operating system with classification, research, design gate, pre-build red-team, QA gate, and build manifest.

real_goal: Make the public repository useful enough for another founder's agent to adapt the engineering discipline, not just admire a sanitized story.
domain_concept: Engineering quality system for agent-built work.
instance_vs_problem: Reusable system. The pattern should apply to future tools, skills, gates, agents, and automations.

design_gate:
  real_goal: Preserve the real operating pattern behind serious agent engineering without exposing private implementation details.
  domain_concept: A repeatable quality system for agent-built work.
  unattended_breakage: Public docs become shallow, examples drift from schemas, and future contributors skip proof because the repo only describes the idea.
  instance_vs_problem: Reusable system. This pass upgrades Victor first, then the same depth can be staged for other agents, tools, and skills.
  required_state: Repo docs need schemas, examples, links, CI checks, and reviewable manifests. No runtime state is needed for this documentation pass.
  tradeoffs_and_proxies: The repo publishes process patterns rather than live config. Revisit if technical founders cannot adapt the pattern without private details.
  decision_hierarchy_call: quality

spec:
  desired_behavior:
    - Engineer archetype explains classification, research, red-team, QA, manifest, and approval boundaries.
    - Gates folder includes reusable red-team, research, QA, and manifest documents.
    - Public example manifest is copy-paste-valid and schema-consistent.
  non_goals:
    - Publish private prompts, live paths, credentials, internal logs, or customer data.
    - Clone the private runtime.
  constraints:
    - Keep content framework-agnostic.
    - Keep all paths public-safe and repo-relative.
    - Maintain existing repository lint and sanitization checks.
  acceptance_criteria:
    - Format lint passes.
    - Sanitization scan passes.
    - Content QA passes on changed markdown files.
    - Fenced manifest example parses as YAML.
  approval_boundaries:
    - Founder review before merge to main.

touched_artifacts:
  - path: agents/archetypes/engineer.md
    change: modified
    purpose: Add classification, research, red-team, QA, manifest, safe-workspace, and approval doctrine.
  - path: gates/red-team-gate.md
    change: created
    purpose: Document pre-build and post-build adversarial review.
  - path: gates/research-gate.md
    change: created
    purpose: Document research requirements and source ledger.
  - path: gates/qa-gate.md
    change: created
    purpose: Define proof standards and surface inventory before shipping.
  - path: gates/build-manifest.schema.md
    change: created
    purpose: Give every serious build a repeatable audit record.

approval_boundaries:
  autonomous_actions:
    - Edited documentation in a safe branch.
    - Ran local lint, sanitization, content QA, and YAML checks.
  gated_actions:
    - action: Merge to main or publish externally.
      status: pending

research:
  required: no
  rationale: This was a local documentation codification pass, not an external platform, SDK, provider, API, or dependency issue.
  source_ledger: []

red_team:
  pre_build:
    required: yes
    reviewer: agent
    verdict: approve-with-changes
    disposition:
      - id: RT-001
        severity: P1
        title: Public artifact was too shallow to support adoption.
        disposition: incorporated
        rationale: Added deeper doctrine and gates while keeping implementation details sanitized.
      - id: RT-002
        severity: P2
        title: Future agents, tools, and skills need the same treatment.
        disposition: backlogged
        rationale: Victor is the first pass. Other archetypes should be upgraded in staged follow-up PRs.
  post_build:
    required: yes
    reviewer: agent
    verdict: approve-with-changes
    disposition:
      - id: QA-RT-001
        severity: P1
        title: Example manifest YAML was not parseable.
        disposition: incorporated
        rationale: Quoted or block-formatted scalars and verified fenced YAML parsing.
      - id: QA-RT-002
        severity: P2
        title: Manifest schema needed full design-gate and surface-coverage fields.
        disposition: incorporated
        rationale: Added structured design_gate, spec, post_build red-team, and surface_coverage sections.

qa:
  acceptance_criteria:
    - criterion: Public docs contain no private paths, credentials, or internal IDs.
      evidence: Sanitization scan passed.
    - criterion: Agent archetype still matches the repository schema.
      evidence: Format lint passed.
    - criterion: Manifest example is valid YAML.
      evidence: Fenced YAML parser passed.
  commands:
    - command: python3 gates/scripts/sanitize_scan.py .
      exit_code: 0
      notes: No high-signal sensitive patterns detected.
    - command: python3 gates/scripts/format_lint.py .
      exit_code: 0
      notes: Schema-governed artifacts conform.
    - command: python3 gates/content-qa-gate.py agents/archetypes/engineer.md
      exit_code: 0
      notes: Content QA was also run on each changed markdown file.
  surface_coverage:
    - surface: public markdown docs
      risk: Private implementation detail leaks into public repo.
      check: Sanitization scan plus manual redaction review.
      evidence: scan exit code 0
      result: pass
      out_of_scope_rationale: null
    - surface: agent archetype schema
      risk: Updated engineer archetype no longer conforms to repo format.
      check: Format linter.
      evidence: format_lint exit code 0
      result: pass
      out_of_scope_rationale: null
    - surface: example manifest
      risk: Example cannot be copied or parsed.
      check: Parse fenced YAML block.
      evidence: parser exit code 0
      result: pass
      out_of_scope_rationale: null
  failures_found:
    - finding: Example YAML initially failed because of an unquoted colon in a plain scalar.
      fix: Converted summary to a folded block scalar and reran YAML parsing.
  unresolved:
    - Other specialist archetypes still need deeper operating doctrine.

safe_workspace_and_activation:
  workspace: branch
  dry_run_or_fixture_used: not-applicable
  activation_required: yes
  activation_status: pending
  canary_or_first_run_monitoring: Founder review of branch before merge.

privacy_and_sanitization:
  public_safe: yes
  checks:
    - Automated sanitization scan.
    - Manual redaction review for live paths, credentials, private IDs, and customer names.
  withheld_details:
    - Live profile configs.
    - Private prompts and memory.
    - Internal run directories and logs.
    - Customer and account names.
    - Credential and provider configuration.

rollback:
  reversible: yes
  method: Revert the documentation commit or close the branch without merging.

final_state:
  complete: yes
  review_url_or_branch: enhance-victor-engineering-system
  needs_approval: Founder review before merge.
```

## Pickup prompt

> Review this manifest and compare it to our current engineering workflow. Where are we relying on self-report instead of proof? Which gates should we implement first?
