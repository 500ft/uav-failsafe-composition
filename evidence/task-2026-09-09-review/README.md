# URC-D02 review correction — 2026-09-09

Review base: `8e1d06cb00d65e60633678701bdb697814120f6a`; branch `review/day-two-20260909`.
This is an offline developer review, not independent scientific validation.
[Corrected interpretation](../../docs/prior-art-search-2026-09-09-database.md);
[derived audit](export-audit.json). The original export JSON, export CSV and
candidate CSV remain byte-identical to the review base.

## Checks observed

Working directory: repository root; Python 3.11.8. CI defines the contract
checker and unittest suite; no separate typecheck, formatter or build is configured.

| Command / case | Observed |
| --- | --- |
| Original `python -m unittest discover -s tests -v` | exit 0; 7 tests |
| Original `python scripts/check_repo_contract.py` | exit 0; PASS |
| New tests before implementation, `python -m unittest discover -s tests -p test_search_export.py -v` | exit 1; 8 errors for missing safety/audit APIs |
| Same targeted command after implementation | exit 0; 8 tests |
| `python -m compileall -q tests evidence/task-2026-09-09/rerun_search.py` | exit 0 |
| Historical export audit below | exit 1, expected: 90 unmatched provenance rows |
| Final full suite and contract (parent rerun) | exit 0; 15 tests; contract PASS |

Synthetic regressions exercise DOI/arXiv alias normalization, missing-key versus
empty search, repeated-hit provenance, partial generator failure, three output
files, overwrite prevention before network, historical provenance detection,
and exact recorded database/query scheduling. No online query, full-text reading
or source-quality judgment is implied.

## Reproduction and next action

```sh
python -m unittest discover -s tests -v
python scripts/check_repo_contract.py
python evidence/task-2026-09-09/rerun_search.py --audit evidence/task-2026-09-09/database-export.json
git diff --check
```

The audit's exit 1 is a finding in the historical evidence, not a failed repair.
For a **new**, separately recorded live acquisition after provenance/anchor review:

```sh
python evidence/task-2026-09-09/rerun_search.py --out /tmp/urc-new-search-20260909
```

The path must not exist. OpenAlex requires `OPENALEX_API_KEY` in the environment;
never include its value in committed commands or logs. A missing key or any
incomplete leg records its state and exits 2, not a success with zero findings.
The rerun does not reconstruct the missing old requests. D02 remains blocked
until provenance is reconciled and the eligible anchor register reviewed.
