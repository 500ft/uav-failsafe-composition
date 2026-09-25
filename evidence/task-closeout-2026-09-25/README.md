# Closeout ledger — 2026-09-25

Branch `task/identity-and-contracts-2026-09-25`, stacked on the WP0 commit in PR #29. Implements
`TODAY-CLOSEOUT-PLAN-2026-09-25.txt`. **Evidence state: engineering work plus one bounded literature audit. No
simulator, oracle, checker or flight ran today.**

## Ledger

| package | criterion | artifact | check identity | status | remaining dependency |
|---|---|---|---|---|---|
| WP0 | PR #29's three defects corrected with discriminating checks; history preserved | `harness/trace.py`, `harness/verify.py`, `harness/reproducibility.py`, `protocols/event-semantics.md` | 130 tests at the WP0 commit | **complete** | none |
| WP1 | scenario, execution and analysis identity separated; all ten captures accounted for | `harness/identity.py`, `evidence/task-measurement-repair-2026-09-24/legacy-captures.json` | `tests/test_identity.py`, 13 cases | **complete** | complete parameter snapshot needs a new run |
| WP2 | every property carries its full contract; one query per obligation; two verdict vocabularies | `protocols/unsafe-composition-properties.json` | `tests/test_unsafe_properties.py` | **partial** | U1 and U4 timing components are not yet evaluable; U2 is unobservable in SITL |
| WP3 | shared delay pot implemented with source locators and six discriminating fixtures | `model/px4_failsafe.py`, `tests/test_shared_delay_memory.py` | 8 cases | **partial** | transcription self-check only; differential validation needs the oracle |
| WP4 | every targeted row has an explicit intent disposition | `literature/register.json`, `literature/identity-audit.json` | `tests/test_literature_register.py` | **complete** | 4 rows stay unresolved; no paper is marked read |
| Oracle | executed pinned output, or a specific documented blocking result | `oracle/run_native_failsafe_test.sh`, `.github/workflows/oracle.yml` | not run | **blocked** | needs one manual dispatch; nothing here claims it builds |

## What the numbers are

| item | value | what it means |
|---|---|---|
| stored captures inventoried | 10 | 5 controls including 1 invalid, 5 injected |
| captures with a unique alias | 10 | legacy ids repeat; the alias is id plus raw content hash |
| ambiguous legacy ids | 2 | reported, never collapsed |
| declared cases in the pinned failsafe test | 9 | read from `failsafe_test.cpp` at `d6f12ad`, not from upstream docs |
| literature rows dispositioned | 55 of 55 | 41 match intent, 8 previously verified, 4 unresolved, 2 corrected |

## Three identity defects the register has now produced

L32 was a cell-biology thesis standing in for the Simplex paper, found by the owner. L43 had the right
identifier and a paraphrased title, found by the machine check. L53's title carried an HTML-escaped ampersand
from the acquisition response, found by this audit. All three keep their erroneous record under
`quarantined_identifier`. None of the three was catchable by the same check.

## The scientific question is unchanged

No expected post-injection recovery-mode transition was observed and no new failsafe announcement was seen.
The internal selected action and its cause remain unresolved. Today's work makes that statement trustworthy
and narrows what could still explain it. It does not explain it.

Two consequences are worth repeating because they limit every future timing claim from this apparatus:

- The injection instant has no defensible upper bound, so **no development run here can produce a passing
  timing verdict**. Discrete comparisons still decide, and an empty response window is still sound.
- The selector is on no channel this rig records, so U2 and U3 cannot be evaluated in SITL at all. They are
  specified, and their observers are the model fixtures and the native oracle.

## What would close the next step

One manual dispatch of `native-failsafe-oracle`. Success gives layer B of the differential and lets the WP3
fixtures be checked against the real class rather than against my transcription. Failure is recorded as an
environment result and closes the environment question for now without touching Study A.
