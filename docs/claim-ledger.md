# Claim Ledger

The ledger controls what the repository may say as evidence changes.

| Claim | Current evidence | Language permitted now | Evidence needed to strengthen it |
| --- | --- | --- | --- |
| Failsafe behavior is configuration-dependent | Official platform documentation | “PX4 and ArduPilot expose configurable failsafe behavior.” | None for the documentation claim |
| Uncoordinated recovery can create fleet conflicts | Official incident investigation and contingency literature | “Fleet-level composition is operationally motivated.” | None for motivation; local risk still requires testing |
| The exact proposed gap is globally novel | Bounded prior-art review, URC-01 gate *partial* (2026-09-15): prior art found on the reconnection and liveness axes as documentation; equivalent intent and coverage unsettled with 17 unread intake rows; formal-composition axis unsearched | “Candidate contribution” or “working gap” | Reading of the unread rows; native patent search; dissertation and standards searches |
| An extracted PX4 failsafe model reproduces SITL behaviour | None | “Planned (Study A)” | Preregistered agreement rate met on ≥ 60 injected-event runs, pinned release |
| Equivalent intentions produce different native traces | None | “Hypothesis” | Pinned SITL, HITL, and preferably physical traces |
| Configuration-specific tubes retain coverage | None | “Planned evaluation” | Held-out coverage with uncertainty |
| Individual tubes reserve less volume | None | “Proposed comparison” | Paired held-out comparison at matched coverage |
| Fleet evacuation improves safety-efficiency | None | “Proposed fleet experiment” | Held-out fleet encounters and physical validation |
| The system is safe | None | Prohibited | Defined operational envelope, safety argument, and appropriate validation |

## Evidence-state vocabulary

- **Literature:** supported by a cited source, not reproduced here.
- **Planned:** specified but not run.
- **Simulation:** generated in a software environment with pinned provenance.
- **HITL:** generated using flight-controller hardware in a controlled rig.
- **Measured:** produced by a physical experiment under a documented protocol.

A stronger label never replaces the need to state its scope and conditions.
