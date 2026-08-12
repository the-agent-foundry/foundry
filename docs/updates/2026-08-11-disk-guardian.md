# Disk Guardian Community publication — 2026-08-11

This update adds the first executable operating-system utility to Agent Foundry: a sanitized macOS/APFS pressure guardian adapted from a production system developed by Darryl Hicks with implementation and hardening support from Dwayne Schofield and SolveWorks.

## Why this exists

Disk monitoring without safe autonomous relief becomes alert wallpaper. Disk Guardian measures the APFS Data container authoritatively and keeps deleting only proven disposable classes, in bounded passes, until it reaches a real target or runs out of defensible authority.

## Included

- size-aware pressure states and absolute overrides;
- bounded cleanup of exact uv, pip, npm, and Homebrew cache roots;
- closed producer-retention contracts for worktrees, backups, staging, and retired runtime caches;
- descriptor-anchored traversal and deletion, active-process and `lsof` blockers, locks, claims, receipts, and boundary revalidation;
- `status`, `doctor`, `scan`, dry-run, cleanup, contract helper, and self-test commands;
- generated user-specific launchd scheduling with healthy silence;
- schemas, example policy, install/uninstall flow, and adversarial tests.

## Deliberately excluded

No private runtime paths or routing, no customer or personal data, no site-specific dashboard adapter, no backup-vendor identity, no arbitrary cleanup, and no Time Machine/APFS snapshot deletion.

## Adoption

Start with `python3 disk-guardian/disk_guardian.py self-test`, then `doctor`, `scan`, and `cleanup --dry-run`. Enable launchd only after reviewing the local policy and confirming the executable classes materially match the machine's pressure.

No migration is required for existing Agent Foundry forks; this package is additive.
