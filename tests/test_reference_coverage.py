"""Reference coverage must account for every day-1 source and match the committed result."""
import hashlib, json, re, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import reference_coverage as RC  # noqa: E402
from scripts.reference_coverage import compute, aliases, REGISTER  # noqa: E402


class ReferenceCoverageTests(unittest.TestCase):
    def test_every_day1_source_is_in_the_register(self):
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


class ProvenanceBindingTests(unittest.TestCase):
    """Review 2 (2026-09-12): coverage must reuse the native-response audit and bind to exact export bytes;
    blank or unrecognised assessments must stay unresolved."""

    def test_public_export_passes_native_audit_and_historical_does_not(self):
        res = compute()["summary"]["recall"]
        self.assertTrue(res["day4_public"]["provenance"]["native_audit_passed"])
        self.assertFalse(res["day2_historical"]["provenance"]["native_audit_passed"])
        self.assertEqual(res["day2_historical"]["recovered"], 0, "an export that fails the native audit is credited for nothing")

    def test_identifier_absent_from_the_raw_response_is_not_credited(self):
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
        rec = json.loads((ROOT / "evidence/task-2026-09-12/reference-coverage.json").read_text())
        for k, p in RC.EXPORTS.items():
            self.assertEqual(rec["summary"]["recall"][k]["provenance"]["export_sha256"], hashlib.sha256(p.read_bytes()).hexdigest(), k)

    def _axes_for(self, records):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "docs").mkdir()
            (Path(d) / "docs/day3-reading-records.json").write_text(json.dumps(records))
            orig = RC.ROOT; RC.ROOT = Path(d)
            try:
                return RC.novelty_axes()["summary"]
            finally:
                RC.ROOT = orig

    def test_committed_records_use_only_allowed_states(self):
        recs = json.loads((ROOT / "docs/day3-reading-records.json").read_text())
        for r in recs:
            self.assertIn("axis_states", r, r["source_id"])
            for ax, st in r["axis_states"].items():
                self.assertIn(st, RC.ASSESSMENT_STATES, (r["source_id"], ax))

    def test_blank_or_unrecognised_assessment_is_unresolved(self):
        bad = [dict(source_id="X1", access="full_text_pdf", locator="", axis_states={"coverage": "not_found_in_inspected"}),
               dict(source_id="X2", access="full_text_pdf", locator="Sec. 3", axis_states={"coverage": ""}),
               dict(source_id="X3", access="full_text_pdf", locator="Sec. 3", axis_states={"coverage": "supported_bounded"})]
        s = self._axes_for(bad)["coverage"]
        self.assertEqual(s["axis_status"], "unresolved"); self.assertEqual(sorted(s["unresolved_for"]), ["X1", "X2", "X3"])

    def test_uninspected_access_cannot_support_or_disclose(self):
        """Plan T02 (2026-09-15): an abstract-only or unknown-access record with an affirmative or negative
        state and a locator must still count as unresolved on every axis."""
        for access in ("abstract_only", "metadata_only", "inaccessible", "not_reinspected", "whatever", None):
            with self.subTest(access=access):
                rec = dict(source_id="X", access=access, locator="Sec. 2",
                           axis_states={"coverage": "disclosed_or_addressed", "reconnection": "not_found_in_inspected",
                                        "equivalent_intent": "not_applicable", "liveness_vs_setpoint_injection": "not_found_in_inspected"})
                s = self._axes_for([rec])
                for ax in RC.AXES:
                    self.assertEqual(s[ax]["unresolved_for"], ["X"], ax)
                    self.assertEqual(s[ax]["disclosed_by"], [], ax)
                    self.assertEqual(s[ax]["not_found_in_inspected"], [], ax)

    def test_missing_axes_stay_visible_as_unresolved(self):
        """Plan T02: an inspected source that omits one or all axes must appear unresolved on the omitted axes,
        and every canonical axis must be present in the summary."""
        recs = [dict(source_id="X", access="full_text_pdf", locator="Sec. 2", axis_states={"coverage": "not_found_in_inspected"}),
                dict(source_id="Y", access="full_text_html", locator="Sec. 4", axis_states={})]
        s = self._axes_for(recs)
        self.assertEqual(set(s), set(RC.AXES))
        self.assertEqual(s["coverage"]["not_found_in_inspected"], ["X"]); self.assertEqual(s["coverage"]["unresolved_for"], ["Y"])
        for ax in ("equivalent_intent", "reconnection", "liveness_vs_setpoint_injection"):
            self.assertEqual(sorted(s[ax]["unresolved_for"]), ["X", "Y"], ax)

    def test_inspected_source_with_locator_counts(self):
        rec = dict(source_id="X", access="official_documentation", locator="Failsafe section",
                   axis_states={"coverage": "not_found_in_inspected", "reconnection": "disclosed_or_addressed",
                                "equivalent_intent": "not_found_in_inspected", "liveness_vs_setpoint_injection": "not_applicable"})
        s = self._axes_for([rec])
        self.assertEqual(s["reconnection"]["axis_status"], "narrowed_by_disclosure"); self.assertEqual(s["reconnection"]["disclosed_by"], ["X"])
        self.assertEqual(s["coverage"]["axis_status"], "supported_bounded"); self.assertEqual(s["coverage"]["not_found_in_inspected"], ["X"])
        self.assertEqual(s["liveness_vs_setpoint_injection"]["unresolved_for"], [])



