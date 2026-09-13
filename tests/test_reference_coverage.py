"""Reference coverage must account for every day-1 source and match the committed result."""
import json, subprocess, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.reference_coverage import compute, aliases, REGISTER  # noqa: E402


class ReferenceCoverageTests(unittest.TestCase):
    def test_every_day1_source_is_in_the_register(self):
        import re
        d01 = set(re.findall(r"^\|\s*(U\d+)\s+\[", (ROOT / "docs/prior-art-search-2026-09-08.md").read_text(), re.M))
        reg = {s["source_id"] for s in json.loads(REGISTER.read_text())["sources"]}
        self.assertEqual(d01, reg, "register must list exactly the day-1 sources; no silent exclusion")

    def test_every_source_has_a_reading_record(self):
        reg = {s["source_id"] for s in json.loads(REGISTER.read_text())["sources"]}
        rec = {r["source_id"] for r in json.loads((ROOT / "docs/day3-reading-records.json").read_text())}
        self.assertEqual(reg - rec, set())

    def test_recall_is_over_eligible_sources_only(self):
        res = compute()
        for row in res["rows"]:
            if not row["eligible"]:
                self.assertTrue(all(v is None for v in row["present"].values()), row["source_id"])
                self.assertTrue(row["eligibility_reason"].startswith("NOT eligible"))

    def test_publisher_doi_alias_credits_pgfuzz_and_routhsearch(self):
        # The defect this script corrects: arXiv-only anchors missed both of these.
        res = compute()
        by = {r["source_id"]: r for r in res["rows"]}
        self.assertTrue(by["U2"]["present"]["day4_public"])
        self.assertFalse(by["U2"]["present"]["day2_historical"], "historical export fails the native audit and is credited for nothing")
        self.assertTrue(by["U4"]["present"]["day4_public"]); self.assertFalse(by["U4"]["present"]["day2_historical"])

    def test_alias_expansion(self):
        self.assertEqual(aliases({"arxiv": "2106.14959", "dois": ["10.48550/arXiv.2106.14959"]}),
                         {"arxiv:2106.14959", "doi:10.48550/arxiv.2106.14959"})

    def test_check_mode_passes_on_committed_output(self):
        p = subprocess.run([sys.executable, "scripts/reference_coverage.py", "--check"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)


if __name__ == "__main__":
    unittest.main()


class ProvenanceBindingTests(unittest.TestCase):
    """Review 2 (2026-09-12): coverage must reuse the native-response audit and bind to exact export bytes;
    blank or unrecognised assessments must stay unresolved."""

    def test_public_export_passes_native_audit_and_historical_does_not(self):
        res = compute()["summary"]["recall"]
        self.assertTrue(res["day4_public"]["provenance"]["native_audit_passed"])
        self.assertFalse(res["day2_historical"]["provenance"]["native_audit_passed"])
        self.assertEqual(res["day2_historical"]["recovered"], 0, "an export that fails the native audit is credited for nothing")

    def test_identifier_absent_from_the_raw_response_is_not_credited(self):
        import tempfile, shutil, copy
        from scripts import reference_coverage as RC
        src = RC.EXPORTS["day4_public"]
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "database-export.json"; shutil.copy(src, p)
            ids_before, _, prov_before = RC.export_ids(p)
            self.assertTrue(prov_before["provenance_clean"])
            data = json.loads(p.read_text()); data["hits"][0]["id"] = "doi:10.1234/not-in-any-response"; p.write_text(json.dumps(data))
            ids_after, _, prov_after = RC.export_ids(p)
            self.assertFalse(prov_after["provenance_clean"]); self.assertEqual(ids_after, set())
            self.assertGreater(prov_after["failures"].get("response_record_mismatches", 0), 0)
            self.assertNotEqual(prov_after["export_sha256"], prov_before["export_sha256"])

    def test_check_is_bound_to_export_bytes(self):
        rec = json.loads(Path(__file__).resolve().parents[1].joinpath("evidence/task-2026-09-12/reference-coverage.json").read_text())
        import hashlib
        from scripts import reference_coverage as RC
        for k, p in RC.EXPORTS.items():
            self.assertEqual(rec["summary"]["recall"][k]["provenance"]["export_sha256"], hashlib.sha256(p.read_bytes()).hexdigest(), k)

    def test_blank_or_unrecognised_assessment_is_unresolved(self):
        import tempfile, shutil
        from scripts import reference_coverage as RC
        recs = json.loads((ROOT / "docs/day3-reading-records.json").read_text())
        for r in recs:
            self.assertIn("axis_states", r, r["source_id"])
            for ax, st in r["axis_states"].items():
                self.assertIn(st, RC.ASSESSMENT_STATES, (r["source_id"], ax))
        # in-memory variants: blank state, unknown state, missing locator -> unresolved
        orig = RC.ROOT
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "docs").mkdir()
            bad = [dict(source_id="X1", access="full_text_pdf", locator="", axes={"a": "not_established_in_inspected_sections"}, axis_states={"a": "not_found_in_inspected"}),
                   dict(source_id="X2", access="full_text_pdf", locator="Sec. 3", axes={"a": ""}, axis_states={"a": ""}),
                   dict(source_id="X3", access="full_text_pdf", locator="Sec. 3", axes={"a": "maybe"}, axis_states={"a": "supported_bounded"})]
            (Path(d) / "docs/day3-reading-records.json").write_text(json.dumps(bad))
            RC.ROOT = Path(d)
            try:
                s = RC.novelty_axes()["summary"]["a"]
            finally:
                RC.ROOT = orig
        self.assertEqual(s["axis_status"], "unresolved"); self.assertEqual(sorted(s["unresolved_for"]), ["X1", "X2", "X3"])
