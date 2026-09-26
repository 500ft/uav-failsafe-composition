"""Verify one run against the hand-derived expectation (section 12 items 1 and 2).

    python -m harness.verify <run directory> [...]

Four questions are answered in order, and a later one is never answered when an earlier one fails:

    1. run validity    did the apparatus produce a usable capture, and is it the capture this case claims?
    2. observability    are the channels this comparison needs actually present?
    3. stimulus         did the injected hazard reach the autopilot?
    4. conformance      did the response match the hand-derived expectation?

Only question 4 can produce `refuted`. Failing 1 or 2 means the experiment could not be compared, which is
`unverified`; the earlier code accumulated those into the same list as a behavioural mismatch and reported
`refuted`, which turns a broken rig into a finding about PX4 (critique 2026-09-24, F2).

The comparison also runs on the response window only: the state entering the window, then the transitions at or
after the stimulus. Takeoff happens before injection in every flying case, so including it guaranteed a mismatch
even for a run that then recovered correctly.

`inconclusive` is a fifth outcome: the observation exists and its uncertainty interval straddles the deadline,
so it neither confirms nor contradicts the expectation.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TIMELINES = json.loads((ROOT / "protocols/expected-timelines.json").read_text())
BY_CASE = {(t["configuration_id"], t["event"], t.get("intended_mode", "offboard")): t for t in TIMELINES["timelines"]}
TOLERANCE_S = TIMELINES["tolerance"]["value_s"]


def _result(status, timeline=None, **kw):
    return dict(status=status, timeline_id=timeline, tolerance_s=TOLERANCE_S,
                **dict(dict(reasons=[], observed={}, expected={}), **kw))


def _span(event: dict) -> tuple[float | None, float | None]:
    """The vehicle-clock bounds on an instant. A measured instant is a point; an open bound stays None."""
    lo, hi = event.get("t_vehicle_interval_s") or [event["t_vehicle_s"], event["t_vehicle_s"]]
    return lo, hi


def _compare(event: dict, base: dict, want: float) -> tuple[str, float, str | None]:
    """Compare an elapsed time against a deadline using both instants' bounds.

    The elapsed time is itself an interval: [event_lo - base_hi, event_hi - base_lo]. It matches only when the
    whole interval sits inside the tolerance, and it misses only when the whole interval sits outside. Anything
    else straddles the deadline and is inconclusive. A measured instant's interval is a point, so this reduces
    to exact arithmetic and the extra machinery costs nothing (critique 2026-09-24, F1).
    """
    e_lo, e_hi = _span(event)
    b_lo, b_hi = _span(base)
    point = round(event["t_vehicle_s"] - base["t_vehicle_s"], 3)
    if None in (e_lo, e_hi, b_lo, b_hi):
        open_sides = [f"{d['name']} ({d['t_source']})" for d in (event, base)
                      if None in (d.get("t_vehicle_interval_s") or [None, None])]
        return "inconclusive", point, ("unbounded on one side: " + ", ".join(open_sides) +
                                       "; a received stamp does not bound a later instant above")
    lo, hi = round(e_lo - b_hi, 3), round(e_hi - b_lo, 3)
    if abs(lo - want) <= TOLERANCE_S and abs(hi - want) <= TOLERANCE_S:
        return "match", point, None
    if (lo - want) > TOLERANCE_S or (hi - want) < -TOLERANCE_S:
        return "mismatch", point, None
    return "inconclusive", point, f"elapsed time is only bounded to [{lo}, {hi}] s against a deadline of {want} s"


def verify(run_dir: Path) -> dict:
    case_file, trace_file = run_dir / "case.json", run_dir / "trace.json"
    if not case_file.is_file() or not trace_file.is_file():
        return _result("unverified", reasons=["case.json or trace.json missing"])
    case = json.loads(case_file.read_text())
    trace = json.loads(trace_file.read_text())

    # 1. run validity and identity. None of these say anything about PX4's behaviour.
    blocking = []
    if trace["manifest"]["run_id"] != case["case_id"]:
        blocking.append(f"trace run_id {trace['manifest']['run_id']} is not case {case['case_id']}")
    if trace["manifest"]["firmware_commit"] != case["firmware_commit"]:
        blocking.append("firmware commit in the trace does not match the case")
    if not trace["validity"]["valid"]:
        blocking.append("run is invalid: " + ", ".join(trace["validity"]["reasons"]))

    intended_mode = trace["manifest"].get("intended_mode")
    if intended_mode is None:
        blocking.append("the capture does not record which mode was intended, so no timeline applies")
    timeline = BY_CASE.get((case["configuration_id"], case["event"], intended_mode))
    if timeline is None and intended_mode is not None:
        blocking.append(f"no hand-derived timeline for ({case['configuration_id']}, {case['event']}, {intended_mode})")
    if blocking:
        return _result("unverified", timeline and timeline["id"], reasons=blocking)

    events = trace["events"]
    injection = next((e for e in events if e["name"] == "injection"), None)
    transitions = [e for e in events if e["name"] == "native_transition"]
    observed = dict(intended_mode=intended_mode,
                    full_mode_sequence=[e["detail"]["to"] for e in transitions],
                    hazard_flags=[(e["detail"].get("flag"), e["detail"].get("edge")) for e in events if e["name"] == "hazard_flag"],
                    announced_actions=[e["detail"].get("announced_action") for e in events if e["name"] == "failsafe_notice"],
                    vehicle_status_failsafe=[e["detail"].get("failsafe") for e in events if e["name"] == "failsafe_state"],
                    mode_source=trace["conversion"]["mode_source"])
    expected = dict(mode_sequence=timeline["expected_mode_sequence"],
                    hazard_flag=(timeline["expected_hazard_flag"] or {}).get("flag"),
                    actions=timeline["expected_actions"])

    # 2. observability: say which channels this comparison had, so a pass cannot be read as covering more.
    observed["channels"] = dict(
        mode_sequence=trace["conversion"]["mode_source"],
        failsafe_flags="autopilot_log" if any(e["name"] == "hazard_flag" for e in events) else "absent",
        vehicle_status_failsafe="autopilot_log" if observed["vehicle_status_failsafe"] else "absent",
        selected_action="absent: PX4 does not publish the framework's selected action over MAVLink")

    if case["event"] == "none":
        # A control run has no stimulus, so its window opens at takeoff. Selecting a flight mode and taking off
        # are setup; only a change after that is the control run changing mode on its own (F2).
        takeoff = next((e for e in events if e["name"] == "takeoff_complete"), None)
        if takeoff is None:
            return _result("unverified", timeline["id"], observed=observed, expected=expected,
                           reasons=["the control run never reported takeoff, so its window cannot be opened"])
        after = [e for e in transitions if e["t_vehicle_s"] >= takeoff["t_vehicle_s"]]
        observed["setup_mode_sequence"] = [e["detail"]["to"] for e in transitions if e["t_vehicle_s"] < takeoff["t_vehicle_s"]]
        observed["mode_sequence"] = [e["detail"]["to"] for e in after]
        observed["state_entering_window"] = observed["setup_mode_sequence"][-1] if observed["setup_mode_sequence"] else None
        if observed["mode_sequence"] != timeline["expected_mode_sequence"]:
            return _result("refuted", timeline["id"], observed=observed, expected=expected,
                           reasons=[f"control run mode sequence after takeoff {observed['mode_sequence']} does "
                                    f"not match expected {timeline['expected_mode_sequence']}"])
        return _result("verified", timeline["id"], observed=observed, expected=expected)

    # 3. stimulus: locate the response window and show the hazard reached the monitor.
    if injection is None:
        return _result("unverified", timeline["id"], observed=observed, expected=expected,
                       reasons=["no injection event in the trace; the stimulus cannot be located"])
    # The window opens at the injection's LOWER bound, which is the only side this rig can justify. A transition
    # before it certainly precedes the stimulus. One at or after it may precede or follow, because the true
    # injection instant is somewhere at or above that bound (owner review 2026-09-25, R1/WP0).
    t0 = injection["t_vehicle_s"]
    inj_lo, inj_hi = (injection.get("t_vehicle_interval_s") or [t0, t0])
    open_at = inj_lo if inj_lo is not None else t0
    before = [e for e in transitions if e["t_vehicle_s"] < open_at]
    response = [e for e in transitions if e["t_vehicle_s"] >= open_at]
    observed["state_entering_window"] = before[-1]["detail"]["to"] if before else None
    observed["setup_mode_sequence"] = [e["detail"]["to"] for e in before]
    observed["mode_sequence"] = [e["detail"]["to"] for e in response]
    # An EMPTY response set is certain even with an open bound: nothing happened after the lower bound, so
    # nothing happened after the injection either. A non-empty one has uncertain membership until the upper
    # side is closed, and that uncertainty is stated rather than resolved by a guessed point.
    observed["window_membership_certain"] = (not response) or (
        inj_hi is not None and all(e["t_vehicle_s"] >= inj_hi for e in response))

    want_flag = (timeline["expected_hazard_flag"] or {}).get("flag")
    rises = [e for e in events if e["name"] == "hazard_flag" and e["detail"].get("flag") == want_flag
             and e["detail"].get("edge") == "rising"]
    flag_event = next((e for e in rises if e["t_vehicle_s"] >= t0 - 1.0), None)
    if flag_event is None:
        return _result("refuted", timeline["id"], observed=observed, expected=expected,
                       reasons=[f"expected hazard flag {want_flag} never rose; the injection did not reach the monitor",
                                "this refutes the detector prediction only; it says nothing about the selector"])
    observed["hazard_flag_t_rel_s"] = round(flag_event["t_vehicle_s"] - t0, 3)
    observed["hazard_flag_clears"] = sum(1 for e in events if e["name"] == "hazard_flag"
                                         and e["detail"].get("flag") == want_flag and e["detail"].get("edge") == "falling")

    # 4. conformance.
    reasons, verdicts = [], []
    want_t = timeline["expected_hazard_flag"].get("t_rel_injection_s")
    if want_t is None:
        # Some hazards are position-triggered, so their time is not predicted; only their occurrence is, and the
        # actions are then timed relative to the flag. Occurrence has already been established above.
        observed["hazard_time_predicted"] = False
    else:
        v, _pt, why = _compare(flag_event, injection, want_t)
        verdicts.append(v)
        if v != "match":
            reasons.append(f"{want_flag} rose at {observed['hazard_flag_t_rel_s']} s after injection, "
                           f"expected {want_t} s" + (f" ({why})" if why else ""))

    if not observed["window_membership_certain"]:
        verdicts.append("inconclusive")
        reasons.append("the injection instant is bounded only below, so whether "
                       f"{observed['mode_sequence']} falls inside the response window is undetermined")
    if observed["mode_sequence"] != timeline["expected_mode_sequence"]:
        verdicts.append("mismatch")
        reasons.append(f"response mode sequence {observed['mode_sequence']} does not match expected "
                       f"{timeline['expected_mode_sequence']} (setup before injection was "
                       f"{observed['setup_mode_sequence']} and is excluded)")
    else:
        timings = []
        for want, e in zip(timeline["expected_actions"], response):
            # An action is timed from the injection, or from the hazard when the hazard time is not predicted.
            if "t_rel_hazard_s" in want:
                base, origin, want_s = flag_event, "hazard", want["t_rel_hazard_s"]
            else:
                base, origin, want_s = injection, "injection", want["t_rel_injection_s"]
            v, got, why = _compare(e, base, want_s)
            verdicts.append(v)
            timings.append(dict(nav_state=want["nav_state"], measured_from=origin, expected_s=want_s,
                                observed_s=got, error_s=round(got - want_s, 3), verdict=v,
                                clock=f"{base['t_source']} -> {e['t_source']}"))
            if v != "match":
                reasons.append(f"{want['nav_state']} at {got} s after {origin}, expected {want_s} s"
                               + (f" ({why})" if why else ""))
        observed["timings"] = timings
        observed["recovery_mode_entered"] = True
        # Entering the mode is not completing the recovery. Nothing here observes a landing or a containment
        # (critique 2026-09-24, F5/U4); that is recorded separately when the physical outcome is measured.
        observed["recovery_completed"] = "not_evaluated"

    status = ("refuted" if "mismatch" in verdicts else
              "inconclusive" if "inconclusive" in verdicts else "verified")
    return _result(status, timeline["id"], reasons=reasons, observed=observed, expected=expected)


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
        worst = max(worst, {"verified": 0, "unverified": 1, "inconclusive": 1, "refuted": 1}[result["status"]])
    return worst


if __name__ == "__main__":
    sys.exit(main())
