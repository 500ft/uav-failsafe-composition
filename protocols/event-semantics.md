# Event, trace and unsafe-state semantics (URC-03) — frozen 2026-09-16, amended 2026-09-24

The 2026-09-24 amendment is at the end of this file. It changes §2 and §5 only, and it corrects the document to match what the harness does; it does not change a definition the study depends on.

Scope: one completely configured PX4 v1.17.0 vehicle in lockstep SITL. Every term below is taken from a cited baseline in [docs/baselines/README.md](../docs/baselines/README.md); numbers that are our own choices are marked **assumption** with a stated basis. The machine-readable form is [trace-schema.json](trace-schema.json); `tests/test_trace_schema.py` holds one valid and several invalid fixtures.

## 1. Vocabulary (roles)

Following the run-time-assurance pattern [B9]: **monitors** are the autopilot's failsafe flags (`failsafe_flags` fields such as `manual_control_signal_lost`, `gcs_connection_lost`, `offboard_control_signal_lost`, `battery_warning`, `geofence_breached`, position-validity flags) [B1]; the **switch** is the action selector that takes the maximum active action in the precedence order [B1 framework.cpp L462-481]; the **recovery functions** are the actions `Hold`, `RTL`, `Land`, `Descend`, `Disarm`, `Terminate` and the three manual fallbacks [B1 framework.h L52-70]. The command link to the ground station is the **C2 Link** [B8 §3.4]; the offboard controller's stream is the **proof-of-life signal** [B4].

## 2. Events (all timestamped on both clocks, §5)

| event | definition | baseline |
|---|---|---|
| `arm`, `takeoff_complete` | armed flag true; first sample with altitude ≥ 0.9 × commanded takeoff altitude and vertical speed < 0.2 m/s (**assumption**: settle test) | — |
| `last_valid_setpoint` | timestamp of the last offboard setpoint or OffboardControlMode message the harness sent before it stopped the stream (stream rate ≥ 2 Hz while active) | [B4] |
| `last_heartbeat_sent` | last GCS HEARTBEAT the harness sent before stopping (rate 1 Hz while active) | [B5] |
| `injection` | the stimulus, one of `offboard_loss` (stream stopped), `datalink_loss` (heartbeats stopped), `rc_loss`, `gps_loss`, `battery_low\|critical\|emergency`, `geofence_breach`, `link_restored` (stream/heartbeats resumed); rc/gps/battery via failure injection with `SYS_FAILURE_EN=1` | [B3] |
| `hazard_flag` | a sample in which the corresponding failsafe flag changes state, in either direction, carrying `edge: rising\|falling` (from `vehicle_status`/`failsafe_flags` over MAVLink or the uLog); the state of every flag at window entry is recorded separately as `flags_at_injection` | [B1] |
| `failsafe_notice` | STATUSTEXT/event "Failsafe activated: switching to X in N seconds" or "Failsafe activated" | [B1 framework.cpp L171-299] |
| `hold_delay_start` / `hold_delay_end` | entry into Hold as the delayed action and the moment the delayed action is applied; expected duration `COM_FAIL_ACT_T` unless the action cannot be delayed (`Disarm`, `Terminate`, `Hold`, non-deferrable flags) or the user takes over | [B1 L489-500], [B2] |
| `native_transition` | first change of the reported navigation state after `injection`; the sequence of all subsequent nav-state changes is `mode_sequence` | [B1] |
| `terminal_state` | first sample in which the vehicle is in `AUTO_LOITER`/`AUTO_RTL`/`AUTO_LAND`/`DESCEND` with |v| < 0.5 m/s for 2 s, or disarmed on ground, or `TERMINATION` (**assumption**: settle test) | [B1 modeFromAction] |
| `reconnect_event` | `link_restored` injection; `post_reconnect_behaviour` records whether the action clears (`WhenConditionClears`) or persists until mode change or disarm (`OnModeChangeOrDisarm`) | [B1 framework.h L72-77], [B6] |

## 3. Timers taken from the configuration (never hard-coded)

