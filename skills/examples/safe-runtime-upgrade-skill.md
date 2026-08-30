---
name: safe-runtime-upgrade
description: Safely upgrades an agent runtime by proving preflight state, preserving local changes, validating post-upgrade health, and keeping rollback possible.
version: 1.0
owner: <YOUR_HANDLE>
tags: [runtime, upgrade, reliability, qa, rollback]
tools: [git, package-manager, test-runner, service-manager, sanitizer]
data_sensitivity: restricted
approval_required: before_live_change
---

# Safe Runtime Upgrade

Agent runtimes are production systems. A green installer exit code is not proof that the agent still works, the gateway still receives messages, scheduled jobs still deliver, or local hardening patches survived. This skill turns upgrades into a controlled change with evidence before, during, and after the move.

## When to use

Use this before upgrading, reinstalling, migrating, or materially changing any always-on agent runtime, messaging gateway, scheduler, model/provider routing layer, tool registry, plugin system, or local runtime dependency.

Use it when:

- The runtime has local patches, private skills, cron jobs, profiles, custom providers, gateway routes, or non-default credentials.
- The upgrade touches messaging, scheduled delivery, memory, tools, model routing, provider auth, browser/computer-use, or external integrations.
- A bug may already be fixed upstream and an upgrade may be safer than a local patch.
- You need a rollback path and a proof bundle, not a heroic terminal session.

Do not use it for:

- One-off package upgrades in a disposable sandbox.
- Pure documentation edits.
- Live restarts, credential moves, or destructive changes without a separate approval gate.

## Inputs

Required:

- Runtime repo or installation location, expressed as a safe placeholder such as `<AGENT_RUNTIME_REPO>`.
- Current version and candidate target version or branch.
- Update command in dry-run/read-only form if available.
- Service inventory: gateway, scheduler, workers, background processes, launch/service manager names.
- Critical acceptance checks: CLI smoke, gateway receive/send smoke, scheduler list, tool list, model/provider smoke, memory/skill load, and any domain-specific probes.
- Local-change inventory: git status, untracked files, local patch ledger if one exists, custom plugins, private skills, config files, and profile-specific overrides.
- Rollback method: backup, tag, package version pin, service restore command, or snapshot.

Optional:

- Upstream release notes, changelog, PRs, issue links, and commits relevant to the bug or upgrade.
- A post-upgrade live-state checklist.
- A canary user/channel for non-sensitive test delivery.
- Independent reviewer instructions.

If missing:

- If current state cannot be captured, stop. You cannot safely upgrade a system you cannot describe.
- If rollback is unknown, treat the upgrade as high risk and ask for approval before touching the live runtime.
- If credentials are required for smoke checks, verify their presence by key names or scoped probes only; never print secret values.

## Procedure

1. **Confirm scope and approval boundary**
   - State what will be read, what will be changed, what will be restarted, and what requires explicit approval.
   - Default mode is read-only preflight. Do not run the live update yet.

2. **Check upstream before patching**
   - Fetch release notes, changelog entries, issues, and commits related to the symptom or target version.
   - Decide whether the safer fix is upgrade, pin, config change, workaround, or local patch.
   - Record the source ledger and the upgrade-vs-patch recommendation.

3. **Create the preflight proof bundle**
   - Capture current version, target version, commit/branch, repo status, ahead/behind count, dirty files, untracked files, installed package versions, runtime config hash/copy with secrets redacted, enabled skills/tools/plugins, scheduler inventory, service status, and relevant logs summarized without secrets.
   - Save everything under a timestamped artifact folder such as `<ARTIFACT_ROOT>/safe-runtime-upgrade/<timestamp>/preflight/`.

4. **Classify local changes**
   - For each dirty or untracked runtime file, decide: preserve, discard, already upstreamed, unknown, or needs manual review.
   - Compare locally modified files against upstream-changed files to identify collision risk.
   - Block automatic upgrade if critical local patches may be overwritten without a reapply plan.

5. **Run baseline smoke checks**
   - Verify CLI responds.
   - Verify config parses.
   - Verify tool/skill/plugin registry loads.
   - Verify scheduler inventory is readable.
   - Verify model/provider routing with a harmless prompt.
   - Verify gateway/service health without sending external messages unless a canary target is approved.

6. **Present the upgrade decision**
   - Report PASS/WARN/FAIL preflight state.
   - Include top blockers, rollback method, expected blast radius, and exact command that would execute the upgrade.
   - Ask for explicit approval before live update or restart.

7. **Execute only after approval**
   - Create backup/snapshot/tag as planned.
   - Run the update command with logs captured to the artifact bundle.
   - Do not move, copy, rotate, or expose credentials as part of the update.
   - Do not restart messaging gateways or schedulers unless the approved scope includes restart.

8. **Run postflight checks**
   - Re-capture version, repo status, config hash, tool/skill/plugin list, scheduler inventory, service status, and relevant smoke checks.
   - Diff preflight vs postflight.
   - Verify critical local patches either survived, were replaced by upstream equivalents, or were intentionally removed.

9. **Reconcile drift**
   - If the update restored stale local changes, inspect them against the local patch plan before accepting them.
   - Reapply only minimal intentional contracts, then rerun targeted tests.
   - If a service restart is required to load fixed code, treat restart as its own gated live action unless already approved.

10. **Close with evidence**
    - Report final PASS/WARN/FAIL, artifact path, upgrade executed yes/no, version before/after, tests run, remaining warnings, rollback status, and whether a live restart is still pending.

## What good looks like

A safe runtime upgrade is not “the command exited 0.” It is complete when:

