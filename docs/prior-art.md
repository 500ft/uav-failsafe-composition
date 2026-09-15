# Prior-Art Boundary

## 2026-09-08 source review

[Dated exact-gap/tooling review](prior-art-search-2026-09-08.md) records executed
queries, 12 selected primary entries, overlap judgments and access limitations.
Prior art is confirmed for broad ingredients; the narrow dataset contribution
remains a supported candidate gap within this retrieval, not established novelty.
URC-D01 completes this first pass; full URC-01 closeout remains pending.
The most consequential protocol correction is to distinguish setpoint loss,
GCS-heartbeat loss and process termination before pinning equivalent intentions.

This is a scoped source map, not a claim of an exhaustive systematic review. Sources are included to define what this project must **not** claim as new.

## Established ingredients

| Area | Source | What it establishes for this project |
| --- | --- | --- |
| Configurable PX4 failsafes | [PX4 Safety / Failsafes](https://docs.px4.io/main/en/config/safety) | Failsafe actions and delays depend on configuration; “PX4 behavior” is not a single intrinsic response. |
| Configurable ArduPilot failsafes | [ArduPilot GCS Failsafe](https://ardupilot.org/copter/docs/gcs-failsafe.html) | Recovery action and mode behavior are parameter- and state-dependent. |
| Failure-injection tooling | [PX4 Failure Injection](https://docs.px4.io/main/en/debug/failure_injection) | Simulation and hardware fault injection are existing capabilities, not a contribution by themselves. |
| Cross-stack behavioral checking | [Avis](https://arxiv.org/abs/2106.14959) | PX4 and ArduPilot have already been subjected to in-situ model checking and bug discovery. |
| Capability-aware safety filtering | [CA-HCBF](https://arxiv.org/abs/2604.13245) | Generic capability-aware heterogeneous barrier functions cannot be a headline novelty claim. |
| Health contracts and reallocation | [Fail-operational swarm architecture](https://arxiv.org/abs/2608.20906) | Safety monitors, contracts, health vectors, and reallocation have already been combined architecturally. |
| Protected contingency trajectory | [Plan-and-Avoid](https://arxiv.org/abs/2608.06648) | Moving cooperative traffic away from a vehicle's contingency path is closely related prior work. |
| Dynamic spatial reservations | [Dynamic air corridors](https://doi.org/10.1016/j.robot.2026.105359) | Space-time corridor reservation under communication loss is not new in general. |
| Operational RTL hazard | [ATSB AO-2023-033](https://www.atsb.gov.au/investigations/ao-2023-033) | A large-drone-operation investigation provides motivation for composing recovery behavior before coordination is lost. |

## Candidate gap

The working gap is not “failsafe coordination.” It is:

> Physical and simulated composition of empirically calibrated native recovery traces from completely configured autopilot systems after companion-level command authority is lost, including mode transitions and reconnection behavior.

This is a **candidate distinctiveness claim**, not proof of global novelty. It must be checked again before submission against new publications, dissertations, standards, and patents.

## Claims explicitly excluded

This repository will not claim invention of:

- UAV failsafes or fault injection
- Collision avoidance or control barrier functions
- Contingency trajectories or spatial reservations
- Health-aware fleet reallocation
- Cross-autopilot testing
- Return-to-launch coordination as a general problem

## Search questions still open

- Has an existing benchmark already mapped equivalent failsafe intentions across pinned PX4 and ArduPilot configurations?
- Has a parameter compiler translated an abstract recovery contract into both stacks and verified trace conformance?
- Has post-companion-loss reconnection behavior been included in empirical fleet recovery tubes?
- Which standards define evidence expectations for operational contingency-volume coverage?

Answers to these questions must be added with dated search strings and primary sources before the novelty statement is frozen.

## URC-01 closeout — 2026-09-15

This section meets the URC-01 done-when in [TASKS.md](TASKS.md#urc-01--close-the-exact-gap-and-tooling-search):
search strings, inclusion/exclusion criteria, a source table, and a conclusion in one of the two allowed forms.
It is bounded by the inspected set below. It is not an exhaustive systematic review.

### Database search strings actually executed

Canonical export: `evidence/task-2026-09-11-public/database-export.json` (provenance-clean, 317 identifier
records, retrieved 2026-09-11T21:25:39Z). Every leg is reproduced from its query log, not retyped:

| database | query | status | n |
|---|---|---|---|
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

Recall of this export against the eligible day-1 set is **3/6**
(`scripts/reference_coverage.py --check`). The 2026-09-09 export fails the native-response audit and is
credited for nothing. The day-1 web-index queries are listed in
[prior-art-search-2026-09-08.md](prior-art-search-2026-09-08.md). Successor screening on 2026-09-15 used
Crossref and OpenAlex by DOI only; no new search legs were added.

### Patent search

**Not searched.** No patent database route was reachable from this repository's tooling on 2026-09-09 or
2026-09-15 (Crossref, OpenAlex and arXiv are scholarly indexes and do not cover patents). One patent (U12) was
read as public text; that is technical overlap only, not legal clearance. A patent search is an open item,
not a closed one.

### Inclusion and exclusion criteria (as applied)

- Day-1 set: the 12 sources selected by the 2026-09-08 review, every one accounted for in
  `docs/source-eligibility-register.json` with an explicit reason.
- Eligible for database recall: a scholarly record with a resolvable DOI or arXiv id (6 of 12).
- Stated, not dropped, and never counted as recall: code repositories, vendor documentation pages, patents
  (6 of 12).
- Successors: any Crossref-surfaced 2026 work citing or extending PGFuzz whose title touches a novelty axis
  (3 found on 2026-09-12, all screened 2026-09-15). They are recorded as S-ids, not added to the day-1
  register.
- A source counts as inspected only when its full text (or repository tree) was opened and hashed.
  Abstract-only or unreachable sources stay `unresolved` on every axis.

### Source table: equivalent-intent PX4/ArduPilot benchmarks and failsafe-configuration tooling

Per-axis state from each reading record's `axis_states` (D = disclosed or addressed, N = not found in the
inspected sections, U = unresolved). Generated from `docs/day3-reading-records.json`.

| id | source | access | intent | reconnection | coverage | liveness/setpoint |
|---|---|---|---|---|---|---|
| U1 | Avis, 2021 v1 | `full_text_sections` | N | N | D | U |
| U2 | PGFuzz, NDSS 2021 | `full_text_pdf` | N | N | D | N |
| U3 | PGFuzz code | `repository_tree_and_source` | N | N | D | N |
| U4 | RouthSearch, 2025 v1 | `full_text_html` | n/a | N | D | N |
| U5 | aerial-autonomy-stack, 2026 v2 | `full_text_sections` | N | N | N | U |
| U6 | PX4 failsafe simulator | `official_documentation` | D | N | D | N |
| U7 | PX4 Offboard | `official_documentation` | D | N | U | U |
| U8 | ArduPilot GCS failsafe | `official_documentation` | U | D | U | U |
| U9 | ArduPilot Guided commands | `official_documentation` | N | N | D | D |
| U10 | Plan-and-Avoid, 2026 v1 | `full_text_html` | n/a | n/a | n/a | n/a |
| U11 | Fail-operational swarm architecture, 2026 v1 | `full_text_html` | D | N | N | D |
| U12 | EP3662460B1 | `patent_claims` | N | D | N | U |
| S1 | UAVConfigFuzzer: Detecting Incorrect Configurations in UAVs via Setpoint Estimation Guided Fuzzing (Registered Report), FUZZING Workshop 2026 | `full_text_pdf` | N | N | N | N |
| S2 | ADGFuzz: Assignment Dependency-Guided Fuzzing for Robotic Vehicles, NDSS 2026 | `full_text_pdf` | N | N | N | N |
| S3 | PGPatch: Policy-Guided Logic Bug Patching for Robotic Vehicles, IEEE S&P 2022 | `full_text_pdf` | N | N | N | N |

Axis summary (from `scripts/reference_coverage.py`):

| axis | status | disclosed by | not found in inspected sections of | unresolved for |
|---|---|---|---|---|
| `equivalent_intent` | **narrowed_by_disclosure** | U7, U6, U11 | U1, U5, U12, U2, U9, U3, S1, S2, S3 | — |
| `reconnection` | **narrowed_by_disclosure** | U8, U12 | U1, U5, U7, U2, U4, U6, U9, U11, U3, S1, S2, S3 | — |
| `coverage` | **narrowed_by_disclosure** | U1, U2, U4, U6, U9, U3 | U5, U12, U11, S1, S2, S3 | — |
| `liveness_vs_setpoint_injection` | **narrowed_by_disclosure** | U9, U11 | U2, U4, U6, U3, S1, S2, S3 | — |

### Conclusion

**Prior art found, per axis.** Taken one at a time, every axis is `narrowed_by_disclosure`: an inspected
source already discloses cross-configuration intent in contract form (U6, U7, U11), documents behaviour on
reconnection (U8, U12), measures a trajectory-distance coverage of some kind (U1, U2, U3, U4, U6, U9), and
separates liveness from setpoint loss (U9, U11). None of these can be a headline claim.

**Supported candidate gap, bounded by this inspected set**, for the composed claim only: no inspected source
fixes one recovery intention, pins two autopilot configurations that are supposed to realise it, injects
liveness loss and setpoint loss as distinct faults, records the command-return phase, and compares the
realised trajectories against a calibrated coverage measure. The three 2026 successors and the PGFuzz code
do not change this: S1 is PX4-only configuration fuzzing, S2 is ArduPilot-only assignment-bug fuzzing, S3
patches per-autopilot fail-safe formulas without comparing them, and U3's code carries two independent
policy lists.

Bounds on that sentence: no patent search; no dissertation or standards search; no source outside the 15
inspected; recall of the canonical export is 3/6 against a 6-source anchor set, so the database leg is known
to miss relevant work. This closes URC-01 as a *dated boundary*, not as a novelty verdict. It does not close
URC-S08 or any owner gate. It must be re-run before any submission.
