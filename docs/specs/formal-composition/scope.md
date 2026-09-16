# uav-failsafe-composition — Adaptive Plan (formal-composition programme)
Date: 2026-09-16 (proposed)

## Must-have (v1 = the pilot result of Study C, or a preregistered verified-null)
- Operational definition of "unsafe composed state" tied to the repo's observables — without it nothing below is falsifiable.
- URC-02 pinned PX4 configuration matrix (one release, one vehicle model, the failsafe parameter sets) — the experimental identity.
- URC-03 event and trace semantics (last valid setpoint, authority-loss, native transition, terminal state, reconnect) — shared by model validation and measurement.
- URC-04 minimal harness: one command launches pinned PX4 SITL, injects one event class, records mode/timestamps/state with a manifest — every study depends on it.
- Study A: extracted timed-automaton model + SITL validation at the preregistered agreement rate (study-a-protocol.md).
- Study B: four properties checked with an existing checker on the composed model; witness traces exported.
- Study C: every witness replayed in SITL through the harness; predicted-and-confirmed, predicted-but-refuted, and verified-null reported alike; any confirmed defect filed upstream as the hard external artifact.
- Rubric axis 5 `formal_composition`, intake re-screen, and the Avis distinction in prior-art.md — before any distinctiveness sentence.

## Nice-to-have (post-v1 queue)
- Interval-abstracted continuous guards replaced by calibrated envelopes from Study A traces (value: tighter reachability; effort: medium).
- URC-09 versioned conformance benchmark release (value: citable regardless of outcome; effort: low once traces exist).
- Held-out tube coverage (RQ2) on the same traces (value: keeps the fallback thesis alive; effort: medium).
- Reconnection-phase model (command return, COM_RCL_EXCEPT, takeover) as an added automaton (value: covers the `reconnection` axis; effort: medium).

## Maybe-later (trigger-gated)
- ArduPilot model extraction (Study D, first half) · Trigger: Study C reports ≥ 1 confirmed interaction or a verified null with the model artifact released · Why wait: a second extraction project; ArduPilot has no unified failsafe framework (U8, S3).
- Hybrid reachability (dReal/SpaceEx-class) instead of timed abstraction · Trigger: a Study B property is inconclusive under interval abstraction on a guard that Study A shows is not monotone · Why wait: tooling cost; timed abstraction may suffice.
- HITL replication (URC-13) · Trigger: funding for a flight controller and bench, plus ≥ 1 SITL-confirmed interaction whose timing is within 2× the failsafe delay granularity · Why wait: hardware-timing claims need hardware; SITL cannot make them.
- Benign-interaction flights (URC-14) · Trigger: HITL replication holds and facility, risk review and kill path exist · Why wait: not authorised; no flight evidence exists.
- RQ3 volume comparison and RQ4 fleet composition (URC-10) · Trigger: URC-08 positive branch (individual tubes retain coverage and save ≥ 10% volume) · Why wait: does not serve the formal spine; expensive.
- Native patent-database search for the formal axis · Trigger: any disclosure or submission decision (XC-02) · Why wait: owner decision; not a research blocker for SITL work.

## Out
- Large physical swarm demonstration — no facility, no safety case, not needed for the thesis.
- Universal autopilot ranking or brand-level safety claims — prohibited by the claim ledger.
- Adversarial/security claims and GPS-denied navigation — different literature and threat model.
- Writing a model checker — an existing checker is a must-have rung.
- Any new broad literature search — owner constraint; bounded re-screens only.

## Milestone watch
1. **First trace produced** (URC-04 minimal): check `evidence/` for a manifest-backed SITL log. Nothing else can start before it.
2. **Study A agreement rate** at n = 60: ≥ 95% continues; 90–95% continues with every disagreement root-caused and documented; < 90% kills the formalisation.
3. **Study B outcome**: count of reachable unsafe compositions with witnesses (0 is a result if preregistered).
4. **Study C confirmation rate**: witnesses confirmed / witnesses replayed; a refuted witness is a model defect to fix in Study A, not a footnote.
5. **Axis-5 screen complete**: all 317 rows and the cached texts re-screened; [129], [265], [77] read; Avis distinction written.
