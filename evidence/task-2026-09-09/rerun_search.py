#!/usr/bin/env python3
"""Review-corrected bounded database retrieval and offline audit.

Use --out NEW_DIRECTORY for a new acquisition, or --audit HISTORICAL_JSON offline.
Never overwrite the historical export. This does not reproduce its missing query legs.
API responses, credential failures, and scientific screening are separate evidence states.
"""
import argparse, csv, json, os, re, sys, time, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from pathlib import Path
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
# Known comparable anchors from docs/prior-art-search-2026-09-08.md U1/U4/U5/U10/U11.
# Patents/specifications are excluded; this is not a complete eligible reference set.
D01_ANCHORS = {"arxiv:2106.14959", "arxiv:2505.02357", "arxiv:2602.07264",
               "arxiv:2608.06648", "arxiv:2608.20906"}
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
    if not key: raise SearchUnavailable("OPENALEX_API_KEY is not set")
    for w in json.loads(get(f"https://api.openalex.org/works?search={urllib.parse.quote(q)}&per-page=50&select=id,doi,title,publication_year,type,primary_location&api_key={key}"))["results"]:
        doi = (w.get("doi") or "").replace("https://doi.org/", "").lower()
        yield dict(db="openalex", id=f"doi:{doi}" if doi else w["id"], title=w.get("title") or "", year=str(w.get("publication_year") or ""), url=w.get("doi") or w["id"], type=w.get("type"), venue=((w.get("primary_location") or {}).get("source") or {}).get("display_name", ""), abstract="")
def score(h):
    txt = (h.get("title", "") + " " + h.get("abstract", "")).lower(); terms = [k for k in CONCEPTS if k in txt]
    return sum(CONCEPTS[k] for k in terms), terms

class SearchUnavailable(RuntimeError):
    """A required service or credential is unavailable, not a zero-result query."""


def canonical_id(identifier):
    value = identifier.strip().lower()
    value = re.sub(r"^https?://(?:dx\.)?doi\.org/", "doi:", value)
    value = re.sub(r"^https?://arxiv\.org/(?:abs|pdf)/", "arxiv:", value)
    value = value.replace("doi:10.48550/arxiv.", "arxiv:")
    if value.startswith("arxiv:"):
        value = re.sub(r"v\d+$", "", value)
    return value


def query_plan():
    # Repeat only recorded database/query pairs; never fabricate missing old legs.
    original = json.loads((Path(__file__).parent / "database-export.json").read_text())
    return [(row["db"], row["query"]) for row in original["query_log"]]


def audit_export(data):
    hits = data["hits"]
    ids = {canonical_id(h["id"]) for h in hits}
    successful = {(q["db"], q["query"]) for q in data["query_log"]
                  if q["status"] == "ok" and isinstance(q.get("n"), int) and q["n"] > 0}
    missing = []
    for h in hits:
        provenance = h.get("provenance") or [{"db": h["db"], "query": h["query"]}]
        if not any((p["db"], p["query"]) in successful for p in provenance):
            missing.append(h["id"])
    return {
        "count_unit": "normalized identifier records; not distinct studies",
        "record_count": len(hits),
        "normalized_identifier_count": len(ids),
        "declared_identifier_count_matches": data.get("n_unique") == len(ids),
        "rows_without_successful_logged_query": len(missing),
        "unlogged_row_ids": sorted(missing),
        "known_anchor_matches": sorted(ids & set(D01_ANCHORS)),
        "anchor_set_complete": False,
        "recall": None,
        "recall_reason": "Incomplete eligible anchor register and query provenance; no recall estimate.",
    }


def collect(plan, fetchers, sleep=time.sleep):
    hits, log = {}, []
    for db, query in plan:
        observed = 0
        entry = {"db": db, "query": query, "n": None, "n_observed": 0}
        try:
            for source in fetchers[db](query):
                observed += 1
                key = canonical_id(source["id"])
                row = hits.setdefault(key, dict(source, id=key, query=query, provenance=[]))
                row["provenance"].append({"db": db, "query": query, "rank": observed,
                                          "source_id": source["id"],
                                          "abstract_available": bool(source.get("abstract"))})
                # Keep richer observed text when an alias/second database has the abstract.
                if len(source.get("abstract", "")) > len(row.get("abstract", "")):
                    row["abstract"] = source["abstract"]
            entry.update(status="ok", n=observed)
        except SearchUnavailable:
            entry.update(status="unavailable", reason="missing required service credential")
        except Exception as error:
            # Do not persist a URL/error string that may contain an API key.
            entry.update(status="error", error_type=type(error).__name__,
                         http_status=getattr(error, "code", None))
        entry["n_observed"] = observed
        log.append(entry)
        sleep(4 if db == "arxiv" else 1)
    for row in hits.values():
        row["matches_known_d01_anchor"] = row["id"] in D01_ANCHORS
        row["screening_status"] = "UNSCREENED"
        row["triage_score"], row["triage_terms"] = score(row)
    return {
        "protocol_version": "2026-09-09-review-1",
        "protocol_note": "New bounded acquisition, not an exact replay of the historical export.",
        "request_limits": {"crossref": 40, "openalex": 50, "arxiv": 60},
        "retrieved_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "query_log": log,
        "n_unique": len(hits),
        "count_unit": "normalized identifier records; not distinct studies",
        "recall": None,
        "hits": sorted(hits.values(), key=lambda h: (-h["triage_score"], h["id"])),
    }


def write_outputs(directory, result):
    names = ("database-export.json", "database-export.csv", "candidates-unscreened.csv")
    if any((directory / name).exists() for name in names):
        raise FileExistsError("Refusing to overwrite a prior evidence artifact")
    with (directory / names[0]).open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    fields = ("id", "title", "year", "url", "abstract", "triage_score",
              "matches_known_d01_anchor", "screening_status", "provenance")
    for name, rows in (
        (names[1], result["hits"]),
        (names[2], [h for h in result["hits"]
                   if not h["matches_known_d01_anchor"] and h["triage_score"] >= 4][:25]),
    ):
        with (directory / name).open("x", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            for row in rows:
                output = {field: row.get(field, "") for field in fields}
                output["provenance"] = json.dumps(output["provenance"], sort_keys=True)
                writer.writerow(output)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path, help="NEW directory; existing directories are rejected")
    mode.add_argument("--audit", type=Path, help="Offline JSON audit; never changes the export")
    args = parser.parse_args(argv)
    if args.audit:
        audit = audit_export(json.loads(args.audit.read_text()))
        print(json.dumps(audit, indent=2))
        return int(audit["rows_without_successful_logged_query"] > 0
                   or not audit["declared_identifier_count_matches"])
    try:
        args.out.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        print("Output must be a new directory; no network requests made.", file=sys.stderr)
        return 2
    result = collect(query_plan(), {"arxiv": arxiv, "crossref": crossref, "openalex": openalex})
    write_outputs(args.out, result)
    incomplete = sum(row["status"] != "ok" for row in result["query_log"])
    print(f"{result['n_unique']} identifier records; {incomplete} incomplete query legs; recall unavailable")
    return 2 if incomplete else 0


if __name__ == "__main__":
    raise SystemExit(main())
