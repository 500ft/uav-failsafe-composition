# Section 12 acceptance checks, and the first injection experiment — 2026-09-21

Branch `task/study-a-verification-2026-09-21`, stacked on `task/study-a-harness-2026-09-20` (PR #19). Merge
order: **#19 → this**. Where each section 12 item now lives:
[section-12-acceptance-2026-09-21.md](../../docs/specs/formal-composition/section-12-acceptance-2026-09-21.md).

**Evidence state: simulation.** Two development runs exist. Per section 12 item 4 they are harness-development
runs and **do not count as held-out model-validation cases**. No model has been validated, no property checked.

## Headline: the controlled parameter-change check did its job, and refuted the prediction

The expectation was written down first, by hand, from the parameter values and the cited source lines, and
committed before either run ([expected-timelines.json](../../protocols/expected-timelines.json)):

| timeline | configuration | one factor | predicted |
|---|---|---|---|
| T1 | `…-rtl` (`COM_FAIL_ACT_T` = 5 s) | — | hazard at +10 s, `AUTO_LOITER` at +10 s, `AUTO_RTL` at +15 s |
| T2 | `…-rtl-delay0` (`COM_FAIL_ACT_T` = 0 s) | the delay only | hazard at +10 s, `AUTO_RTL` at +10 s, no `AUTO_LOITER` |

Observed, in both runs:

| | T1 run | T2 run |
|---|---|---|
| `gcs_connection_lost` rose | +12.5 s after injection | +11.9 s |
| mode sequence | `OFFBOARD` only | `OFFBOARD` only |
| autopilot announced an action | none | none |
| `vehicle_status.failsafe` | 0 throughout | 0 throughout |
| verdict | **refuted** | **refuted** |

**The stimulus reached the system and the monitor activated. No failsafe action followed.** The autopilot
logged *"Connection to ground station lost"*, the flag stayed true for about 33 s while the vehicle was armed
and flying, and the vehicle held Offboard to the horizon. `NAV_DLL_ACT` read back as 2 and `COM_DLL_EXCEPT` as
0, so the configuration was applied, and the source block that consumes them
(`failsafe.cpp` L498-519) has no exception that covers Offboard when `COM_DLL_EXCEPT` is 0.

### Classification, per the registered decision tree

Not a simulator artifact and not an injection artifact: the monitor fired, on the autopilot's own log. It is
either a **guard-input modelling error** (a condition exists that the hand derivation and the code
transcription both missed) or a **model-structure error**. Under the frozen rule the model is *not* repaired
after seeing this, and the next diagnostic is named instead:

1. **Test whether the failsafe module sees the parameter.** The parameters are set over MAVLink after boot.
   Confirm the effect is present when the same values are applied before the module initialises, by restarting
   the autopilot after configuring and repeating the case.
2. **Discriminate the path.** Run one geofence-breach case on the same configuration, whose action is also RTL.
   If that failsafe fires, parameters do reach the framework and the defect is specific to the datalink path;
   if it does not, the problem is parameter delivery and every configured event class is affected.

Until one of those returns, no statement is made about PX4's behaviour. What is established is narrower and
still useful: **a run can execute cleanly, report valid, and contain no failsafe at all.** Had the 50-case
campaign been launched on day 3 as originally planned, it would have produced fifty clean, valid, empty runs.

### Timing, separately

The flag rose at +12.5 s and +11.9 s against a predicted +10 s. Part of that is explained and part is not. The
timer starts from the last heartbeat the autopilot *received*, which can be up to one heartbeat period (1 s)
before the moment the harness stopped sending. That is a derivation refinement, not a repair, and it is
recorded here rather than folded silently into the timeline.

## Frame, unit and clock probe (item 5)

Worked numerically from a day-2 control run, not from a plot or a remembered convention.

| check | expected | observed | verdict |
|---|---|---|---|
| NED z sign | negative is above the origin | mean −10.016 m at a commanded −10.0 | pass |
| NED z magnitude | 10.000 m | 10.016 m, error +0.016 m | pass |
| vertical velocity at hover | ≈ 0 | +0.014 m/s | pass |
| altitude AMSL | `SIH_LOC_H0` 489.4 + 10 = 499.400 m | 499.334 m, error −0.066 m | pass |
| horizontal position | origin | +0.45 m north, −0.01 m east | pass |
| vehicle clock monotonic in the sample series | yes | **no** | **fail, fixed** |
| host-minus-vehicle offset | one value | recorded +2.34 s, actual mean +7.34 s, spread 10.25 s | **fail, fixed** |

The clock failures were a real defect in the normaliser: the sample series mixed two time bases (messages
carrying `time_boot_ms` used the vehicle clock, heartbeats and status text used host time minus an offset),
and the offset was estimated from the first ten messages, during start-up, where it is biased by launch
latency. The offset is now the median over every message that carries a vehicle timestamp, the spread is
recorded beside it, and the sample series is ordered. Had this not been caught, every timing figure derived
from heartbeat-based samples would have carried a multi-second error.

## What else changed

- **Mode observation** now comes from the autopilot's own `vehicle_status` log rather than the 1 Hz heartbeat
  stream, and the trace records which source was used.
- **Stages** are recorded for launch, configuration, tracking, injection, capture and normalisation.
- **Parameter read-back** is compared against the request; a mismatch fails the configuration stage and stops
  the run, so a parameter file that was written but never applied cannot pass silently.
- **Surviving publishers** are recorded at the injection instant: in these runs the setpoint stream continued
  while the GCS heartbeat stopped, which is what makes datalink loss distinct from offboard loss.
- **Verification** is a separate verdict from execution: `verified`, `unverified` or `refuted`. A missing
  oracle or a missing observation yields `unverified`, never `verified`.

## Checks observed

| command | result |
|---|---|
| `python -m unittest discover -s tests -q` | OK, 91 tests (11 new) |
| `python scripts/check_repo_contract.py` | PASS |
| `python scripts/acquisition_ledger.py --check` | consistent |
| `python scripts/reference_coverage.py --check` | OK, 0/6 and 3/6 |
| `python tools/check_presentation.py . "UAV Failsafe Composition" uav-failsafe-composition` | no issues |
| `python tools/test_presentation.py` | OK |
| `git diff --check` | clean |
| `python -m harness.verify` on both runs | refuted, as recorded above |

One setup refusal is also worth recording: a stray process still held the telemetry port and the runner
refused both cases at setup with the reason, instead of launching and timing out. That is the port pre-check
added on day 2 working as intended.

## Not done

The 50-case campaign has not run and should not run until the refutation above is resolved. UPPAAL is still
absent (D8). D7, D9 and D13 still need owner answers.
