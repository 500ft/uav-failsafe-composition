# URC-D02 — database export integrity review, 2026-09-09

> **2026-09-11 update — URC-D04.** The provenance defect described below is corrected by a
> separately dated, provenance-clean acquisition: [evidence/task-2026-09-11](../evidence/task-2026-09-11/README.md)
> (317 records, 0 unlogged rows, 2 of 5 known anchors present).
> This export is retained unchanged as the historical record; it is not repaired or merged.

**Partial evidence; D02 acceptance is blocked.** The historical export is retained,
but its claimed recall and complete per-query provenance do not survive an offline
review. This revision supersedes the original day-2 interpretation; it does not
rewrite the original JSON/CSV or treat a rerun as a reconstruction of that acquisition.

## What is verified from the committed export

| Observation | Value and interpretation |
| --- | --- |
| Stored rows / distinct literal identifiers | 402 / 402; not 402 distinct studies |
| Rows without any successful logged database/query pair | 90, all labeled arXiv |
| arXiv query log | two HTTP 429 failures, one HTTP 503 failure, two timeouts, and one successful zero-result query |
| Explicitly comparable known day-1 anchors present | 0; incomplete anchor set, not a recall ratio |
| Candidate file | 25 rows, still UNSCREENED; original ranking is provisional |

Sources: [immutable export JSON](../evidence/task-2026-09-09/database-export.json),
[CSV](../evidence/task-2026-09-09/database-export.csv), and the new
[offline derived audit](../evidence/task-2026-09-09-review/export-audit.json).
The audit checks each hit's database/query against the query log. A query string
attached to a hit is not evidence of an observed successful request. Missing
request provenance must be recovered from the original acquisition record or
left unresolved; do not backfill a success count from the rows.

The original 0/6 denominator included an unqueried patent. Five arXiv anchors
are comparable after version/DOI normalization; none is present. That is a
bounded identifier-overlap observation, not search recall: the eligible
day-1 reference register is incomplete and 90 rows have unresolved request
provenance. The JSON lists five resolvable arXiv IDs but does not retain the
claimed three diagnostic OpenAlex top-100 responses. The conclusion that this
is "not a query-wording accident" and demonstrates distinct discovery
populations is withdrawn. Ranking, query wording, indexing and incomplete
retrieval remain possible explanations.

The raw flags and candidate shortlist are historical, not corrected scientific
judgments. Do not count the same preprint and journal version as separate studies
without manual reconciliation. Exact-title matches are review candidates, not
automatic identity proofs. Keyword scores use uneven title/abstract availability
and are only a reading aid, not a relevance or importance grade.

## Development performed

The [rerun tool](../evidence/task-2026-09-09/rerun_search.py) now:

- Requires a **new** output directory and refuses overwrite before network access.
- Repeats only the recorded database/query pairs, not their Cartesian product.
- Writes all three promised outputs; records every observed query/rank for a
  deduplicated identifier, including source ID and abstract availability.
- Distinguishes successful empty results from missing credentials, partial
  failures and request errors; incomplete acquisitions exit 2.
- Normalizes DOI/arXiv aliases and version suffixes, reports only known-anchor
  matches, and leaves recall unavailable.
- Offers a read-only audit of historical JSON. The historical audit intentionally
  exits 1 for unresolved provenance; the regression tests pass by detecting it.

The acquisition is a **new bounded protocol**, not an exact historical replay:
original responses and complete request parameters were not retained. Current
request caps are explicit in the tool. No live database rerun occurred in this
review; offline tests do not establish API availability or search completeness.
The [arXiv API manual](https://info.arxiv.org/help/api/user-manual.html) documents
query construction and versioned identifiers; unchanged API availability still
needs a real acquisition check.

## Better next step and what remains closed

Keep day 1's focused, bounded source review. Before another large export:
recover the missing acquisition provenance if available; complete a scholarly
anchor registry with DOI/arXiv aliases and explicit exclusions; then screen the
closest competitors under day 1's rubric. Preserve the historic corpus as an
unreconciled input and save any new acquisition separately.

Prioritize full-text comparison of Avis/PGFuzz and the cross-stack tools, then a small equivalent-event configuration table. A large hit count is not progress toward the single-vehicle conformance question.
No new paper was fully read in this review. Novelty, resources, measurement and
owner gates stay open. No simulator,
fabrication, rotor operation, safety verdict or patent clearance is authorized.
