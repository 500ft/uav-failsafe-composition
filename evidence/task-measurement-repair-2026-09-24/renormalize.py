"""Re-derive every stored development capture under the 2026-09-24 normaliser and compare the verdicts.

    python evidence/task-measurement-repair-2026-09-24/renormalize.py [--runs DIR]

The stored runs are never touched. Each is copied into a scratch directory, re-normalised there, verified, and
compared against the derivation that shipped with it. The old derivation stays exactly as it was: a corrected
pipeline does not get to rewrite what an earlier one reported, only to say what it now reports and why.
"""
from __future__ import annotations
import argparse, json, shutil, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from harness.cases import MATRIX          # noqa: E402
from harness.trace import build_trace     # noqa: E402
from harness import verify as verifier    # noqa: E402

DEFAULT_RUNS = Path.home() / ".cache/uav-failsafe-composition/runs"
HERE = Path(__file__).resolve().parent


def redo(run: Path, scratch: Path, n: int) -> dict:
    work = scratch / f"{n:03d}-{run.name}"
    shutil.copytree(run, work)
    case = json.loads((work / "case.json").read_text())
    old = json.loads((work / "trace.json").read_text()) if (work / "trace.json").is_file() else {}
    trace = build_trace(work, case, MATRIX)
    (work / "trace.json").write_text(json.dumps(trace, indent=1) + "\n")
    new = verifier.verify(work)
    old_v = old.get("verification") or {}
    inj = next((e for e in trace["events"] if e["name"] == "injection"), None)
    old_inj = next((e for e in old.get("events", []) if e["name"] == "injection"), None)
    return dict(
        run=str(run.relative_to(run.parents[2])),
        case_id=case["case_id"],
        intended_mode=trace["manifest"]["intended_mode"],
        intended_mode_source=trace["conversion"]["intended_mode_source"],
        old_status=old_v.get("status"), new_status=new["status"],
        old_reasons=old_v.get("reasons", []), new_reasons=new["reasons"],
        old_injection_t_vehicle_s=old_inj and old_inj.get("t_vehicle_s"),
        new_injection_t_vehicle_s=inj and inj.get("t_vehicle_s"),
        new_injection_t_source=inj and inj.get("t_source"),
        old_mode_sequence=old_v.get("observed", {}).get("mode_sequence"),
        setup_mode_sequence=new["observed"].get("setup_mode_sequence"),
        response_mode_sequence=new["observed"].get("mode_sequence"),
        instants_by_source=trace["conversion"]["instants_by_source"],
        hazard_flag_edges=len(new["observed"].get("hazard_flags", [])),
        old_hazard_t_rel_s=old_v.get("observed", {}).get("hazard_flag_t_rel_s"),
        new_hazard_t_rel_s=new["observed"].get("hazard_flag_t_rel_s"),
        old_offset_spread_s=old.get("clock", {}).get("offset_spread_s"),
        new_offset_spread_s=trace["clock"]["offset_spread_s"],
    )


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=Path, default=DEFAULT_RUNS)
    a = ap.parse_args(argv)
    runs = sorted(p.parent for p in a.runs.rglob("raw.jsonl"))
    if not runs:
        print(f"no captures under {a.runs}; the raw data lives outside git and may not be present here",
              file=sys.stderr)
        return 1
    try:
        import pyulog  # noqa: F401
    except ImportError:
        print("pyulog is not importable: the autopilot log would be silently ignored and every run would lose "
              "its mode transitions. Run this under the project venv.", file=sys.stderr)
        return 2
    rows = []
    with tempfile.TemporaryDirectory() as d:
        for run in runs:
            try:
                rows.append(redo(run, Path(d), len(rows)))
            except Exception as exc:            # a capture that cannot be re-derived is a result, not a crash
                rows.append(dict(run=str(run), error=f"{type(exc).__name__}: {exc}"))
    (HERE / "rederivation.json").write_text(json.dumps(dict(
        derived_on="2026-09-24", normaliser="harness/trace.py at the 2026-09-24 measurement repair",
        source_of_truth="raw.jsonl and flight.ulg in each run directory; stored derivations were not modified",
        rows=rows), indent=1) + "\n")
    for r in rows:
        print(json.dumps(r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
