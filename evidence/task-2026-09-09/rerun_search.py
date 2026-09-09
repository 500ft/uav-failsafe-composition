#!/usr/bin/env python3
"""Re-run the native-database prior-art export recorded in this directory.

usage: OPENALEX_API_KEY=... python rerun_search.py [--out .]
Queries and triage weights are the ones used on 2026-09-09; arXiv's search API rate-limits
aggressively, so the arXiv leg sleeps 4 s between queries and backs off on HTTP 429.
No patent database is queried. Output: database-export.json/.csv, candidates-unscreened.csv.
"""
import argparse, csv, json, os, re, sys, time, urllib.parse, urllib.request, xml.etree.ElementTree as ET
QUERIES = [
 "PX4 ArduPilot failsafe differential testing",
 "PX4 ArduPilot recovery benchmark",
 "UAV autopilot failsafe configuration testing fuzzing",
 "UAV communication loss contingency recovery contract",
 "multicopter failsafe behaviour conformance testing simulation",
 "PX4 ArduPilot failsafe",
 "PX4 ArduPilot testing",
 "ArduPilot fuzzing",
 "UAV failsafe recovery contingency",
 "multicopter autopilot conformance testing simulation",
 "UAV communication loss contingency recovery"
]
CONCEPTS = {
 "px4": 3,
 "ardupilot": 3,
 "failsafe": 3,
 "fail-safe": 3,
 "contingency": 2,
 "recovery": 2,
 "differential testing": 3,
 "conformance": 3,
 "fuzz": 2,
 "configuration": 1,
 "autopilot": 2,
 "multicopter": 1,
 "quadrotor": 1,
 "uav": 1,
 "communication loss": 3,
 "link loss": 3,
 "return-to-launch": 3,
 "geofence": 2,
 "benchmark": 1
}
D01_SCREENED = ["arxiv:2106.14959", "arxiv:2505.02357", "arxiv:2602.07264", "arxiv:2608.06648", "arxiv:2608.20906", "patent:EP3662460B1"]
def get(url, tries=5):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url), timeout=60) as r: return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 429 and i < tries - 1: time.sleep(8 * (i + 1)); continue
            raise
def arxiv(q):
    query = " AND ".join(f"all:{t}" for t in re.findall(r'"[^"]+"|\S+', q))
    root = ET.fromstring(get(f"http://export.arxiv.org/api/query?search_query={urllib.parse.quote(query)}&max_results=60")); ns = {"a": "http://www.w3.org/2005/Atom"}
    for e in root.findall("a:entry", ns):
        aid = re.sub(r"v\d+$", "", e.find("a:id", ns).text.rsplit("/", 1)[-1])
        yield dict(db="arxiv", id=f"arxiv:{aid}", title=" ".join(e.find("a:title", ns).text.split()), year=e.find("a:published", ns).text[:4], url=f"https://arxiv.org/abs/{aid}", abstract=" ".join((e.find("a:summary", ns).text or "").split())[:1500])
def crossref(q):
    for it in json.loads(get(f"https://api.crossref.org/works?query={urllib.parse.quote(q)}&rows=40&select=DOI,title,issued,abstract,type,container-title"))["message"]["items"]:
        y = (it.get("issued", {}).get("date-parts") or [[None]])[0][0]
        yield dict(db="crossref", id=f"doi:{it['DOI'].lower()}", title=" ".join((it.get("title") or [""])[0].split()), year=str(y or ""), url=f"https://doi.org/{it['DOI']}", type=it.get("type"), venue=(it.get("container-title") or [""])[0], abstract=re.sub(r"<[^>]+>", "", it.get("abstract", ""))[:1500])
def openalex(q):
    key = os.environ.get("OPENALEX_API_KEY")
    if not key: print("OPENALEX_API_KEY not set; skipping OpenAlex", file=sys.stderr); return
    for w in json.loads(get(f"https://api.openalex.org/works?search={urllib.parse.quote(q)}&per-page=50&select=id,doi,title,publication_year,type,primary_location&api_key={key}"))["results"]:
        doi = (w.get("doi") or "").replace("https://doi.org/", "").lower()
        yield dict(db="openalex", id=f"doi:{doi}" if doi else w["id"], title=w.get("title") or "", year=str(w.get("publication_year") or ""), url=w.get("doi") or w["id"], type=w.get("type"), venue=((w.get("primary_location") or {}).get("source") or {}).get("display_name", ""), abstract="")
def score(h):
    txt = (h.get("title", "") + " " + h.get("abstract", "")).lower(); terms = [k for k in CONCEPTS if k in txt]
    return sum(CONCEPTS[k] for k in terms), terms
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="."); a = ap.parse_args()
    hits, log = {}, []
    for q in QUERIES:
        for fn in (arxiv, crossref, openalex):
            try:
                n = 0
                for h in fn(q):
                    h["query"] = q; n += 1; hits.setdefault(h["id"], h)
                log.append(dict(query=q, db=fn.__name__, n=n, status="ok"))
            except Exception as e:
                log.append(dict(query=q, db=fn.__name__, n=0, status=f"error: {type(e).__name__}: {str(e)[:80]}"))
            time.sleep(4 if fn is arxiv else 1)
    for h in hits.values():
        h["already_screened_d01"] = h["id"] in D01_SCREENED; h["triage_score"], h["triage_terms"] = score(h)
    out = dict(retrieved_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), queries=QUERIES, query_log=log, n_unique=len(hits), n_overlap_with_d01=sum(h["already_screened_d01"] for h in hits.values()), hits=sorted(hits.values(), key=lambda h: -h["triage_score"]))
    json.dump(out, open(os.path.join(a.out, "database-export.json"), "w"), indent=1)
    print(f"{len(hits)} unique | overlap with D01 {out['n_overlap_with_d01']}/{len(D01_SCREENED)} | errors {sum(l['status'] != 'ok' for l in log)}")
if __name__ == "__main__":
    main()