class ReviewPacketAcceptanceTests(unittest.TestCase):
    """Plan T15 (2026-09-15): mandatory-source accounting that regeneration cannot satisfy by omission."""
    EVIDENCE = ROOT / "evidence/task-prior-art-closeout-2026-09-15"
    MANDATORY = {f"U{i}" for i in range(1, 13)} | {"S1", "S2", "S3"}

    def records(self):
        return json.loads((ROOT / "docs/day3-reading-records.json").read_text())

    def test_ids_unique_and_mandatory_sources_present(self):
        ids = [r["source_id"] for r in self.records()]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(self.MANDATORY - set(ids), set())

    def test_every_record_has_exactly_the_four_axes_with_valid_states(self):
        for r in self.records():
            self.assertEqual(set(r.get("axis_states", {})), set(RC.AXES), r["source_id"])
            for ax, st in r["axis_states"].items():
                self.assertIn(st, RC.ASSESSMENT_STATES, (r["source_id"], ax))
            self.assertEqual(set(r.get("axes", {})) & set(RC.AXES), set(RC.AXES), r["source_id"])

    def test_unread_access_is_unresolved_everywhere(self):
        for r in self.records():
            if r.get("access") not in RC.INSPECTED_ACCESS or not str(r.get("locator", "")).strip():
                self.assertEqual(set(r["axis_states"].values()), {"unresolved"}, r["source_id"])

    def test_candidate_screening_accounts_for_every_intake_row(self):
        import csv
        hits = json.loads((ROOT / "evidence/task-2026-09-11-public/database-export.json").read_text())["hits"]
        ids = {r["source_id"] for r in self.records()}
        with (self.EVIDENCE / "candidate-screening.csv").open(newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(sorted(int(r["raw_index"]) for r in rows), list(range(len(hits))))
        valid = {"exclude_out_of_scope", "duplicate_identifier", "linked_inspected", "needs_full_text", "unresolved_metadata"}
        for r in rows:
            i = int(r["raw_index"])
            self.assertEqual(r["id"], hits[i]["id"], i)
            self.assertIn(r["decision"], valid, i)
            self.assertTrue(r["reason"].strip(), i)
            if r["decision"] in {"linked_inspected", "needs_full_text", "unresolved_metadata", "duplicate_identifier"}:
                self.assertIn(r["reading_source_id"], ids, (i, r["reading_source_id"]))
            if r["decision"] == "duplicate_identifier":
                self.assertTrue(r["duplicate_of"].isdigit() and int(r["duplicate_of"]) != i, i)
            if r["decision"] in {"needs_full_text", "unresolved_metadata"}:
                self.assertEqual(r["reading_source_id"], f"C{i + 1:03d}", i)


if __name__ == "__main__":
    unittest.main()
