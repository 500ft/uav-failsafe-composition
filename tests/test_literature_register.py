"""The literature register is honest: identifiers are recorded, access is stated, and nothing claims a finding."""
import json, re, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "literature"))
from search_plan import AXES, QUERIES, plan  # noqa: E402

ACCESS = {"inspected_earlier", "metadata_only", "identifier_unresolved"}


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


if __name__ == "__main__":
    unittest.main()
