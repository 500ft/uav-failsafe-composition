"""Compare repeated runs of one case (week plan W3.3, corrected by critique finding 6).

    python -m harness.reproducibility <run dir> <run dir> ...

Byte identity of the autopilot log is NOT expected and is not checked: a uLog embeds boot and wall-clock
timestamps, so a hash comparison would fail every time and would be read as non-determinism. What must match
is the normalised mode/action sequence; what is measured is the spread of the event timestamps on the vehicle
clock. The spread is the jitter figure the timing tolerance in study-a-protocol.md has to survive.
"""
from __future__ import annotations
import json, statistics, sys
from pathlib import Path

EVENTS_COMPARED = ("arm", "takeoff_complete", "injection", "horizon_reached")


def summarise(run_dir: Path) -> dict:
    trace = json.loads((run_dir / "trace.json").read_text())
    events = {}
    for e in trace["events"]:
        events.setdefault(e["name"], e["t_vehicle_s"])
    return dict(
        run=run_dir.name,
        valid=trace["validity"]["valid"],
        reasons=trace["validity"]["reasons"],
        parameters_sha256=trace["manifest"]["parameters_sha256"],
        firmware_commit=trace["manifest"]["firmware_commit"],
        sequence=[e["detail"].get("to") for e in trace["events"] if e["name"] == "native_transition"],
        event_times={k: events.get(k) for k in EVENTS_COMPARED},
        samples=len(trace["samples"]),
    )


def compare(run_dirs: list[Path]) -> dict:
    runs = [summarise(d) for d in run_dirs]
    sequences = {tuple(r["sequence"]) for r in runs}
    identities = {(r["firmware_commit"], r["parameters_sha256"]) for r in runs}
    spread = {}
    for name in EVENTS_COMPARED:
        values = [r["event_times"][name] for r in runs if r["event_times"].get(name) is not None]
        if len(values) >= 2:
            spread[name] = dict(n=len(values), min=min(values), max=max(values),
                                range_s=round(max(values) - min(values), 3),
                                stdev_s=round(statistics.pstdev(values), 3))
    return dict(
        runs=runs,
        n=len(runs),
        all_valid=all(r["valid"] for r in runs),
        identical_identity=len(identities) == 1,
        identical_mode_sequence=len(sequences) == 1,
        distinct_sequences=[list(s) for s in sequences],
        timestamp_spread=spread,
        byte_identity_expected=False,
        note="A matching sequence with a non-zero timestamp spread is the expected lockstep outcome; the spread is the jitter the timing tolerance must survive.",
    )


def main(argv=None) -> int:
    dirs = [Path(d) for d in (argv or sys.argv[1:])]
    if len(dirs) < 2:
        print("usage: python -m harness.reproducibility <run dir> <run dir> [...]", file=sys.stderr)
        return 2
    result = compare(dirs)
    print(json.dumps(result, indent=1))
    return 0 if (result["all_valid"] and result["identical_mode_sequence"] and result["identical_identity"]) else 1


if __name__ == "__main__":
    sys.exit(main())
