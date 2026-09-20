# Study A contracts and decisions (week plan, day 1) — 2026-09-19

Branch `task/study-a-contracts-2026-09-19` off main `929cc8a` (the merge of PR #6, which you merged on 2026-09-16 after the audit PR; the handoff named this commit but was written from a checkout 19 commits behind it). Machine-readable environment: [environment.json](environment.json). Handoff being executed: `NEXT-WEEK-PLAN-2026-09-19.txt`, held outside the repository. Its critique: [plan-critique-2026-09-19.md](../../docs/specs/formal-composition/plan-critique-2026-09-19.md).

**Evidence state of everything in this PR: planned.** No study result, no trace, no model-checking outcome exists. Two apparatus probes were executed and are reported as apparatus facts, not results.

## What was executed

| task | outcome |
|---|---|
| M1.1 baseline and environment | Recorded in `environment.json`: macOS 14.7.3 arm64; repository gate on Python 3.11.8 with jsonschema 4.26.0; a separate isolated venv for SITL work with pymavlink 2.4.49 and pyulog; cmake, ninja and ccache installed via homebrew on 2026-09-16. |
| M1.1 PX4 availability | **PX4 v1.17.0 cloned and built.** Commit `d6f12ad1c4f70ad3230afd7d86e971421e02fef4`, target `px4_sitl_default`, 1109 ninja targets, build succeeded. The clone and build live outside git under `~/.cache/uav-failsafe-composition/px4/`. |
| M1.1 checker availability | **UPPAAL/verifyta absent.** No binary on PATH, nothing in `/Applications`, no homebrew formula. Raised as owner decision D8; Study B cannot start until it is answered. |
| M1.2 owner decisions | [decisions-2026-09-19.md](../../docs/specs/formal-composition/decisions-2026-09-19.md), twelve decisions with the three that need your answer marked. |
| T2.1 URC-02 matrix | [protocols/configuration-matrix.md](../../protocols/configuration-matrix.md) and its JSON: six rows, one pinned firmware and airframe, an equivalence rule computed from the pinned parameter maps rather than asserted, per-row parameter hashes, and the unsupported cases named. |
| T2.2/T2.3 URC-03 contract | [protocols/event-semantics.md](../../protocols/event-semantics.md), [protocols/trace-schema.json](../../protocols/trace-schema.json), one valid fixture and eight invalid variants in `tests/test_trace_schema.py`. |
| R4.3 properties, brought forward | [protocols/unsafe-composition-properties.json](../../protocols/unsafe-composition-properties.json): U1-U4 with five source-linked exclusions, corrected per critique findings 2 and 3, status `planned, not executed`. |
| model tables | [model/px4_failsafe.py](../../model/px4_failsafe.py): the discrete parameter-to-action maps and the action selector transcribed from the pinned source with per-rule line references, plus an assert-based self-check. This is the transcription the timed model will be built from; it is not the timed model. |
| baseline register | [docs/baselines/README.md](../../docs/baselines/README.md): eleven sources, each with what was read, its SHA-256, why it was chosen, and how it is adapted. `tests/test_baselines.py` fails if a citation does not resolve or an entry is never cited. |

## Apparatus probes (facts about the rig, not results)

1. **SITL runs and is observable.** The bring-up script launches the pinned build, and HEARTBEAT, LOCAL_POSITION_NED, GLOBAL_POSITION_INT, SYS_STATUS and STATUSTEXT arrive on UDP 14550. Matrix parameters can be set and read back, which is what the manifest hash needs.
2. **Arming is blocked.** With no fault injected the vehicle refuses to arm: *"Arming denied: Resolve system health failures first"*, and the pre-arm health bit was not observed within 120 s. Failure injection being enabled was ruled out as the cause: `SYS_FAILURE_EN` is not an arming check in the pinned tree. The GCS link was registered, because the autopilot only reported losing it after the script stopped heartbeats.

   **This is the week's real blocker.** The no-fault control, the five-run reproducibility check and the whole validation campaign sit behind it. Next diagnostic, in order: set `SDLOG_MODE` to log from boot and read the `health_report` topic from the uLog; failing that, query the running instance's pre-arm check list directly. Neither needs an owner decision.

## Scope of the bring-up script

`harness/` is included so the blocker is reproducible. It is **apparatus bring-up, not the runner contract**: it does not yet resolve a case from the frozen matrix, refuse a hash mismatch, or schedule injection on vehicle time (decision D6). URC-04 is not complete and is not claimed.

## Checks observed

| command | result |
|---|---|
| `python -m unittest discover -s tests -q` | OK, 70 tests (18 new) |
| `python scripts/check_repo_contract.py` | PASS |
| `python scripts/acquisition_ledger.py --check` | consistent |
| `python scripts/reference_coverage.py --check` | OK, day2 0/6, day4 3/6 |
| `python evidence/task-2026-09-09/rerun_search.py --audit evidence/task-2026-09-11-public/database-export.json` | exit 0 |
| `python tools/check_presentation.py . "UAV Failsafe Composition" uav-failsafe-composition` | no issues |
| `python tools/test_presentation.py` | OK |
| `git diff --check` | clean |
| `python model/px4_failsafe.py` | self-check OK |

## Final review checklist from the handoff

Branch from latest main: **yes** (`929cc8a`). Owner-approved direction recorded: **yes**, the five tasks you agreed on 2026-09-16. PX4 identity pinned by commit: **yes**. Vehicle model fixed: **yes**. Every event class explicit about the interrupted input: **yes**, and one proposed class was found not to be separable and was deferred. Configuration variants one-factor: **yes**. Seeds, horizon, units, clocks, frames frozen: **yes**. Runner refuses a mismatched configuration: **no, not built** (URC-04 open). No-fault control exists: **no, blocked and documented**. Invalid runs preserved: **policy frozen, no runs yet**. Raw and normalised traces separate: **yes in the contract**. Model transitions source-linked: **yes for the discrete tables; the timed model is not built**. U1-U4 frozen before checking: **yes**. Witness replay with matching hashes: **not built** (Friday). Disagreements classified without post-hoc changes: **rule frozen, nothing to classify yet**. Simulation claims separated from safety claims: **yes**. Repository gate passed on the recorded interpreter: **yes**. PR describes what was not done: **yes**.

**Foundation incomplete.** Next task: diagnose the arming blocker, then build the runner to the contract with vehicle-time injection.

## What cannot be claimed

Nothing here says anything about PX4's safety, about hardware or flight timing, about ArduPilot, or about fleets. No prior-art distinctiveness statement is made: URC-01 is partial and the formal-composition axis is still unsearched.
