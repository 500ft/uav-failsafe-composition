"""Check that each registered identifier resolves to the work the entry says it is.

    python literature/audit_identity.py            # audit online, rewrite identity-audit.json
    python literature/audit_identity.py --check    # offline: the stored audit still matches the register

Resolving an identifier proves the identifier exists. It does not prove the identifier names the work the
entry was selected for: L32 resolved cleanly to a cell-biology thesis. So the audit compares the registry's
own title against the recorded title and reports `match`, `mismatch` or `unchecked`. A mismatch is never
repaired automatically; a human decides whether the title, the identifier or the selection was wrong.
"""
from __future__ import annotations
import json, re, sys, time, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
REGISTER, AUDIT = HERE / "register.json", HERE / "identity-audit.json"
# Enough to catch "a cell-cycle thesis is not the Simplex paper" without pretending to be a bibliographic tool.
SIMILAR = 0.60


def _norm(s: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", s.lower()) if len(w) > 2}


def similarity(a: str, b: str) -> float:
    x, y = _norm(a), _norm(b)
    return round(len(x & y) / len(x | y), 3) if x and y else 0.0


def resolve(identifier: str) -> dict | None:
    """Registered metadata for a DOI or arXiv id, or None when the scheme is not resolvable here."""
    if identifier.startswith("doi:"):
        url = "https://api.crossref.org/works/" + identifier[4:]
        time.sleep(1.0)      # Crossref answers 429 to an unpaced sweep; the audit is not in a hurry
        with urllib.request.urlopen(url, timeout=30) as r:
            m = json.load(r)["message"]
        return dict(source="crossref", title=(m.get("title") or [""])[0],
                    year=(m.get("issued", {}).get("date-parts") or [[None]])[0][0],
                    venue=(m.get("container-title") or [""])[0])
    if identifier.startswith("arxiv:"):
        url = "http://export.arxiv.org/api/query?id_list=" + identifier[6:]
        with urllib.request.urlopen(url, timeout=30) as r:
            x = r.read().decode()
        t = re.search(r"<entry>.*?<title>(.*?)</title>", x, re.S)
        y = re.search(r"<entry>.*?<published>(\d{4})", x, re.S)
        return dict(source="arxiv", title=" ".join(t.group(1).split()) if t else "",
                    year=int(y.group(1)) if y else None, venue="arXiv")
    return None


def audit(entries: list[dict]) -> list[dict]:
    out = []
    for e in entries:
        row = dict(id=e["id"], identifier=e["identifier"], recorded_title=e["title"])
        try:
            meta = resolve(e["identifier"]) if e["identifier"] else None
        except Exception as exc:                       # a network or lookup failure is a result, not a match
            row.update(status="unchecked", reason=f"{type(exc).__name__}: {exc}")
            out.append(row); continue
        if meta is None:
            row.update(status="unchecked", reason="identifier scheme is not machine-resolvable here")
        else:
            s = similarity(e["title"], meta["title"])
            row.update(status="match" if s >= SIMILAR else "mismatch", similarity=s,
                       registered_title=meta["title"], registered_year=meta["year"],
                       registered_venue=meta["venue"], resolver=meta["source"])
        out.append(row)
    return out


def main(argv: list[str]) -> int:
    reg = json.loads(REGISTER.read_text())
    if "--check" in argv:
        stored = json.loads(AUDIT.read_text())
        by_id = {r["id"]: r for r in stored["rows"]}
        bad = [e["id"] for e in reg["entries"]
               if e["id"] not in by_id or by_id[e["id"]]["identifier"] != e["identifier"]
               or by_id[e["id"]]["recorded_title"] != e["title"]]
        if bad:
            print("stale identity audit for: " + ", ".join(bad), file=sys.stderr)
            return 1
        unresolved = [r["id"] for r in stored["rows"] if r["status"] == "mismatch"
                      and by_id[r["id"]].get("accepted_mismatch") is not True]
        if unresolved:
            print("unaccepted title mismatch: " + ", ".join(unresolved), file=sys.stderr)
            return 1
        print(f"identity audit current: {len(stored['rows'])} rows")
        return 0
    rows = audit(reg["entries"])
    AUDIT.write_text(json.dumps(dict(
        schema_version="2026-09-24",
        method="registry title compared with the recorded title by word-overlap; >= %.2f is a match" % SIMILAR,
        what_this_does_not_establish="a title match shows the identifier names the work; it does not show the "
                                     "work was read, is topically eligible, or supports any claim",
        rows=rows), indent=1) + "\n")
    for r in rows:
        if r["status"] != "match":
            print(json.dumps(r))
    print(json.dumps({s: sum(1 for r in rows if r["status"] == s) for s in ("match", "mismatch", "unchecked")}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
