# Literature review acquisition — 2026-09-22

Branch `task/literature-2026-09-22` off main `674790f`. Deliverable: [literature/](../../literature/).
Machine-readable acquisition record: [acquisition.json](acquisition.json).

**Evidence state: literature.** No study result, no simulation, and no claim about any source that was not read.

## The owner's amendment

This repository froze a standing rule of **no new broad literature search** on 2026-09-15, when the prior-art
packet closed with URC-01 partial. The owner lifted it for this task on 2026-09-22. The rule stands for
everything else; a future broad search needs its own amendment.

## What was executed

A frozen plan of 21 queries across eight axes, run through the same collectors as the canonical prior-art
export (`evidence/task-2026-09-09/rerun_search.py`), so the acquisition carries the same guarantees: every hit
records its database, query and rank, and the SHA-256 of the raw response it came from.

| | |
|---|---|
| legs planned | 53 (Crossref 21, OpenAlex 21, arXiv 11) |
| legs succeeded | 47 |
| legs incomplete | 6, all OpenAlex, HTTP 429 |
| identifier records | 1546 |
| native-response audit | every failure key zero: no unsupported route, no missing request provenance, no response-record or count mismatch, no unlogged row |

The six throttled OpenAlex legs were re-issued as a **separate** export and throttled again. The two exports
are never merged: that is the defect the 2026-09-11 correction exists to prevent. All six queries were also
run against Crossref, so no axis lost its only source.

Canonical works that the query plan did not surface were resolved by **bounded identity lookup**, not by a new
discovery leg: a Crossref bibliographic query per work, first five results, with the raw response retained.
That is the same distinction the prior-art packet drew.

## Honest limits

- **54 of 55 register entries have a verified identifier; 45 of them have not been read.** The register marks
  every entry's access, and nothing in it claims what an unread work shows. A test enforces that.
- One entry, the robotic-vehicle accident root-cause paper, is **unresolved**: it is absent from Crossref and
  the guessed conference URL returned 404. It stays on the list as unresolved rather than being dropped or
  given a plausible identifier.
- Two works are USENIX Security papers with **no Crossref DOI**; their conference pages were confirmed to
  resolve and the identifier source says so.
- The feature-interaction queries returned heavy noise from computer vision, where "feature interaction" means
  something else entirely. That is a property of the term, and it is why the axis was screened by hand.
- **This review does not change URC-01.** The frozen denominators, the eligibility register and the coverage
  numbers are untouched. Where a register entry corresponds to an unread row from the earlier intake, the
  mapping is recorded so a later task can resolve it deliberately.

## Checks observed

| command | result |
|---|---|
| `python -m unittest discover -s tests -q` | OK, 98 tests (7 new) |
| `python scripts/check_repo_contract.py` | PASS |
| `python scripts/acquisition_ledger.py --check` | consistent |
| `python scripts/reference_coverage.py --check` | OK, 0/6 and 3/6, unchanged |
| `python tools/check_presentation.py . "UAV Failsafe Composition" uav-failsafe-composition` | no issues |
| `python tools/test_presentation.py` | OK |
| `git diff --check` | clean |
