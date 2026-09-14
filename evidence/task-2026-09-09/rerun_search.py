#!/usr/bin/env python3
"""Review-corrected bounded database retrieval and offline audit.

Use --out NEW_DIRECTORY for a new acquisition, or --audit HISTORICAL_JSON offline.
Never overwrite the historical export. This does not reproduce its missing query legs.
API responses, credential failures, and scientific screening are separate evidence states.
"""
import argparse, csv, hashlib, json, os, re, sys, time, urllib.parse, urllib.request, xml.etree.ElementTree as ET
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
AUDIT_FAILURE_KEYS = ("unsupported_provenance_routes", "missing_request_provenance", "response_record_mismatches",
                      "query_count_mismatches", "response_hash_mismatches", "rows_without_successful_logged_query")
REQUEST_ATTEMPTS = []

def utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def get(url, tries=2):
    parsed = urllib.parse.urlsplit(url)
    safe_query = urllib.parse.urlencode([(k, "[REDACTED]" if k == "api_key" else v)
        for k, v in urllib.parse.parse_qsl(parsed.query)])
    route = urllib.parse.urlunsplit(parsed._replace(query=safe_query))
    for i in range(tries):
        entry = dict(route=route, attempt=i + 1, started_utc=utc())
        REQUEST_ATTEMPTS.append(entry)
        try:
            with urllib.request.urlopen(urllib.request.Request(url), timeout=30) as r:
                body = r.read()
                entry.update(http_status=r.status, response_bytes=len(body),
                    response_sha256=hashlib.sha256(body).hexdigest(),
                    raw_response=body.decode("utf-8"), finished_utc=utc())
                return body
        except urllib.error.HTTPError as e:
            body = e.read()
            entry.update(http_status=e.code, response_bytes=len(body),
                response_sha256=hashlib.sha256(body).hexdigest(),
                error_type=type(e).__name__, finished_utc=utc())
            if e.code == 429 and i < tries - 1: time.sleep(8); continue
            raise
        except Exception as error:
            entry.update(error_type=type(error).__name__, finished_utc=utc())
            raise
def arxiv(q):
    query = " AND ".join(f"all:{t}" for t in re.findall(r'"[^"]+"|\S+', q))
    root = ET.fromstring(get(f"https://export.arxiv.org/api/query?search_query={urllib.parse.quote(query)}&max_results=60")); ns = {"a": "http://www.w3.org/2005/Atom"}
    for e in root.findall("a:entry", ns):
        if "/api/errors" in e.find("a:id", ns).text:
            raise ValueError("arXiv returned an API error entry, not a scholarly record")
        aid = re.sub(r"v\d+$", "", e.find("a:id", ns).text.rsplit("/", 1)[-1])
        yield dict(db="arxiv", id=f"arxiv:{aid}", title=" ".join(e.find("a:title", ns).text.split()), year=e.find("a:published", ns).text[:4], url=f"https://arxiv.org/abs/{aid}", abstract=" ".join((e.find("a:summary", ns).text or "").split())[:1500])
def crossref(q):
    for it in json.loads(get(f"https://api.crossref.org/works?query={urllib.parse.quote(q)}&rows=40&select=DOI,title,issued,abstract,type,container-title"))["message"]["items"]:
        y = (it.get("issued", {}).get("date-parts") or [[None]])[0][0]
        yield dict(db="crossref", id=f"doi:{it['DOI'].lower()}", title=" ".join((it.get("title") or [""])[0].split()), year=str(y or ""), url=f"https://doi.org/{it['DOI']}", type=it.get("type"), venue=(it.get("container-title") or [""])[0], abstract=re.sub(r"<[^>]+>", "", it.get("abstract", ""))[:1500])
def openalex(q):
    key = os.environ.get("OPENALEX_API_KEY")
    credential = "&api_key=" + urllib.parse.quote(key, safe="") if key else ""
    for w in json.loads(get(f"https://api.openalex.org/works?search={urllib.parse.quote(q)}&per-page=50&select=id,doi,title,publication_year,type,primary_location{credential}"))["results"]:
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



def native_response_ids(database, body):
    """Decode the retained native response offline; no new retrieval or screening."""
    if database == "crossref":
        return [canonical_id("doi:" + row["DOI"])
                for row in json.loads(body)["message"]["items"]]
    if database == "openalex":
        return [canonical_id(row.get("doi") or row["id"])
                for row in json.loads(body)["results"]]
    if database == "arxiv":
        root = ET.fromstring(body)
        identifiers = [row.find("{http://www.w3.org/2005/Atom}id").text
                      for row in root.findall("{http://www.w3.org/2005/Atom}entry")]
        if any("/api/errors" in value for value in identifiers):
            raise ValueError("API error feed is not a result")
        return [canonical_id(value) for value in identifiers]
    raise ValueError("Unsupported native database")


def response_evidence(data):
    missing, mismatches, expected = 0, 0, {}
    for query in data["query_log"]:
        if query["status"] != "ok":
            continue
        attempts = query.get("requests") or []
        good = [a for a in attempts if type(a.get("http_status")) is int
                and 200 <= a["http_status"] < 300 and isinstance(a.get("raw_response"), str)]
        if not good:
            missing += 1
            continue
        response = good[-1]
        body = response["raw_response"]
        required = ("route", "started_utc", "finished_utc", "response_sha256")
        if (any(not isinstance(response.get(k), str) or not response[k] for k in required)
                or response.get("response_bytes") != len(body.encode("utf-8"))
                or response.get("response_sha256") != hashlib.sha256(body.encode("utf-8")).hexdigest()):
            missing += 1
            continue
        try:
            source_ids = native_response_ids(query["db"], body)
        except (ValueError, KeyError, TypeError, AttributeError, ET.ParseError):
            missing += 1
            continue
        expected[(query["db"], query["query"])] = source_ids
        mismatches += type(query.get("n")) is not int or query["n"] != len(source_ids)
    for row in data["hits"]:
        for provenance in row.get("provenance", []):
            source_ids = expected.get((provenance["db"], provenance["query"]))
            rank = provenance.get("rank")
            if source_ids is None:
                continue
            if type(rank) is not int or not 1 <= rank <= len(source_ids):
                mismatches += 1
            elif (canonical_id(row["id"]) != source_ids[rank - 1]
                  or canonical_id(provenance.get("source_id", row["id"])) != source_ids[rank - 1]):
                mismatches += 1
    return missing, mismatches

