# Number-provenance audit — 2026-09-25

Every quantity in this repository whose value could change a verdict, a gate or a claim, with where it came
from and what it does not support. The canonical register is
[`protocols/quantities.json`](../protocols/quantities.json); `tests/test_quantities.py` checks each entry
against the code that uses it, so the register cannot quietly diverge from the thing it describes.

**Findings first.** Twenty-one quantities are consequential. Twelve are chosen by us, five are read from PX4 or
a standard, two are measured outcomes, one is calculated, and one has no value at all and blocks the timing
half of two properties.

## What the audit found

**Most of the numbers in this repository are choices, not derivations.** Twelve of twenty-one are `selected`.
That is not a defect in a study whose apparatus is still being trusted, but it was not visible before: a reader
met 1.5 s, 10 s, 45 s and 0.60 with no way to tell which were forced and which were judgement. Each now states
its rationale, what it is not, and what would validate it.

**One quantity has no value and is load-bearing.** `Q-RESIDUAL`, the update and transport residual on any
latency, is unresolved because the injection instant is a cached telemetry stamp with no defensible upper
bound. It is why U1's and U4's deadlines are labelled not yet evaluable rather than filled in, and why no
timing verdict from this apparatus can pass. Naming it is the honest alternative to picking a plausible number.

**Two quantities were being read as stronger than they are.** `Q-REPEAT-NEW` at 0.352 s is the range of one
event over four repeats of one scenario. It is repeatability, and it was briefly used to argue that the frozen
tolerance was conservative. It supports no such claim, and the register now records that it is reported and
never consumed, with a test that fails if a consumer appears. `Q-HB-RATE` at 1 Hz is the resolution of one
observation route and was being generalised into a universal margin for every kind of event.

**Three sourced quantities are transcriptions that no independent check has confirmed.** `Q-RECHARGE`,
`Q-DELAY-EPS` and the action tables come from reading `framework.cpp` at the pinned commit. Their validation
field says transcription self-check only. The native oracle is what would change that.

**One measured discrepancy is unexplained and is not hidden by the audit.** `Q-DL-LOSS-T` predicts a hazard at
10.0 s; the runs show 11.4 s to 12.0 s. The verdict is inconclusive rather than refuted only because the
timing route is unbounded, not because the discrepancy went away.

## The register at a glance

| provenance | count | what it means here |
|---|---|---|
| selected | 12 | chosen by us, defensible, not forced |
| sourced | 5 | read from PX4 source, vendor docs or a standard, with a locator |
| measured_result | 2 | observed in a run; one of them superseded |
| calculated | 1 | derived from other registered quantities |
| provisional | 1 | no support yet; a dependent conclusion is open |

| evidence status | count |
|---|---|
| frozen | 12 |
| source_verified | 6 |
| observed | 1 |
| superseded | 1 |
| unresolved | 1 |

## Decisions and their gaps

| quantity | value | provenance | gap, and what it would cost to be wrong | priority |
|---|---|---|---|---|
| `Q-RESIDUAL` | none | provisional | No timing property can be evaluated. A latency reported as passing would be unsupported. | **high** |
| `Q-RECHARGE` | dt/4 | sourced | Transcribed, not differentially checked. If wrong, every shared-delay prediction is wrong, and that is the mechanism the interaction study targets. | **high** |
| `Q-DL-LOSS-T` | 10 s | sourced | The observed 11.4 to 12.0 s is unexplained. If the detector is slower than documented, T1, T2 and T5 all mispredict. | **high** |
| `Q-TOL` | 1.5 s | selected | Frozen on a superseded basis. Too wide hides a real deviation; it cannot be re-derived from these runs without fitting. | medium |
| `Q-U3-WINDOW` | 10 s | selected | Unvalidated study parameter. Too short misses slow flapping; too long admits legitimate escalation. | medium |
| `Q-HORIZON` | 45 s | selected | Only partly validated. If a recovery were slower than 45 s, the runs would report a false absence. | medium |
| `Q-SETTLE` | 1 m, 0.3 m/s | selected | Fires before the autopilot's own transition, which is why T6 expects an extra mode change. A tighter test would move that transition across the window boundary. | medium |
| `Q-U4-MARGIN` | 2 s | selected | Generalises a heartbeat period to events that do not use that route. Inert while U4's deadline is unevaluable. | low |
| `Q-SEED-OFFSETS` | ±2 s | selected | Values are fine; the defect was calling them independent worlds. Now labelled designed coverage. | low |
| `Q-ORACLE-BUDGET` | 60 min | selected | No PX4 build has ever been observed on this runner, so the budget is a guess. A timeout is recorded as an environment result. | low |

## What this audit does not do

It does not make any number correct. It records what each one is, so a reader can see which conclusions rest
on a measurement, which rest on a reading of the source, and which rest on our judgement. Three of the four
high-priority gaps resolve only with the native oracle or a new run.

It also does not inventory every literal. Ports, retry counts, buffer sizes and timeouts that cannot change a
verdict are deliberately absent, and the register says so.
