"""Replay predeclared metadata variants; no experiment or safety validation."""
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
candidate = json.loads((HERE / "candidate.json").read_text())
for name, digest in candidate["files"].items():
    assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, "Candidate drift: " + name
spec = importlib.util.spec_from_file_location("contract", ROOT / "scripts/check_repo_contract.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)
plan = json.loads((HERE / "evaluation-cases.json").read_text())
original = json.loads((ROOT / plan["source_fixture"]).read_text())
schema = json.loads((ROOT / plan["schema"]).read_text())
results = []
for case in plan["cases"]:
    instance = deepcopy(original)
    parent = instance
    for key in case["path"][:-1]:
        parent = parent[key]
    parent[case["path"][-1]] = case["value"]
    errors = checker.manifest_errors(instance, schema)
    accepted = not errors
    results.append(dict(id=case["id"], expected_accept=case["accept"], observed_accept=accepted,
                        matches=accepted == case["accept"], errors=errors))
print(json.dumps(dict(kind="developer software counterexamples", cases=results,
                     denominator=len(results), all_matched=all(r["matches"] for r in results)), indent=2))
raise SystemExit(0 if all(r["matches"] for r in results) else 1)
