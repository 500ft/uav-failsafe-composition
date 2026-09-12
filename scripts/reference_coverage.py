#!/usr/bin/env python3
"""Reference-coverage reconciliation for the day-1 prior-art set (URC-R02).

Accounts for EVERY day-1 source: resolves its identifiers (recorded in
docs/source-eligibility-register.json, resolved from primary metadata on 2026-09-12),
decides whether a scholarly-database export could in principle have returned it, and
then checks each database export for it under every identifier alias -- arXiv id,
arXiv DOI, and publisher DOI. Recall is reported over ELIGIBLE sources only, with each
exclusion stated. Nothing is dropped silently: ineligible sources appear in the output
with their reason.

Why this exists: the day-2 and day-4 exports each reported recall against an anchor
set that carried arXiv ids only. That missed PGFuzz (NDSS DOI 10.14722/ndss.2021.24096)
and the published RouthSearch (ACM DOI 10.1145/3728904), both of which the exports DID
return. Reported 0/6 and 2/5; actual 2/6 and 3/6. The denominators also differed. This
script fixes both and is the number the docs must cite.

usage: python scripts/reference_coverage.py            # print + write evidence JSON
       python scripts/reference_coverage.py --check    # exit 1 if committed JSON is stale
"""
import argparse, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "docs/source-eligibility-register.json"
EXPORTS = {"day2_historical": ROOT / "evidence/task-2026-09-09/database-export.json",
           "day4_public":     ROOT / "evidence/task-2026-09-11-public/database-export.json"}
OUT = ROOT / "evidence/task-2026-09-12/reference-coverage.json"

def aliases(ids):
    out = set()
    if ids.get("arxiv"):
        out |= {f"arxiv:{ids['arxiv']}".lower(), f"doi:10.48550/arxiv.{ids['arxiv']}".lower()}
    for d in ids.get("dois", []):
        out.add(f"doi:{d}".lower())
    return out

def export_ids(path):
    exp = json.loads(path.read_text()); s = set()
    for h in exp["hits"]:
        s.add(str(h["id"]).lower())
        for k in ("doi", "arxiv"):
            if h.get(k): s.add(f"{k}:{str(h[k]).lower()}")
    return s, exp.get("retrieved_utc")

def compute():
    reg = json.loads(REGISTER.read_text())
    exports = {k: export_ids(p) for k, p in EXPORTS.items()}
    rows = []
    for s in reg["sources"]:
        row = dict(source_id=s["source_id"], title=s["title"], eligible=s["eligible_for_database_export"],
                   eligibility_reason=s["eligibility_reason"], aliases=sorted(aliases(s["identifiers"])), present={})
        for k, (ids, _) in exports.items():
            row["present"][k] = (bool(aliases(s["identifiers"]) & ids) if row["eligible"] else None)
        rows.append(row)
    elig = [r for r in rows if r["eligible"]]
    summary = dict(d01_sources=len(rows), eligible=len(elig), not_eligible=len(rows) - len(elig),
                   recall={k: {"recovered": sum(bool(r["present"][k]) for r in elig), "of_eligible": len(elig),
                               "recovered_ids": [r["source_id"] for r in elig if r["present"][k]],
                               "missed_ids": [r["source_id"] for r in elig if not r["present"][k]],
                               "export_retrieved_utc": exports[k][1]} for k in EXPORTS},
                   previously_reported={"day2_historical": "0 of 6 (arXiv-id anchors only; NDSS and ACM DOIs not in the anchor set)",
                                        "day4_public": "2 of 5 (same anchor set; PGFuzz DOI present but uncredited)"},
                   not_eligible_ids=[r["source_id"] for r in rows if not r["eligible"]])
    return dict(register_version=reg["version"], summary=summary, rows=rows)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--check", action="store_true"); a = ap.parse_args()
    res = compute()
    if a.check:
        if not OUT.exists(): print(f"STALE: {OUT} missing"); sys.exit(1)
        old = json.loads(OUT.read_text())
        if old["summary"] != res["summary"] or old["rows"] != res["rows"]:
            print("STALE: committed reference-coverage.json differs from recomputation"); sys.exit(1)
        print("reference coverage OK:", json.dumps({k: f"{v['recovered']}/{v['of_eligible']}" for k, v in res["summary"]["recall"].items()})); return
    OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(res, indent=1) + "\n")
    s = res["summary"]
    print(f"D01 sources {s['d01_sources']}: eligible {s['eligible']}, not eligible {s['not_eligible']} ({', '.join(s['not_eligible_ids'])})")
    for k, v in s["recall"].items(): print(f"  {k:16s} recall {v['recovered']}/{v['of_eligible']}  recovered={v['recovered_ids']} missed={v['missed_ids']}")
    print("wrote", OUT.relative_to(ROOT))

if __name__ == "__main__":
    main()
