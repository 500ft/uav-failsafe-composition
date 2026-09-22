"""The hand-derived expectations are complete, and they agree with the independent code transcription.

Section 12 item 1: the expected outcome is derived outside the model translator. These tests check that the two
derivations agree; a disagreement means one of them is wrong, which is exactly what an independent check is for.
"""
import json, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model.px4_failsafe import DEFAULTS, configured_action  # noqa: E402


class ExpectedTimelineTests(unittest.TestCase):
    def setUp(self):
        self.doc = json.loads((ROOT / "protocols/expected-timelines.json").read_text())
        self.matrix = json.loads((ROOT / "protocols/configuration-matrix.json").read_text())
        self.rows = {r["configuration_id"]: r for r in self.matrix["rows"]}
        self.timelines = {t["id"]: t for t in self.doc["timelines"]}

    def test_every_timeline_shows_its_arithmetic_and_parameters(self):
        for tid, t in self.timelines.items():
            self.assertTrue(t["hand_derivation"], tid)
            self.assertGreaterEqual(len(t["hand_derivation"]), 2, tid)
            self.assertTrue(t["parameters_used"], tid)
            self.assertIn(t["configuration_id"], self.rows, tid)

    def test_hand_derivation_agrees_with_the_code_transcription(self):
        """The independent check: the final action each timeline predicts must equal the action the parameter
        maps in model/px4_failsafe.py produce for that configuration and event."""
        for tid, t in self.timelines.items():
            if t["event"] == "none":
                self.assertEqual(t["expected_actions"], [], tid)
                continue
            row = self.rows[t["configuration_id"]]
            params = dict(DEFAULTS, **row["deltas_from_defaults"])
            from_code = configured_action(t["event"], params)
            final_by_hand = t["expected_actions"][-1]["action"]
            self.assertEqual(final_by_hand, from_code, f"{tid}: hand says {final_by_hand}, code says {from_code}")
            self.assertEqual(from_code, row["realised_action_per_class"][t["event"]], tid)

    def test_parameters_used_match_the_matrix_row(self):
        for tid, t in self.timelines.items():
            row = self.rows[t["configuration_id"]]
            effective = {**self.matrix["common_params"], **row["deltas_from_defaults"], **DEFAULTS}
            effective.update({**self.matrix["common_params"], **row["deltas_from_defaults"]})
            for name, value in t["parameters_used"].items():
                self.assertEqual(float(effective.get(name, DEFAULTS.get(name))), float(value), (tid, name))

    def test_the_two_development_cases_differ_by_exactly_one_factor(self):
        t1, t2 = self.timelines["T1"], self.timelines["T2"]
        self.assertEqual(t2["one_factor_change_from"], "T1")
        differing = {k for k in set(t1["parameters_used"]) | set(t2["parameters_used"])
                     if t1["parameters_used"].get(k) != t2["parameters_used"].get(k)}
        self.assertEqual(differing, {"COM_FAIL_ACT_T"})
        self.assertNotEqual(t1["expected_mode_sequence"], t2["expected_mode_sequence"])

    def test_tolerance_is_frozen_relative_to_injection(self):
        tol = self.doc["tolerance"]
        self.assertGreater(tol["value_s"], 0)
        self.assertIn("relative to the injection", tol["applies_to"])
        self.assertIn("jitter", tol["basis"])


if __name__ == "__main__":
    unittest.main()
