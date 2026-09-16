# Project directions — evidence-traced, scored, with first experiments (proposed 2026-09-16)

Ingredients extracted from the repo's own evidence (reading records U1–U12, S1–S3, C-ids; docs U6–U9): **methods** — policy-guided fuzzing with MTL policies (U2, S3), assignment-dependency fuzzing (S2), setpoint-estimation fuzzing (S1), in-situ model checking with invariant monitors (U1), PID-specification search with per-mode MTL oracles (U4), contract-form safety architecture (U11); **systems** — PX4 failsafe state machine with browser-executable code (U6), PX4 Offboard proof-of-life/timeout semantics (U7), ArduPilot GCS failsafe and reconnection behaviour (U8), Guided setpoint timeout (U9), a shared PX4/ArduPilot ROS 2 interface (U5); **outcomes** — mode sequence, transition latency, time-to-safe-state, held-out trajectory coverage, reserved volume (research-plan.md); **available** — configuration-manifest schema, event vocabulary (pending URC-03), provenance tooling, no traces yet; **limitations in the evidence** — no inspected source composes failsafes or decides reachability offline; the `equivalent_intent` and `coverage` axes are unsettled with 17 unread rows; the formal axis is unsearched.

Scores: 30% evidence · 25% specificity · 20% execution fit · 15% distinctiveness · 10% traceability. "Distinctiveness" is measured against the inspected set only; nothing here claims global novelty.

## D1 — Formal composition of PX4 failsafes: timed-automata model + reachability + SITL witness replay

**Why this, why now.** PX4's failsafe logic is a separable, prioritised state machine whose code runs in the docs simulator (U6). Every inspected tool finds failsafe misbehaviour by search (U2, S1, S2) or patches it per formula (S3); none decides, offline and compositionally, whether configured failsafes can interact into an unsafe state and produces a witness. The witness can be replayed with the harness this repo already specifies (URC-04).

**Supporting evidence.** U6 (executable state machine, delayed actions COM_FAIL_ACT_T); U7 (offboard proof-of-life vs setpoint semantics, COM_OBL_RC_ACT, COM_RCL_EXCEPT); U2/S3 (known logic bugs in failsafe triggering: negative COM_POS_FS_DELAY); S2 (fence without RTL, Rover); U1 (Avis: the method neighbour to distinguish from); U11 (contract form).

**Scope.** In: PX4 only, one pinned release, multicopter SITL, the failsafe classes with documented parameters (RC loss, datalink loss, offboard loss, battery, geofence, position/velocity estimate loss, user takeover), timed abstraction first. Out: ArduPilot (D3/Study D), hardware timing, GPS-denied navigation, security.

**First experiment (Study A, two weeks).** Hypothesis: a timed-automaton model extracted from the pinned PX4 failsafe code reproduces SITL's mode sequence for injected single events at ≥ 95% agreement with median transition-time error ≤ 0.2 s. Setup: pinned PX4 SITL (lockstep), one vehicle model, the repo's manifest schema; UPPAAL (exists, free); the harness (URC-04, must be built to a minimal version first). Variables: varied — event class (≥ 6), configuration (≥ 2 per class), injection time; measured — mode sequence, timestamps, action taken; constant — vehicle model, environment seed, logging rate. Success: the numbers above over ≥ 60 runs. Timebox: 10 working days after a minimal harness. Kill: agreement < 90% after each disagreement is root-caused, or any disagreement traceable to model structure rather than simulator artifact that requires state the code does not have.

**Risks and honest limits.** The harness does not exist; continuous guards need estimator/battery modelling; a verified-null result must be preregistered as acceptable; distinctiveness is *candidate* until the formal axis is searched and Avis is written up. No hardware-timing claim.

**Score.** evidence 24/30 · specificity 22/25 · execution fit 14/20 · distinctiveness 11/15 · traceability 10/10 → **81**.

## D2 — Empirical recovery-contract benchmark (RQ1–RQ2): pinned cross-stack traces, calibrated tubes, held-out coverage

**Why this, why now.** This is the repo's registered thesis (research-plan.md, experiment-01). Its measurements (transition latency, mode sequence, trajectory after authority loss, reconnection) are exactly the calibration data D1's continuous guards need, and its benchmark survives a null D1.

**Supporting evidence.** U7/U8/U9 (documented timeouts and non-restoration on reconnect: the behaviours to measure); U6 (per-configuration action tables); U5 (shared ROS 2 interface as harness substrate); the coverage axis is `supported_bounded` with unread rows, so "calibrated whole-trajectory coverage" remains a candidate endpoint, not a claim.

**Scope.** In: URC-02 to URC-08 as written. Out: fleet composition (URC-10) until its trigger.

**First experiment (two weeks).** Hypothesis: for one PX4 configuration, held-out time-to-native-transition after offboard loss has run-to-run spread below 0.5 s (lockstep), and the mode sequence is identical across ≥ 30 seeds. Setup: same harness as D1. Variables: seed, initial speed bin; measured: transition timestamp, mode sequence; constant: configuration hash. Success: spread and identity as stated. Kill: mode sequences differ across seeds under identical configuration — the "configured identity" unit of analysis is then not reproducible in SITL and D1's validation cannot be trusted either.

**Risks.** Same harness dependency; the tube/volume estimands (RQ3) are effort that does not serve the spine.

**Score.** evidence 22/30 · specificity 20/25 · execution fit 15/20 · distinctiveness 7/15 · traceability 10/10 → **74**.

## D3 — Cross-autopilot intent-equivalence conformance (PX4 vs ArduPilot under an explicit equivalence rule)

**Why this, why now.** `equivalent_intent` is `supported_bounded`: no inspected source defines equivalence of a stated recovery intention across pinned configurations and compares realised behaviour (13 not-found, 17 unread). ArduPilot documents non-restoration on reconnect (U8); PX4's page is silent (U7): a documented asymmetry to test.

**Supporting evidence.** U8, U7, U9, U6, S3 (per-autopilot formulas as the "form" to generalise), U5 (one interface for both stacks).

**Scope.** In: an equivalence rule for Hold/Land/RTL and offboard-loss actions; differential SITL. Out: brand-level ranking.

**First experiment (two weeks, after D1's Study A).** Hypothesis: under a written equivalence rule, at least one intention pair produces different mode sequences or a > 1 s difference in time-to-safe-state across the two stacks. Setup: both SITLs via the U5-style interface. Variables: stack, intention; measured: sequence, timing, reconnection response. Success/kill as stated in experiment-01 (differences below run-to-run spread ⇒ pivot to benchmark-only).

**Risks.** ArduPilot extraction/harness cost; the unread C rows (C001, C005, C135, C180) bear on this axis and must be read first.

**Score.** evidence 20/30 · specificity 18/25 · execution fit 10/20 · distinctiveness 12/15 · traceability 10/10 → **70**.

## Merge decision

D1 is the spine. D2 is folded into D1 as Study A's measurement layer and the fallback thesis (same harness, same traces, RQ1–RQ2 only). D3 becomes Study D's first half (ArduPilot extraction) once D1's Study C has a result. RQ3–RQ4 are trigger-gated (scope.md).
