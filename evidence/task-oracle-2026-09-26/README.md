# The native failsafe oracle runs — 2026-09-26

Decision D14, route (b). GitHub Actions run
[36222455516](https://github.com/500ft/uav-failsafe-composition/actions/runs/36222455516), 9 minutes wall clock
against a 60-minute budget.

**Evidence state: executed, pinned.** This is layer B of the three-layer differential. It is not an independent
safety oracle: it is the implementation under study, driving its own test fixture.

## What ran

| | |
|---|---|
| PX4 commit | `d6f12ad1c4f70ad3230afd7d86e971421e02fef4`, describes as `v1.17.0` |
| Runner | `ubuntu-24.04`, kernel 6.17.0-1022-azure, x86_64 |
| Compiler | `c++ (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0` |
| CMake | 3.31.6 |
| Build target | `px4_sitl_test`, 1686 targets |
| Test binary | `functional-failsafe_test`, sha256 `682696ce5168d1ad74ceb252b738eb6ba981f5dc4ddd7c3a78fb31172e976991` |
| Cases declared in source | 9 |
| Cases listed by the binary | 9 |
| Cases run, each in its own process | 9 |
| Cases passed | 9 |

All nine: `general`, `takeover`, `takeover_denied`, `can_takeover_degraded_failsafe`,
`no_immediate_takeover_when_failsafe_on_mode_switch`, `defer`, `defer_and_clear`, `skip_failsafe`,
`user_termination`.

## The first dispatch was green and proved nothing

Run [36221992524](https://github.com/500ft/uav-failsafe-composition/actions/runs/36221992524) reported
`1/1 Test #74: functional-failsafe_test ... Passed 0.00 sec` and exited zero. ctest runs the whole gtest binary
as one entry and suppresses its output on success, so that line says a process exited zero. No gtest case name
appeared anywhere in the 1834-line log, and 0.00 seconds for nine functional cases with uORB and parameter
setup is a reason to doubt, not to celebrate.

The script now locates the executable, records its hash, asserts it lists exactly as many cases as the source
declares, and runs each case in its own process because PX4 warns that repeated setup in one process may not
clean up fully. A count mismatch fails the job. That check is the reason this packet can say nine rather than
one.

## What this establishes, and what it does not

**Establishes.** PX4's failsafe framework builds and its own unit tests pass on an ordinary Ubuntu runner at
the pinned commit. The environment question behind D14 is closed: no WSL, no cloud instance, no reboot of the
headless host. The apparatus for layer B exists and is reproducible from a hash-pinned binary.

**Does not establish anything about the integrated anomaly.** These are PX4's own tests driving the class with
synthetic state. They do not exercise whether `checkStateAndMode` is called in the running autopilot, whether
it sees the armed state and flags instance that get logged, or why no recovery mode is committed. The class
selecting actions correctly under its own fixture makes the integration a more likely location for the fault
than the selector logic, and that is an inference about where to look next, not a diagnosis.

**Does not validate the Python model.** The transcription in `model/px4_failsafe.py` has still never been
compared against this class on the same inputs. `Q-RECHARGE` and `Q-DELAY-EPS` remain
transcription-checked. Running the upstream suite is not a differential result, and this packet does not
claim one.

## Next discriminating step

Drive the same six shared-delay sequences from `tests/test_shared_delay_memory.py` through this binary via a
minimal adapter, and compare its selected actions against the model's. That is the first comparison that could
localise a discrepancy between layers A and B. Only after A and B agree does a disagreement with layer C, the
integrated runtime, point at the integration.

## Reproducing

```bash
gh workflow run native-failsafe-oracle
```

Artifacts are retained for 90 days on the run; the durable copies and their `checksums.json` are in this
directory. `build_and_run.log.gz` is the complete build and ctest log.