- There is a timestamped proof bundle with preflight, update logs, postflight, and diff summary.
- Current version, target version, ahead/behind state, dirty files, local patches, and untracked files are known before the update.
- Critical config, skills, tools, plugins, scheduler jobs, gateway routes, and provider/model routes are inventoried before and after.
- Secrets are never printed, copied into public artifacts, or moved casually.
- Live restarts and external sends happen only after approval.
- Local patches are preserved, intentionally removed, or replaced by proven upstream equivalents.
- Smoke checks exercise the actual production runtime path, not a convenient but irrelevant Python/package environment.
- The final report includes remaining WARN/FAIL items instead of burying them under “done.”

## Output contract

Primary output: safe runtime upgrade report plus artifact bundle.

Required report fields:

```md
Status: PASS | WARN | FAIL
Upgrade executed: yes | no
Runtime: <agent/runtime name>
Before version: <version/commit>
After version: <version/commit or n/a>
Artifact bundle: <safe artifact path or repo-relative location>
Approval: <who approved what, or pending>
Top warnings/blockers:
- <item>
Checks run:
- <check>: <pass/fail/blocked>
Local changes:
- preserved: <count/list>
- upstream-equivalent: <count/list>
- unresolved: <count/list>
Rollback:
- method: <snapshot/tag/pin/backup>
- status: ready | used | unavailable
Next action:
- <none, approve update, approve restart, reconcile patch, rollback>
```

Required artifact bundle shape:

```text
safe-runtime-upgrade/<timestamp>/
  preflight/
    version.txt
    repo-status.txt
    config-hash-or-redacted-allowlist.yaml
    skills-tools-plugins.txt
    scheduler-inventory.txt
    service-status.txt
    baseline-smoke.md
    local-change-classification.md
    source-ledger.md
  upgrade/
    command.txt
    output-redacted.log
    backup-or-snapshot.txt
  postflight/
    version.txt
    repo-status.txt
    diff-summary.md
    smoke-results.md
    local-patch-reconciliation.md
  summary.md
```

Required tool capabilities: read-only file inspection, git status/log/diff, version command, scheduler list, service status, config parse, test runner, redacted log capture, backup/snapshot, and optional canary delivery.

## Privacy and approval

Data allowed:

- Public release notes, sanitized changelog findings, generic runtime file categories, redacted config keys, counts of jobs/tools/plugins, PASS/WARN/FAIL state, and synthetic fixture outputs.

Data blocked:

- Credential values, tokens, private keys, session cookies, raw `.env` content, real chat/user IDs, private hostnames, customer/vendor names, private memory, raw logs containing sensitive text, private prompts, exact source-of-truth records, and live internal paths in public artifacts.

Redaction rules:

- Show key names and presence/absence, never values.
- Replace private paths with placeholders such as `<AGENT_RUNTIME_REPO>`, `<AGENT_HOME>`, and `<ARTIFACT_ROOT>`.
- Summarize logs by event and count; include exact stack traces only in approved private artifacts.
- Keep public versions framework-agnostic. Name commands as examples, not mandates.

Approval required before:

- Running the live update.
- Restarting a gateway, scheduler, service manager, or worker.
- Changing provider/model routing.
- Moving, copying, deleting, or rotating credentials.
- Sending canary messages outside an approved private target.
- Disabling old runtimes, watchdogs, or gateways.
- Publishing any non-sanitized artifact.

## Verification

Minimum verification before claiming done:

- Preflight artifact exists and includes version, repo state, config parse, local changes, scheduler inventory, service status, and smoke results.
- The update command and output are captured with secrets redacted.
- Postflight re-runs the same checks and records before/after differences.
- Critical local patch contracts have targeted verification or an explicit upstream-equivalent proof.
- Scheduler jobs are still readable and delivery targets are unchanged unless approved.
- Gateway/service live state is verified after any approved restart.
- Public reports pass sanitizer and manual redaction review.

Suggested check matrix:

```text
CLI version: pass/fail
Config parse: pass/fail
Tool registry: pass/fail
Skill load: pass/fail
Scheduler list: pass/fail
Model/provider smoke: pass/fail
Gateway/service status: pass/fail/not approved
Local patch reconciliation: pass/warn/fail
Rollback artifact: ready/missing
```

## Maintenance

Update this skill when:

- A new runtime component becomes critical, such as a desktop app, mobile gateway, MCP server, browser service, or external worker lane.
- A post-upgrade regression reveals a missing acceptance check.
- An update command changes behavior or stops supporting dry-run/backup flags.
- A local patch is upstreamed and should move from “reapply” to “verify upstream equivalent.”
- A sanitizer misses a private path, ID, secret-like value, or raw log detail.

Keep a short reference note for each painful upgrade: what broke, which check should have caught it, and the new guardrail.

## Landmines

- **Green updater, broken agent**: installer success does not prove messaging, cron, tools, memory, or provider routing work. Always run postflight acceptance checks.
- **Dirty repo roulette**: upgrading over local patches can silently drop private hardening. Classify and reconcile local changes before calling the update safe.
- **Wrong runtime smoke**: tests run in a developer shell may not match the gateway or service environment. Verify the environment that actually serves users.
- **Credential panic moves**: copying or rotating secrets during an upgrade creates new failure modes and leak risk. Keep credential operations separate and approved.
- **Self-restart trap**: an agent talking through a gateway should not casually restart the gateway hosting the conversation without an external control plane and approval.
- **Public artifact leak**: upgrade bundles often contain paths, IDs, logs, and config residue. Public versions should publish the protocol, not the private bundle.
- **Rollback theater**: “we can roll back” means there is a known command, backup, pin, tag, or snapshot and someone has verified it exists.
