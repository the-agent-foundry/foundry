# Build Manifest: Robust Sanitized Finance Control

```yaml
manifest_version: 1
build_id: foundry-finance-control-2026-07-27
date: 2026-07-27
owner: maintainer
classification: COMPLEX
status: candidate-ready-for-independent-review

summary: >
  Strengthens the generic finance-control archetype and adds a complete synthetic
  operating package with a digest-bound mission envelope, source provenance,
  claim-scoped precedence, complete Class B approval packets, actionable blockers,
  timestamped mutation receipts, readback, undo, closeout, and validation contracts.

real_goal: >
  Let another founder adapt a useful finance-cleanup specialist without copying a
  private profile or granting money, payroll, tax, legal, external-send, or
  irreversible source-of-truth authority.
domain_concept: evidence-backed finance control
instance_vs_problem: reusable public operating pattern

acceptance_contract:
  contract_id: foundry-finance-control-v1
  base_commit: b63b38d
  approved_outcome: >
    Publish a robust generic finance-control archetype, synthetic mixed-mission
    fixture, closed validator, adversarial tests, discoverability, and release notes.
  acceptance_ids:
    - FC-ARCHETYPE
    - FC-SYNTHETIC-PACKAGE
    - FC-AUTHORITY-CLOSURE
    - FC-EVIDENCE-CLOSURE
    - FC-MUTATION-READBACK-UNDO
    - FC-ADVERSARIAL-VALIDATION
    - FC-PUBLIC-SANITIZATION
  non_goals:
    - publish a named private profile or named archetype
    - publish personal-finance workflows or classification data
    - publish live accounting details, credentials, routes, identities, amounts, or runtime state
    - connect a live finance system or execute a real write
    - commit, push, open, merge, or release from the isolated builder lane
  deployment_required: no
  publication_target_state: PR_OPEN_CHECKS_GREEN
  builder_terminal_state: BUILT_LOCAL_QA_PASSED

safety_contract:
  class_a: concrete pre-bound action-layer write grant
  class_b: complete preview/impact/rollback/owner packet plus exact closed-schema receipt
  class_c: capability absent and not approval-unlockable
  mission_envelope: closed roles, exact entity/book/period/system, versioned inputs, safe destinations, required closeout
  evidence: authorized source version/digest/as-of/validity/pinpoints plus claim-scoped precedence resolution; unmarked value disagreements force contested state
  blockers: concrete reason/evidence/owner/human action and deterministic recovery
  mutation_receipt: timestamped write-time precondition, explicit readback method, rollback/undo binding
  direct_entry_write_authority: false
  evidence_instruction_authority: false
  open_output_schemas: rejected
  cross_scope_writes: rejected
  duplicate_operation_effect: idempotent_noop
  honest_pending_closeout: PARTIAL_VERIFIED

synthetic_fixture_result:
  terminal_state: PARTIAL_VERIFIED
  executed_writes: 1
  already_satisfied_noops: 1
  idempotent_replay_noops: 1
  awaiting_class_b_approval: 1
  blocked_or_unresolved: 8
  external_sends: 0
  money_movements: 0
  class_c_executions: 0
  adjacent_class_a_completed: true
  undo_rehearsal: passed
  live_system_affected: false

changed_path_inventory:
  archetype_and_indexes:
    - agents/archetypes/finance-control.md
    - agents/README.md
    - examples/README.md
    - gates/README.md
    - README.md
  fixture:
    - examples/finance-control-v1/README.md
    - examples/finance-control-v1/profile.example.json
    - examples/finance-control-v1/mission-request.json
    - examples/finance-control-v1/evidence-ledger.jsonl
    - examples/finance-control-v1/before-snapshot.json
    - examples/finance-control-v1/action-candidates.jsonl
    - examples/finance-control-v1/approval-packets.jsonl
    - examples/finance-control-v1/blocker-ledger.jsonl
    - examples/finance-control-v1/mutation-ledger.jsonl
    - examples/finance-control-v1/after-snapshot.json
    - examples/finance-control-v1/undo-receipt.json
    - examples/finance-control-v1/mission-closeout.json
    - examples/finance-control-v1/eval-cases.jsonl
    - examples/finance-control-v1/eval-matrix.json
  validation_and_tests:
    - gates/scripts/fixture_smoke.py
    - gates/scripts/sanitize_scan.py
    - gates/tests/test_finance_fixture.py
    - gates/tests/test_finance_adversarial_matrix.py
    - gates/tests/test_sanitize_scan.py
  release_surfaces:
    - CHANGELOG.md
    - MIGRATION.md
    - docs/updates/2026-07-27.md
    - docs/updates/2026-07-27-sterling-finance-build-manifest.md

qa:
  format_lint: clean, 32 artifacts
  sanitizer: clean on the exact linked worktree and exported candidate
  linked_worktree_git_pointer_regression: passed
  fixture_smoke: clean
  focused_finance_tests: 22 tests passed
  adversarial_mutations: 154 of 154 rejected with specific expected errors
  full_unit_suite: 55 tests passed
  changed_markdown_content_qa: 10 of 10 passed without warnings
  json_jsonl_parse: clean, 35 JSON and 10 JSONL files
  gitleaks_current_tree: clean
  gitleaks_history: clean, 31 commits scanned
  git_diff_check: clean
  exact_diff_inspection: passed, 28 changed paths
  unresolved_direct_p0_p1: pending-independent-review

privacy_and_sanitization:
  public_safe_intent: true
  fixture_authorizing: false
  live_effect_claimed: false
  synthetic_only: true
  excluded:
    - credentials and connector details
    - private paths, profiles, routes, logs, databases, screenshots, and runtime state
    - private entity, account, vendor, employee, customer, partner, and approver identities
    - amounts, private thresholds, real receipts, and run identifiers
    - personal-finance tools, taxonomies, aliases, data, and benchmarks

review:
  deterministic_local_review: passed
  independent_cross_model_review: parent-owned-pending
  local_direct_p0_p1: 0
  independent_direct_p0_p1: pending
  candidate_binding: exact scoped review commit

rollback:
  reversible: true
  method: discard the isolated worktree changes before commit
  live_rollback_required: false

completion_ledger:
  local_build: passed
  focused_validation: passed
  full_local_qa: passed
  independent_review: pending
  commit: parent-owned review checkpoint
  push_and_pr: parent-owned
  merge_and_release: maintainer-owned
```
