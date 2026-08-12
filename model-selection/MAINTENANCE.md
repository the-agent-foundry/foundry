# Model roster maintenance

This roster is maintained, not immortal.

## Cadence

- **Monthly review:** due 31 days after `as_of` unless an earlier provider event forces review.
- **Event-driven review:** major model launch, retirement/deprecation, material price change, route or endpoint change, privacy/data-use change, context/tool change, or credible evaluation regression.
- **Visible staleness:** if `review_due_at` is in the past, readers and agents must treat recommendations as stale until reviewed.

A monthly check may create a proposal or issue. It must not silently rewrite editorial guidance, publish, merge, activate routes, or spend on evaluations.

## Maintainer procedure

1. Read `public-model-roster.json`, this policy, and relevant official sources.
2. Confirm every source is still official and reachable.
3. Reconcile launches, aliases, previews, deprecations, and retirements.
4. Refresh standard direct-route prices and material modifiers: long context, cache, batch/flex, priority/fast, residency, tools, storage, and plan/credit semantics.
5. Keep public catalogue state separate from local entitlement and runtime validation.
6. Reassess editorial best-fit and weakness text. Label it `editorial` unless backed by a published fixed evaluation.
7. Move image, audio, video, embedding, and other specialist routes to the specialist appendix rather than bloating the main table.
8. Update `as_of`, `review_due_at`, source access dates, and `roster_version`.
9. Run:

```bash
python3 model-selection/scripts/validate_roster.py --today "$(date -u +%F)"
python3 model-selection/scripts/render_roster.py --check
python3 gates/scripts/format_lint.py .
python3 gates/scripts/sanitize_scan.py .
python3 gates/scripts/fixture_smoke.py .
python3 -m unittest discover -s gates/tests -v
```

Operators validate a private exact-route overlay separately before use:

```bash
python3 model-selection/scripts/validate_roster.py --overlay /private/path/local-overlay.json
```

10. Review the rendered diff for unsupported certainty, duplicate rows, guessed prices, or route/model confusion.
11. Run an independent privacy/usefulness review before publication.
12. Publish through a normal reviewed PR. Never auto-merge a roster refresh.

## Admission rules

Add a route to the main baseline when all are true:

- it is agent-capable rather than only a specialist media/embedding route;
- an official model/catalogue source exists;
- an official pricing or explicit non-metered accounting source exists, or the price is honestly `unknown`;
- the first-party model candidate is explicit, and exact route mechanics remain in the private overlay;
- status and freshness are explicit;
- suitability is clearly marked official, observed, or editorial;
- the row does not expose private entitlement or runtime configuration.

Remove or mark a route legacy/retiring when official evidence warrants it. Keep a short migration note when removal could surprise users.

## Price discipline

- Do not assign direct-API prices to subscription, OAuth, cloud-marketplace, or router routes without labeling the accounting difference.
- Do not convert “included in my plan” into zero cost.
- Keep tool, storage, cache, long-context, residency, and priority charges visible when material.
- If provider documentation conflicts, mark the field unresolved and cite both sources. Do not resolve a billing dispute with vibes.

## Public/private boundary

Never publish:

- credentials or account identifiers;
- actual local provider enablement;
- negotiated contract rates;
- private prompt adapters;
- internal profile, tool, or cron assignments;
- private evaluation prompts, outputs, or business data;
- raw usage or billing records.

The public baseline is safe for broad reuse. Local truth belongs in a private overlay.

## Automation boundary

Allowed automation:

- check whether the review date is due;
- fetch public catalogues and official pages without inference;
- compute diffs;
- validate schema and stale source dates;
- create a proposal-only maintenance candidate.

Human-reviewed boundary:

- change editorial recommendations;
- accept ambiguous provider claims;
- publish a PR;
- activate or retire live routes;
- run paid evaluations;
- merge the public update.
