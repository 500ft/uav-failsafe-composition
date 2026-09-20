# Configured-vehicle matrix (URC-02) — frozen 2026-09-16

Identity = autopilot + firmware commit + airframe + complete parameter set + recovery intention (research-plan.md). This file pins one PX4 identity family; ArduPilot is Study D. Machine-readable form: [configuration-matrix.json](configuration-matrix.json); `tests/test_configuration_matrix.py` recomputes every realised action from the model and every parameter hash.

**Firmware.** PX4-Autopilot `v1.17.0`, commit `d6f12ad1c4f70ad3230afd7d86e971421e02fef4` [B1][B10]. **Vehicle.** `10040_sihsim_quadx`, PX4's simulation-in-hardware quadrotor (no external physics simulator), lockstep enabled; SIH mass 1.0 kg, inertia diag(0.025, 0.025, 0.030) kg·m², max thrust 5 N per rotor, origin 47.397742 N 8.545594 E 489.4 m [B10]. **Common parameters** (all rows): `SYS_FAILURE_EN=1` so failure injection is accepted [B3]; RTL altitudes at defaults [B10]; no exception bits.

**Equivalence rule.** A configuration realises intention I for hazard class H iff the parameter map of the pinned code [B1 failsafe.cpp L43-443] yields action I for H (model/px4_failsafe.py configured_action). A configured identity intends I iff every supported class maps to I; classes for which PX4 cannot express I are listed under unsupported and the row still intends I for the remaining classes. Vendor defaults intend nothing and are the reference row.

**Timers** (defaults unless a row says otherwise): `COM_OF_LOSS_T`=1.0 s [B4], `COM_DL_LOSS_T`=10 s, `COM_RC_LOSS_T`=0.5 s, `COM_FAIL_ACT_T`=5 s [B10][B2]. The `dll5` row sets the C2 Link timer to 5 s to match the MAVLink heartbeat convention [B5] and ArduPilot's default [B6].

| configuration_id | intention | deltas from defaults | realised action per class | unsupported for intention |
|---|---|---|---|---|
| `px4-v1.17.0-sih-quadx-defaults` | vendor_defaults | — | datalink_loss→None, rc_loss→RTL, offboard_loss→FallbackPosCtrl, geofence_breach→Hold, position_low→RTL, battery_critical→Warn, battery_emergency→Warn | — |
| `px4-v1.17.0-sih-quadx-hold` | Hold | NAV_DLL_ACT=1, NAV_RCL_ACT=1, COM_OBL_RC_ACT=5, GF_ACTION=2, COM_POS_LOW_ACT=2 | datalink_loss→Hold, rc_loss→Hold, offboard_loss→Hold, geofence_breach→Hold, position_low→Hold, battery_critical→Warn, battery_emergency→Warn | battery_critical, battery_emergency |
| `px4-v1.17.0-sih-quadx-rtl` | RTL | NAV_DLL_ACT=2, NAV_RCL_ACT=2, COM_OBL_RC_ACT=3, GF_ACTION=3, COM_POS_LOW_ACT=3, COM_LOW_BAT_ACT=1 | datalink_loss→RTL, rc_loss→RTL, offboard_loss→RTL, geofence_breach→RTL, position_low→RTL, battery_critical→RTL, battery_emergency→RTL | — |
| `px4-v1.17.0-sih-quadx-land` | Land | NAV_DLL_ACT=3, NAV_RCL_ACT=3, COM_OBL_RC_ACT=4, GF_ACTION=5, COM_POS_LOW_ACT=5, COM_LOW_BAT_ACT=2 | datalink_loss→Land, rc_loss→Land, offboard_loss→Land, geofence_breach→Land, position_low→Land, battery_critical→Land, battery_emergency→Land | — |
| `px4-v1.17.0-sih-quadx-rtl-delay0` | RTL | NAV_DLL_ACT=2, NAV_RCL_ACT=2, COM_OBL_RC_ACT=3, GF_ACTION=3, COM_POS_LOW_ACT=3, COM_LOW_BAT_ACT=1, COM_FAIL_ACT_T=0.0 | datalink_loss→RTL, rc_loss→RTL, offboard_loss→RTL, geofence_breach→RTL, position_low→RTL, battery_critical→RTL, battery_emergency→RTL | — |
| `px4-v1.17.0-sih-quadx-rtl-dll5` | RTL | NAV_DLL_ACT=2, NAV_RCL_ACT=2, COM_OBL_RC_ACT=3, GF_ACTION=3, COM_POS_LOW_ACT=3, COM_LOW_BAT_ACT=1, COM_DL_LOSS_T=5 | datalink_loss→RTL, rc_loss→RTL, offboard_loss→RTL, geofence_breach→RTL, position_low→RTL, battery_critical→RTL, battery_emergency→RTL | — |

**Unsupported cases.** Terminate and Disarm actions are not exercised in SITL flight (they end the run; recorded as reachable actions only) · VTOL/fixed-wing rows · battery Hold intention (not expressible) · RC-loss injection is supported only if the failure-injection unit for RC signal is available on this build; otherwise the class is skipped and recorded · ArduPilot rows (Study D)

**Cross-autopilot counterparts (for Study D, not exercised here).** `NAV_DLL_ACT` ↔ `FS_GCS_ENABLE`, `COM_DL_LOSS_T` ↔ `FS_GCS_TIMEOUT [B6]`, `COM_LOW_BAT_ACT` ↔ `FS_BATT_ENABLE`, `GF_ACTION` ↔ `FENCE_ACTION`, `COM_FAIL_ACT_T` ↔ `no direct counterpart (ArduPilot acts immediately)`.

Each row's `parameters_sha256` is the hash of the sorted full parameter dictionary (common + deltas); the harness recomputes the hash from the vehicle's actual parameter export at run time and refuses to record a trace whose export disagrees.
