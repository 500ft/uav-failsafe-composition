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
import argparse, hashlib, json, sys
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

def _native_audit(export):
    """Reuse the export's own native-response audit (rerun_search.audit_export): every hit must be
    present in a logged raw response whose hash matches, on a logged successful query. This is the
    stronger check the review asked coverage to bind to; provenance_clean means it passed."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("rerun_search", ROOT / "evidence/task-2026-09-09/rerun_search.py")
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    a = mod.audit_export(export)
    failures = {k: a[k] for k in mod.AUDIT_FAILURE_KEYS if a[k]}
    return dict(native_audit={k: a[k] for k in mod.AUDIT_FAILURE_KEYS}, native_audit_passed=(not failures), failures=failures)


def export_ids(path):
    """Identifier aliases of every hit in an export that is TRACEABLE to a logged successful query.
    Hits whose (db, query) has no status=ok log line are excluded from credit and enumerated,
    so coverage is provenance-bound: an export can only be credited for what it can show it
    searched. Returns (ids, retrieved_utc, provenance)."""
    raw = path.read_bytes(); d = json.loads(raw)
    ok = {(l.get("db"), l.get("query")) for l in d.get("query_log", []) if l.get("status") == "ok"}
    ids, untraceable = set(), []
    for h in d["hits"]:
        traceable = (h.get("db"), h.get("query")) in ok
        if not traceable:
            untraceable.append(h.get("id")); continue
        ids.add(str(h["id"]).lower())
        for k in ("doi", "arxiv"):
            if h.get(k): ids.add(f"{k}:{str(h[k]).lower()}")
    na = _native_audit(d)
    clean = (len(untraceable) == 0) and na["native_audit_passed"]
    if not clean:
        ids = set()      # an export that fails the native audit is credited for NOTHING
    prov = dict(hits=len(d["hits"]), traceable=len(d["hits"]) - len(untraceable), untraceable=len(untraceable),
                untraceable_ids_sample=sorted(untraceable)[:10], export_sha256=hashlib.sha256(raw).hexdigest(),
                provenance_clean=clean, **na)
    return ids, d.get("retrieved_utc"), prov


ASSESSMENT_STATES = {"disclosed_or_addressed", "not_found_in_inspected", "not_applicable", "unresolved"}
AXES = ("equivalent_intent", "liveness_vs_setpoint_injection", "reconnection", "coverage")
# Same allowlist as acquisition_ledger.INSPECTED_ACCESS (kept local on purpose: no shared module).
INSPECTED_ACCESS = {"full_text_sections", "full_text_pdf", "full_text_html", "official_documentation",
                    "patent_claims", "repository_files"}


def novelty_axes():
    """Per canonical axis, per source, the record's EXPLICIT reviewed assessment (axis_states). Every
    record is scored on all four AXES: a missing axis is unresolved, so is anything outside
    ASSESSMENT_STATES, and so is EVERY axis of a record whose access is not in INSPECTED_ACCESS or
    whose locator is empty (unread text cannot disclose or support anything). An axis is
    supported_bounded only if no source discloses it AND at least one inspected source records
    not_found_in_inspected for it; unresolved sources are always listed alongside."""
    recs = json.loads((ROOT / "docs/day3-reading-records.json").read_text())
    table = {ax: [] for ax in AXES}
    for r in recs:
        states = r.get("axis_states") or {}
        inspected = r.get("access") in INSPECTED_ACCESS and bool(str(r.get("locator", "")).strip())
        for ax in AXES:
            st = states.get(ax)
            if not inspected or st not in ASSESSMENT_STATES:
                st = "unresolved"
            table[ax].append(dict(source_id=r["source_id"], state=st, access=r.get("access"), locator=str(r.get("locator", ""))[:160]))
    summary = {}
    for ax, xs in table.items():
        disc = [x["source_id"] for x in xs if x["state"] == "disclosed_or_addressed"]
        nf = [x["source_id"] for x in xs if x["state"] == "not_found_in_inspected"]
        un = [x["source_id"] for x in xs if x["state"] == "unresolved"]
        summary[ax] = dict(axis_status=("narrowed_by_disclosure" if disc else ("supported_bounded" if nf else "unresolved")),
                           disclosed_by=disc, not_found_in_inspected=nf, unresolved_for=un)
    return dict(summary=summary, detail=table)


def compute():
    reg = json.loads(REGISTER.read_text())
    exports = {k: export_ids(p) for k, p in EXPORTS.items()}
    rows = []
    for s in reg["sources"]:
        al = aliases(s["identifiers"])
        row = dict(source_id=s["source_id"], title=s["title"], eligible=s["eligible_for_database_export"],
                   eligibility_reason=s["eligibility_reason"], aliases=sorted(al), present={})
        for k, (ids, _, _) in exports.items():
            row["present"][k] = (bool(al & ids) if row["eligible"] else None)
        rows.append(row)
    elig = [r for r in rows if r["eligible"]]
    axes = novelty_axes()
    summary = dict(d01_sources=len(rows), eligible=len(elig), not_eligible=len(rows) - len(elig),
                   recall={k: {"recovered": sum(bool(r["present"][k]) for r in elig), "of_eligible": len(elig),
                               "recovered_ids": [r["source_id"] for r in elig if r["present"][k]],
                               "missed_ids": [r["source_id"] for r in elig if not r["present"][k]],
                               "export_retrieved_utc": exports[k][1], "provenance": exports[k][2]} for k in EXPORTS},
                   canonical_export=next((k for k in EXPORTS if exports[k][2]["provenance_clean"]), None),
                   rejected_exports=[k for k in EXPORTS if not exports[k][2]["provenance_clean"]],
                   novelty_axes=axes["summary"],
                   previously_reported={"day2_historical": "0 of 6 (arXiv-id anchors only; NDSS and ACM DOIs not in the anchor set)",
                                        "day4_public": "2 of 5 (same anchor set; PGFuzz DOI present but uncredited)"},
                   not_eligible_ids=[r["source_id"] for r in rows if not r["eligible"]])
    return dict(register_version=reg["version"], summary=summary, rows=rows, novelty_axes_detail=axes["detail"])

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--check", action="store_true"); a = ap.parse_args()
    res = compute()
    if a.check:
        if not OUT.exists(): print(f"STALE: {OUT} missing"); sys.exit(1)
        old = json.loads(OUT.read_text())
        if old["summary"] != res["summary"] or old["rows"] != res["rows"] or old.get("novelty_axes_detail") != res["novelty_axes_detail"]:
            print("STALE: committed reference-coverage.json differs from recomputation"); sys.exit(1)
        print("reference coverage OK:", json.dumps({k: f"{v['recovered']}/{v['of_eligible']}" for k, v in res["summary"]["recall"].items()})); return
    OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(res, indent=1) + "\n")
    s = res["summary"]
    print(f"D01 sources {s['d01_sources']}: eligible {s['eligible']}, not eligible {s['not_eligible']} ({', '.join(s['not_eligible_ids'])})")
    for k, v in s["recall"].items(): print(f"  {k:16s} recall {v['recovered']}/{v['of_eligible']}  recovered={v['recovered_ids']} missed={v['missed_ids']}  provenance: {v['provenance']['traceable']}/{v['provenance']['hits']} traceable")
    print(f"  canonical export: {s['canonical_export']}  rejected: {s['rejected_exports']}")
    for ax, v in s["novelty_axes"].items(): print(f"  axis {ax}: {v['axis_status']} | disclosed_by={v['disclosed_by']} not_found_in={v['not_found_in_inspected']} unresolved={v['unresolved_for']}")
    print("wrote", OUT.relative_to(ROOT))

if __name__ == "__main__":
    main()
