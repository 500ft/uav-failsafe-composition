# Evidence-gap correction

Status: in-progress. Frozen before clean acquisition, 2026-09-11.

Scope: repair observable acquisition provenance, execute a new bounded native
export, preserve invalid historical exports and withdrawals, and report partial
versus blocked acceptance without changing research/disclosure gates.

Baseline: clean requested main; 21 tests, contract and acquisition-ledger check
pass using `python` (/Users/redhose/ENTER/bin/python). System `python3` lacks
jsonschema; it is not the selected validation interpreter.

Gates: no separate configured typecheck/lint/build. Run `python -m unittest
discover -s tests -q`, `python scripts/check_repo_contract.py`, `python scripts/
acquisition_ledger.py --check`, CI presentation checks and `git diff --check`.

## Frozen procedure

Use exactly the ordered (database, query) pairs in the retained historical
database-export.json query_log. Do not add query legs based on new hits. Caps:
Crossref 40, OpenAlex 50, arXiv 60; no pagination. arXiv all-token AND semantics,
HTTPS transport; at most two attempts for 429, 8-second retry, 4-second inter-leg
delay (other databases 1 second). Request timeout 30 seconds. OpenAlex without
configured key is unavailable, not zero results. Retain request UTC, redacted
route, HTTP status, response bytes/hash and successful raw response text, plus
query observed counts, all identifier routes and selected-abstract provenance.

Known anchors remain the pre-existing D01_ANCHORS constants, selected from day-1
stable scholarly identifiers before this rerun. They are an incomplete reference
set: report exact overlap only, not recall; exclude patent/specification/code
entries from the scholarly denominator. Unresolved scholarly identifiers remain
unresolved, not silently excluded to improve recall. No post-result anchor edits.
New outputs: evidence/task-2026-09-11-clean/. Preserve all old JSON/CSV unchanged.

## Tasks

- [x] Verify clean baseline and freeze this plan before implementation/network.
- [ ] Regress missing request audit trail and ambiguous richer-abstract source;
  minimally repair, verify tests before acquisition.
- [ ] Execute frozen pairs against actual APIs; audit all routes/counts/response
  hashes. No synthetic data or placeholders in acquired hits.
- [ ] Update D02 and precise Agent-owned remaining public reading work; distinguish
  credentials/access blockers from unfinished reading and owner-only gates.
- [ ] Run full gates, retain detailed report and commit; no push/merge.
