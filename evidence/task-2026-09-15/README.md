# URC-R03 — successors screened, U3 re-inspected, URC-01 closeout — 2026-09-15

**Superseded the same day** by [task-prior-art-closeout-2026-09-15](../task-prior-art-closeout-2026-09-15/README.md) (replacement plan, PR #13): the result paragraph below no longer holds. Kept as the record of PR #14.

Branch `task/prior-art-closeout-20260914` off `main` bf4d4a7 (plan merged as PR #12; the plan named 09-14, execution was 09-15). Plan: [docs/specs/prior-art-closeout/plan.md](../../docs/specs/prior-art-closeout/plan.md). Deliverables: [prior-art.md § URC-01 closeout](../../docs/prior-art.md#urc-01-closeout--2026-09-15), [reference-coverage 2026-09-15 subsection](../../docs/reference-coverage-2026-09-12.md#2026-09-15-morning--successors-screened-u3-re-inspected-urc-r03-superseded-the-same-day), records in `docs/day3-reading-records.json`.

## Texts inspected (SHA-256 in [fetched-text-hashes.json](fetched-text-hashes.json))

| id | source | route | access |
|---|---|---|---|
| S1 | UAVConfigFuzzer, FUZZING 2026 (`10.14722/fuzzing.2026.23009`) | Crossref `resource.primary` → ndss-symposium.org PDF, HTTP 200 | full text, 10 pp |
| S2 | ADGFuzz, NDSS 2026 (`10.14722/ndss.2026.231014`) | Crossref `resource.primary` → ndss-symposium.org PDF, HTTP 200 | full text, 20 pp |
| S3 | PGPatch, IEEE S&P 2022 (`10.1109/sp46214.2022.9833567`, resolved by Crossref bibliographic query) | OpenAlex `oa_status=closed`; Semantic Scholar `openAccessPdf` empty; IEEE landing HTTP 202 (bot-blocked); author page kimhyungsub.github.io → `S&P22_hskim.pdf`, HTTP 200, authors match Crossref | author-posted full text, 20 pp |
| U3 | PGFuzz code, github.com/purseclab/PGFuzz | shallow clone, commit `7eaebf21116087249b8329d4ba7337a24a34ecb9` (2023-09-18), 1327 files; read, not executed | repository tree and source |

Text extraction: `pdftotext -layout`; hash over the UTF-8 text; PDF byte hashes also recorded. Successors are S-ids in the reading records only; the day-1 register is unchanged (a test pins it to the day-1 set).

## Result
No axis is `unresolved`. Every axis is `narrowed_by_disclosure` by a day-1 source taken alone; S1–S3 and U3 add `not_found_in_inspected` on every axis except U3 `coverage` (`disclosed_or_addressed`, same as U2). The prior-art conclusion is written in the two allowed forms: prior art found per axis; supported candidate gap, bounded, for the composed claim. Patent databases were not searched (no route). No owner gate closed; URC-S08 unchanged.

Correction recorded: the axis table in the coverage doc had lagged the JSON since the 2026-09-13 `axis_states` repair (`coverage` was already `narrowed_by_disclosure`); the table is now re-copied from script output.

## Checks observed
| command | observed |
|---|---|
| `python -m unittest discover -s tests` | Ran 40 tests, OK |
| `python scripts/check_repo_contract.py` | PASS |
| `python scripts/reference_coverage.py --check` | OK, day2 0/6, day4 3/6 (unchanged) |
| `python scripts/acquisition_ledger.py --check` | consistent (regenerated from the records) |
| `python tools/check_presentation.py . "UAV Failsafe Composition" uav-failsafe-composition` | no issues |
| `python tools/test_presentation.py` | OK |
| negative control: delete the S1 record | `reference_coverage --check` exit 1 and `acquisition_ledger --check` exit 1, as required; restored |
| `git diff --check` | clean |

## Not done
No new search legs; no patent, dissertation or standards search; no novelty verdict; no owner gate. PGPatch's publisher copy was not obtained; the author-posted text was read instead and its provenance is stated.
