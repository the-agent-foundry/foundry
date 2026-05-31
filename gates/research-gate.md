# The Research Gate

The research gate prevents local patches for problems the outside world already solved. Use it before spec and build when the work touches external systems or when the failure signature may not be unique to your stack.

This is a reasoning gate with a concrete output: a source ledger that changes the spec or explains why it did not.

## When research is required

Run this gate for MODERATE or COMPLEX work involving:

- External APIs, SDKs, model providers, auth providers, schedulers, browsers, databases, or third-party platforms.
- Dependency errors, version conflicts, deprecations, timeouts, rate limits, streaming failures, webhooks, or provider behavior changes.
- Security, privacy, or delivery behavior where upstream semantics matter.
- Error messages that look searchable.
- Any build where an upgrade, existing issue, changelog note, or community workaround may be safer than a local patch.

Research is optional for purely local documentation, formatting, one-file text cleanup, or deterministic internal logic with no external error signature. If skipped, say why.

## The two questions

Research must answer both:

1. **Who else has this issue?**
2. **How did they fix or work around it?**

If the answer is "nobody," record the searches and sources checked. A failed search is still evidence if it is specific enough.

## Minimum source mix

Use the sources that fit the problem:

- Official docs, changelogs, release notes, migration guides, and status pages.
- GitHub issues, pull requests, discussions, and package trackers.
- Vendor forums, Stack Overflow, Reddit, X, Discord, or community posts when official sources are silent.
- Known-good examples from working projects.

Prefer fresh and authoritative sources. Old posts are useful only when the behavior is stable or the same version is involved.

## Source ledger schema

```yaml
research:
  required: yes
  rationale: External provider error signature with possible upstream fix.
  source_ledger:
    - url: https://example.com/provider/changelog
      source_type: official changelog
      freshness: 2026-05-20
      quoted_signal: "Fixed intermittent streaming disconnects in version 1.2.3."
      fix_or_workaround: Upgrade SDK to 1.2.3 or disable streaming.
      match_strength: high
      implication: Prefer vetted upgrade before local retry wrapper.
    - url: https://example.com/community/thread
      source_type: community report
      freshness: 2026-05-18
      quoted_signal: Multiple users report identical timeout after model release.
      fix_or_workaround: Pin prior model until provider patch lands.
      match_strength: medium
      implication: Add rollback/pin option to spec.
```

Required fields:

- `url`
- `source_type`
- `freshness`
- `quoted_signal`
- `fix_or_workaround`
- `match_strength`: low, medium, or high
- `implication`: what changed in the spec because of this source

## Upgrade before patch

When research finds a safe, vetted upstream fix, prefer the upgrade or configuration change before writing a local patch. Local patches add maintenance surface. Use them when:

- No safe upstream fix exists.
- The upgrade has unacceptable risk.
- The workaround is urgent and reversible.
- The local behavior is genuinely specific to your system.

Record the tradeoff in the manifest.

## Passing the gate

The research gate passes when:

- The two questions are answered.
- Sources are listed with freshness and match strength.
- The spec states what research changed.
- Upgrade, pin, workaround, or local patch choice is explicit.
- Skipped research has a narrow, defensible rationale.

## Pickup prompt

> Review this problem and run the research gate before we build. Find who else has hit it, how they fixed or worked around it, and what should change in our spec because of that evidence.
