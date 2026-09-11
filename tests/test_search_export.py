"""Offline regressions for retrieval integrity; synthetic cases are not literature evidence."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "evidence/task-2026-09-09/rerun_search.py"
spec = importlib.util.spec_from_file_location("rerun_search", SCRIPT)
search = importlib.util.module_from_spec(spec)
spec.loader.exec_module(search)


class SearchExportTests(unittest.TestCase):

    def native_fixture(self):
        body = json.dumps({"message": {"items": [{"DOI": "10.1234/example",
            "title": ["synthetic"], "issued": {"date-parts": [[2026]]}}]}})
        with patch.object(search, "get", return_value=body.encode()):
            result = search.collect([("crossref", "synthetic")],
                                    {"crossref": search.crossref}, sleep=lambda _: None)
        result["query_log"][0]["requests"] = [{
            "route": "https://api.crossref.org/works?query=synthetic&rows=40",
            "started_utc": "2026-09-11T00:00:00Z",
            "finished_utc": "2026-09-11T00:00:01Z", "http_status": 200,
            "response_bytes": len(body.encode()), "raw_response": body,
            "response_sha256": search.hashlib.sha256(body.encode()).hexdigest()}]
        return result

    def test_native_audit_requires_response_even_for_zero_results(self):
        result = self.native_fixture()
        self.assertEqual(search.audit_export(result).get("missing_request_provenance", 0), 0)
        result["query_log"][0]["requests"] = []
        self.assertGreater(search.audit_export(result).get("missing_request_provenance", 0), 0)
        result["hits"] = []
        result["n_unique"] = 0
        result["query_log"][0]["n"] = 0
        self.assertGreater(search.audit_export(result).get("missing_request_provenance", 0), 0)

    def test_native_audit_rejects_invented_identifier_despite_valid_query(self):
        result = self.native_fixture()
        self.assertEqual(search.audit_export(result).get("response_record_mismatches", 0), 0)
        result["hits"][0]["id"] = "doi:10.1234/not-in-response"
        self.assertGreater(search.audit_export(result).get("response_record_mismatches", 0), 0)

    def test_missing_rank_does_not_skip_count_validation(self):
        result = self.native_fixture()
        del result["hits"][0]["provenance"][0]["rank"]
        self.assertGreater(search.audit_export(result)["query_count_mismatches"], 0)
    def test_arxiv_error_feed_is_not_a_paper(self):
        body = b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><id>http://arxiv.org/api/errors#incorrect_id_format</id><title>Error</title><published>2026-09-11</published><summary>Invalid query</summary></entry></feed>'
        with patch.object(search, "get", return_value=body):
            with self.assertRaises(ValueError):
                list(search.arxiv("synthetic"))

    def test_requests_retain_timestamp_route_response_and_hash(self):
        from unittest.mock import MagicMock
        response = MagicMock()
        response.__enter__.return_value = response
        response.read.return_value = b'{"message": "synthetic"}'
        response.status = 200
        search.REQUEST_ATTEMPTS = []
        with patch.object(search.urllib.request, "urlopen", return_value=response):
            search.get("https://example.test/works?api_key=secret&query=test")
        entry = search.REQUEST_ATTEMPTS[0]
        self.assertNotIn("secret", json.dumps(entry))
        self.assertEqual(entry["response_sha256"], search.hashlib.sha256(response.read.return_value).hexdigest())
        self.assertEqual(entry["raw_response"], response.read.return_value.decode())
        self.assertEqual(entry["http_status"], 200)
        self.assertIn("started_utc", entry)

    def test_richer_abstract_retains_its_specific_source_route(self):
        def fetch(query):
            yield dict(id="doi:10.1234/example", title="synthetic", abstract=query, db="mock")
        result = search.collect([("mock", "x"), ("mock", "longer")],
                                {"mock": fetch}, sleep=lambda _: None)
        self.assertEqual(result["hits"][0]["abstract_provenance"]["query"], "longer")
        self.assertIn("started_utc", result["query_log"][0])

    def test_audit_checks_every_route_and_rank_count_not_only_any_route(self):
        def fetch(query):
            yield dict(id="doi:10.1234/example", title="synthetic", abstract="", db="mock")
        result = search.collect([("mock", "first")], {"mock": fetch}, sleep=lambda _: None)
        result["hits"][0]["provenance"].append(dict(db="mock", query="invented", rank=1))
        audit = search.audit_export(result)
        self.assertEqual(audit["unsupported_provenance_routes"], 1)
        result["query_log"][0]["n"] = 2
        self.assertEqual(search.audit_export(result)["query_count_mismatches"], 1)

    def test_identifier_aliases_do_not_hide_arxiv_overlap(self):
        self.assertEqual(search.canonical_id("doi:10.48550/arXiv.2106.14959v2"),
                         "arxiv:2106.14959")
        self.assertEqual(search.canonical_id("https://doi.org/10.2322/TJSASS.60.1"),
                         "doi:10.2322/tjsass.60.1")

    def test_openalex_without_key_attempts_public_route(self):
        with patch.dict(search.os.environ, {}, clear=True), patch.object(search, "get", return_value=b'{"results": []}') as get:
            self.assertEqual(list(search.openalex("synthetic")), [])
            self.assertNotIn("api_key=", get.call_args.args[0])

    def test_openalex_service_rejection_is_not_a_zero_result(self):
        error = search.urllib.error.HTTPError("https://example.test", 401, "unauthorized", {}, None)
        with patch.dict(search.os.environ, {}, clear=True), patch.object(search, "get", side_effect=error):
            result = search.collect([("openalex", "synthetic")], {"openalex": search.openalex}, sleep=lambda _: None)
        self.assertEqual(result["query_log"][0]["status"], "error")
        self.assertIsNone(result["query_log"][0]["n"])

    def test_all_observed_queries_survive_deduplication(self):
        def fetch(query):
            yield dict(id="doi:10.1234/example", title="synthetic", abstract="", db="mock")
        result = search.collect([("mock", "first"), ("mock", "second")],
                                {"mock": fetch}, sleep=lambda seconds: None)
        self.assertEqual(len(result["hits"]), 1)
        self.assertEqual(len(result["hits"][0]["provenance"]), 2)
        self.assertEqual([row["n"] for row in result["query_log"]], [1, 1])

    def test_partial_failure_retains_rows_without_zero_or_success_claim(self):
        def fetch(query):
            yield dict(id="doi:10.1234/example", title="synthetic", abstract="", db="mock")
            raise ValueError("bad response")
        result = search.collect([("mock", "first")], {"mock": fetch}, sleep=lambda _: None)
        self.assertEqual(len(result["hits"]), 1)
        self.assertEqual(result["query_log"][0]["status"], "error")
        self.assertIsNone(result["query_log"][0]["n"])
        self.assertEqual(result["query_log"][0]["n_observed"], 1)

    def test_export_writes_all_three_promised_files(self):
        result = search.collect([], {}, sleep=lambda _: None)
        with tempfile.TemporaryDirectory() as tmp:
            search.write_outputs(Path(tmp), result)
            names = {p.name for p in Path(tmp).iterdir()}
            self.assertEqual(names, {"database-export.json", "database-export.csv",
                                    "candidates-unscreened.csv"})
            with self.assertRaises(FileExistsError):
                search.write_outputs(Path(tmp), result)

    def test_existing_output_directory_is_rejected_before_network(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(search, "collect") as collect:
            self.assertNotEqual(search.main(["--out", tmp]), 0)
            collect.assert_not_called()

    def test_offline_audit_exposes_unlogged_rows_not_just_literal_overlap(self):
        raw = json.loads((SCRIPT.parent / "database-export.json").read_text())
        audit = search.audit_export(raw)
        self.assertGreater(audit["rows_without_successful_logged_query"], 0)
        self.assertIsNone(audit["recall"])
        self.assertEqual(audit["count_unit"], "normalized identifier records; not distinct studies")
        self.assertEqual(audit["known_anchor_matches"], sorted(
            key for key in search.D01_ANCHORS if key in {
                search.canonical_id(h["id"]) for h in raw["hits"]}))

    def test_revised_schedule_preserves_logged_db_query_pairs(self):
        raw = json.loads((SCRIPT.parent / "database-export.json").read_text())
        self.assertEqual(search.query_plan(),
                         [(row["db"], row["query"]) for row in raw["query_log"]])


if __name__ == "__main__":
    unittest.main()
