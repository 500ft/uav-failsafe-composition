"""Compare repeated runs of one case (week plan W3.3, corrected by critique finding 6).

    python -m harness.reproducibility <run dir> <run dir> ...

Byte identity of the autopilot log is NOT expected and is not checked: a uLog embeds boot and wall-clock
timestamps, so a hash comparison would fail every time and would be read as non-determinism. What must match
is the normalised mode sequence; what is measured is the repeat-to-repeat range of the event timestamps.

That range is REPEATABILITY, not accuracy. It says how much the same scenario moved between runs. It does not
bound the error of an injection-relative latency, and four repeats do not establish a tail (owner review
2026-09-25, R3). It is reported as `repeat_range_s` and never as a validated jitter budget.

A statistic is only formed over a COHORT: runs that are valid, share a composite identity, and observed the
event through one clock source with one event definition. PR #29 gated the statistic on clock provenance alone,
so an invalid run with a different parameter hash could still produce a quotable 89 s "jitter", two different
intended modes counted as one identity, and two clock sources were pooled under a promise not to pool (R2).
Every input record stays visible; exclusion is reported with its reason, never by dropping the row.
"""
from __future__ import annotations
import json, statistics, sys
from pathlib import Path

EVENTS_COMPARED = ("arm", "takeoff_complete", "injection", "horizon_reached")
MIN_COHORT = 2


def identity(run: dict) -> tuple:
    """Composite scenario identity. Intended mode belongs in it: an Auto Loiter repeat is not an Offboard one."""
    return (run["firmware_commit"], run["parameters_sha256"], run["intended_mode"])


def summarise(run_dir: Path) -> dict:
    trace = json.loads((run_dir / "trace.json").read_text())
    events = {}
    for e in trace["events"]:
        events.setdefault(e["name"], e)
    return dict(
        run=run_dir.name,
        valid=trace["validity"]["valid"],
        reasons=trace["validity"]["reasons"],
        parameters_sha256=trace["manifest"]["parameters_sha256"],
        firmware_commit=trace["manifest"]["firmware_commit"],
        # Missing rather than defaulted: a historical capture that never recorded a mode is not an Offboard run.
        intended_mode=trace["manifest"].get("intended_mode"),
        sequence=[e["detail"].get("to") for e in trace["events"] if e["name"] == "native_transition"],
        event_times={k: events[k]["t_vehicle_s"] if k in events else None for k in EVENTS_COMPARED},
        # A trace from before the 2026-09-24 repair carries no provenance. Calling that `vehicle_observation`
        # would launder an estimate into a measurement, so it is its own answer.
        event_clocks={k: events[k].get("t_source", "unrecorded") if k in events else None for k in EVENTS_COMPARED},
        event_bounded={k: None not in (events[k].get("t_vehicle_interval_s") or [None, None]) if k in events else None
                       for k in EVENTS_COMPARED},
        samples=len(trace["samples"]),
    )


def cohort(runs: list[dict]) -> dict:
    """The runs a statistic may be formed over, and why each of the others is out."""
    excluded, included = [], []
    ids = {identity(r) for r in runs if r["valid"]}
    majority = max(ids, key=lambda i: sum(1 for r in runs if r["valid"] and identity(r) == i)) if ids else None
    for r in runs:
        if not r["valid"]:
            excluded.append(dict(run=r["run"], reason="run is invalid: " + ", ".join(r["reasons"])))
        elif r["intended_mode"] is None:
            excluded.append(dict(run=r["run"], reason="intended mode was never recorded, so identity is incomplete"))
        elif identity(r) != majority:
            excluded.append(dict(run=r["run"], reason="different scenario identity (firmware, parameters or mode)"))
        else:
            included.append(r)
    return dict(included=included, excluded=excluded, identity=None if majority is None else list(majority))


def compare(run_dirs: list[Path]) -> dict:
    runs = [summarise(d) for d in run_dirs]
    c = cohort(runs)
    members = c["included"]
    sequences = {tuple(r["sequence"]) for r in members}
    spread, missing = {}, {}
    for name in EVENTS_COMPARED:
        have = [r for r in members if r["event_times"].get(name) is not None]
        missing[name] = len(members) - len(have)
        by_source: dict[str, list[float]] = {}
        for r in have:
            by_source.setdefault(r["event_clocks"][name], []).append(r["event_times"][name])
        for source, values in by_source.items():
            # One statistic per clock source. Different sources may share a clock domain, but equal event
            # semantics has not been established for them, so they are reported apart (R2).
            if len(values) < MIN_COHORT:
                continue
            spread[f"{name}@{source}"] = dict(
                event=name, clock_source=source, n=len(values), min=min(values), max=max(values),
                repeat_range_s=round(max(values) - min(values), 3),
                stdev_s=round(statistics.pstdev(values), 3),
                quotable=source in ("vehicle_observation", "autopilot_log"))
    quotable = {k: v for k, v in spread.items() if v["quotable"]}
    enough = len(members) >= MIN_COHORT
    return dict(
        runs=runs,
        counts=dict(total=len(runs), included=len(members), excluded=len(c["excluded"]), missing_event=missing),
        cohort_identity=c["identity"],
        excluded=c["excluded"],
        n=len(members),
        all_valid=all(r["valid"] for r in runs),
        cohort_sufficient=enough,
        identical_identity=bool(c["identity"]) and not any(
            e["reason"].startswith("different scenario") for e in c["excluded"]),
        # Two empty but identical mode sequences are not evidence of reproducibility. Say so instead of
        # reporting True from an absence (R2).
        identical_mode_sequence=(len(sequences) == 1 and enough and any(s for s in sequences)),
        mode_sequence_observed=bool(any(s for s in sequences)),
        distinct_sequences=[list(s) for s in sequences],
        timestamp_spread=spread,
        # Repeat-to-repeat range over one cohort and one clock source. NOT an accuracy or tail bound.
        repeat_range_s=({k: v["repeat_range_s"] for k, v in quotable.items()} if enough and quotable else None),
        repeatability_reportable=bool(enough and quotable),
        byte_identity_expected=False,
        note="Statistics are formed only over valid runs sharing one composite identity, per clock source. `repeat_range_s` is how far the same scenario moved between repeats; it does not bound the error of an injection-relative latency and four repeats establish no tail.",
    )


def main(argv=None) -> int:
    dirs = [Path(d) for d in (argv or sys.argv[1:])]
    if len(dirs) < 2:
        print("usage: python -m harness.reproducibility <run dir> <run dir> [...]", file=sys.stderr)
        return 2
    result = compare(dirs)
    print(json.dumps(result, indent=1))
    return 0 if (result["all_valid"] and result["cohort_sufficient"]
                 and result["identical_mode_sequence"] and result["identical_identity"]) else 1


if __name__ == "__main__":
    sys.exit(main())
