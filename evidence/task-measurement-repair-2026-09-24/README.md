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

## Corrected 2026-09-25 after owner review

The owner reviewed PR #29 and reproduced three defects with in-memory probes. All three reproduce here exactly
as reported, and the numbers in the table below are now read differently than when this packet was written.

**The receive-time bracket was not a bound.** This packet published an interval built from the nearest received
stamps either side of an instant. A packet can be delayed past the instant, so the later stamp can be earlier
than the vehicle's true time there, and the interval need not contain the event. Only the lower side survives.
The runner's injection timestamp is also a cached telemetry stamp rather than a reading taken at the instant,
so it too is open above. The consequence is stated plainly in `protocols/event-semantics.md`: **no development
run in this apparatus can produce a passing timing verdict.** Every latency below is now `inconclusive`.

What does not change: the discrete comparisons. An empty response window is still sound, because nothing
happening after the injection's lower bound means nothing happened after the injection either. The five
injected runs remain refuted on their mode sequences.

**The repeat range is repeatability, not accuracy.** The table below reports how far the same scenario moved
between four repeats of one event. It does not bound the error of an injection-relative latency, four repeats
establish no tail, and the earlier claims that 1.5 s is "about 4.3 times the measured jitter" and that the
direction is "safe" are withdrawn. A wider tolerance hides real deviations as readily as it suppresses false
alarms. 1.5 s is retained because it was frozen before the runs it judges, and for no other reason.

**The reproducibility statistic had no cohort.** `jitter_quotable` depended on clock provenance alone, so one
valid record at 10 s and an invalid, differently configured record at 99 s reported 89 s as quotable jitter;
two different intended modes counted as one identity; and two clock sources were pooled under a promise not to
pool. Statistics are now formed only over valid runs sharing a composite identity, per clock source.

## The retained repeat range



The 1.5 s tolerance in `protocols/expected-timelines.json` was frozen before the runs as three times a measured
apparatus jitter of 0.51 s. That figure came from `harness/reproducibility.py` over the 2026-09-20 control
repeats, computed when every instant was reconstructed from host time, so it folded per-run offset-estimation
variance into the spread. Re-derived over the four valid repeats on the vehicle's own clock:

| Event (n=4 repeats) | Range, old conversion | Range, vehicle clock | Observation route |
| --- | --- | --- | --- |
| `arm` | — | 0.163 s | host estimate, not reportable |
| `takeoff_complete` | 0.338 s | 0.336 s | vehicle stamp, reportable |
| `horizon_reached` | 0.514 s | 0.352 s | vehicle stamp, reportable |

**The tolerance value is not changed.** It was frozen before the runs, and tightening it now against the data
it has to judge would be fitting. Only its basis text is corrected. No claim is made that 1.5 s is validated,
conservative or safe: this range does not support any of those readings.

`harness/reproducibility.py` now reports spreads per clock source and refuses to pool them. A spread is
`measured` only when every instant came from the vehicle's own clock; `estimated`, `mixed_clock_sources` and
`unrecorded_provenance` are reported but cannot be quoted as apparatus jitter. A trace from before this repair
carries no `t_source`, and is labelled `unrecorded_provenance` rather than assumed to be measured.

## Earlier evidence records

The packets from 21, 22 and 23 September state verdicts produced by the pre-repair pipeline. They are kept
exactly as written and each now carries a dated pointer to this re-derivation.

## What this packet does not establish

It does not explain the missing recovery. No expected post-injection recovery-mode transition was observed and no new failsafe announcement was seen; the internal selected action and its cause remain unresolved. The selector is not on any channel this rig records, so `selected_action` is `unobserved`, and an absent announcement is not a continuous record of selector state (owner review 2026-09-25, R4). It repairs the chain that reports the observation, which is
what the critique asked for before the diagnosis continues. The offline differential oracle remains the
critical path and remains blocked on an environment. Nothing here promotes a literature reading status,
closes an owner gate, or releases the held campaign.