def audit_export(data):
    hits = data["hits"]
    ids = {canonical_id(h["id"]) for h in hits}
    successful = {(q["db"], q["query"]) for q in data["query_log"]
                  if q["status"] == "ok" and isinstance(q.get("n"), int) and q["n"] > 0}
    missing, unsupported, ranks = [], 0, {}
    for h in hits:
        provenance = h.get("provenance") or [{"db": h["db"], "query": h["query"]}]
        for p in provenance:
            pair = (p["db"], p["query"])
            unsupported += pair not in successful
            ranks.setdefault(pair, []).append(p.get("rank"))
        if not any((p["db"], p["query"]) in successful for p in provenance):
            missing.append(h["id"])
    mismatches = 0
    for q in data["query_log"]:
        if q["status"] != "ok":
            continue
        observed_ranks = ranks.get((q["db"], q["query"]), [])
        if type(q.get("n")) is not int or q["n"] < 0 or any(type(r) is not int for r in observed_ranks):
            mismatches += 1
        elif sorted(observed_ranks) != list(range(1, q["n"] + 1)):
            mismatches += 1
    missing_requests, response_mismatches = response_evidence(data)
    bad_hashes = sum(hashlib.sha256(a["raw_response"].encode()).hexdigest() != a["response_sha256"]
        for q in data["query_log"] for a in q.get("requests", []) if "raw_response" in a)
    return {
        "unsupported_provenance_routes": unsupported,
        "missing_request_provenance": missing_requests,
        "response_record_mismatches": response_mismatches,
        "query_count_mismatches": mismatches,
        "response_hash_mismatches": bad_hashes,
        "count_unit": "normalized identifier records; not distinct studies",
        "record_count": len(hits),
        "normalized_identifier_count": len(ids),
        "declared_identifier_count_matches": data.get("n_unique") == len(ids),
        "rows_without_successful_logged_query": len(missing),
        "unlogged_row_ids": sorted(missing),
        "known_anchor_matches": sorted(ids & set(D01_ANCHORS)),
        "anchor_set_complete": False,
        "recall": None,
        "recall_reason": "Incomplete eligible anchor register; overlap is not recall. Query-route completeness is reported separately.",
    }


def collect(plan, fetchers, sleep=time.sleep):
    global REQUEST_ATTEMPTS
    hits, log = {}, []
    for db, query in plan:
        REQUEST_ATTEMPTS = []
        observed = 0
        entry = {"db": db, "query": query, "n": None, "n_observed": 0,
                 "started_utc": utc()}
        try:
            for source in fetchers[db](query):
                observed += 1
                key = canonical_id(source["id"])
                row = hits.setdefault(key, dict(source, id=key, query=query, provenance=[]))
                row["provenance"].append({"db": db, "query": query, "rank": observed,
                                          "source_id": source["id"],
                                          "abstract_available": bool(source.get("abstract"))})
                if "abstract_provenance" not in row:
                    row["abstract_provenance"] = dict(row["provenance"][-1])
                # Keep richer observed text when an alias/second database has the abstract.
                if len(source.get("abstract", "")) > len(row.get("abstract", "")):
                    row["abstract"] = source["abstract"]
                    row["abstract_provenance"] = dict(row["provenance"][-1])
            entry.update(status="ok", n=observed)
        except SearchUnavailable:
            entry.update(status="unavailable", reason="missing required service credential")
        except Exception as error:
            # Do not persist a URL/error string that may contain an API key.
            entry.update(status="error", error_type=type(error).__name__,
                         http_status=getattr(error, "code", None))
        entry["n_observed"] = observed
        entry.update(requests=REQUEST_ATTEMPTS, finished_utc=utc())
        log.append(entry)
        sleep(4 if db == "arxiv" else 1)
    for row in hits.values():
        row["matches_known_d01_anchor"] = row["id"] in D01_ANCHORS
        row["screening_status"] = "UNSCREENED"
        row["triage_score"], row["triage_terms"] = score(row)
    return {
        "protocol_version": "2026-09-11-clean-2",
        "protocol_note": "New bounded acquisition, not an exact replay of the historical export.",
        "request_limits": {"crossref": 40, "openalex": 50, "arxiv": 60},
        "retrieved_utc": utc(),
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
              "matches_known_d01_anchor", "screening_status", "provenance", "abstract_provenance")
    for name, rows in (
        (names[1], result["hits"]),
        (names[2], [h for h in result["hits"]
                   if not h["matches_known_d01_anchor"] and h["triage_score"] >= 4][:25]),
    ):
        with (directory / name).open("x", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            for row in rows:
                output = {field: row.get(field, "") for field in fields}
                # Display-only normalization; authoritative JSON/raw responses are unchanged.
                for field in ("title", "abstract"):
                    output[field] = " ".join(output[field].split())
                output["provenance"] = json.dumps(output["provenance"], sort_keys=True)
                output["abstract_provenance"] = json.dumps(output["abstract_provenance"], sort_keys=True)
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
        return int(any(audit[k] for k in AUDIT_FAILURE_KEYS) or not audit["declared_identifier_count_matches"])
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
