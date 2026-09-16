# Study A — Extract and validate the PX4 failsafe model (protocol, proposed 2026-09-16)

Evidence state on execution: **simulation** (pinned SITL). Nothing here is measured or HITL. Preregistration is the merged version of this file; numbers below are the executor's proposal for the owner to edit, and they are frozen before the first validation run.

## 1. Framing

**Asked.** Does a timed-automaton network extracted from the pinned PX4 failsafe code reproduce the autopilot's mode sequence and transition timing under injected events, to a stated tolerance?

**Knowns.** PX4 ≥ v1.14 failsafe logic is a separable state machine whose code the docs simulator executes (U6). Failsafe delays and actions are parameters (COM_FAIL_ACT_T; COM_OF_LOSS_T and COM_OBL_RC_ACT for offboard loss, U7; COM_RCL_EXCEPT for RC-loss exceptions, U7; COM_POS_FS_DELAY for position-estimate loss, U2/S3). Lockstep SITL is deterministic for a fixed seed.

**Unknowns.** Which continuous quantities drive each guard, how they are estimated in flight, and how large the timing spread is between the framework's decision and the observable mode change.

**Success criterion (numbers).** Over N ≥ 60 injected-event runs spanning ≥ 6 event classes × ≥ 2 configurations each:
- Discrete agreement: model-predicted mode/action sequence equals the observed sequence in ≥ 95% of runs (≤ 3 of 60).
- Timing: median |Δt| between predicted and observed transition ≤ 0.2 s; 95th percentile ≤ 1.0 s.
- Every disagreement root-caused and classified: simulator artifact, injection artifact, guard-input modelling error, or model-structure error.

**Kill criterion.** After root-causing, agreement < 90%, **or** any disagreement classified as model-structure error that cannot be fixed without adding state the pinned code does not contain. Either outcome means the formalisation is not faithful and Studies B–C do not start on this model.

**Unsafe composed state — operational definition (Study B uses this; defined here so Study A records the observables).** Any of: (U1) a hazard flag active for longer than its configured delay plus 1.0 s with no failsafe action engaged; (U2) two hazards active and the engaged action of lower documented priority than the highest active hazard's action; (U3) an action engaged and then disengaged without the hazard clearing (flapping) more than once within 10 s; (U4) time from hazard onset to a terminal safe mode (Hold, Land, RTL, or disarmed on ground) exceeding the sum of configured delays plus 2.0 s. All four are observable from mode, action and hazard-flag channels.

## 2. Assumptions, each marked conservative (C) or optimistic (O)

| assumption | status | if wrong |
|---|---|---|
| Lockstep SITL timing is deterministic for a fixed seed | O; verify in the harness with 5 identical runs before validation | timing tolerance must widen; record measured jitter |
| The docs simulator's code path equals the vehicle's decision logic at the pinned release | O; verify by diffing the pinned source module against the docs' build reference | model extraction source must be the pinned firmware tree, not the docs |
| Guard inputs can be observed on uORB/MAVLink at ≥ 10 Hz | C for battery and estimator flags; O for geofence distance | add a logged channel or derive from position and fence definition |
| Interval abstraction of continuous guards is monotone within the tested envelope | O; state the envelope | trigger for hybrid reachability (scope.md) |
| Hardware timing is not represented | C; no hardware claim is made | none |

## 3. Load path: from event to observed mode

Injected event → hazard-flag source (RC/datalink/offboard timer, battery estimator, estimator validity, geofence check) → failsafe framework state (delay timer, user-takeover check, RC-loss exception) → selected action → mode change → navigator behaviour → terminal state. The model covers the middle three; the harness observes the endpoints and the flags. Interfaces (flag sources) get their own agreement statistics because that is where disagreements will concentrate.

## 4. Model form (rung: existing checker, no new tool)

One timed automaton per hazard class (flag, delay timer, exception), one action-selector automaton encoding the documented priority order, one user-takeover automaton, one environment automaton that can raise/clear flags and flap links. Continuous guard inputs enter as interval-valued signals with bounded rate. Checker: UPPAAL (timed). Properties for Study B: P1 safety (no U1/U2 state reachable), P2 deadlock freedom, P3 priority consistency, P4 bounded time-to-safe-state (U4). Witness traces exported as event schedules the harness can replay.

## 5. Verification of the model itself (three ways)

- Order of magnitude: predicted times are sums of configured delays; anything else is a modelling error.
- Independent path: the docs simulator (U6) as a second oracle for the discrete sequence at the same parameters (it is the same code, so it checks extraction, not physics).
- Comparable behaviour: PGFuzz/PGPatch's documented failsafe bugs (negative COM_POS_FS_DELAY) reproduced as a known-positive test of the model on that release, if the pinned release predates the fix; otherwise as a known-negative.

## 6. Failure modes enumerated

Injection artifacts (event raised while another hazard is active); estimator-flag hysteresis unmodelled; parameter ranges outside documentation (the S3 defect class); mode-requirement rejections (offboard entry requirements, U7) masking a transition; clock alignment between injection and log; SITL lockstep desynchronisation. Each gets a detection rule in the analysis before runs start.

## 7. Procedure

1. Pin release, vehicle model, parameter sets; archive manifests (URC-02). 2. Build the minimal harness and prove 5-run timing reproducibility (URC-04). 3. Extract the model from the pinned source; commit it with its source-file hashes. 4. Freeze this protocol (owner merge). 5. Run the validation matrix; log raw and normalised traces with provenance. 6. Root-cause every disagreement; classify; fix only guard-input models, never the discrete structure after seeing results (a structure change restarts validation with new seeds). 7. Report agreement, timing error distribution, classification table, and the kill decision. 8. Update the claim ledger: "the extracted model reproduces SITL failsafe behaviour within stated tolerances" becomes *simulation*-grade, scoped to the pinned release.

## 8. What Study A cannot claim

Hardware timing; behaviour outside the tested envelope; anything about ArduPilot; novelty on the formal axis (unsearched); fleet safety.
