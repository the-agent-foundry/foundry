# The QA Gate

QA is the line between "the agent says it is done" and "the artifact is actually done." This gate exists because agents are very good at sounding finished before anything has been proven.

Use it for any build, repair, automation, skill, tool, or agent workflow that should survive beyond the current chat.

## The rule

Artifacts prove done. Narrative does not.

A passing QA gate must include real evidence: commands run, tests passed, files opened, outputs inspected, logs checked, screenshots captured, dry-runs executed, or independent review completed.

## Start from the domain action

Do not start QA from a file list. A file list is a proxy.

Start with the real-world action the system performs, then enumerate every surface where that action can happen.

Example surface inventory:

- User command path.
- Scheduled or event-triggered path.
- Helper or wrapper path.
- Retry path.
- Failure and error-notice path.
- Egress path: sends, writes, publishes, updates, posts, edits.
- Media or attachment path.
- State write path.
- Recovery or rollback path.
- Dashboard or human-readable status path.

If a surface is intentionally out of scope, document why.

## QA checklist

For MODERATE and COMPLEX work, collect evidence for each item that applies:

- **Spec match:** acceptance criteria mapped to tests or checks.
- **Surface coverage:** live entry points and side-effect paths inventoried.
- **Happy path:** main workflow works on realistic input.
- **Failure path:** bad input, missing dependency, denied approval, or empty result fails loudly.
- **State behavior:** high-water marks, freshness, dedupe, retries, provenance, and health checks work or are not needed.
- **Regression:** the original bug or risk has a direct repro or fixture when practical.
- **Privacy/security:** sensitive data, secrets, credentials, external sends, and source-of-truth writes are blocked or approved at the right boundary.
- **Idempotence:** reruns do not duplicate work or corrupt state unless duplication is explicitly safe.
- **Rollback/recovery:** the change can be reverted or safely disabled.
- **Human legibility:** logs, manifests, or dashboards explain what happened without spelunking.

## Evidence standards

Good evidence:

- Exact command and exit code.
- Test name and pass/fail output.
- File path or artifact link.
- Screenshot or rendered output.
- Diff summary plus the specific behavior changed.
- Sanitization scan and format lint results for public artifacts.
- Independent reviewer finding plus disposition.

Weak evidence:

- "I inspected it."
- "Should work."
- "The helper test passes" when the live path was not exercised.
- "No errors in logs" without checking the surface that emits errors.
- A self-report from the same agent that built it.

## Hard-stop failures

Do not ship if any of these remain unresolved:

- The artifact cannot be run, opened, rendered, or exercised.
- A required test or scan fails.
- A live side-effect path is unreviewed.
- A P0/P1 red-team finding is unresolved.
- A secret, credential, real private path, private ID, or personal data appears in a public artifact.
- The system can silently become stale or wrong and nobody is alerted.
- The approval gate can be bypassed for a gated action.

## QA report shape

Use this shape in the build manifest:

```yaml
qa:
  acceptance_criteria:
    - criterion: Public docs contain no private paths or secrets.
      evidence: python3 gates/scripts/sanitize_scan.py . exited 0
  commands:
    - command: python3 gates/scripts/format_lint.py .
      exit_code: 0
      notes: All schema-governed artifacts passed.
  surface_coverage:
    - surface: scheduled job path
      risk: stale or duplicated output
      check: dry-run with fixture and rerun
      evidence: <command/output/artifact>
      result: pass
      out_of_scope_rationale: null
  failures_found:
    - finding: Format linter failed on missing required heading.
      fix: Added required heading and reran lint.
  unresolved:
    - none
```

## Passing the gate

The QA gate passes when:

- Every acceptance criterion has evidence.
- Every required surface is checked or explicitly ruled out.
- All P0/P1 issues are closed.
- Remaining P2/P3 issues are documented with owner, risk, and revisit trigger.
- The manifest makes the proof inspectable by someone who was not in the chat.
