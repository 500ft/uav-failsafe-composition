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
