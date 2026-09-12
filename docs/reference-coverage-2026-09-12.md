# Reference coverage and closest-competitor review — 2026-09-12 (URC-R02)

Closes the reconciliation that URC-D02/D03 left open. Every day-1 source is accounted for, the
coverage number is computed by a committed script, and the competing-work statement below is
tied to sections actually read. No novelty gate, patent question or owner gate is closed by this.

## 1. Every original reference accounted for

`docs/source-eligibility-register.json` lists all 12 day-1 sources with identifiers resolved from
primary metadata and an explicit eligibility decision. `scripts/reference_coverage.py` computes
recall from it against both database exports under every identifier alias (arXiv id, arXiv DOI,
publisher DOI); `--check` fails if the committed result drifts.

| | count | ids |
|---|---:|---|
| day-1 sources | 12 | U1–U12 |
| eligible for a scholarly-database export | 6 | U1, U2, U4, U5, U10, U11 |
| not eligible (stated, not dropped) | 6 | U3 code repo · U6–U9 vendor docs · U12 patent |
| **recovered by day-2 historical export** | **2/6** | U2, U4 |
| **recovered by day-4 public export** | **3/6** | U2, U4, U5 |
| missed by both | 3 | U1 Avis (not in OpenAlex), U10, U11 |

**Correction to earlier figures.** Day 2 reported 0/6 and day 4 reported 2/5. Both anchor sets
carried arXiv ids only, so PGFuzz (retrieved by both exports as `doi:10.14722/ndss.2021.24096`)
and the published RouthSearch (`doi:10.1145/3728904`, retrieved by both) were never credited, and
the two denominators were not the same set. The historical export's provenance defect (90 rows
without a logged query) is unchanged and that export stays rejected; this correction is about how
its recall was *counted*, not about repairing it. The qualitative day-2 conclusion survives —
the two discovery routes still surface different populations — but the gap is 3 of 6, not 6 of 6.

## 2. Closest-competitor review, per rubric axis

Reading records for all 12 sources are in `docs/day3-reading-records.json` (7 added today, U7/U8
re-inspected with exact locators and text hashes). Grades and aboutness follow
`docs/day3-reading-rubric.md`. Text hashes of the fetched copies are in `evidence/task-2026-09-12/`.

| axis | what competing work already establishes | source | consequence for the claim |
|---|---|---|---|
| Equivalent recovery intention across pinned configurations | Nothing inspected states or tests intent equivalence across autopilots/configurations. PGFuzz's 56 policies are per-autopilot propositions (A.RC.FS2, PX.GPS.FS1 …); U11 writes a link-loss → RTB *contract* for one architecture; U6 evaluates one configuration's action at a time. | U2 §I, Table II · U11 §III-C eq. 6 · U6 | **Gap holds** on inspected sources. U11 is the nearest neighbour in form and must be cited. |
| Distinct liveness vs. setpoint failure injection | Both vendors document that heartbeat/proof-of-life and setpoint streams are separate (PX4 `COM_OF_LOSS_T` vs OffboardControlMode; ArduPilot `FS_GCS_TIMEOUT` vs the 3 s Guided setpoint stop). No inspected paper injects them as distinct faults. | U7 · U9 · U8 · U2 §VI | **Gap holds**, and the distinction is *vendor-documented*, which strengthens the motivation. |
| Behaviour when commands return | ArduPilot documents "will remain in its failsafe mode … will not automatically return". PX4's Offboard page says nothing about resumption. The EP patent discloses waiting for a user command after reconnect. No paper evaluates it. | U8 · U7 · U12 | **Narrows**: the ArduPilot side is documented behaviour, not a research finding; the claim must be *cross-autopilot comparison under pinned configs*, not "unstudied". |
| Calibrated whole-trajectory coverage | PGFuzz's distance is proximity to one policy violation; RouthSearch's oracle is per-mode trajectory shape; Avis compares to profiling runs. None is calibrated recovery-trajectory coverage. | U2 §I · U4 §4.3 · U1 | **Gap holds** on inspected sources. |

**Statement of what competing work establishes.** Policy-guided fuzzing of autopilots (PGFuzz)
and its successors establish that configuration parameters and commands can drive an autopilot
into failsafe-policy violations, and give a distance-metric method to find them. Vendor docs
establish that link loss and setpoint loss are separate timeouts with separately parameterised
actions, and (ArduPilot) that mode is not restored on reconnection. A contract-form link-loss
recovery intention exists in a 2026 swarm architecture paper. What none of the inspected work
does is fix a recovery intention, pin two autopilot configurations that are supposed to realise it,
inject liveness and setpoint loss separately, and compare the realised trajectories including the
command-return phase against a calibrated coverage measure.

## 3. Explicitly unresolved

- Crossref surfaced three 2026 successors not in the day-1 set — ADGFuzz (NDSS 2026,
  `10.14722/ndss.2026.231014`), UAVConfigFuzzer (`10.14722/fuzzing.2026.23009`) and PGPatch
  (S&P 2022). They are **unscreened**; UAVConfigFuzzer's title puts it on axis 1 and it must be
  read before any novelty statement is published.
- U12's claims were read as public text only; that is not legal clearance.
- The arXiv API returned 429 on every id_list call today; identifiers were resolved via OpenAlex
  and Crossref instead, and the arXiv HTML pages were fetched directly. Avis (U1) is not indexed
  in OpenAlex, so no database leg could have recovered it.
- The historical export's unlogged rows remain rejected; URC-D02 stays as the day-4 review left it.


## Review repair (URC-R02b, same day) — one provenance-bound record, axes tied to inspection

**Provenance.** Coverage now credits an export only for hits traceable to a logged successful query. The 2026-09-09 export has 90 of 402 rows with no such line (all arXiv, from the throttled re-run); they are excluded from credit and the export is marked **rejected** and retained. The 2026-09-11 public export is provenance-clean (317/317) and is the **canonical** record. Recall is unchanged by the exclusion — none of the anchor hits was among the untraceable rows — but the number is now bound to what the export can show it searched. `URC-D02` is closed against this record; no successor task was created.

**Novelty axes, by inspection status.** `narrowed_by_disclosure` = an inspected source discloses the axis; `supported_bounded` = no inspected source discloses it, with the unresolved sources named; nothing is "supported" by an abstract.

| axis | status | disclosed by | not found in inspected sections of | unresolved for |
|---|---|---|---|---|
| `equivalent_intent` | **narrowed_by_disclosure** | U6, U11 | U1, U5, U7, U12, U2, U4, U9, U10 | U3 |
| `reconnection` | **narrowed_by_disclosure** | U8, U12 | U1, U5, U7, U2, U4, U6, U9, U10, U11 | U3 |
| `coverage` | **supported_bounded** | — | U1, U5, U12, U2, U4, U6, U9, U10, U11 | U3 |
| `liveness_vs_setpoint_injection` | **narrowed_by_disclosure** | U9 | U2, U4, U6, U10, U11 | U3 |

What this measures: overlap with a small known-reference set and disclosure in the sections inspected. It is not exhaustive literature recall and not established novelty.
