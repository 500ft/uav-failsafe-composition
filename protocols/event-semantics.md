# Event, trace and unsafe-state semantics (URC-03) — frozen 2026-09-16

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
| `hazard_flag` | first sample in which the corresponding failsafe flag is true (from `vehicle_status`/`failsafe_flags` over MAVLink or the uLog) | [B1] |
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
| **U4 unbounded time-to-safe-state** | time from `hazard_flag` to `terminal_state` exceeds (configured loss timer + `COM_FAIL_ACT_T` + expected manoeuvre time) + 2.0 s, where the expected manoeuvre time is computed from `RTL_RETURN_ALT`, `RTL_DESCEND_ALT` and the SIH model's speed limits | a contingency must end inside the declared buffer [B7 §2.2.4]; the delay structure is Hold-then-act [B2][B1]; 2.0 s margin = two heartbeat periods [B5] (**assumption**) |
| **containment (recorded, not decided)** | position leaves the declared flight geography (geofence) or the contingency volume during recovery | operational volume = flight geography + contingency volume [B7 §2.2.1-2.2.3]; PX4 `GF_ACTION` [B1 failsafe.cpp L86-127] |

Inherited invalid-run oracles (a run is invalid, not unsafe): no vehicle heartbeat for 2 s [B11 S2]; vehicle stationary with an incomplete mission before injection [B11 S1]; lockstep desync or log gap > 1 s (**assumption**).

## 5. Clocks, frames, units, missing data

- Two clocks per sample: host monotonic (`t_host_s`, from the harness) and vehicle `time_boot_ms` from the MAVLink message; alignment offset estimated from the first 10 heartbeats and stored in the manifest; all durations in §4 use the vehicle clock.
- Frames: local NED from `LOCAL_POSITION_NED`, global WGS-84 lat/lon (1e-7 deg) and altitude AMSL (mm) from `GLOBAL_POSITION_INT`; SI units in the normalised trace (m, m/s, s); origin = `SIH_LOC_LAT0/LON0/H0` [B10].
- Sampling: ≥ 10 Hz for position/velocity, every HEARTBEAT (1 Hz) and every STATUSTEXT/event; nav state from `HEARTBEAT.custom_mode` (main and sub mode) [B5].
- Missing data: a sample with a null field is kept; a gap > 1 s in position or > 3 s in heartbeat marks the run `invalid` with reason.
- Invalid-run policy: simulator crash, injection before `takeoff_complete`, any oracle in §4's last paragraph, or a manifest that fails `protocols/trace-schema.json`. Invalid runs are counted and reported, never dropped silently.

## 6. What this protocol does not define

Hardware timing; ArduPilot events (Study D); fleet separation (DO-365 well clear, deferred); ground-risk arithmetic of SORA (only its volume vocabulary is used) [B7].
