"""Map every stored capture to a typed legacy record (owner review 2026-09-25, WP1).

    ~/.cache/uav-failsafe-composition/venv/bin/python evidence/task-measurement-repair-2026-09-24/map_legacy_captures.py

Legacy case IDs are NOT unique: five 2026-09-20 control repeats share one. The key is therefore the legacy id
PLUS the raw capture's own content hash. An id that resolves to more than one capture is reported as ambiguous
and is not silently collapsed. Fields the capture never recorded stay `unknown`; none is invented, and a
historical record does not have to meet the new identity standard to stay interpretable.
"""
from __future__ import annotations
import json, shutil, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from harness.cases import MATRIX          # noqa: E402
from harness.identity import file_sha256  # noqa: E402
from harness.trace import build_trace     # noqa: E402

RUNS = Path.home() / ".cache/uav-failsafe-composition/runs"
HERE = Path(__file__).resolve().parent


def main() -> int:
    captures = sorted(p.parent for p in RUNS.rglob("raw.jsonl"))
    if not captures:
        print(f"no captures under {RUNS}", file=sys.stderr)
        return 1
    rows, by_legacy = [], {}
    with tempfile.TemporaryDirectory() as d:
        for i, run in enumerate(captures):
            work = Path(d) / f"{i:03d}"
            shutil.copytree(run, work)
            case = json.loads((work / "case.json").read_text())
            raw_sha = file_sha256(work / "raw.jsonl")
            try:
                trace = build_trace(work, case, MATRIX)
                ident, valid = trace["identity"], trace["validity"]["valid"]
                mode, mode_src = trace["manifest"]["intended_mode"], trace["conversion"]["intended_mode_source"]
            except Exception as exc:
                ident, valid, mode, mode_src = None, None, None, f"{type(exc).__name__}: {exc}"
            row = dict(
                legacy_case_id=case["case_id"],
                capture_path=str(run),
                raw_sha256=raw_sha,
                ulog_sha256=file_sha256(work / "flight.ulg"),
                alias=f"{case['case_id']}@{(raw_sha or '')[:12]}",
                valid=valid,
                intended_mode=mode,
                intended_mode_source=mode_src,
                scenario_id=ident and ident["scenario"]["scenario_id"],
                execution_id=ident and ident["execution"]["execution_id"],
                # Named, not guessed. These captures predate the fields.
                executable_sha256="unknown",
                build_identity="unknown",
                complete_parameter_snapshot="unknown: only explicitly set overrides were read back",
            )
            by_legacy.setdefault(case["case_id"], []).append(row["alias"])
            rows.append(row)
    for r in rows:
        r["legacy_id_unique"] = len(by_legacy[r["legacy_case_id"]]) == 1
        r["legacy_id_resolves_to"] = by_legacy[r["legacy_case_id"]]
    out = dict(
        schema_version="2026-09-25",
        what_this_is=("Every stored capture, keyed by legacy id plus raw content hash. A legacy id alone is "
                      "ambiguous where it maps to more than one capture and must not be used as a key."),
        captures_found=len(rows),
        ambiguous_legacy_ids={k: v for k, v in by_legacy.items() if len(v) > 1},
        rows=rows)
    (HERE / "legacy-captures.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(dict(captures=len(rows), valid=sum(1 for r in rows if r["valid"]),
                          invalid=sum(1 for r in rows if r["valid"] is False),
                          unresolvable_mode=sum(1 for r in rows if r["intended_mode"] is None),
                          ambiguous_legacy_ids=len(out["ambiguous_legacy_ids"]),
                          unique_aliases=len({r["alias"] for r in rows}))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
