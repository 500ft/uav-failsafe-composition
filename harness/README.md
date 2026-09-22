# SITL harness (URC-04)

Four small modules, no framework, standard library plus `pymavlink`, `pyulog` and `jsonschema`. The repository
gate imports none of them: every contract test in `tests/test_runner_contract.py` runs without the SITL
dependencies because the MAVLink import is deferred until a case has been accepted.

| module | job |
|---|---|
| `cases.py` | Derives the frozen case set from the matrix, the event classes and the seed list. A case ID is computed, never typed, so a case cannot be quietly added or renamed after results exist. |
| `run_case.py` | Runs exactly one case: resolve, refuse, isolate, manifest, launch, establish tracking, inject on the vehicle clock, capture, stop, normalise. |
| `trace.py` | Turns one run directory into the normalised trace and validates it against `protocols/trace-schema.json`. |
| `normalize.py` | Re-derives `trace.json` from `raw.jsonl` without re-flying, so a normaliser fix does not cost a flight. |
| `reproducibility.py` | Compares repeated runs of one case: sequence identity and timestamp spread, deliberately not log byte identity. |

## Running one case

```bash
python -m harness.run_case --config px4-v1.17.0-sih-quadx-rtl --event datalink_loss --seed 1 \
    --px4-build ~/.cache/uav-failsafe-composition/px4/PX4-Autopilot/build/px4_sitl_default \
    --out evidence/<task>/runs/
```

`--dry-run` resolves the case and writes the manifest without launching anything, which is what the contract
tests exercise. Exit codes: `0` a completed run, even when the behaviour differs from the model; `2` setup
refusal; `3` capture or schema failure. A refused or failed run is preserved, never retried under another seed.

## What the runner refuses

An unknown configuration, event class or seed; a build whose git HEAD does not match the commit pinned in the
matrix; a missing PX4 binary; an output directory that already exists; and an event class listed in
`cases.NOT_INJECTABLE`, with the reason printed.

## Run directory

```
<case id>/
  case.json      resolved case, written before the vehicle is launched
  raw.jsonl      every message, command, parameter and event, host-clock stamped
  px4.log        autopilot stdout
  flight.ulg     autopilot log, copied out of the isolated working directory
  trace.json     normalised trace, schema-valid or marked invalid with reasons
  summary.json   case id, exit status, validity, observed transitions
  px4-work/      the autopilot's isolated working directory
```

## Two decisions that are easy to get wrong

**Injection is scheduled on the vehicle clock, not the host clock.** Lockstep ties simulation time to the
autopilot, but the stimulus arrives over UDP from this process; scheduling on host time would charge that
jitter to the autopilot. The runner waits for the vehicle's own timestamp to cross the scheduled value.

**Offboard is selected before the pre-arm gate.** The vehicle boots into Position, which requires a
manual-control source; with none present the mode cannot run, so the mode check blocks arming and the health
word never sets its pre-arm bit. Streaming setpoints and selecting Offboard first removes the dependency the
study never needed. This cost a day to find; the evidence is in
`evidence/task-study-a-harness-2026-09-20/README.md`.
