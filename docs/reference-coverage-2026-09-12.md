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
| **recovered by day-2 historical export** | **2/6** (superseded 2026-09-13: the export fails the native-response audit and is credited **0/6**) | U2, U4 |
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

**Superseded 2026-09-15 (evening)** by the reconciled table in the last section; kept for the record.

| axis | status | disclosed by | not found in inspected sections of | unresolved for |
|---|---|---|---|---|
| `equivalent_intent` | **narrowed_by_disclosure** | U7, U6, U11 | U1, U5, U12, U2, U9, U3, S1, S2, S3 | — |
| `reconnection` | **narrowed_by_disclosure** | U8, U12 | U1, U5, U7, U2, U4, U6, U9, U11, U3, S1, S2, S3 | — |
| `coverage` | **narrowed_by_disclosure** | U1, U2, U4, U6, U9, U3 | U5, U12, U11, S1, S2, S3 | — |
| `liveness_vs_setpoint_injection` | **narrowed_by_disclosure** | U9, U11 | U2, U4, U6, U3, S1, S2, S3 | — |

What this measures: overlap with a small known-reference set and disclosure in the sections inspected. It is not exhaustive literature recall and not established novelty.

## 2026-09-15 (morning) — successors screened, U3 re-inspected (URC-R03, superseded the same day)

