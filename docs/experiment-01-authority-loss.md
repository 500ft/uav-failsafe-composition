# Experiment 01 — Offboard-Authority-Loss Conformance Pilot

## Objective

Determine whether completely configured PX4 and ArduPilot SITL vehicles exhibit operationally distinguishable native recovery behavior after offboard setpoints stop.

This experiment does not test fleet safety. It tests whether individualized recovery contracts are worth developing.

## Hypothesis

At least one equivalent recovery intention produces a difference in transition latency, mode sequence, braking response, or recovery-envelope volume that exceeds run-to-run variation.

## Timebox

One to two weeks after the harness and pinned software environments are available.

## Setup

- One matched simulated multirotor model
- One pinned PX4 release or commit
- One pinned ArduPilot release or commit
- Equivalent-intent Hold, Land, and RTL configurations
- A common offboard setpoint generator and termination event
- Deterministic environment seeds plus registered randomized initial conditions
- Synchronized state and mode logging

The example manifest in [`../protocols/example-configuration-manifest.json`](../protocols/example-configuration-manifest.json) shows the metadata contract; it is not an executed run.

## Factors

| Type | Variables |
| --- | --- |
| Deliberately varied | Autopilot stack, complete parameter configuration, recovery intention, initial horizontal speed, altitude, battery state, termination time |
| Measured | Last accepted setpoint, native-mode transition, position, velocity, attitude, mode, armed state, recovery completion, reconnection response |
| Held constant | Airframe model, mass/inertia, environment, estimator inputs, logging rate, command history, and analysis code |

## Pilot matrix

Use a balanced design across both stacks and three recovery intentions. Initial-state bins and repetitions are fixed after verifying that every case is valid for both platforms. Invalid configurations are corrected before data collection, not silently discarded afterward.

The pilot and confirmatory sets use different random seeds. Pilot runs may set the final sample size but cannot be counted as held-out confirmation.

## Procedure

1. Archive the firmware identifier, complete parameter export, simulator version, vehicle model, and environment seed.
2. Verify normal offboard tracking for the registered pre-failure interval.
3. Terminate the setpoint stream or companion process at the scheduled event.
4. Record the first native mode transition and all subsequent mode changes.
5. Continue through the registered horizon or terminal recovery state.
6. In a separate condition, restore the setpoint stream and record whether and when authority returns.
7. Mark any simulator crash, invalid state, or logging loss before inspecting performance outcomes.

## Analysis

- Plot aligned mode timelines and velocity/position traces.
- Estimate latency and braking-response distributions by configured identity.
- Calibrate a recovery tube without held-out traces.
- Evaluate full-trajectory held-out coverage.
- Compare integrated tube volume with one global envelope at the same coverage target.
- Report sensitivity to horizon, state bin, and recovery intention.

## Provisional engineering gates

These numbers guide project continuation and are not validated scientific thresholds.

- **Continue to HITL:** held-out coverage reaches its registered target and individual tubes reduce integrated reserved volume by at least 10%.
- **Strong continuation signal:** the reduction reaches approximately 20% without a coverage penalty.
- **Pivot:** reduction is below 5%, mode traces are functionally equivalent, or tube calibration is unstable across seeds.

## Safety and interpretation limits

- RTL is tested in simulation first because home-position and altitude settings can generate hazardous trajectories.
- SITL timing does not establish hardware timing.
- A matched vehicle model does not make the two control stacks equivalent controllers.
- No brand-level safety ranking is permitted from this experiment.
