# Day 2 — apparatus bring-up, runner contract, reproducibility (URC-04) — 2026-09-20

Branch `task/study-a-harness-2026-09-20` off main `ff557a5` (the merge of PR #18). This is the revised
Wednesday of [plan-critique-2026-09-19.md](../../docs/specs/formal-composition/plan-critique-2026-09-19.md):
apparatus bring-up first, then the runner contract, then the reproducibility check.

**Evidence state: simulation.** Six SITL runs exist. They are apparatus evidence — they show the rig can
produce a trustworthy trace of normal operation. No failsafe was injected, no model was validated, and
nothing here says anything about safety, hardware, ArduPilot or fleets.

## The blocker from day 1, diagnosed and cleared

Day 1 recorded that the vehicle refused to arm with no fault injected, and named the next diagnostic. Running
it took four steps, each of which eliminated a hypothesis:

| step | finding |
|---|---|
| Console `commander check` with stock parameters | `Preflight check: OK`. The rig is sound; the blocker is in the configuration or the harness, not PX4. |
| Same console, applying the matrix parameters one group at a time | Every parameter is individually fine. Only `NAV_DLL_ACT=2` fails, and only because enabling the datalink failsafe adds a GCS-presence pre-arm check and the console run has no ground station. |
| A live MAVLink ground station with `NAV_DLL_ACT=2` | The pre-arm bit stays set. So the parameter set is fine when a real link exists, and the harness did have a link (`gcs_connection_lost: False`). |
| `health_report` and `vehicle_status` read from the running instance during a failing harness run | `arming_check_error_flags` = the **System** component, `nav_state` = 2 (Position), `manual_control_signal_lost: True`. Position mode requires a manual-control source; without one the mode cannot run, so the mode check blocks arming. |

Two defects in the harness followed from that, and both are now fixed:

1. **A second UDP socket silently swallowed every offboard setpoint.** Setpoints were sent on their own
   `udpin` socket, which only transmits once the autopilot has addressed it. It never did, so the offboard
   signal was never established, Offboard could not run, and the vehicle stayed in Position. Setpoints now go
   over the single existing link. This was the actual root cause.
2. **The stream thread swallowed exceptions.** Any send that raised was discarded silently. Stream errors are
   now collected and the runner refuses to arm if any occurred.

The manual-control stream was removed rather than repaired: no frozen event class needs it, and PX4 in this
rig did not accept MAVLink `MANUAL_CONTROL` as a manual-control source. That makes RC loss uninjectable here,
which is recorded as decision **D13** rather than quietly dropped — the class stays in the frozen list, the
campaign excludes it, and the runner refuses it with the reason.

## Runner contract (W3.1)

`harness/run_case.py` implements the eleven-point contract, with decision D6 applied: **injection is
scheduled on the vehicle clock**, because lockstep does not bound host-side UDP jitter. Eight offline tests in
`tests/test_runner_contract.py` exercise refusal of an unknown case, a missing binary, a firmware-commit
mismatch, an existing run directory and a non-injectable class, plus manifest-before-launch and case-ID
determinism. None of them launches PX4 or touches the network: the MAVLink import is deferred until after a
case is accepted, so the contract holds in the repository gate environment.

## No-fault control (W3.2)

One control case, `px4-v1.17.0-sih-quadx-rtl__none__seed1`: arm on the first attempt, climb to 10 m, hold
through the registered horizon, exit 0, trace schema-valid. That is the first trace this repository has ever
produced.

## Five-run reproducibility (W3.3, corrected by critique finding 6)

Five attempts at the same control case, same seed, same parameter hash, same firmware commit. Byte identity
of the autopilot log is **not** expected and is not checked: a uLog embeds boot and wall-clock timestamps, so
hashing it would fail every time and read as non-determinism.

| attempt | outcome |
|---|---|
| rep1 | **invalid** — `simulator_crash`: no vehicle heartbeat within 60 s. A previous instance still held the telemetry port when the loop started the next run. Preserved, excluded from the statistics, and the runner now refuses a busy port at setup rather than failing at capture. |
| rep2-rep5 | valid |

Across the four valid runs: identical firmware commit and parameter hash, and an identical normalised mode
sequence (empty — the control never leaves Offboard, which is the point of a no-fault control).

| event | n | spread (range) | standard deviation | vehicle time |
|---|---|---|---|---|
| `arm` | 4 | 0.094 s | 0.034 s | ≈ 7.3 s |
| `takeoff_complete` | 4 | 0.338 s | 0.123 s | ≈ 17.0 s |
| `horizon_reached` | 4 | 0.514 s | 0.186 s | ≈ 111.9 s |

### What this says about the registered timing tolerance

The protocol registers median |Δt| ≤ 0.2 s and p95 ≤ 1.0 s for model-versus-SITL transition times. The rig's
own repeat-to-repeat spread is 0.09 s at 7 s of vehicle time and 0.51 s at 112 s: **jitter grows with elapsed
time**, which is what an accumulating clock-offset estimate does. At the far end of a run the apparatus alone
consumes half the p95 budget and more than twice the median budget.

Two consequences, both of which change the analysis rather than the tolerance:

1. **Transition-time error must be measured relative to the injection instant, not to absolute vehicle time.**
   The offset that accumulates over a run is common to the injection and the transition, so a difference
   taken across them cancels most of it. Study A's comparison should use `t(transition) − t(injection)`.
2. **The measured jitter must be reported beside every timing figure**, so a disagreement inside the
   apparatus spread is never counted as a model error.

Neither is a licence to widen the tolerance after seeing data. The tolerance stands as registered; the
measurement is redefined before any validation run, which is the point of doing this check first.

## Artifacts

Full raw captures, normalised traces and autopilot logs are immutable and held outside git
(186 MB; repository policy for large artifacts). [run-index.json](run-index.json) pins each by SHA-256 and
records its location; [runs/](runs/) holds the committed per-run manifest, clock, events and validity without
the sample series; [reproducibility.json](reproducibility.json) is the comparison output.

## Checks observed

| command | result |
|---|---|
| `python -m unittest discover -s tests -q` | OK, 80 tests (10 new) |
| `python scripts/check_repo_contract.py` | PASS |
| `python scripts/acquisition_ledger.py --check` | consistent |
| `python scripts/reference_coverage.py --check` | OK, 0/6 and 3/6 |
| `python tools/check_presentation.py . "UAV Failsafe Composition" uav-failsafe-composition` | no issues |
| `python tools/test_presentation.py` | OK |
| `git diff --check` | clean |
| `python -m harness.reproducibility` on the four valid runs | exit 0 |

## What is still not done

No failsafe has been injected. The single-event campaign (50 cases: five injectable classes × two
configurations × five seeds) has not run. No model has been validated, no property checked, no witness
replayed. UPPAAL is still absent (decision D8), and D7, D9 and D13 still need your answer.
