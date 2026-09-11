# Clean acquisition correction — 2026-09-11

## Result, not an inferred completion

Fresh [native export](../evidence/task-2026-09-11-public/database-export.json): **317 normalized identifier records; 16/16 query legs completed**. CSV and ranked unscreened subset are beside it. Every leg has request UTC, route, status, raw response/hash and observed count; every retained record's provenance maps to a successful native response at its recorded rank.

The offline audit reports zero unsupported routes, missing successful response records, identifier/rank mismatches, count mismatches and response-hash mismatches. This fixes the **new acquisition's** provenance. It does not retrospectively repair the rejected historical export. Old data and its withdrawn recall claims are preserved, not overwritten.

Current known-anchor overlap: arxiv:2505.02357; arxiv:2602.07264. **Recall remains null** because the complete eligible D01 scholarly identifier register is still unresolved. Do not call this the old 0/6 or 1/6 claim, a global literature recall, or proof that discovery routes find different populations. Full URC-D02 remains in progress for that Agent-owned closeout; the clean acquisition subtask URC-R01 is complete.

## What was corrected and exercised

1. Request timestamp, redacted route, HTTP outcome, raw successful response, bytes/hash and each source/rank are now retained.
2. Richer abstract text names its source route; an arXiv error feed is rejected rather than counted as a paper.
3. Parent regression controls exposed missing-response acceptance, invented IDs despite a logged query, and missing ranks silently skipping count checks. All three failed before correction and pass now; the audit decodes native response identifiers rather than trusting attached query strings.
4. A mandatory OpenAlex-key check was an avoidable software restriction. [Current official authentication guidance](https://help.openalex.org/api/authentication/) permits basic anonymous requests. The [public-route amendment](specs/evidence-gap-correction/public-route-amendment.md) was committed before the new run; queries/caps were unchanged. No account, paid access or credential was needed. Actual service errors remain errors, not zero-result success.
5. Historical and initial correction attempts are retained separately. The clean-network attempt skipped OpenAlex because of the old script restriction; it is not evidence that the service rejected anonymous access. The first clean attempt also recorded network URLError failures before the escalated network rerun; zero retained rows in that attempt was not a zero-hit literature result.

The procedure was amended after earlier results were seen. This is reproducible development acquisition, not an untouched preregistration or independent held-out evaluation.

## Reproduce

From repository root:

```sh
python -m unittest discover -s tests -q
python scripts/check_repo_contract.py
python scripts/acquisition_ledger.py --check
python evidence/task-2026-09-09/rerun_search.py --audit evidence/task-2026-09-11-public/database-export.json
```

Observed: 29 tests pass; repository contract passes; historical reconciliation is consistent; new export audit passes. The existing acquisition_ledger.py intentionally verifies the **historical day-3 ledger**; it does not claim to include this new export. Current acquisition evidence is the versioned native export linked above. Source/commands/raw response provenance are reviewable without network access.

To make another acquisition, use `--out` with a **new, nonexistent directory**; existing output directories are rejected. Live APIs can return different rankings later; retained responses reproduce this run's audit, not future query output. Caps: Crossref 40, OpenAlex 50, arXiv 60 per recorded query, no pagination. Returned identifiers are not distinct studies or relevant-paper counts. Ranked candidates remain UNSCREENED.

## Derived CSV formatting

Staged whitespace checking exposed CRLF record endings and embedded API abstract whitespace in the generated CSV display layer. A regression now requires LF records and normalized title/abstract spacing; the full raw response and extracted text remain unchanged in authoritative JSON. Only new correction CSVs were regenerated from retained JSON, without any network call or historical export rewrite. Final suite: 30 tests.

## Remaining work, with correct ownership

- **Agent, not Owner:** finish the entire D01 eligible identifier register and report descriptive reference-set coverage with explicit inclusion/exclusion. Do not silently drop unresolved papers to improve a fraction.
- **Agent:** read accessible remaining close competitors under the existing [rubric](day3-reading-rubric.md), retain exact version/sections/per-axis judgment, then screen the ranked candidates. Public reading is not blocked merely because earlier prose assigned it to an owner.
- **External only where demonstrated:** obtain unavailable full text or qualified IP review; document the specific failed source route. Existing public claim reads do not constitute legal clearance.
- **Owner:** choose/confirm intended vehicle configurations, available apparatus and lab/safety review.
- No new full competitor-reading campaign, simulator run, prototype, measurement, novelty clearance, independent human review or publication is claimed by this export.

## Detailed test evidence

Baseline was clean main at `e0f01f62e82b19a2763a0d362d62b1eee46715e2`; 21 tests and repo/ledger checks passed using existing Python 3.11.8. Initial four exporter regressions increased the suite to 25; parent added three native-audit regressions and one net extra OpenAlex regression, giving 29. Parent's first named-test invocation used a nonexistent tests package and failed to import; the repository's actual unittest-discover command then reproduced the three intended assertion failures. No failed run was counted as a passing test.

The source commits before acquisition and subsequent PR preserve the procedure identity. No credentials or private lab data belong in raw evidence.
