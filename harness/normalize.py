"""Rebuild the normalised trace for one run directory from its raw capture, without re-flying it.

    python -m harness.normalize <run directory> [...]

Normalisation is deliberately a separate step from capture: raw.jsonl and the autopilot log are the record,
trace.json is derived and may be regenerated when the normaliser is corrected. Raw values are never discarded.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

from harness.cases import MATRIX
from harness.trace import build_trace


def normalize(run_dir: Path) -> dict:
    case = json.loads((run_dir / "case.json").read_text())
    trace = build_trace(run_dir, case, MATRIX)
    (run_dir / "trace.json").write_text(json.dumps(trace, indent=1) + "\n")
    return trace


def main(argv=None) -> int:
    dirs = [Path(d) for d in (argv or sys.argv[1:])]
    if not dirs:
        print("usage: python -m harness.normalize <run directory> [...]", file=sys.stderr)
        return 2
    for d in dirs:
        trace = normalize(d)
        transitions = [e["detail"] for e in trace["events"] if e["name"] == "native_transition"]
        print(json.dumps(dict(run=d.name, valid=trace["validity"], samples=len(trace["samples"]),
                              events=len(trace["events"]), transitions=transitions)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
