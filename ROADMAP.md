# Research Roadmap

This roadmap is gate-driven. Later stages do not start merely because an earlier date has passed.

## Stage 0 — Research contract

**Status:** complete for the concept repository.

- Define the configured-vehicle unit of analysis.
- Separate established prior art from the candidate research gap.
- Register hypotheses, observables, baselines, and failure branches.
- Define configuration and data manifests.

**Exit gate:** a cold reader can identify the question, evidence state, first experiment, and stop condition without assuming results exist.

## Stage 1 — SITL conformance pilot

**Status:** not started.

- Pin one PX4 and one ArduPilot release.
- Configure equivalent Hold, Land, and RTL intentions.
- Archive every parameter and environmental assumption.
- Remove offboard authority from randomized bounded states.
- Record mode traces, transition latencies, trajectories, and reconnection behavior.

**Exit gate:** the pilot estimates variability and invalid-run frequency. Then freeze the coverage target, sample size, split, horizon, and volume rule before generating separate confirmatory traces. Only the confirmatory set can establish held-out coverage and the provisional 10% volume-reduction continuation target.

**Failure branch:** if differences are below 5% and operationally negligible, stop the fleet algorithm and release a versioned conformance benchmark.

**Indeterminate branch:** a 5–10% reduction or uncertainty spanning a decision boundary does not authorize fleet expansion. Report the interval; preregister one additional bounded confirmation or stop at the benchmark. Do not recycle pilot observations as confirmation or move the threshold after inspection.

## Stage 2 — HITL replication

**Status:** blocked on Stage 1.

- Repeat the decisive conditions with matched flight-controller hardware.
- Measure timing jitter and hardware-specific transition delays.
- Update, but do not retrospectively relax, the registered uncertainty model.

**Exit gate:** the qualitative Stage 1 finding survives held-out HITL trials.

## Stage 3 — Offline fleet composition

**Status:** blocked on positive Stage 1 confirmation. Stage 2 is not required for explicitly simulated/offline composition; it remains required for hardware-timing claims.

- Insert held-out recovery traces into prerecorded or simulated fleet encounters.
- Compare native behavior, a global tube, individualized tubes, and neighbor evacuation.
- Report safety margins and mission-cost differences together.

**Exit gate:** individualized contracts improve the registered mission-cost estimand at matched recovery-tube coverage.

## Stage 4 — Contained physical validation

**Status:** contingent; not authorized.

- Begin with one airframe flashed alternately with both stacks.
- Use a second airframe only for external-validity checks.
- Progress to two slow vehicles only after single-vehicle conformance is established.

**Exit gate:** facility approval, completed risk review, trained operators, independent kill path, and no unresolved Stage 1–3 conformance failures.

## Stage 5 — Thesis-scale extensions

These do not block the minimum publishable core:

- Abstract failsafe-intent compiler
- Online distribution-shift detection
- Capability-aware mission allocation
- Joint mission and recovery optimization
- Larger heterogeneous fleet demonstration
