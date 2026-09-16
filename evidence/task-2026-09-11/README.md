# URC-D04 — provenance-clean re-acquisition of the D02 database export, 2026-09-11

**What this closes:** the D02 provenance defect. The 2026-09-09 export retained
90 rows whose query tag had no successful logged request (hits from one run were
merged with the query log of another). This directory is one clean run of the same bounded
protocol from a non-throttled network: every retained row traces to a logged successful
query **in this run**, and every query leg completed.

**What this does not close:** screening (all candidates remain UNSCREENED), search recall as a
ratio (the eligible anchor register is still incomplete, so `recall` stays `null`), patent
review (no patent database is reachable), the parent novelty task, and every owner gate.

## Observed

| Item | Observed |
| --- | --- |
| protocol | `2026-09-09-review-1` (new bounded acquisition; not a replay of the 09-09 export) |
| retrieved (UTC) | 2026-09-11T18:03:17Z |
| query legs | 16 total; 16 ok, 0 incomplete |
| identifier records retained | 317 (normalized identifiers, not distinct studies) |
| rows without a successful logged query | **0** (historical 09-09 export: 90) |
| known D01 anchors present | 2 of 5 comparable (`arxiv:2505.02357`, `arxiv:2602.07264`); historical export: 0 of 5 |
| overlap with the historical 09-09 identifier set | 276 of 402 historical ids reappear; 41 new, 126 not re-observed |
| candidates listed, all UNSCREENED | 22 (keyword triage score >= 4, anchors excluded) |
| patents | not queried — no patent database reachable |

Anchor overlap is a bounded identifier-overlap observation, not recall: the denominator is the
known comparable anchor set, which the 09-09 review found incomplete. Counts drift as the
databases grow; the provenance property (0 unlogged rows) is the reproducible fact.

### Query legs, in the order executed

| db | query | status | n |
| --- | --- | --- | --- |
| crossref | `PX4 ArduPilot failsafe differential testing` | ok | 40 |
| openalex | `PX4 ArduPilot failsafe differential testing` | ok | 17 |
| crossref | `PX4 ArduPilot recovery benchmark` | ok | 40 |
| openalex | `PX4 ArduPilot recovery benchmark` | ok | 50 |
| crossref | `UAV autopilot failsafe configuration testing fuzzing` | ok | 40 |
| openalex | `UAV autopilot failsafe configuration testing fuzzing` | ok | 18 |
| crossref | `UAV communication loss contingency recovery contract` | ok | 40 |
| openalex | `UAV communication loss contingency recovery contract` | ok | 50 |
| crossref | `multicopter failsafe behaviour conformance testing simulation` | ok | 40 |
| openalex | `multicopter failsafe behaviour conformance testing simulation` | ok | 2 |
| arxiv | `PX4 ArduPilot failsafe` | ok | 0 |
| arxiv | `PX4 ArduPilot testing` | ok | 5 |
| arxiv | `ArduPilot fuzzing` | ok | 2 |
| arxiv | `UAV failsafe recovery contingency` | ok | 0 |
| arxiv | `multicopter autopilot conformance testing simulation` | ok | 0 |
| arxiv | `UAV communication loss contingency recovery` | ok | 0 |

The 4 arXiv legs with `n = 0` are genuine zero-result queries, not disguised
throttling: each was re-issued independently with `max_results=1` on 2026-09-11 and the feed's
`opensearch:totalResults` was 0 in every case. The tool ANDs every term (`all:t1 AND all:t2 ...`),
which is restrictive by design; loosening the query set would be a protocol amendment, not a fix.

## Files (sha256)

| file | sha256 |
| --- | --- |
| `database-export.json` | `cdbcad43887528f75bb086eba4f8b044f52ed0c200f93563ef9d702a2355c19a` |
| `database-export.csv` | `2828e56e6ed851fc6e3c159500323258b46aac16377b1cad600e0161eaf40528` |
| `candidates-unscreened.csv` | `0981aef174245ab167f6cfc1045528ae5f6f8ce1c6911aad7313e0324baef960` |
| `export-audit.json` | derived offline from `database-export.json` by `rerun_search.py --audit` |

## Reproduce and verify

```sh
# offline audit of this acquisition (expected exit 0; 0 unlogged rows)
python evidence/task-2026-09-09/rerun_search.py --audit evidence/task-2026-09-11/database-export.json
# regression test pinning the property
python -m unittest discover -s tests -p test_search_export.py -v
python scripts/check_repo_contract.py
# a NEW acquisition (path must not exist; OPENALEX_API_KEY in env, never in a committed command)
OPENALEX_API_KEY=... python evidence/task-2026-09-09/rerun_search.py --out evidence/task-<date>
```

## Relationship to the historical export and the day-3 ledger

The 09-09 export, CSV and candidate list are unchanged. The day-3 acquisition ledger
(`scripts/acquisition_ledger.py`, `evidence/task-day3-2026-09-09/acquisition-ledger.json`)
still reads the historical export and is **not** regenerated from this one: merging rows from
two runs is the defect this directory corrects. Any future ledger that consumes this export must
consume it whole, with its own query log, as a separately dated route.

Run from the sandbox on 2026-09-11 with Python 3 and no credential value written to disk or logs.
