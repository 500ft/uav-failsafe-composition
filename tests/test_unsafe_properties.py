"""U1-U4 are frozen, machine-readable, source-linked, and consistent with the model's precedence order."""
import json, unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model.px4_failsafe import ACTIONS  # noqa: E402


class UnsafePropertyTests(unittest.TestCase):
    def setUp(self):
        self.p = json.loads((ROOT / "protocols/unsafe-composition-properties.json").read_text())
        self.props = {x["id"]: x for x in self.p["properties"]}

    def test_exactly_the_four_registered_properties(self):
        self.assertEqual(sorted(self.props), ["U1", "U2", "U3", "U4"])

    def test_every_property_is_source_linked_and_planned(self):
        self.assertEqual(self.p["status"], "planned, not executed")
        for pid, prop in self.props.items():
            for field in ("natural_language", "source", "required_channels", "witness_format", "known_limitations", "excludes"):
                self.assertTrue(prop.get(field), (pid, field))
            self.assertTrue(all(e.startswith("X") for e in prop["excludes"]), pid)

    def test_exclusions_resolve(self):
        known = {x["id"] for x in self.p["shared_exclusions"]}
        for pid, prop in self.props.items():
            self.assertEqual(set(prop["excludes"]) - known, set(), pid)
        for x in self.p["shared_exclusions"]:
            self.assertTrue(x["rule"] and x["source"], x["id"])

    def test_precedence_matches_the_model(self):
        self.assertEqual(tuple(self.props["U2"]["precedence"]), ACTIONS)

    def test_u4_does_not_sum_per_hazard_delays(self):
        """The correction that keeps U4 from hiding violations: one shared delay, not a sum."""
        self.assertIn("COM_FAIL_ACT_T", self.props["U4"]["bound_s"])
        self.assertIn("NOT the sum", self.props["U4"]["correction_note"])

    def test_terminal_modes_are_not_called_safe(self):
        blob = json.dumps(self.p).lower()
        self.assertNotIn("safe state", blob)
        self.assertNotIn("proven", blob)


if __name__ == "__main__":
    unittest.main()
