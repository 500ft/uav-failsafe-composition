# Measurement repair and re-derivation — 2026-09-24

Branch `task/measurement-repair-2026-09-24` off main `9db5112`. This is the packet for the owner's
2026-09-24 literature critique, findings F1, F2, F3 and F11, and its TASK 1 and TASK 2.

**Evidence state: simulation, re-derived.** No new run was flown and no simulator was launched. Every number
below comes from re-deriving the existing development captures with the corrected normaliser.

## What was re-derived

`renormalize.py` copies each stored capture into a scratch directory, rebuilds its trace from `raw.jsonl` and
`flight.ulg` only, verifies it, and writes the comparison to `rederivation.json`. The stored runs are not
modified, and the derivations that shipped with them are not rewritten. Run it under the project venv:

```bash
~/.cache/uav-failsafe-composition/venv/bin/python evidence/task-measurement-repair-2026-09-24/renormalize.py
```

The script refuses to run without `pyulog`. Without it the autopilot log is silently ignored, every run loses
its mode transitions and its hazard flags, and the comparison looks meaningful while measuring nothing. That
failure was hit once during this work and is now an upfront refusal.

## Verdicts before and after

| Run | Before | After | Why it changed |
| --- | --- | --- | --- |
| 2026-09-20 rep1 control | not verified | **unverified** | the capture is already marked `simulator_crash`, and an invalid run cannot be compared |
| 2026-09-20 rep2–rep5 control | not verified | **verified** | selecting Offboard before takeoff is setup, not a control run changing mode |
| 2026-09-21 datalink, delay 0 | refuted | **refuted** | same conclusion, different reason |
| 2026-09-21 datalink | refuted | **refuted** | same conclusion, different reason |
| 2026-09-22 geofence, Terminate | refuted | **refuted** | same conclusion, different reason |
| 2026-09-22 geofence | refuted | **refuted** | same conclusion, different reason |
| 2026-09-23 datalink, Auto Loiter | refuted | **refuted** | same conclusion, different reason |

**The finding survives the repair.** In all five injected runs the response window after the stimulus contains
no mode transition at all. The earlier verifier reached `refuted` partly by comparing the takeoff that happened
*before* injection against the expected recovery, which would have refuted a correct recovery too. With the
setup excluded, the response sequence is empty and the mismatch is with nothing rather than with takeoff.

## What the corrected clock changed

Every injection instant moved later, to the reading the runner took from the vehicle's own clock at the moment
it injected. The earlier normaliser discarded that reading and rebuilt the instant from host time.

| Run | Injection, before | Injection, after | Hazard latency, before | After |
| --- | --- | --- | --- | --- |
| 2026-09-21 datalink, delay 0 | 56.222 s | 56.740 s | 11.930 s | 11.412 s |
| 2026-09-21 datalink | 55.727 s | 56.244 s | 12.525 s | 12.008 s |
| 2026-09-22 geofence, Terminate | 55.952 s | 56.384 s | 4.020 s | 3.588 s |
| 2026-09-22 geofence | 55.410 s | 55.948 s | 4.522 s | 3.984 s |
| 2026-09-23 datalink, Auto Loiter | 57.780 s | 58.128 s | 12.100 s | 11.752 s |

One verdict detail changes with it. The 2026-09-21 delay-0 run's datalink latency was reported as 11.93 s
against a predicted 10.0 s, outside the 1.5 s tolerance. On the vehicle's own clock it is 11.412 s, inside it.
That run's remaining mismatch is the absent recovery, not the detector. The other datalink latencies are still
outside tolerance, by less than before.

The host-to-vehicle offset spread is unchanged at 11.4 s to 19.3 s across the runs, and is now reported as
what it is: a dispersion, not an uncertainty bound. Instants that genuinely have no vehicle-clock reading are
bracketed by the nearest real readings either side of them instead.

## The Auto Loiter run is no longer read as the Offboard case

`intended_mode` was written onto the manifest after normalisation, so re-deriving the 2026-09-23 capture
produced an Offboard manifest and compared it against the Offboard timeline. It is now recorded in
`case.json` by the runner, and for captures that predate that, recovered from the `DO_SET_MODE` command in
`raw.jsonl` — a primary observation, not the derived summary. The 2026-09-23 run re-derives as `auto_loiter`
with `intended_mode_source: raw_capture_do_set_mode`, and the 2026-09-20 rep1 capture, which records no such
command, re-derives with a null intended mode and is `unverified` rather than silently compared.

## What this packet does not establish

It does not explain why no action is selected. It repairs the chain that reports the observation, which is
what the critique asked for before the diagnosis continues. The offline differential oracle remains the
critical path and remains blocked on an environment. Nothing here promotes a literature reading status,
closes an owner gate, or releases the held campaign.
