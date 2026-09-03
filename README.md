# UAV Recovery Contracts

[![CI](https://github.com/500ft/UAV-Recovery-Contracts/actions/workflows/ci.yml/badge.svg)](https://github.com/500ft/UAV-Recovery-Contracts/actions/workflows/ci.yml)
![Status: research design](https://img.shields.io/badge/status-research%20design-415a77)
![Evidence: no results yet](https://img.shields.io/badge/evidence-no%20results%20yet-6b7280)
[![License: MIT](https://img.shields.io/badge/license-MIT-276c6b)](LICENSE)

**A research plan for measuring what configured UAV autopilots do after offboard control is lost, then composing those native recovery behaviors into fleet-level safety constraints.**

**[Research question](#research-question) · [First experiment](#first-experiment) · [Evidence boundary](#evidence-boundary) · [Roadmap](ROADMAP.md)**

![Conceptual pipeline from authority loss to an empirical recovery contract and fleet response](assets/recovery-contracts-overview.svg)

*Conceptual method diagram—not a result. Evidence state: **planned**. No simulation, HITL, or flight results have been generated for this repository.*

## Overview

When a companion computer stops providing setpoints, a vehicle's native autopilot—not the fleet planner—determines the immediate response. That response depends on the autopilot, firmware version, airframe, and complete parameter configuration. This project asks whether measured, configuration-specific recovery envelopes can reserve less airspace than one fleet-wide worst-case envelope while preserving held-out trajectory coverage.

| | |
| --- | --- |
| **Unit of analysis** | Autopilot + firmware + airframe + complete parameter configuration |
| **Proposed platforms** | PX4 and ArduPilot multirotors |
| **Primary event** | Loss of offboard setpoints or companion process |
| **Primary outputs** | Mode trace, authority-transition latency, trajectory tube, conformance verdict |
| **Current evidence** | Literature and protocol design only |
| **Physical testing** | Not started; requires supervised, contained facilities |

## Research question

> At matched held-out coverage, can empirical recovery contracts for completely configured vehicles reduce reserved space-time volume and fleet conflicts relative to one global worst-case recovery envelope?

The working hypothesis is deliberately conditional: configuration-specific contracts are useful only if observed transition semantics or recovery trajectories differ by more than run-to-run uncertainty. If they do not, the simpler global envelope wins.

## Proposed method

1. Record exact firmware, airframe, parameters, environment, and initial condition.
2. Remove offboard command authority at randomized but bounded states.
3. Measure mode transitions, response latency, braking, descent, recovery trajectory, and reconnection behavior.
4. Calibrate recovery tubes on one trace set and test coverage on held-out traces.
5. Compare native recovery, a global tube, configuration-specific tubes, and neighbor evacuation.
6. Fall back to the global envelope whenever online conformance leaves the calibrated domain.

The full questions, estimands, baselines, and failure branches are frozen only when a dated preregistration commit is created. Until then, the thresholds in this repository are engineering gates, not publication claims.

## First experiment

The first experiment is a one- to two-week SITL conformance pilot—not a swarm flight.

| Field | Registered pilot intent |
| --- | --- |
| **Hypothesis** | At least one equivalent recovery intention produces distinguishable authority-transition or trajectory-envelope behavior across pinned PX4 and ArduPilot configurations. |
| **Setup** | Matched simulated multirotor; pinned firmware; archived parameters; Hold, Land, and RTL intentions; randomized bounded velocity, altitude, and battery state. |
| **Measured** | Command-loss time, mode sequence, transition latency, velocity response, position trajectory, landing/loiter outcome, and reconnection behavior. |
| **Held constant** | Vehicle model, environment, logging rate, offboard command pattern, and test harness. |
| **Continue gate** | Held-out tube coverage reaches its registered target and individualized tubes reduce integrated reserved volume by at least 10% in the pilot. |
| **Stop/pivot gate** | Differences remain below 5% and mode traces are functionally equivalent; publish the conformance benchmark and do not build a fleet allocator. |

See the complete [`Experiment 01 protocol`](docs/experiment-01-authority-loss.md). The numerical gates are provisional project decisions and will not be presented as validated performance thresholds.

## Evidence boundary

### Present now

- A scoped research question and explicit unit of analysis
- A primary-source prior-art boundary
- Falsifiable hypotheses and provisional decision gates
- Configuration-manifest and data-layout contracts
- An automated documentation-integrity check

### Not present

- No SITL, HITL, flight, separation, or tube-coverage results
- No evidence that PX4 is safer or less safe than ArduPilot
- No validated fleet-safety guarantee
- No proof that configuration-specific tubes outperform a global envelope
- No authorization to conduct physical flight tests

## Check the repository contract

The current executable work checks documentation integrity and protocol structure; it does **not** simulate a UAV.

```bash
python scripts/check_repo_contract.py
python -m unittest discover -s tests -v
```

## Documentation

| Document | Purpose |
| --- | --- |
| [`docs/research-plan.md`](docs/research-plan.md) | Research questions, hypotheses, estimands, baselines, and analysis plan |
| [`docs/prior-art.md`](docs/prior-art.md) | What is established, what remains uncertain, and why the claim is narrow |
| [`docs/experiment-01-authority-loss.md`](docs/experiment-01-authority-loss.md) | Smallest decisive SITL experiment |
| [`docs/claim-ledger.md`](docs/claim-ledger.md) | Permitted language for each evidence state |
| [`docs/data-and-figures.md`](docs/data-and-figures.md) | Planned data lineage and figure rules |
| [`docs/decision-log.md`](docs/decision-log.md) | Decisions, rejected framings, and rationale |
| [`ROADMAP.md`](ROADMAP.md) | Gate-driven path from protocol to possible contained flight |

## Repository map

```text
assets/      conceptual diagrams; never presented as measurements
data/        schema and future data-location guidance; currently no observations
docs/        research plan, literature boundary, protocol, and claim controls
protocols/   machine-readable configuration manifest and example
results/     explicit placeholder; currently no results
scripts/     repository-integrity checks
tests/       tests for documentation and protocol contracts
```

## Safety boundary

This repository does not authorize flight testing. Any HITL or physical test requires a written risk assessment, geofenced and contained space, an independent kill path, a trained safety operator, and approval from the responsible laboratory or facility. RTL testing must begin in simulation because home-position, altitude, and navigation behavior can create hazards.

## Contributing and license

See [`CONTRIBUTING.md`](CONTRIBUTING.md). Source and repository tooling are available under the [MIT License](LICENSE). Third-party papers and documentation remain under their original licenses.
