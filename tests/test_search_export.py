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
    def test_identifier_aliases_do_not_hide_arxiv_overlap(self):
        self.assertEqual(search.canonical_id("doi:10.48550/arXiv.2106.14959v2"),
                         "arxiv:2106.14959")
        self.assertEqual(search.canonical_id("https://doi.org/10.2322/TJSASS.60.1"),
                         "doi:10.2322/tjsass.60.1")

    def test_missing_openalex_key_is_not_successful_empty_search(self):
        with patch.dict(search.os.environ, {}, clear=True):
            with self.assertRaises(search.SearchUnavailable):
                list(search.openalex("synthetic"))

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
