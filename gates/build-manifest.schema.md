# Build Manifest Schema

A build manifest is the audit record for meaningful agent-system work. It turns "trust me, it is done" into a compact artifact that another human or agent can inspect later.

Use this for MODERATE and COMPLEX builds, public repo changes, recurring automations, agent profile changes, quality gates, security/privacy work, and any build where future you will care what happened.

## Required fields

```yaml
manifest_version: 1
build_id: <short human-readable id>
date: <YYYY-MM-DD>
owner: <agent or human responsible>
classification: <TRIVIAL | MODERATE | COMPLEX>
status: <complete | blocked | partial | reverted>

summary: <one paragraph describing what changed>

real_goal: <underlying need, not the implementation>
domain_concept: <real-world concept modeled by the design>
instance_vs_problem: <one-off | reusable system | conscious hybrid>

design_gate:
  real_goal: <answer to design question 1>
  domain_concept: <answer to design question 2>
  unattended_breakage: <answer to design question 3>
  instance_vs_problem: <answer to design question 4>
  required_state: <answer to design question 5>
  tradeoffs_and_proxies: <answer to design question 6>
  decision_hierarchy_call: <quality | reliability | privacy | control | cost | speed>

spec:
  desired_behavior:
    - <what the finished system must do>
  non_goals:
    - <what is intentionally out of scope>
  constraints:
    - <privacy, platform, dependency, delivery, or business constraint>
  acceptance_criteria:
    - <observable condition that proves done>
  approval_boundaries:
    - <what requires human approval>

touched_artifacts:
  - path: <repo-relative or public-safe path>
    change: <created | modified | deleted>
    purpose: <why this file changed>

approval_boundaries:
  autonomous_actions:
    - <safe action performed without approval>
  gated_actions:
    - action: <action requiring approval, or none>
      status: <not-needed | approved | pending | blocked>

research:
  required: <yes | no>
  rationale: <why research was required or not applicable>
  source_ledger:
    - url: <public URL, if any>
      source_type: <official docs | changelog | issue | forum | social | example | other>
      freshness: <date or unknown>
      quoted_signal: <short quote or summary>
      fix_or_workaround: <what others did>
      match_strength: <low | medium | high>
      implication: <what this changed in the spec>

red_team:
  pre_build:
    required: <yes | no>
    reviewer: <human | model | agent | not applicable>
    verdict: <approve | approve-with-changes | block | not-run>
    disposition:
      - id: <RT-001>
        severity: <P0 | P1 | P2 | P3>
        title: <finding title>
        disposition: <incorporated | backlogged | canaried | rejected | override-approved>
        rationale: <why>
  post_build:
    required: <yes | no>
    reviewer: <human | model | agent | not applicable>
    verdict: <approve | approve-with-changes | block | not-run>
    disposition:
      - id: <QA-RT-001>
        severity: <P0 | P1 | P2 | P3>
        title: <finding title>
        disposition: <incorporated | backlogged | canaried | rejected | override-approved>
        rationale: <why>

qa:
  acceptance_criteria:
    - criterion: <what had to be true>
      evidence: <command, file, artifact, or reviewer proof>
  commands:
    - command: <exact command>
      exit_code: <integer>
      notes: <what it proved>
  surface_coverage:
    - surface: <user command | scheduled job | egress | state write | retry | failure notice | other>
      risk: <what could go wrong on this surface>
      check: <test, dry-run, inspection, or rationale>
      evidence: <command/output/artifact>
      result: <pass | fail | not-applicable>
      out_of_scope_rationale: <null or explanation>
  failures_found:
    - finding: <what failed during QA, or none>
      fix: <how it was fixed>
  unresolved:
    - <remaining issue, or none>

safe_workspace_and_activation:
  workspace: <branch | fork | sandbox | local fixture | production>
  dry_run_or_fixture_used: <yes | no | not-applicable>
  activation_required: <yes | no>
  activation_status: <not-needed | pending | approved | complete | blocked>
  canary_or_first_run_monitoring: <plan or not-applicable>

privacy_and_sanitization:
  public_safe: <yes | no>
  checks:
    - <sanitization scan, manual redaction review, or other proof>
  withheld_details:
    - <category withheld, e.g. live paths, credentials, private IDs>

rollback:
  reversible: <yes | no>
  method: <how to revert or disable>

final_state:
  complete: <yes | no>
  review_url_or_branch: <public branch, PR, or local branch>
  needs_approval: <none, or exact gated action>
```

## Rules

- Keep paths public-safe. Use repo-relative paths, not private machine paths.
- Do not include secrets, chat IDs, customer names, raw logs, private prompts, or private memory.
- Link to sanitized artifacts, not private run directories.
- Preserve all six design-gate answers for MODERATE and COMPLEX work.
- If research was skipped, explain why.
- If red-team was skipped, explain why.
- If QA was partial, mark the build `partial` and state what remains.
- If a reviewer blocks, classify the finding by P0/P1/P2/P3 and record the disposition.
- Structured fields are the authority. Free-form prose is not a hard gate.

## Minimal manifest for small work

TRIVIAL work can use a compressed version:

```yaml
manifest_version: 1
classification: TRIVIAL
summary: <what changed>
touched_artifacts: [<paths>]
qa:
  commands: [<checks>]
final_state:
  complete: yes
  needs_approval: none
```
