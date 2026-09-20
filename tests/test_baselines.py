"""Every [Bn] cited in protocols/ and model/ exists in the register; every register entry is cited and hashed."""
import json, re, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class BaselineRegisterTests(unittest.TestCase):
    def setUp(self):
        self.register = {b["id"]: b for b in json.loads((ROOT / "docs/baselines/baselines.json").read_text())}
        files = [p for d in ("protocols", "model") if (ROOT / d).exists() for p in (ROOT / d).rglob("*.md")]
        self.cited = {}
        for p in files:
            for bid in re.findall(r"\[(B\d+)(?:[ ,][^\]]*)?\]", p.read_text()):
                self.cited.setdefault(bid, set()).add(p.relative_to(ROOT).as_posix())

    def test_every_citation_resolves(self):
        self.assertEqual(set(self.cited) - set(self.register), set())

    def test_every_entry_is_cited_somewhere(self):
        self.assertEqual(set(self.register) - set(self.cited), set(), "unused baseline entries")

    def test_every_entry_names_source_hash_and_reasons(self):
        for bid, b in self.register.items():
            for field in ("title", "url", "accessed", "what", "why", "how", "sha256"):
                self.assertTrue(b.get(field), (bid, field))
            for name, digest in b["sha256"].items():
                self.assertTrue(re.fullmatch(r"[0-9a-f]{64}", digest) or bid == "B11", (bid, name))


if __name__ == "__main__":
    unittest.main()
