# Disk Guardian Community

A deterministic macOS/APFS pressure-relief engine with actual teeth and a narrow blast radius.

Disk Guardian does not merely warn that your drive is full. When the APFS Data container crosses a configured pressure boundary, it can autonomously remove **proven regenerable package-cache contents** and **exact producer-contracted Hermes lifecycle artifacts** until it reaches the configured free-space target or exhausts a bounded transaction. Every destructive candidate is revalidated immediately before descriptor-relative deletion. No model chooses paths.

This package is adapted from a production system developed by Darryl Hicks with implementation and hardening support from Dwayne Schofield and SolveWorks. The public package preserves the reusable safety and execution contracts while omitting private runtime bindings.

## What it can delete

### Autonomous package caches

Exact roots under the installing user's passwd home:

- uv: `.cache/uv` and `Library/Caches/uv`
- pip: `Library/Caches/pip`
- npm: `.npm/_cacache`
- Homebrew downloads: `Library/Caches/Homebrew/downloads`

A root is executable only when it is same-user, same-device, a real directory, free of active class-local processes, and clear under exact-path `lsof`. Candidate traversal is bounded and descriptor-anchored. Non-uv symlinks fail closed; uv leaf symlinks may be unlinked only after inode and link-text fingerprinting, never followed.

### Contracted Hermes lifecycle artifacts

Producers may nominate exact direct children of four registered roots:

- worktrees: `.hermes/worktrees`
- backups: `.hermes/backups`
- staging: `.hermes/staging`
- retired runtime caches: `.hermes/runtime-retired`

A filename is not authority. The closed contract must bind the exact device, inode, owner, type, modification time, logical bytes, node count, and tree digest. It must include every class proof, an empty active-reference list, an expiry, and a private authority lock. Guardian independently rechecks all of it, obtains the exclusive producer lock, writes a single-use claim, and revalidates again at the deletion boundary.

## What it never deletes

- Hermes sessions, databases, vaults, memory, model weights, or container data
- Time Machine or APFS snapshots
- Uncontracted backups or worktrees
- Arbitrary temporary folders
- Any path outside the closed cache registry or contract-root registry
- Any candidate with unresolved process, open-handle, ownership, device, type, symlink, identity, lock, proof, reference, age, or traversal evidence

Docker data, local models, databases, snapshots, and source-of-truth files may be the real disk problem. `doctor` reports when Guardian has no proven autonomous relief instead of pretending a tiny cache purge solved RED pressure.

## Requirements

- macOS with an APFS Data container mounted at `/System/Volumes/Data`
- `/usr/bin/python3` 3.9 or newer
- `/usr/sbin/diskutil`, `/usr/sbin/lsof`, `/usr/bin/pgrep`, `launchctl`
- no Python packages; the engine is standard-library only

## Quick start

```bash
cd disk-guardian
python3 disk_guardian.py self-test
python3 disk_guardian.py --policy policy.example.json status
python3 disk_guardian.py --policy policy.example.json doctor
python3 disk_guardian.py --policy policy.example.json scan
python3 disk_guardian.py --policy policy.example.json cleanup --dry-run
```

Read the dry-run output. If it identifies the right exact classes, execute one bounded pass:

```bash
python3 disk_guardian.py --policy policy.example.json cleanup
```

A nonzero exit from scheduled cleanup means pressure remains unresolved after all safe autonomous candidates were exhausted. That is not a crash; it is the system refusing to call failure success.

## Installation

Installation and scheduling are separate on purpose:

```bash
bash install.sh install
# Review ~/.local/share/disk-guardian-community/policy.json
bash install.sh enable
bash install.sh status
```

`install` writes user-private code, policy, logs, and a generated plist. It does not load launchd. `enable` runs `doctor`, then bootstraps only `org.agent-foundry.disk-guardian`. The job runs every 15 minutes, emits empty stdout when healthy, and writes local receipts under `~/.disk-guardian/`.

Uninstall while retaining receipts:

```bash
bash install.sh uninstall
```

