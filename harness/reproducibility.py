"""Compare repeated runs of one case (week plan W3.3, corrected by critique finding 6).

    python -m harness.reproducibility <run dir> <run dir> ...

Byte identity of the autopilot log is NOT expected and is not checked: a uLog embeds boot and wall-clock
timestamps, so a hash comparison would fail every time and would be read as non-determinism. What must match
is the normalised mode/action sequence; what is measured is the spread of the event timestamps on the vehicle
clock. The spread is the jitter figure the timing tolerance in study-a-protocol.md has to survive.

That makes clock provenance load-bearing here, not decorative. A spread over `host_reconstructed` instants
includes the run-to-run variance of the offset ESTIMATE, which is not vehicle jitter: the 0.51 s figure the
tolerance was originally set against was 0.352 s once the same runs were re-derived on the vehicle's own clock
(critique 2026-09-24, F1). Spreads are therefore reported per clock source and never pooled across sources,
and only a `measured` spread may be quoted as apparatus jitter.
"""
from __future__ import annotations
import json, statistics, sys
from pathlib import Path

EVENTS_COMPARED = ("arm", "takeoff_complete", "injection", "horizon_reached")
MEASURED = ("vehicle_observation", "autopilot_log")


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
        intended_mode=trace["manifest"].get("intended_mode"),
        sequence=[e["detail"].get("to") for e in trace["events"] if e["name"] == "native_transition"],
        event_times={k: events[k]["t_vehicle_s"] if k in events else None for k in EVENTS_COMPARED},
        # A trace from before the 2026-09-24 repair carries no provenance. Calling that `vehicle_observation`
        # would launder an estimate into a measurement, so it is its own answer.
        event_clocks={k: events[k].get("t_source", "unrecorded") if k in events else None for k in EVENTS_COMPARED},
        samples=len(trace["samples"]),
    )


def compare(run_dirs: list[Path]) -> dict:
    runs = [summarise(d) for d in run_dirs]
    sequences = {tuple(r["sequence"]) for r in runs}
    identities = {(r["firmware_commit"], r["parameters_sha256"]) for r in runs}
    spread = {}
    for name in EVENTS_COMPARED:
        pairs = [(r["event_times"][name], r["event_clocks"][name]) for r in runs
                 if r["event_times"].get(name) is not None]
        if len(pairs) < 2:
            continue
        sources = {c for _v, c in pairs}
        values = [v for v, _c in pairs]
        quality = ("measured" if sources <= set(MEASURED) else
                   "mixed_clock_sources" if len(sources) > 1 else
                   "estimated" if sources == {"host_reconstructed"} else "unrecorded_provenance")
        spread[name] = dict(n=len(values), min=min(values), max=max(values),
                            range_s=round(max(values) - min(values), 3),
                            stdev_s=round(statistics.pstdev(values), 3),
                            clock_sources=sorted(sources), quality=quality)
    jitter = {k: v for k, v in spread.items() if v["quality"] == "measured"}
    return dict(
        runs=runs,
        n=len(runs),
        all_valid=all(r["valid"] for r in runs),
        identical_identity=len(identities) == 1,
        identical_mode_sequence=len(sequences) == 1,
        distinct_sequences=[list(s) for s in sequences],
        timestamp_spread=spread,
        # Only these may be quoted as apparatus jitter. Everything else in `timestamp_spread` is reported so it
        # stays visible, and labelled so it cannot be mistaken for a measurement of the vehicle.
        apparatus_jitter_s=({k: v["range_s"] for k, v in jitter.items()} or None),
        jitter_quotable=bool(jitter),
        byte_identity_expected=False,
        note="A matching sequence with a non-zero timestamp spread is the expected lockstep outcome. Only a spread whose instants all came from the vehicle's own clock (quality `measured`) is apparatus jitter; a spread over reconstructed instants also contains offset-estimate variance.",
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
