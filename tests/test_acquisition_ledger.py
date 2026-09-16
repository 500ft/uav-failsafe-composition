"""Developer provenance checks; these do not screen literature."""
import json
import unittest
from pathlib import Path
from scripts.acquisition_ledger import build, canonical, day1_rows, render, ROOT


class LedgerTests(unittest.TestCase):
    def test_identifier_normalization(self):
        self.assertEqual(canonical("https://arxiv.org/abs/2106.14959v1"), "arxiv:2106.14959")
        self.assertEqual(canonical("https://doi.org/10.2322/TJSASS.60.1"), "doi:10.2322/tjsass.60.1")

    def test_merge_keeps_both_routes_without_invented_log(self):
        source = dict(id="U1", title="Paper", url="https://arxiv.org/abs/2106.14959v1", assessment="sections inspected")
        raw = dict(retrieved_utc="2026-09-09T00:00:00Z", query_log=[],
                   hits=[dict(id="arxiv:2106.14959", title="Paper", db="arxiv", query="q")])
        output = build([source], raw)
        self.assertEqual(len(output["records"]), 1)
        self.assertEqual(output["rows_without_successful_logged_query"], 1)
        self.assertEqual(output["records"][0]["screening_status"], "day1_assessment_available")
        self.assertIsNone(output["records"][0]["acquisitions"][0]["query"])
        self.assertIsNone(output["recall"])

    def test_logged_zero_does_not_support_returned_hit(self):
        raw = dict(retrieved_utc="date", query_log=[dict(db="arxiv", query="q", n=0, status="ok")],
                   hits=[dict(id="arxiv:1", title="hit", db="arxiv", query="q")])
        self.assertEqual(build([], raw)["rows_without_successful_logged_query"], 1)

    def test_unscreened_hit_stays_unscreened_even_if_raw_flag_says_read(self):
        raw = dict(retrieved_utc="date", query_log=[dict(db="arxiv", query="q", n=1, status="ok")],
                   hits=[dict(id="arxiv:1", title="hit", db="arxiv", query="q", already_screened_d01=True)])
        row = build([], raw)["records"][0]
        self.assertEqual(row["screening_status"], "unscreened")
        self.assertTrue(row["acquisitions"][0]["query_log_supported"])

    def test_day1_source_count_and_existing_provenance_holes(self):
        text = (ROOT / "docs/prior-art-search-2026-09-08.md").read_text()
        raw = json.loads((ROOT / "evidence/task-2026-09-09/database-export.json").read_text())
        sources = day1_rows(text)
        self.assertEqual(len(sources), 12)
        result = build(sources, raw)
        self.assertEqual(result["rows_without_successful_logged_query"], 90)
        self.assertEqual(result["raw_day2_rows"], len(raw["hits"]))
        self.assertEqual(sum(a["route"] == "day2_native_reported" for x in result["records"] for a in x["acquisitions"]), len(raw["hits"]))

    def test_committed_ledger_reproduces(self):
        self.assertEqual((ROOT / "evidence/task-day3-2026-09-09/acquisition-ledger.json").read_text(), render())


class AccessPromotionTests(unittest.TestCase):
    """Plan T02 (2026-09-15): unread text must not become an available assessment."""
    RAW = dict(retrieved_utc="date", query_log=[], hits=[])

    def reading(self, access, locator="Sec. 3"):
        return dict(source_id="X", title="Paper", url="https://doi.org/10.1234/x", access=access,
                    locator=locator, retrieved_on="2026-09-15")

    def test_abstract_only_reading_is_not_promoted(self):
        for access in ("abstract_only", "metadata_only", "inaccessible", "not_reinspected", "", None):
            with self.subTest(access=access):
                row = build([], self.RAW, [self.reading(access)])["records"][0]
                self.assertEqual(row["screening_status"], "unscreened")

    def test_inspected_access_without_locator_is_not_promoted(self):
        row = build([], self.RAW, [self.reading("full_text_pdf", locator="")])["records"][0]
        self.assertEqual(row["screening_status"], "unscreened")

    def test_inspected_access_with_locator_is_promoted(self):
        row = build([], self.RAW, [self.reading("full_text_pdf")])["records"][0]
        self.assertEqual(row["screening_status"], "day3_assessment_available")

    def test_failed_later_access_keeps_day1_assessment(self):
        source = dict(id="U1", title="Paper", url="https://doi.org/10.1234/x", assessment="sections inspected")
        row = build([source], self.RAW, [self.reading("inaccessible")])["records"][0]
        self.assertEqual(row["screening_status"], "day1_assessment_available")

if __name__ == "__main__":
    unittest.main()