## Pressure policy

Defaults are proportional to container size:

| State | Free space |
|---|---:|
| GREEN | at least 15% |
| YELLOW | below 15% |
| ORANGE | below 10% |
| RED | below 7% |
| CRITICAL | below 4% |
| Cleanup target | 20% |

Set all five `*_free_bytes` values to use absolute thresholds. Partial absolute overrides are rejected because mixed algebra is easy to misread. The default per-pass cap is 50 GiB, per-candidate cap is 20 GiB, and runtime cap is 45 minutes. A pass stops immediately after fresh APFS measurement reaches the target.

## Commands

- `status`: authoritative APFS measurement and effective thresholds.
- `scan`: pressure plus sanitized cache/contract eligibility and blockers.
- `doctor`: whether proven eligible bytes can plausibly close the current deficit.
- `cleanup --dry-run`: exact decision path without deletion.
- `cleanup`: bounded autonomous pass with immutable local receipt.
- `cleanup --scheduled`: healthy silence; unresolved pressure exits nonzero with JSON.
- `make-contract`: producer helper for an already-proven exact candidate.
- `self-test`: policy and measurement-contract sanity check.

Machine output deliberately omits candidate paths, raw process rows, and contract payloads. It reports class, blocker category, and byte counts.

## Producer contract workflow

1. The producer creates the exact registered root and private `0600` `.disk-guardian-retention.lock`.
2. The producer proves the class lifecycle state from its own authoritative records.
3. It calls `make-contract` with the exact direct-child name. The helper fingerprints live bytes and writes a `0600`, SHA-256-named contract into the private `0700` contract directory.
4. The producer takes a shared lock before changing references, lifecycle state, or the candidate. Guardian takes the exclusive lock during final proof and deletion.
5. Guardian consumes the contract once. An existing claim blocks replay even after interruption.

Example for a worktree after the producer has proved it clean, merged, terminal, non-current, unlocked, reachable, and unreferenced:

```bash
python3 disk_guardian.py make-contract worktree old-worktree \
  --proofs-file worktree-proofs.json \
  --minimum-age-seconds 1209600
```

`make-contract` refuses to invent lifecycle facts: `--proofs-file` must contain the exact closed Boolean proof set for the selected class. Only the producer that actually owns those facts should create that file. Guardian verifies filesystem facts and contract integrity; it cannot independently know whether a Git branch was semantically safe to discard. If your producer cannot prove the lifecycle contract, do not create one.

## Safety model and limits

The engine protects against stale metadata, accidental root widening, symlink/path races, active processes, open handles, identity replacement, mount crossing, malformed contracts, replay, and bounded traversal failure. It is not a sandbox against malicious code already running as the same macOS user; that code can delete user-owned files without Guardian.

APFS container-free change is reported as an observation, not causal proof. Logical deletion may not immediately increase APFS free space because snapshots or filesystem behavior retain blocks.

Snapshot deletion is intentionally absent from this release. It is powerful enough to deserve a separate adapter and threat model, not a checkbox hidden in a cache cleaner.

## Validation

```bash
python3 -m unittest gates.tests.test_disk_guardian_community -v
python3 gates/scripts/sanitize_scan.py .
python3 gates/scripts/format_lint.py .
python3 gates/scripts/fixture_smoke.py .
python3 -m unittest discover -s gates/tests -v
```

The focused suite includes destructive synthetic fixtures for exact cache and contracted-artifact deletion plus adversarial cases for symlinks, identity drift, active processes, unavailable `lsof`, caps, high-watermark stopping, missing proofs, active references, replay, and uncontracted Hermes worktrees.

## Pickup prompt

> Review `disk-guardian/` as executable reference code, not a turnkey promise. Run `self-test`, `status`, `doctor`, `scan`, and `cleanup --dry-run`. Tell me which proven classes materially contribute to our deficit, which large consumers remain outside autonomous authority, and what local thresholds fit our disk size. Do not enable launchd or create retention contracts until I approve the exact local policy and producer proofs.
