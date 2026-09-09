# URC-01 source closeout, first pass — 2026-09-08

## Question and decision

Does prior work already compare pinned PX4 and ArduPilot configurations under
equivalent companion-authority-loss events, including reconnection, and calibrate
whole-trajectory recovery coverage?

**Prior art found** for cross-stack testing, common interfaces, parameter
constraints, and protection of contingency trajectories. **Supported candidate
gap, within this bounded retrieval only:** a reproducible equivalent-intent,
configuration-specific native-recovery conformance dataset with reconnection
semantics and held-out trajectory coverage. That combination was not established
by the reviewed material. This is not proof that it is absent elsewhere.

Today's URC-D01 completes the first-pass source review within URC-01. It does not
close the full novelty gate: several sources were abstract-only, no exhaustive
database export was available, and no candidate tool was installed. Do not unlock
the configured matrix merely because this report exists.

## Retrieval and eligibility

Search date: 2026-09-08; English; no publication-date cutoff. Method: web discovery
with arXiv/publisher/official-doc and Google Patents domain queries, followed by
opening primary records. These are **web-index searches of databases**, not native
Scopus, Web of Science, IEEE Xplore or patent claim-chart exports. Search result
ordering and total hit counts are not stable; no denominator for the world's
literature is claimed.

Exact executed strings (repeat verbatim, then open the listed primary sources):

1. `PX4 ArduPilot equivalent failsafe differential testing recovery reconnection Avis PGFuzz`
2. `site.arxiv.org PX4 ArduPilot differential testing failsafe configuration benchmark`
3. `site.arxiv.org "PX4" "ArduPilot" "recovery" "benchmark"`
4. `site.patents.google.com UAV failsafe contingency trajectory communication loss`
5. `site.patents.google.com "PX4" "ArduPilot" failsafe`
6. `site.patents.google.com "PX4" "ArduPilot" contract compiler`

Include work on cross-autopilot execution, timed safety/configuration policies,
communication-loss recovery, or trajectory reservations. Exclude ordinary drone
tutorials, unsupported forum anecdotes, communication-throughput optimization,
and marketing. A shared interface is relevant tooling, not automatically an
equivalent-failsafe benchmark. Missing detail means **not established here**, not
“absent from the paper.”

Aboutness: 3 directly studies the target combination; 2 a material ingredient;
1 background; 0 excluded. Evidence grade: B controlled empirical evaluation
reported by authors; C simulation/model; D architectural argument. An abstract
describing experiments is marked provisional B, not independently reproduced.
Official docs and patents are specifications/disclosures, not performance grades.
Selection/ranking below is by relevance, not prestige or citation count.

## Evidence table (12 primary entries)

