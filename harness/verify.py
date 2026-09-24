"""Verify one run against the hand-derived expectation (section 12 items 1 and 2).

    python -m harness.verify <run directory> [...]

Execution status is never a pass. A run is `verified` only when its files parse, its identity agrees with the
case, the required observations exist, and every expected event lands inside the frozen tolerance. When the
oracle or a required observation is missing the answer is `unverified`, never `verified`; when an observation
exists and contradicts the expectation the answer is `refuted`, which is a result, not an error.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TIMELINES = json.loads((ROOT / "protocols/expected-timelines.json").read_text())
BY_CASE = {(t["configuration_id"], t["event"], t.get("intended_mode", "offboard")): t for t in TIMELINES["timelines"]}
TOLERANCE_S = TIMELINES["tolerance"]["value_s"]


def verify(run_dir: Path) -> dict:
    reasons: list[str] = []
    case_file, trace_file = run_dir / "case.json", run_dir / "trace.json"
    if not case_file.is_file() or not trace_file.is_file():
        return dict(status="unverified", timeline_id=None, tolerance_s=TOLERANCE_S,
                    reasons=["case.json or trace.json missing"], observed={}, expected={})
    case = json.loads(case_file.read_text())
    trace = json.loads(trace_file.read_text())

    # identity: the trace must describe the case it claims to (section 12 item 7, stale result from another case)
    if trace["manifest"]["run_id"] != case["case_id"]:
        reasons.append(f"trace run_id {trace['manifest']['run_id']} is not case {case['case_id']}")
    if trace["manifest"]["firmware_commit"] != case["firmware_commit"]:
        reasons.append("firmware commit in the trace does not match the case")
    if not trace["validity"]["valid"]:
        reasons.append("run is invalid: " + ", ".join(trace["validity"]["reasons"]))

    intended_mode = trace["manifest"].get("intended_mode", "offboard")
    timeline = BY_CASE.get((case["configuration_id"], case["event"], intended_mode))
    if timeline is None:
        reasons.append(f"no hand-derived timeline for ({case['configuration_id']}, {case['event']}, {intended_mode})")
        return dict(status="unverified", timeline_id=None, tolerance_s=TOLERANCE_S, reasons=reasons,
                    observed={}, expected={})

    events = trace["events"]
    injection = next((e for e in events if e["name"] == "injection"), None)
    transitions = [e for e in events if e["name"] == "native_transition"]
    observed_sequence = [e["detail"]["to"] for e in transitions]
    observed = dict(intended_mode=intended_mode, mode_sequence=observed_sequence,
                    hazard_flags=[e["detail"].get("flag") for e in events if e["name"] == "hazard_flag"],
                    announced_actions=[e["detail"].get("announced_action") for e in events if e["name"] == "failsafe_notice"],
                    mode_source=trace["conversion"]["mode_source"])
    expected = dict(mode_sequence=timeline["expected_mode_sequence"],
                    hazard_flag=(timeline["expected_hazard_flag"] or {}).get("flag"),
                    actions=timeline["expected_actions"])

    if case["event"] == "none":
        if observed_sequence:
            reasons.append(f"control run changed mode: {observed_sequence}")
            status = "refuted"
        else:
            status = "verified" if not reasons else "unverified"
        return dict(status=status, timeline_id=timeline["id"], tolerance_s=TOLERANCE_S, reasons=reasons,
                    observed=observed, expected=expected)

    if injection is None:
        reasons.append("no injection event in the trace; the stimulus cannot be located")
        return dict(status="unverified", timeline_id=timeline["id"], tolerance_s=TOLERANCE_S, reasons=reasons,
                    observed=observed, expected=expected)
    t0 = injection["t_vehicle_s"]

    # the hazard must actually have been raised: the input change must be shown to have reached the system
    want_flag = (timeline["expected_hazard_flag"] or {}).get("flag")
    flag_event = next((e for e in events if e["name"] == "hazard_flag" and e["detail"].get("flag") == want_flag), None)
    if flag_event is None:
        reasons.append(f"expected hazard flag {want_flag} never rose; the injection did not reach the monitor")
        return dict(status="refuted", timeline_id=timeline["id"], tolerance_s=TOLERANCE_S, reasons=reasons,
                    observed=observed, expected=expected)
    observed["hazard_flag_t_rel_s"] = round(flag_event["t_vehicle_s"] - t0, 3)
    want_t = timeline["expected_hazard_flag"].get("t_rel_injection_s")
    if want_t is None:
        # Some hazards are position-triggered, so their time is not predicted; only their occurrence is, and the
        # actions are then timed relative to the flag. Occurrence has already been established above.
        observed["hazard_time_predicted"] = False
    elif abs(observed["hazard_flag_t_rel_s"] - want_t) > TOLERANCE_S:
        reasons.append(f"{want_flag} rose at {observed['hazard_flag_t_rel_s']} s after injection, expected {want_t} s")

    if observed_sequence != timeline["expected_mode_sequence"]:
        reasons.append(f"mode sequence {observed_sequence} does not match expected {timeline['expected_mode_sequence']}")
    else:
        timings = []
        for want, e in zip(timeline["expected_actions"], transitions):
            # An action is timed from the injection, or from the hazard when the hazard time is not predicted.
            if "t_rel_hazard_s" in want:
                base, origin, expected = flag_event["t_vehicle_s"], "hazard", want["t_rel_hazard_s"]
            else:
                base, origin, expected = t0, "injection", want["t_rel_injection_s"]
            got = round(e["t_vehicle_s"] - base, 3)
            timings.append(dict(nav_state=want["nav_state"], measured_from=origin, expected_s=expected,
                                observed_s=got, error_s=round(got - expected, 3)))
            if abs(got - expected) > TOLERANCE_S:
                reasons.append(f"{want['nav_state']} at {got} s after {origin}, expected {expected} s")
        observed["timings"] = timings

    status = "verified" if not reasons else "refuted"
    return dict(status=status, timeline_id=timeline["id"], tolerance_s=TOLERANCE_S, reasons=reasons,
                observed=observed, expected=expected)


def main(argv=None) -> int:
    dirs = [Path(d) for d in (argv or sys.argv[1:])]
    if not dirs:
        print("usage: python -m harness.verify <run directory> [...]", file=sys.stderr)
        return 2
    worst = 0
    for d in dirs:
        result = verify(d)
        trace_file = d / "trace.json"
        if trace_file.is_file():
            trace = json.loads(trace_file.read_text())
            trace["verification"] = result
            trace_file.write_text(json.dumps(trace, indent=1) + "\n")
        print(json.dumps(dict(run=d.name, **result)))
        worst = max(worst, {"verified": 0, "unverified": 1, "refuted": 1}[result["status"]])
    return worst


if __name__ == "__main__":
    sys.exit(main())
