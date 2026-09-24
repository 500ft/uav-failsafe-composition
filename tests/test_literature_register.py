"""The literature register is honest: identifiers are recorded, access is stated, and nothing claims a finding."""
import json, re, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "literature"))
import audit_identity, render_axes  # noqa: E402
from search_plan import AXES, QUERIES, plan  # noqa: E402

ACCESS = {"inspected_earlier", "metadata_only", "identifier_unresolved"}
RESOLVED = {"resolved", "unresolved", "not_machine_resolvable"}
MATCHED = {"verified", "unverified", "corrected"}
FIXTURE = json.loads((ROOT / "tests/fixtures/literature-l32-mismatch.json").read_text())


class LiteratureRegisterTests(unittest.TestCase):
    def setUp(self):
        self.reg = json.loads((ROOT / "literature/register.json").read_text())
        self.entries = self.reg["entries"]

    def test_ids_unique_and_axes_known(self):
        ids = [e["id"] for e in self.entries]
        self.assertEqual(len(ids), len(set(ids)))
        for e in self.entries:
            self.assertIn(e["axis"], AXES, e["id"])

    def test_every_entry_states_access_and_why(self):
        for e in self.entries:
            self.assertIn(e["access"], ACCESS, e["id"])
            self.assertTrue(e["why_selected"].strip(), e["id"])
            self.assertTrue(e["what_it_would_settle"].strip(), e["id"])

    def test_an_identifier_always_carries_its_source(self):
        for e in self.entries:
            if e["identifier"]:
                self.assertTrue(e["identifier_source"], e["id"])
                self.assertRegex(e["identifier"], r"^(doi:|arxiv:|https://|JARUS )")
            else:
                self.assertEqual(e["access"], "identifier_unresolved", e["id"])

    def test_unread_sources_are_never_described_as_established(self):
        """A reading list may say why a work was chosen; it may not report what it shows."""
        banned = re.compile(r"\b(establishes|proves|demonstrates that|shows that|confirms)\b", re.I)
        for e in self.entries:
            if e["access"] != "inspected_earlier":
                self.assertIsNone(banned.search(e["why_selected"]), (e["id"], "why_selected"))
                self.assertIsNone(banned.search(e["what_it_would_settle"]), (e["id"], "what_it_would_settle"))

    def test_read_entries_point_at_a_repository_record(self):
        records = {r["source_id"] for r in json.loads((ROOT / "docs/day3-reading-records.json").read_text())}
        for e in self.entries:
            if e["access"] == "inspected_earlier" and e.get("relates_to_repository_record", "").startswith(("U", "S")):
                self.assertIn(e["relates_to_repository_record"], records, e["id"])

    def test_the_search_plan_is_frozen_and_covers_every_axis(self):
        self.assertEqual({a for a, _ in QUERIES}, set(AXES))
        self.assertEqual(plan(), plan())
        self.assertGreaterEqual(len(plan()), len(QUERIES))

    def test_register_does_not_claim_to_be_findings(self):
        self.assertIn("NOT a set of findings", self.reg["status"])

    def test_identity_is_recorded_as_separate_questions(self):
        """Resolving an identifier and identifying the intended work are different facts (F11, 2026-09-24)."""
        for e in self.entries:
            ident = e["identity"]
            self.assertIn(ident["identifier_resolved"], RESOLVED, e["id"])
            self.assertIn(ident["intended_work_matched"], MATCHED, e["id"])
            if not e["identifier"]:
                self.assertEqual(ident["identifier_resolved"], "unresolved", e["id"])

    def test_the_l32_biology_identifier_never_returns(self):
        """The wrong work resolved cleanly and matched its own recorded title, so only this check catches it."""
        wrong = FIXTURE["erroneous_entry"]["identifier"]
        self.assertNotIn(wrong, [e["identifier"] for e in self.entries])
        l32 = next(e for e in self.entries if e["id"] == "L32")
        self.assertEqual(l32["identifier"], FIXTURE["intended_work"]["identifier"])
        self.assertEqual(l32["title"], FIXTURE["intended_work"]["title"])
        self.assertEqual(l32["quarantined_identifier"]["identifier"], wrong)
        self.assertEqual(l32["identity"]["intended_work_matched"], "corrected")
        self.assertNotEqual(l32["identifier"], next(e for e in self.entries if e["id"] == "L33")["identifier"])

    def test_a_title_check_alone_would_not_have_caught_l32(self):
        """State the limit of the automated audit rather than letting it imply the register is now trustworthy."""
        sim = audit_identity.similarity(FIXTURE["erroneous_entry"]["title"], FIXTURE["intended_work"]["title"])
        self.assertLess(sim, 0.60, "the two titles are unrelated, so the register's own title was also wrong")
        self.assertIn("identifier_resolved", self.reg["identity_vocabulary"])

    def test_a_quarantined_record_explains_itself(self):
        for e in self.entries:
            q = e.get("quarantined_identifier")
            if q:
                for field in ("identifier", "what_it_actually_is", "how_it_got_here", "found_by", "kept_because"):
                    self.assertTrue(str(q.get(field, "")).strip(), (e["id"], field))

    def test_an_unresolved_entry_stays_on_the_list(self):
        unresolved = FIXTURE["unresolved_case"]["id"]
        e = next(x for x in self.entries if x["id"] == unresolved)
        self.assertIsNone(e["identifier"])
        self.assertEqual(e["access"], "identifier_unresolved")

    def test_axes_md_is_generated_from_the_register(self):
        self.assertEqual((ROOT / "literature/axes.md").read_text(), render_axes.render(self.reg))

    def test_the_stored_identity_audit_matches_the_register(self):
        rows = {r["id"]: r for r in json.loads((ROOT / "literature/identity-audit.json").read_text())["rows"]}
        for e in self.entries:
            self.assertIn(e["id"], rows)
            self.assertEqual(rows[e["id"]]["identifier"], e["identifier"], e["id"])
            self.assertEqual(rows[e["id"]]["recorded_title"], e["title"], e["id"])
            self.assertNotEqual(rows[e["id"]]["status"], "mismatch", e["id"])


if __name__ == "__main__":
    unittest.main()
