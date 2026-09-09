# URC-D02 verification — 2026-09-09

**Superseded historical handoff:** see [the review correction](../task-2026-09-09-review/README.md).
D02 is blocked on acquisition provenance; the original recall claim is withdrawn.

Base: head of `task/priority-one-20260908`. Deliverable: [database search export and recall
check](../../docs/prior-art-search-2026-09-09-database.md). Authoritative status: [SPRINT_TASKS.csv](../../docs/SPRINT_TASKS.csv).

| Item | Observed |
| --- | --- |
| unique records retained | 402 |
| overlap with the 6 resolvable D01 identifiers | 0 |
| query legs failing | arXiv search API: 5/6 (HTTP 429); Crossref 0; OpenAlex 0 |
| candidates listed, all UNSCREENED | 25 (keyword triage score ≥ 4) |
| patents | not queried — no patent database reachable |

Reproduce: `OPENALEX_API_KEY=... python evidence/task-2026-09-09/rerun_search.py --out <tmp>`.
Counts will drift as the databases grow; the recall check and the throttling behaviour are the
reproducible facts. Files: `database-export.json`, `database-export.csv`, `candidates-unscreened.csv`.

This closes nothing: the parent novelty task, the close-competitor full-text reads, institutional
database access, patent claim review and every owner gate remain exactly as day 1 left them.
# Review correction — original results above are superseded

The original recall/complete-provenance interpretation was not supported.
Read [the offline integrity review](../task-2026-09-09-review/README.md) and
[corrected source interpretation](../../docs/prior-art-search-2026-09-09-database.md).
The raw export and candidate CSVs are retained, not repaired or newly screened.
The authoritative D02 ledger status is blocked pending provenance reconciliation.
