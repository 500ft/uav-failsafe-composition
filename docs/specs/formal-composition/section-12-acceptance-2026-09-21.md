# Section 12 acceptance checks — what changed, and where each item lives

The week handoff gained a section 12 on 2026-09-21 adopting a CAD/simulation briefing as planning guidance.
Items 1-7 are acceptance checks inside the existing trace-contract, runner, reproducibility and model-review
tasks, not a separate workstream. This file records where each one is satisfied, so a reviewer can check the
claim rather than take it.

## The cross-referenced briefing, as used

| field | value |
|---|---|
| repository | `500ft/engineering-audit` |
| file | `docs/cad_agent_briefing.md` |
| reviewed commit | `cf56cdff50b09c9a266292006cbf5b2a0f2e8ac6` |
| recorded blob | `530550e230f7b9de8dc350a60e6dd19eb1d94c31` |
| local copy | `/Users/redhose/Developer/engineering-audit/docs/cad_agent_briefing.md` |
| checked on | 2026-09-21, 8397 bytes, git blob hash recomputed locally |
| result | **matches** the recorded blob; the local copy at commit `cf56cdf` is the version these checks were written against |

Its capabilities and run outcomes are reported by that briefing and were not reproduced here. Nothing in this
repository claims a CAD, FEA or hardware result.

## Items 1-7, applied

| item | what it requires | where it now lives | status |
|---|---|---|---|
| **1** Define the expected outcome first, outside the translator | A hand-worked timeline from pinned parameter values and source semantics, kept separate from the model and the normaliser | `protocols/expected-timelines.json` — three timelines, each with its arithmetic, the parameters used and the source lines. `tests/test_expected_timelines.py` cross-checks the hand derivation against the code transcription in `model/px4_failsafe.py` and fails if they disagree | **applied** |
| **2** Separate successful execution from verified behaviour | A run is accepted only when files parse, identity agrees and the required observations exist; otherwise unverified | `harness/verify.py` returns `verified`, `unverified` or `refuted` into a new `verification` block in the trace. A missing oracle or a missing observation can never produce `verified` | **applied** |
| **3** Prove the input change reached the system | Log requested injection, observed cessation, surviving publishers, monitor activation, selected action and observed mode separately | The trace now carries the scheduled and observed injection instants, `streams_at_injection` (which publishers were still running), the `hazard_flag` rise from the autopilot's own log, the action the autopilot announced in its status text, and the observed mode sequence from `vehicle_status`. The verifier refutes a run whose expected hazard flag never rose | **applied** |
| | Confirm the transport actually permits separate liveness and setpoint interruption | Already settled: over MAVLink the keep-alive *is* a setpoint message, so the two are not separable. Recorded as critique finding 1 and decision D11, with the ROS 2 path as the trigger | **applied** |
| **4** Controlled parameter-change check during development | Read back a parameter, change it in range, repeat the case, predict the effect from the pinned code first, verify readback and behaviour, restore and verify | Timelines T1 and T2 differ in exactly `COM_FAIL_ACT_T` (5.0 s → 0.0 s) with the predicted difference written down before the runs; the runner now compares every parameter read-back against the request and fails the `configuration_applied` stage on a mismatch. Results in `evidence/task-study-a-verification-2026-09-21/` | **applied** |
| **5** Probe coordinates and clocks before interpreting traces | Verify axis signs, frames, units and time alignment numerically; freeze tolerances justified by channel resolution and logging rate | The frame and unit probe is in the evidence README below, worked from the existing control runs. The 1.5 s tolerance in `expected-timelines.json` is justified by the measured apparatus jitter and the topic rates, and is frozen before the runs | **applied** |
| **6** Validate trace export and re-import | Save, reload through the consumer and compare identity, units, timestamps, ordering, labels, row count and invalid flags; keep the raw log | `tests/test_conversion_and_silent_failure.py` round-trips a synthetic capture and compares all of those, plus a new `conversion` block in every trace recording raw line counts, message counts, samples and events written, the mode source and any unmapped event names. The raw capture is retained and its path recorded | **applied** |
| **7** Instrument each stage and test silent failure | Stage-level results; negative fixtures for unapplied parameters, ineffective injection and stale results; bounded waits | Every run now carries a `stages` array (launch, configuration applied, normal tracking, injection, capture, normalization). Negative fixtures cover an ineffective injection, a stale result from another case and a missing oracle. Waits were already bounded and time-outs preserved | **applied** |
| **8** Preserve the acquisition route of every physical input | Distinguish provisional, vendor-drawing and measured values if hardware enters | Not applicable yet: this project has no physical input. The rule is recorded here and the existing `docs/baselines/README.md` already carries acquisition routes for every software source | **deferred, recorded** |

## Conditional CAD and FEA guidance

Nothing in this repository needs CAD today. When a fixture, controller mount or enclosure does become
relevant, the briefing's `cadloop/` tooling is the starting point, and its stated limits travel with it:
native assembly documents and mates and dimensioned drawing automation are untested, some feature positions
are not fully parameter-driven, and host completion times vary. Its FEA example has **no independent
acceptance oracle**, so any future stress or displacement number here needs a reference calculation, unit,
load and support checks and mesh-convergence evidence before it means anything. A completed solve validates
nothing on its own. Any such work starts with a project-specific dimension contract, units and acquisition
routes, exactly as item 8 requires.

## What this changed about earlier work

Two things in the day-1 and day-2 artifacts were weaker than section 12 requires, and both are fixed here:
the expected action came only from the code transcription, so a transcription error was invisible to itself;
and a run that executed cleanly was reported as valid without anything checking that the injected failure had
reached a monitor. Neither produced a wrong result yet, because no injection case had been run.