| ID / source / version | Aboutness; evidence/access | Overlap and boundary |
| --- | --- | --- |
| U1 [Avis, 2021 v1](https://arxiv.org/html/2106.14959v1) | 2; B/C, HTML mode-execution and bug-table sections inspected | In-situ sensor-failure checking on both stacks. Cross-stack fault testing is established; the source does not establish the proposed calibrated recovery dataset. |
| U2 [PGFuzz, NDSS 2021](https://www.ndss-symposium.org/ndss-paper/pgfuzz-policy-guided-fuzzing-for-robotic-vehicles/) | 2; provisional B, abstract | Timed policy fuzzing of commands, configuration and physical state on multiple stacks. Generic “contract conformance” is not enough to distinguish URC. |
| U3 [PGFuzz code](https://github.com/purseclab/PGFuzz) | 2; artifact README inspected, not executed | Existing ArduPilot/PX4 tooling and explicit failsafe bug examples. Legacy setup instructions must not be copied as a verified modern install. |
| U4 [RouthSearch, 2025 v1](https://arxiv.org/abs/2505.02357v1) | 2; provisional B/C, abstract | Infers PID parameter validity on both stacks. Relevant to configuration constraints, not evidence of an abstract recovery-policy compiler. |
| U5 [aerial-autonomy-stack, 2026 v2](https://arxiv.org/abs/2602.07264v2) | 2; C, abstract | Common ROS2 interface and end-to-end simulated stack already exist. Evaluate reuse before writing another cross-stack launcher; installation/compatibility untested here. |
| U6 [PX4 failsafe simulator](https://docs.px4.io/main/en/config/safety_simulation) | 2; official live docs | Native state-machine simulation is existing apparatus. Useful for expected mode transitions, not a substitute for vehicle motion traces. |
| U7 [PX4 Offboard](https://docs.px4.io/main/en/flight_modes/offboard) | 2; official live docs | Offboard liveness depends on transport/message family. Pin interface and timeout parameters rather than a brand-level assumption. |
| U8 [ArduPilot GCS failsafe](https://ardupilot.org/copter/docs/gcs-failsafe.html) | 2; official live docs | Monitors GCS heartbeat and configured actions; restoring heartbeat does not automatically restore the previous mode. |
| U9 [ArduPilot Guided commands](https://ardupilot.org/dev/docs/copter-commands-in-guided-mode.html) | 2; official live docs | Velocity/acceleration command expiry is distinct from GCS-heartbeat loss. “Stop setpoints” is not synonymous with “trigger RTL.” |
| U10 [Plan-and-Avoid, 2026 v1](https://arxiv.org/abs/2608.06648v1) | 2; C, abstract | Cooperative traffic is already rerouted around a priority/contingency path. Reservation/evacuation alone cannot be the contribution. |
| U11 [Fail-operational swarm architecture, 2026 v1](https://arxiv.org/abs/2608.20906v1) | 2; C/D, abstract | Safety monitor, formal contracts, health vectors and reallocation already coexist architecturally. No measured fleet-safety claim follows for URC. |
| U12 [EP3662460B1](https://patents.google.com/patent/EP3662460B1/en) | 2; patent disclosure, abstract/description | Communication-failure emergency routing and attempts to regain communication are disclosed. Not a legal opinion or evidence of a PX4/ArduPilot benchmark. |

No grade-3 exact match was established among these **12 selected entries** (11
distinct works/specification pages plus a separately reviewed code artifact).
This is not a recall estimate. Existing CA-HCBF and dynamic-air-corridor sources
remain in the parent map; this table does not pretend to re-audit all their
claims. The dynamic-air-corridor DOI resolver failed during this pass and is
not new supporting evidence. No withdrawal notice was visible in the opened
arXiv records; no separate retraction-database search was performed.

## Claim ledger and concrete protocol consequences

**Claim A:** Cross-stack validation and timed policies are established.
Support U1–U4; high confidence in overlap, limited to accessed material.
Consequence: use conformance *data and evaluation design*, not a new wrapper,
as the proposed contribution.

**Claim B:** Command-loss event equivalence must be tested, not assumed.
Support U7–U9; high confidence in documented distinction, implementation version
still unpinned. Proposed URC-02/03 acceptance amendment:

- Record transport (MAVLink versus ROS2), message type and last valid setpoint.
- Separately record liveness/heartbeat publisher, identity and last heartbeat.
- Distinguish setpoint-only cessation, companion process kill, and loss of the
  monitored GCS stream; unrelated surviving publishers must be recorded.
- Log the native mode and acceptance of restored commands after reconnect.
- Establish the active monitors before injection; never infer a triggered
  failsafe from elapsed time alone.

For example, PX4 ROS2 liveness and trajectory setpoints can be separate streams;
ArduPilot GCS failsafe monitors heartbeat, while Guided velocity expiry has its
own behavior. An apparent “stack difference” could instead be different signals
being interrupted. These are design implications, not results of our own flights.

**Claim C:** Traffic evacuation around contingency paths is existing work.
Support U10–U12; moderate confidence at the abstract/disclosure level.
Consequence: stay at single-vehicle conformance first. Fleet horizon, joint
risk and correlated losses remain later requirements, not solved by this review.

## Tooling decision and remaining closeout

Shortlist existing PGFuzz for policy/test ideas, aerial-autonomy-stack for common
interfaces, and the PX4 failsafe simulator for native mode expectations. Do not
claim any was installed, compare their performance, or adopt their versions
without a clean install and a fixed no-fault trace.

Before marking URC-01 fully closed: inspect full texts/code for the exact
equivalent-intent and reconnection axes; run a native scholarly-database search
where access is available; retain a screened export; inspect relevant patent
claims with qualified help if that path matters. Patent discovery here is
technical overlap screening, not clearance or patentability advice. Owner
configuration/resource and disclosure choices remain unchanged.

Evidence strength is sufficient to reject broad novelty language and improve
the experiment's event definition. It is insufficient to establish global
novelty, flight safety or a publishable benchmark result.
