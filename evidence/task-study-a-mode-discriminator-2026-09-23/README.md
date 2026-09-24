# The mode hypothesis is eliminated too — 2026-09-23

Branch `task/study-a-mode-discriminator-2026-09-23` off main `3b65482`. This tests the last structural
hypothesis left by [the 2026-09-22 diagnostics](../task-study-a-diagnostics-2026-09-22/README.md): that
action selection is suppressed specifically while the user-intended mode is Offboard.

**Evidence state: simulation.** One development run, not a held-out validation case.

## Result

It is not Offboard. The same datalink loss, on the same configuration, with the vehicle flying in **Auto
Loiter** instead of Offboard, produces the same outcome: the monitor fires and no action follows.

| | Offboard (2026-09-21) | Auto Loiter (today) |
|---|---|---|
| run valid | yes | yes |
| `gcs_connection_lost` rose | +12.5 s after injection | +12.1 s |
| action announced by the autopilot | none | none |
| mode after the hazard | Offboard held | Auto Loiter held |
| `vehicle_status.failsafe` | 0 | 0 |

Auto Loiter needs neither a setpoint stream nor a manual-control source, so this run also removes the
offboard stream from the picture entirely. The prediction, committed before the run as timeline T5, was
`AUTO_RTL` about 15 s after the injection. It is **refuted**.

## The elimination list is now

Not datalink-specific · not the delayable or takeover-able actions · not deferral · not land detection · not
arming · not parameter delivery · **not Offboard**. What remains is narrow: the framework's
`checkStateAndMode` not running at all, or the framework seeing a different armed state or a different
`failsafe_flags` instance than the one published to the log. Both are questions about the autopilot's
internals that the rig cannot answer from outside, which is why the offline oracle is now the critical path.

## Three harness defects this run exposed

Each was found because a stage failed loudly rather than passing quietly, and each would have corrupted the
campaign if it had been launched.

1. **Parameter read-back could return a bit pattern instead of a value.** PX4 emits a `PARAM_VALUE` broadcast
   after a set as well as a reply to an explicit read, and the two encode integers differently: the reply
   carries the numeric value, the broadcast carries the integer's bit pattern, so a value of 1 arrives as
   1.4e-45. Reading without draining first could pick up the broadcast. The reader now drains, requests, and
   accepts either encoding. An independent check against the autopilot confirmed the values themselves were
   correct throughout, so no earlier conclusion changes.
2. **The takeoff altitude was sent as a relative height in an absolute field.** The autopilot treated the
   target as already reached, never climbed, and disarmed. The vehicle now uses its configured takeoff
   altitude, declared once in `harness/cases.py`.
3. **The climb was the one stage with no record.** When it failed there was nothing to read. It now emits a
   probe every five seconds carrying the best altitude reached against the target.

## Checks observed

| command | result |
|---|---|
| `python -m unittest discover -s tests -q` | OK, 98 tests |
| `python scripts/check_repo_contract.py` | PASS |
| `python scripts/acquisition_ledger.py --check` | consistent |
| `python scripts/reference_coverage.py --check` | OK, 0/6 and 3/6 |
| presentation checks | no issues |
| `git diff --check` | clean |

## The remote machine, and what it can and cannot do

The GPU host is reachable and was surveyed non-interactively: Windows 11 Home, an RTX 4070 SUPER, 38 GB free,
and **WSL is not installed**. The decisive next test is PX4's own failsafe unit test driving the real
`Failsafe` class, which needs Linux because the binary will not run on macOS. Installing WSL means a system
change and a restart on a machine with no monitor, so it is recorded as a decision rather than taken.

**No CAD is needed for this task or any task currently in scope.** The project has no fixture, mount or
enclosure, and section 12's CAD guidance is explicitly conditional on one existing. When that changes, the
first deliverable is a dimension contract with units and acquisition routes, not a model.