**Superseded** by the reconciled section below (replacement plan, PR #13): the axis table and the sentence "no axis is unresolved any more" here no longer hold, because the clarified axis definitions changed 18 judgments and 17 unread intake rows are now visible as unresolved.

Records added to `docs/day3-reading-records.json` (each with the SHA-256 of the text actually read, in
[evidence/task-2026-09-15/fetched-text-hashes.json](../evidence/task-2026-09-15/fetched-text-hashes.json)):

- **S1 UAVConfigFuzzer** (FUZZING 2026 registered report, full text). PX4-only configuration fuzzing with a
  reused setpoint generator; oracles are mission deviation, vertical-velocity fluctuation and "interruption".
  No failsafe, link, heartbeat or reconnection content anywhere in the text. Axis 1 threat from the title does
  not materialise: **not found** on all four axes.
- **S2 ADGFuzz** (NDSS 2026, full text). ArduPilot-only (Copter/Plane/Rover SITL). Heartbeat absence is a
  crash *oracle*, not an injected fault; one Rover bug is a fence-without-RTL failsafe defect found as a bug
  instance. **Not found** on all four axes.
- **S3 PGPatch** (S&P 2022, author-posted full text; publisher copy closed). Per-autopilot fail-safe
  formulas (PX4 GPS, ArduPilot battery→RTL, Paparazzi FailSafe) are the nearest neighbour *in form* to a
  recovery contract, but nothing is defined or compared across autopilots or pinned configurations.
  **Not found** on all four axes.
- **U3 PGFuzz code** re-inspected at commit `7eaebf2` (read, not run). Separate ArduPilot/ and PX4/ trees with
  separate hard-coded policy lists, including RC/GPS fail-safe policies; heartbeat absence (5 s) triggers a
  simulator reboot as a crash oracle; per-policy distance guidance matches U2. `coverage` **disclosed** (same
  as U2), the other three axes **not found**. No axis is unresolved any more.

The axis table above was re-copied from `reference_coverage.py` output. Note for the record: the table
committed on 2026-09-13 still showed `coverage` as `supported_bounded`, while the JSON already classified it
`narrowed_by_disclosure` (U1, U2, U4, U6, U9) after the explicit `axis_states` repair. The JSON was right; the
prose lagged. Nothing in today's records changed that status.

What this still is not: exhaustive recall, patent clearance, or established novelty. The URC-01 conclusion
that these records support is written in [prior-art.md](prior-art.md#urc-01-closeout--2026-09-15).

## 2026-09-15 (reconciled) — current axis table under the replacement plan (URC-R03)

Generated by `scripts/reference_coverage.py` after the T03 consumer fixes (unread access and missing axes are
unresolved, all four axes scored for every record) and the T10 reconciliation against re-opened primary
locators. Register byte-identical; canonical export unchanged; known-reference coverage still
**3/6** (public) and **0/6** (historical, audit-failed). Coverage of a 6-source anchor set is not literature
relevance or global recall.

| axis | status | disclosed by | not found in inspected sections of | not applicable | unresolved for |
|---|---|---|---|---|---|
| `equivalent_intent` | **supported_bounded** | — | U1, U5, U7, U8, U12, U2, U6, U9, U11, U3, S1, S2, S3 | U4, U10 | C001, C087, C158, C180, C186, C214, C228, C004, C005, C021, C135, C166, C182, C218, C219, C225, C266 |
| `reconnection` | **narrowed_by_disclosure** | U8, U12 | U1, U5, U7, U2, U4, U6, U9, U11, U3, S1, S2, S3 | U10 | C001, C087, C158, C180, C186, C214, C228, C004, C005, C021, C135, C166, C182, C218, C219, C225, C266 |
| `coverage` | **supported_bounded** | — | U1, U5, U7, U8, U12, U2, U4, U6, U9, U11, U3, S1, S2, S3 | U10 | C001, C087, C158, C180, C186, C214, C228, C004, C005, C021, C135, C166, C182, C218, C219, C225, C266 |
| `liveness_vs_setpoint_injection` | **narrowed_by_disclosure** | U7, U9 | U1, U5, U8, U12, U2, U4, U6, U11, U3, S1, S2, S3 | U10 | C001, C087, C158, C180, C186, C214, C228, C004, C005, C021, C135, C166, C182, C218, C219, C225, C266 |

**Judgments changed 2026-09-15 (old → new, each with the re-opened locator; full list in
[decision-changes.json](../evidence/task-prior-art-closeout-2026-09-15/decision-changes.json)):**

| source | axis | old | new | reason | locator |
|---|---|---|---|---|---|
| U1 | `coverage` | disclosed_or_addressed | not_found_in_inspected | clarified coverage definition: a state-deviation invariant vs profiling runs (threshold tau, eq. 1) is a distance-to-profile oracle, not calibrated whole-recovery-trajectory containment | Sec. IV-C, eq. (1): 'for all i: d(S_F,t, S_i,t) > tau'; normalised per-component distances |
| U1 | `liveness_vs_setpoint_injection` | (missing) | not_found_in_inspected | axis was missing; fault model is sensor-instance failure, no link/heartbeat or setpoint-loss stimulus | Sec. IV (fault scenarios: subsets of sensor instances failing; 'Avis injects faults at t2 as it did at t1') |
| U2 | `coverage` | disclosed_or_addressed | not_found_in_inspected | clarified coverage definition excludes policy-distance scores | Sec. I and Sec. V-B: global distance (negative = violation) and propositional distances guide mutation toward  |
| U4 | `coverage` | disclosed_or_addressed | not_found_in_inspected | clarified coverage definition excludes per-mode MTL oracles | Sec. 4.3 Misbehavior Validation, eq. (8) and the RTL-ascent MTL formula |
| U5 | `liveness_vs_setpoint_injection` | (missing) | not_found_in_inspected | axis missing or unassessed; whole HTML re-read by keyword (fail-safe, link loss, heartbeat, setpoint, reconnect, coverage): none describe a stimulus or endpoint | Whole HTML v2: Sec. IV-A integrations table (PX4, ArduPilot, MAVROS, Zenoh); architecture figure (autopilot_in |
| U6 | `equivalent_intent` | disclosed_or_addressed | not_found_in_inspected | clarified definition: making one configuration's action explicit is related work, not equivalence of a stated intention across identified configurations | Whole page: embedded failsafe simulator ('configure the parameters on the left'), note that delayed action COM |
| U6 | `coverage` | disclosed_or_addressed | not_found_in_inspected | prose said 'none: static decision table' while the state was affirmative; static action tables are excluded by the clarified definition | Whole page: the simulator output is a static action table per parameter set |
| U7 | `equivalent_intent` | disclosed_or_addressed | not_found_in_inspected | the earlier affirmative state carried a liveness finding under the wrong axis | Technical Summary; Mode Requirements |
| U7 | `liveness_vs_setpoint_injection` | (missing) | disclosed_or_addressed | documented distinction between a proof-of-life stream and setpoint topics (specification, not experiment) | Technical Summary: 'continuous 2Hz proof of life signal'; 'exit Offboard mode if ... messages stop being recei |
| U7 | `coverage` | (missing) | not_found_in_inspected | axis was missing | Whole page: no coverage or trajectory-containment endpoint |
| U8 | `liveness_vs_setpoint_injection` | (missing) | not_found_in_inspected | axis was missing; heartbeat loss alone does not establish the liveness-vs-setpoint distinction | 'The GCS failsafe monitors the time since the last MAVLink heartbeat from the GCS. If no heartbeat is received |
| U8 | `coverage` | (missing) | not_found_in_inspected | axis missing | Whole page |
| U8 | `equivalent_intent` | (missing) | not_found_in_inspected | axis missing or unassessed | Whole page: FS_GCS_ENABLE actions and FS_OPTIONS bits for one autopilot |
| U9 | `coverage` | disclosed_or_addressed | not_found_in_inspected | prose said 'none' while the state was affirmative | Whole page |
| U11 | `liveness_vs_setpoint_injection` | disclosed_or_addressed | not_found_in_inspected | clarified definition: heartbeat loss alone does not establish the distinction | Sec. III-C Communication Contract C_comm (heartbeat timestamp + SNR -> Return-to-Base); 'The FMU monitors the  |
| U11 | `equivalent_intent` | disclosed_or_addressed | not_found_in_inspected | clarified definition: a contract stating one architecture's intention is related work, not equivalence across identified configurations | Sec. III-C eq. (6) Communication Contract; Sec. V-D ConOps verification |
| U12 | `liveness_vs_setpoint_injection` | (missing) | not_found_in_inspected | axis was missing; the disclosure concerns loss of the radio link to the home location | Claims 1-3 and description (communication failure due to obstruction of line-of-sight; signal-quality threshol |
| U3 | `coverage` | disclosed_or_addressed | not_found_in_inspected | clarified definition excludes policy-distance scores (same reason as U2) | ArduPilot/update_distance.py (per-policy altitude/roll/pitch/heading error); ArduPilot/fuzzing.py print_distan |

**Unread candidates now visible** (metadata-only screen of all 317 canonical rows,
[candidate-screening.csv](../evidence/task-prior-art-closeout-2026-09-15/candidate-screening.csv); their
full-text reading is named next work, not part of this packet):

| id | intake row | decision | title |
|---|---|---|---|
| C001 | row 0 | needs_full_text | SAFLITE: Fuzzing Autonomous Systems via Large Language Models |
| C087 | row 86 | needs_full_text | VIGOR: Distributed Multi-UAV Exploration with Connectivity Recovery in Communication-Limit |
| C158 | row 157 | needs_full_text | Model-based System Health Management and Contingency Planning for Autonomous UAS |
| C180 | row 179 | needs_full_text | Self-Adaptive Mechanisms for Misconfigurations in Small Uncrewed Aerial Systems |
| C186 | row 185 | needs_full_text | A Smart Contract-Based Algorithm for Offline UAV Task Collaboration: A New Solution for Ma |
| C214 | row 213 | needs_full_text | Resilient Drone Swarm Control: Manual Leader-Follower Architecture with Autonomous Failove |
| C228 | row 227 | needs_full_text | Reconfigurable Mission Plans for RPAS |
| C004 | row 3 | unresolved_metadata | Flight log analysis and recovery for open-source drones: Focusing on ArduPilot, PX4, and B |
| C005 | row 4 | unresolved_metadata | A Universal Large Language Model -- Drone Command and Control Interface |
| C021 | row 20 | unresolved_metadata | UAV Trajectory Management: Ardupilot Based Trajectory Management System |
| C135 | row 134 | unresolved_metadata | Control-Aware Manipulation of ArduPilot via Legitimate MAVLink Commands: Simulation and Ha |
| C166 | row 165 | unresolved_metadata | ConfuSense: Sensor Reconfiguration Attacks for Stealthy UAV Manipulation |
| C182 | row 181 | unresolved_metadata | Automated Identification and Qualitative Characterization of Safety Concerns Reported in U |
| C218 | row 217 | unresolved_metadata | A Requirements-Driven Platform for Validating Field Operations of Small Uncrewed Aerial Ve |
| C219 | row 218 | unresolved_metadata | LLM-Agents Driven Automated Simulation Testing and Analysis of small Uncrewed Aerial Syste |
| C225 | row 224 | unresolved_metadata | Automated system-level testing of unmanned aerial systems |
| C266 | row 265 | unresolved_metadata | Applying Formal Methods to Build a Safe Continuous-Control Architecture for an Unmanned Ae |

What this measures: overlap with a small known-reference set and disclosure in the sections inspected. It is
not exhaustive recall and not established novelty. The URC-01 decision derived from it is in
[prior-art.md](prior-art.md#urc-01-decision--2026-09-15-replacement-plan).
