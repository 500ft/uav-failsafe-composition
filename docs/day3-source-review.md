# Day-3 convergence decision — 2026-09-09

**Recommendation: narrow the headline to configuration-specific recovery conformance, not generic reconnection or a new cross-stack wrapper.** No simulator run or flight result is added.

The [reading rubric](day3-reading-rubric.md) was pushed first at `382e09d`, after earlier screens were known. [Reading records](day3-reading-records.json) distinguish inspected full-text sections, official specifications and patent claims. This is targeted source review, not an independent systematic review.

## What changes the design

- [Avis, IV-C](https://arxiv.org/html/2106.14959v1) already compares time-aligned position, acceleration and mode against profiling runs. A trajectory-distance score alone is therefore not a distinct contribution. The remaining proposed endpoint is held-out **whole-recovery-trajectory coverage** for specified authority-loss conditions, not merely deviation from a fault-free trace.
- [aerial-autonomy-stack, III/IV-A](https://arxiv.org/html/2602.07264v2) describes a shared simulator and autopilot integrations. Reuse should be evaluated before building another launcher. Those inspected sections do not establish equivalent failsafe stimuli across its distinct bridges; no installation compatibility has been tested here.
- [PX4 Offboard documentation](https://docs.px4.io/main/en/flight_modes/offboard) separates ROS2 liveness from setpoints. [ArduPilot GCS failsafe](https://ardupilot.org/copter/docs/gcs-failsafe.html) monitors an established heartbeat stream and does not automatically restore the previous mode on reconnection. First compare **MAVLink-based** intentions as a proposed common route; reserve ROS2 liveness separation for a later explicitly different condition. Still log publisher identity and all surviving streams.
- [EP3662460B1, claims 1–3](https://patents.google.com/patent/EP3662460B1/en) discloses returning through a healthy communication waypoint and waiting for a user command after reconnection. Thus “we consider reconnect” cannot be the novelty. Public claim text was accessible this time; this is technical overlap reading, not patentability or freedom-to-operate advice.

Candidate statement: **We propose a versioned dataset and evaluation of native recovery behavior across explicitly configured autopilots under equivalent recovery intentions, separating the loss stimulus, authority transition, reconnection acceptance and held-out trajectory coverage.** This combination remains unresolved beyond the bounded material inspected. It is not a claim that the gap is globally established or that safety contracts are new.

## One acquisition ledger

[acquisition-ledger.json](../evidence/task-day3-2026-09-09/acquisition-ledger.json) combines all 402 raw day-2 rows with all 12 day-1 source entries and today's targeted opens. Stable identifiers merge routes without erasing their dates or original raw row indices. Day-1 queries are explicitly null per source because only the report's query set was preserved. Original search logs and exports are unchanged.

Ninety day-2 rows still lack support from a successful logged query. Later direct access cannot retroactively repair this. Recall remains null; “different source populations” is not an established result. Unscreened records stay unscreened even if an old export flag asserts otherwise.

Reproduce: `python scripts/acquisition_ledger.py --check`, `python -m unittest discover -s tests -q`, `python scripts/check_repo_contract.py`. To regenerate only the derived ledger, run the first command without `--check`. This performs no network retrieval.

## Next work, bounded by the actual gates

First close the remaining named full-text/code competitors, including PGFuzz and the newer reservation/architecture papers, against the same axes. A proposed acquisition form is already encoded by the reading-record fields: identifier/version, date, sections, access, evidence grade and per-axis finding. Missing text is not a negative finding.

Then perform a clean simulator/tooling pilot and record real firmware commits, complete parameter export, interface and one no-fault trace before choosing the fault matrix. No version is “pinned” merely because a documentation URL contains a release number. URC-01/D02 and configuration/access gates remain open; this task supplies convergence tooling and narrower decisions, not an experimental release.