`COM_OF_LOSS_T` (offboard proof-of-life timeout, default 1.0 s) [B4][B10]; `COM_DL_LOSS_T` (C2 Link loss, default 10 s) [B10]; `COM_RC_LOSS_T` (0.5 s) [B10]; `COM_FAIL_ACT_T` (hold delay, default 5 s) [B10][B2]; the MAVLink convention that a link is considered lost after four or five missed 1 Hz heartbeats [B5] is the reason `COM_DL_LOSS_T` variants in the matrix are 4, 5 and 10 s; ArduPilot's `FS_GCS_TIMEOUT` default 5 s is the cross-autopilot counterpart [B6].

## 4. Unsafe composed state — the four conditions Study B decides and Study A records

Each is observable from `mode_sequence`, the selected action, the hazard flags and the clocks. Margins are **assumptions** stated with their basis; the owner may edit them before the first validation run.

| id | condition | basis |
|---|---|---|
| **U1 no recovery engaged** | a hazard flag stays true for longer than its configured timer + `COM_FAIL_ACT_T` + 1.0 s while the selected action is `None` or `Warn` and no exception bit (`COM_RCL_EXCEPT`, `COM_DLL_EXCEPT`) or "already landing/RTL" rule applies | a breached monitor must engage a recovery function [B9]; PX4's exception bits and UX rules are the only legitimate reasons not to [B1 failsafe.cpp L465-513, framework.cpp L617-644]; the 1.0 s margin is one heartbeat period [B5] |
| **U2 priority inconsistency** | two or more hazards active and the engaged action is lower in the precedence order than the action configured for the highest active hazard, outside the documented fallback chain | precedence is defined by the code [B1 framework.h L52-70]; arbitration between several recovery functions is a stated design obligation of RTA [B9] |
| **U3 flapping** | the selected action leaves and re-enters a recovery function more than once within 10 s while the hazard has not cleared | the code contains explicit toggling protection, so oscillation is a recognised hazard [B1 framework.cpp L121-141]; the 10 s window equals `COM_DL_LOSS_T` default [B10] and follows the windowed-oracle form of S2's 7 s deviation oracle [B11] |
| **U4 unbounded time-to-safe-state** (bound defective, see amendment) | time from `hazard_flag` to `terminal_state` exceeds (configured loss timer + `COM_FAIL_ACT_T` + expected manoeuvre time) + 2.0 s, where the expected manoeuvre time is computed from `RTL_RETURN_ALT`, `RTL_DESCEND_ALT` and the SIH model's speed limits | a contingency must end inside the declared buffer [B7 §2.2.4]; the delay structure is Hold-then-act [B2][B1]; 2.0 s margin = two heartbeat periods [B5] (**assumption**) |
| **containment (recorded, not decided)** | position leaves the declared flight geography (geofence) or the contingency volume during recovery | operational volume = flight geography + contingency volume [B7 §2.2.1-2.2.3]; PX4 `GF_ACTION` [B1 failsafe.cpp L86-127] |

Inherited invalid-run oracles (a run is invalid, not unsafe): no vehicle heartbeat for 2 s [B11 S2]; vehicle stationary with an incomplete mission before injection [B11 S1]; lockstep desync or log gap > 1 s (**assumption**).

## 5. Clocks, frames, units, missing data

- Two clocks per sample: host monotonic (`t_host_s`, from the harness) and vehicle `time_boot_ms` from the MAVLink message. Every instant carries `t_source` saying which clock produced it, and all durations in §4 use the vehicle clock. See the 2026-09-24 amendment: the offset is no longer estimated from the first 10 heartbeats, and a host-only instant is bounded rather than assumed.
- Frames: local NED from `LOCAL_POSITION_NED`, global WGS-84 lat/lon (1e-7 deg) and altitude AMSL (mm) from `GLOBAL_POSITION_INT`; SI units in the normalised trace (m, m/s, s); origin = `SIH_LOC_LAT0/LON0/H0` [B10].
- Sampling: ≥ 10 Hz for position/velocity, every HEARTBEAT (1 Hz) and every STATUSTEXT/event; nav state from `HEARTBEAT.custom_mode` (main and sub mode) [B5].
- Missing data: a sample with a null field is kept; a gap > 1 s in position or > 3 s in heartbeat marks the run `invalid` with reason.
- Invalid-run policy: simulator crash, injection before `takeoff_complete`, any oracle in §4's last paragraph, or a manifest that fails `protocols/trace-schema.json`. Invalid runs are counted and reported, never dropped silently.

