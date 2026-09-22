# Diagnosing the refutation: the framework takes no action on any hazard — 2026-09-22

Branch `task/study-a-diagnostics-2026-09-22` off main `11ca7c3`. This runs the two diagnostics named in
[task-study-a-verification-2026-09-21](../task-study-a-verification-2026-09-21/README.md), plus a third that
the second one made necessary.

**Evidence state: simulation.** Development runs, not held-out validation cases. No model has been validated.

## Result

The hypothesis space has collapsed. In this configuration the PX4 failsafe framework **selects no action for
any hazard tested**, while the monitor for that hazard is demonstrably active.

| run | monitor that fired | configured action | delayable? | takeover-able? | observed |
|---|---|---|---|---|---|
| 2026-09-21, `…-rtl` | `gcs_connection_lost` | RTL via `NAV_DLL_ACT` | yes | yes | no action, Offboard held |
| 2026-09-21, `…-rtl-delay0` | `gcs_connection_lost` | RTL, no Hold delay | n/a | yes | no action, Offboard held |
| today, `…-rtl` | `geofence_breached` | RTL via `GF_ACTION=3` | yes | yes | no action, Offboard held |
| today, `…-rtl-gf-terminate` | `geofence_breached` | **Terminate** via `GF_ACTION=4` | **no** | **no** | **no action, Offboard held** |

`vehicle_status.failsafe` stayed 0 in every run. The flag stayed true for 33 to 41 seconds each time, while the
vehicle was armed, flying and in Offboard.

## What this rules out

Each of these was a live hypothesis before today and is now eliminated:

- **Not datalink-specific.** A geofence breach behaves identically, through a different monitor and a
  different parameter.
- **Not parameter delivery.** `GF_ACTION`'s vendor default is 2, which is Hold. If the module were running on
  boot defaults it would still have selected Hold. It selected nothing.
- **Not the Hold-first delay, and not user takeover.** Terminate is excluded from both by the pinned source
  (`framework.cpp` L490-493 and L647-651) and it did not fire either.
- **Not deferral.** Geofence actions are registered `cannotBeDeferred`, and `failsafe_defer_state` stayed 0.
- **Not the land detector.** `vehicle_land_detected.landed` went false at 9.1 s and stayed false.
- **Not arming.** `arming_state` was 2 throughout, and the mode did change at boot
  (`AUTO_LOITER` → `OFFBOARD`), so mode changes work.

## What remains

Something common to every hazard suppresses action selection in this configuration. The candidates left are:
the framework's `checkStateAndMode` not running at all; `state.armed` being false as the framework sees it
despite the vehicle being armed; the `failsafe_flags` instance passed to the framework differing from the one
published to the log; or something specific to Offboard as the user-intended mode.

**Study A stays blocked, and the 50-case campaign stays held.** A model of failsafe composition cannot be
validated against a rig in which no failsafe is observed. Under the registered decision tree the model is not
repaired to match; the observation is recorded and the next step is named.

## Next step

Instrument the framework's own view rather than inferring it. The two that need no new machinery: log
`vehicle_status.nav_state_user_intention` alongside the flags and confirm what the framework receives as the
intended mode; and run one case where the intended mode is **not** Offboard, to test the last structural
hypothesis directly. A non-Offboard case needs a manual-control source, which decision D13 records as
unavailable in this rig, so that test may require the ROS 2 path that decision D11 already defers.

## An oracle that could not be run here

PX4 ships a unit test for the failsafe framework. Driving the real `Failsafe` class from it, with the matrix
parameters set directly, would separate the derivation from every delivery question in one offline step. The
test was written and the target built, but the binary would not run on this host: it links against
AddressSanitizer symbols that macOS `libSystem` does not provide, and preloading the toolchain's sanitizer
runtime did not resolve it. The firmware tree was restored to its pinned commit
`d6f12ad1c4f70ad3230afd7d86e971421e02fef4` afterwards and verified clean. This is recorded as a limitation of
the host, not of the method: on Linux it is the cheapest decisive test available and it should be the first
thing tried next.

## Additions to the frozen artifacts

- Timeline **T3** (geofence breach on the RTL row) and **T4** (geofence breach with Terminate), each derived by
  hand from parameter values and source lines and committed before its run.
- Matrix row `px4-v1.17.0-sih-quadx-rtl-gf-terminate`, a one-factor variant, marked diagnostic-only because
  Terminate ends the flight.
- The verifier now accepts a hazard whose time is not predicted, because a geofence breach is triggered by
  position rather than a timer, and times the actions from the hazard in that case.
- Parameters that exist only to make one event class injectable are declared once in `harness/cases.py`
  instead of sitting as literals in the runner.

## Checks observed

| command | result |
|---|---|
| `python -m unittest discover -s tests -q` | OK, 98 tests |
| `python scripts/check_repo_contract.py` | PASS |
| `python scripts/acquisition_ledger.py --check` | consistent |
| `python scripts/reference_coverage.py --check` | OK, 0/6 and 3/6 |
| `python tools/check_presentation.py . "UAV Failsafe Composition" uav-failsafe-composition` | no issues |
| `python tools/test_presentation.py` | OK |
| `git diff --check` | clean |
| pinned firmware tree after the oracle attempt | `git status --porcelain` empty at `d6f12ad` |
