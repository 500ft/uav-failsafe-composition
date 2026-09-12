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
        self.assertTrue(by["U2"]["present"]["day2_historical"] and by["U2"]["present"]["day4_public"])
        self.assertTrue(by["U4"]["present"]["day2_historical"] and by["U4"]["present"]["day4_public"])

    def test_alias_expansion(self):
        self.assertEqual(aliases({"arxiv": "2106.14959", "dois": ["10.48550/arXiv.2106.14959"]}),
                         {"arxiv:2106.14959", "doi:10.48550/arxiv.2106.14959"})

    def test_check_mode_passes_on_committed_output(self):
        p = subprocess.run([sys.executable, "scripts/reference_coverage.py", "--check"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)


if __name__ == "__main__":
    unittest.main()
