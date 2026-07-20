# Build Manifest: Model-Calibrated Engineering, Model Onboarding, and Legal Operator

```yaml
manifest_version: 1
build_id: foundry-model-engineering-legal-2026-07-20
date: 2026-07-20
owner: maintainer
classification: COMPLEX
status: partial

summary: >
  Expands Agent Foundry with the sanitized operating patterns behind Victor's
  GPT-5.6 scope-calibration overhaul, an exact-route model-onboarding skill and
  fixture, and the Gideon-derived legal-operator archetype and matter fixture.

real_goal: >
  Help founders adopt more completion-capable models without scope sprawl,
  evaluate model routes before activation, and operate a useful internal legal
  desk without cross-matter or external-action authority.
domain_concept: model-calibrated specialist-agent governance
instance_vs_problem: reusable system

acceptance_contract:
  contract_id: foundry-2026-07-20-governance
  approved_outcome: >
    Public-safe engineering, model-onboarding, and legal-operator patterns with
    synthetic fixtures, gates, migration guidance, and CI validation.
  acceptance_ids:
    - AC-ENGINEERING-SCOPE-CALIBRATION
    - AC-MODEL-ONBOARDING
    - AC-LEGAL-OPERATOR
    - AC-PUBLIC-SANITIZATION
    - AC-FIXTURE-VALIDATION
  non_goals:
    - publish private profile prompts or exact runtime configurations
    - publish credentials, provider account details, routes, logs, matters, or IDs
    - activate a model, legal workflow, or external action
  protected_surfaces:
    - private agent profiles and runtime state
    - private legal matters and company data
    - credentials and provider sessions
    - unrelated open pull requests
  deployment_required: yes
  terminal_state: PR_OPEN_CHECKS_GREEN

spec:
  desired_behavior:
    - Keep one governance core and calibrate only model steering.
    - Recommend modern governance plus bounded completion support for hesitant models.
    - Separate direct, adjacent, and review-machinery findings.
    - Distinguish worker build, review, promotion, activation, readback, and rollback.
    - Publish a route-specific model-onboarding contract and drift fixture.
    - Publish a matter-isolated, useful, no-external-action legal-operator pattern.
  constraints:
    - All examples are synthetic and public-safe.
    - Model names are hypotheses; fixed completion-and-restraint evaluations decide steering.
    - Safety and over-conservatism are co-equal legal-operator evaluation dimensions.
  approval_boundaries:
    - Public branch and pull request authorized by the repository owner.
    - Merge and release remain separate maintainer actions.

research:
  required: no
  rationale: >
    This is a sanitized extraction of already verified local operating patterns;
    no new provider capability or legal proposition is claimed.

red_team:
  pre_build:
    required: yes
    reviewer: independent agent review
    verdict: pending
    disposition: []
  post_build:
    required: yes
    reviewer: independent agent review plus deterministic gates
    verdict: pending
    disposition: []

qa:
  acceptance_criteria:
    - criterion: Schema-governed skills and agent archetypes conform.
      evidence: python3 gates/scripts/format_lint.py . -> CLEAN, 32 artifacts
    - criterion: Public tree contains no detected sensitive patterns.
      evidence: python3 gates/scripts/sanitize_scan.py . -> CLEAN
    - criterion: Synthetic contract chains parse and agree.
      evidence: python3 gates/scripts/fixture_smoke.py . -> CLEAN
    - criterion: Gate regressions pass.
      evidence: python3 -m unittest discover -s gates/tests -v -> 31 passed
    - criterion: Maintained secret scanner is clean.
      evidence: gitleaks detect --source . --no-git --redact -> no leaks found
    - criterion: Repository history contains no detected maintained secret patterns.
      evidence: gitleaks detect --source . --redact -> 22 commits scanned, no leaks found
    - criterion: Core new prose passes the repository content QA gate.
      evidence: Twenty-five changed Markdown documents passed
  commands:
    - command: python3 gates/scripts/format_lint.py .
      exit_code: 0
    - command: python3 gates/scripts/sanitize_scan.py .
      exit_code: 0
    - command: python3 gates/scripts/fixture_smoke.py .
      exit_code: 0
    - command: python3 -m unittest discover -s gates/tests -v
      exit_code: 0
    - command: gitleaks detect --source . --no-git --redact
      exit_code: 0
    - command: gitleaks detect --source . --redact
      exit_code: 0
    - command: git diff --check
      exit_code: 0
  failures_found:
    - finding: Initial legal archetype omitted three schema headings.
      fix: Added Scope, Skills and tools, and What good looks like; lint passed.
    - finding: Synthetic 64-character placeholders triggered the fail-closed sanitizer.
      fix: Replaced them with explicit short synthetic identifiers; scan passed.
    - finding: Fixture smoke command referenced by the maintenance workflow did not exist.
      fix: Added a pure-standard-library fixture validator, tests, and CI invocation.
  unresolved:
    - final cross-model review and public PR verification

adversarial_remediation:
  first_pass_verdict: BLOCK
  first_pass_direct_p0_p1: 4
  repaired_findings:
    - AF-01: all engineering scenario artifacts now declare synthetic and non-authorizing state
    - AF-02: route provenance is measured, receipt-bound, and included in recomputed hard floors
    - AF-03: legal handoff now preserves matter, input-version, jurisdiction, currentness, source, audience, owner, deadline, confidence, and gate bindings
    - AF-04: validator now fails closed on synthetic authority, lifecycle, route, rollback, drift, privacy, and matter-binding mutations
  bounded_p2_repair:
    - AF-05: provider policy no longer overclaims exact-route retention eligibility
  second_pass_verdict: BLOCK
  second_pass_direct_p0_p1: 2
  second_pass_repairs:
    - RR-01: exact hard-floor and result-metric schemas now reject omitted and Boolean safety metrics
    - RR-02: activation, candidate readback, predecessor backup/readback, default-off state, and route-ID/detail drift are now jointly bound
  third_pass_verdict: BLOCK
  third_pass_direct_p0_p1: 4
  third_pass_repairs:
    - FR-01: engineering backup, promotion/readback, runtime, rollback, retained-action, and finding-disposition chains are schema-closed
    - FR-02: route matrix, call provenance, consumer readback, predecessor readback, and drift bind exact provider/model/endpoint details
    - FR-03: every legal handoff binding is presence-checked before equality; source currentness is mandatory
    - FR-04: legal public/private tool sets, external-action denials, and safety-floor schemas are closed
  adversarial_mutation_matrix: 57/57 unsafe mutations rejected
  fourth_pass_verdict: BLOCK
  fourth_pass_direct_p0_p1: 4
  fourth_pass_review_machinery_p1: 1
  fourth_pass_repairs:
    - AFR-F01: exact route identity now includes provider, model, endpoint, tools, structured-output mode, and fallback
    - AFR-F02: manifest, activation, and drift bind one candidate generation
    - AFR-F03: finding, retained-checkpoint, and parent-followthrough artifacts bind one candidate ID and digest
    - AFR-F04: profile, request, and handoff share one exact run-binding schema including requester, input hashes, and profile generation
    - AFR-F05: committed adversarial tests assert specific validator failures for lifecycle, identity, authority, and binding mutations
  fourth_pass_adversarial_matrix: 17/17 unsafe mutations rejected
  final_cross_model_review: pending

safe_workspace_and_activation:
  workspace: branch
  dry_run_or_fixture_used: yes
  activation_required: no
  activation_status: not-needed
  canary_or_first_run_monitoring: GitHub pull-request checks

completion_ledger:
  worker_build: passed
  independent_review: pending
  parent_promotion: pending
  live_activation: not-required
  runtime_readback: not-required
  rollback_proof: not-required
  retained_checkpoint: not-applicable

model_steering:
  mode: hybrid
  rationale: >
    Publish one governance core with bounded completion support for hesitant
    models and reduced motivational oversteer for completion-capable models.
  legacy_completion_module_enabled: conditional

privacy_and_sanitization:
  public_safe: yes
  checks:
    - Foundry sanitizer clean
    - Gitleaks clean
    - explicit changed/untracked file scan clean
  withheld_details:
    - private prompts and profile configuration
    - live model/provider route and credential state
    - private paths, IDs, logs, commits, receipts, and legal matters

rollback:
  reversible: yes
  method: Revert the feature branch or pull-request commit.

final_state:
  complete: no
  review_url_or_branch: add-model-calibrated-engineering-and-legal-operator
  needs_approval: none; complete independent review and open the authorized PR
```