## 6. What this protocol does not define

Hardware timing; ArduPilot events (Study D); fleet separation (DO-365 well clear, deferred); ground-risk arithmetic of SORA (only its volume vocabulary is used) [B7].

## 7. Amendment — 2026-09-24

Recorded after the measurement repair
([critique](../docs/specs/formal-composition/critique-2026-09-24.md),
[packet](../evidence/task-measurement-repair-2026-09-24/README.md)). The clock paragraph in §5 had been wrong
since 2026-09-21 and described neither the estimator in use nor what an estimated instant is worth.

**Clock provenance replaces a single offset.** Every event and sample carries `t_source`:

| `t_source` | what it is |
|---|---|
| `vehicle_observation` | the vehicle stamped this message itself; the reading is exact |
| `autopilot_log` | a native uLog timestamp, stamped by the autopilot at the event |
| `cached_vehicle_observation` | the newest telemetry stamp the runner held when it acted, with `cache_age_host_s`; a lower bound on the vehicle clock at that moment, not that moment's timestamp |
| `host_reconstructed` | host time minus the median offset, which is an estimate, not a measurement |

The offset is the median over every message carrying `time_boot_ms`, not the first ten heartbeats: an estimate
taken during start-up is biased by launch latency.

**`t_vehicle_interval_s` is bounded below only.** A packet stamped at vehicle time v and received at host time
h proves the vehicle clock had reached v by h, and both clocks advance, so every later host instant is at or
after v. The upper side does not follow. A packet may be delayed in transit and arrive after the instant in
question, so the next received stamp can be *earlier* than the vehicle's true time at that instant:

> a sample generated at 8 arrives at host 10; a local action happens at host 11; a sample generated at 9
> arrives at host 12. Both clocks and both samples are monotone, and [8, 9] does not contain the action.

An earlier draft of this amendment asserted containment between neighbouring received stamps and was wrong
(owner review 2026-09-25, R1). Closing the upper side needs a justified transport or timebase bound, or a
causally post-event acknowledgment with stated timestamp semantics. This rig has neither, so the upper side is
null, every latency that depends on it is inconclusive rather than a pass, and no point estimate is clamped
into an interval and then called known.

One consequence is worth stating plainly: **no development run in this apparatus can produce a passing timing
verdict.** The discrete comparisons still decide. An empty response window is still a sound observation,
because nothing happening after the lower bound means nothing happened after the injection either.

`clock.offset_spread_s` is reported as a dispersion of the offset estimates. It is not an uncertainty budget
and must not be used as one.

**§2's `native_transition` was already right; the code was not.** This document has always said the sequence
begins after `injection`. The verifier collected every transition in the trace, including the takeoff before
the stimulus, which guaranteed a mismatch even for a correct recovery. `mode_sequence` now means the response
window only, and the transitions before the stimulus are kept separately as `setup_mode_sequence` with the
state entering the window. A control run, having no stimulus, opens its window at `takeoff_complete`.

**Flag values are kept native, and coverage is kept apart from edges.** `battery_warning` is an enum, so
1 → 2 → 3 is three transitions; converting every flag to a boolean collapsed them to one. `hazard_flag` events
now carry `value` and `previous_value` at their native types. `flags_at_injection` records the sample at or
after the injection *and* the one before it with its age, because the first sample inside the window may
already be a changed state; when no preceding sample exists it says so rather than guessing. Per-flag recording
coverage lives in `conversion.failsafe_flag_channels`: a channel that was present and never changed is not an
absent channel, and an absent channel is not evidence that its flag never rose.

**An unobserved selector is not the action `None`.** PX4 does not publish the framework's selected action over
MAVLink, so no sample observes one. Samples record the string `unobserved`. `Action::None` is a value in the
enum and JSON null was being read as it.

**U4's manoeuvre bound is defective and U4 must not be evaluated against measured runs.** Dividing the return
distance by the SIH speed limits gives the *least* time the manoeuvre can take, so §4 uses a lower bound on
time as a deadline. Every run flying at less than full speed would violate it. The replacement is a protocol
amendment and is tracked as decision D17 with the rest of the property rewrite; `harness/verify.py` does not
evaluate U4 and does not use §2's generic terminal-mode list.
