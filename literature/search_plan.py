"""Frozen query plan for the 2026-09-22 literature review, executed through the audited acquisition code.

The owner lifted the repository's standing "no new broad search" rule on 2026-09-22 for this task only; the
amendment is recorded in literature/README.md. Everything else about the acquisition is unchanged: the same
`evidence/task-2026-09-09/rerun_search.py` collectors are used, so every hit carries its database, query,
rank and the hash of the raw response it came from, and `audit_export` can check the result.

Axes are the project's own question axes plus the two the prior-art packet never searched: formal
composition, and the feature-interaction framing of "individually correct mechanisms that conflict".
"""
from __future__ import annotations

AXES = {
    "A_failsafe_testing": "Testing and fuzzing of autopilot failsafe and configuration behaviour",
    "B_formal_autopilot": "Formal verification and model checking of autopilot and flight-control software",
    "C_timed_hybrid": "Timed automata, hybrid reachability and the tooling a composition check would use",
    "D_runtime_assurance": "Run-time assurance architectures: monitor, switch, recovery function",
    "E_contingency_ops": "Lost link, contingency management and recovery operations for uncrewed aircraft",
    "F_feature_interaction": "Feature interaction and mode confusion: individually correct mechanisms that conflict",
    "G_sim_fidelity": "Simulation fidelity, software-in-the-loop validity and the simulation-to-reality gap",
    "H_fleet_composition": "Multi-vehicle composition of recovery behaviour (deferred scope, tracked)",
}

QUERIES = [
    ("A_failsafe_testing", "PX4 ArduPilot failsafe differential testing"),
    ("A_failsafe_testing", "robotic vehicle control software configuration bug fuzzing"),
    ("A_failsafe_testing", "UAV configuration parameter range bug detection simulation"),
    ("B_formal_autopilot", "formal verification autopilot flight control software"),
    ("B_formal_autopilot", "model checking unmanned aerial vehicle control software"),
    ("B_formal_autopilot", "verification of flight mode logic state machine"),
    ("B_formal_autopilot", "extracting formal model from source code embedded control"),
    ("C_timed_hybrid", "timed automata verification cyber-physical system UPPAAL"),
    ("C_timed_hybrid", "reachability analysis hybrid automata safety verification"),
    ("C_timed_hybrid", "bounded model checking control software counterexample"),
    ("D_runtime_assurance", "run-time assurance simplex architecture unmanned aircraft"),
    ("D_runtime_assurance", "safety monitor recovery control function aircraft assurance"),
    ("E_contingency_ops", "UAV command and control link loss contingency management"),
    ("E_contingency_ops", "contingency landing planning unmanned aircraft emergency"),
    ("E_contingency_ops", "return to launch behaviour drone loss of control link"),
    ("F_feature_interaction", "feature interaction detection safety requirements conflict"),
    ("F_feature_interaction", "mode confusion automation flight deck formal analysis"),
    ("F_feature_interaction", "conflicting safety mechanisms emergent behaviour cyber-physical"),
    ("G_sim_fidelity", "software in the loop simulation fidelity flight control validation"),
    ("G_sim_fidelity", "simulation to reality gap unmanned aerial vehicle control"),
    ("H_fleet_composition", "multi-UAV safety contract composition recovery"),
]

# Which database each query goes to. Crossref and OpenAlex cover published venues; arXiv covers preprints and
# is kept to the axes where preprints dominate, because its API throttles aggressively (2026-09-12 record).
DATABASES = {"crossref": [q for _, q in QUERIES],
             "openalex": [q for _, q in QUERIES],
             "arxiv": [q for a, q in QUERIES if a in ("B_formal_autopilot", "C_timed_hybrid", "F_feature_interaction", "H_fleet_composition")]}


def plan() -> list[tuple[str, str]]:
    """(database, query) pairs in a frozen order, so a rerun reproduces the same legs."""
    return [(db, q) for db in ("crossref", "openalex", "arxiv") for q in DATABASES[db]]


def axis_of(query: str) -> str:
    return next(a for a, q in QUERIES if q == query)
