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

    CONTRACT_FIELDS = ("natural_language", "source", "required_channels", "witness_format", "known_limitations",
                       "excludes", "requirement_source", "antecedent", "allowed_outputs", "deadline_origin",
                       "deadline", "deadline_status", "persistence", "exceptions", "observables",
                       "inconclusive_rule", "antecedent_reachability_query", "observer", "model_boundary",
                       "executability")
    WORKED_EXAMPLES = ("example_satisfying", "example_violating", "example_inconclusive",
                       "example_not_triggered", "example_disabled_action")

    def test_every_property_is_source_linked_and_carries_its_full_contract(self):
        self.assertIn("Amended 2026-09-25", self.p["status"])
        for pid, prop in self.props.items():
            for field in self.CONTRACT_FIELDS + self.WORKED_EXAMPLES:
                self.assertTrue(prop.get(field), (pid, field))
            self.assertTrue(all(e.startswith("X") for e in prop["excludes"]), pid)

    def test_an_unbounded_deadline_is_labelled_not_invented(self):
        """A residual this apparatus cannot bound is named, never filled with a number (WP2)."""
        for pid, prop in self.props.items():
            self.assertIn(prop["deadline_status"],
                          ("source_derived", "study_parameter", "not_yet_evaluable"), pid)
            if prop["deadline_status"] == "not_yet_evaluable":
                self.assertTrue(prop.get("deadline_note"), pid)

    def test_u4_no_longer_deadlines_on_a_speed_quotient(self):
        """Distance over a MAXIMUM speed is the least time a manoeuvre can take, so it is a lower bound."""
        u4 = self.props["U4"]
        self.assertNotIn("expected_manoeuvre_time", u4)
        self.assertNotIn("terminal_modes", u4, "a generic terminal list let the pre-injection mode satisfy RTL")
        self.assertIn("lower bound", u4["model_boundary"])

    def test_every_in_scope_obligation_has_a_query_or_a_declared_gap(self):
        mapped = {q["property"] for q in self.p["query_map"].values() if isinstance(q, dict) and q.get("property")}
        self.assertEqual(mapped, set(self.props), "U3 previously had no query at all")

    def test_the_two_verdict_vocabularies_are_kept_apart(self):
        v = self.p["verdict_vocabularies"]
        self.assertEqual(set(v["per_run_observation"]) - {"must_carry"},
                         {"satisfied", "violated", "inconclusive", "unverified", "not_applicable"})
        self.assertIn("established_over_the_abstract_model", v["study_or_checker_claim"])

    def test_exclusions_resolve(self):
        known = {x["id"] for x in self.p["shared_exclusions"]}
        for pid, prop in self.props.items():
            self.assertEqual(set(prop["excludes"]) - known, set(), pid)
        for x in self.p["shared_exclusions"]:
            self.assertTrue(x["rule"] and x["source"], x["id"])

    def test_precedence_matches_the_model(self):
        self.assertEqual(tuple(self.props["U2"]["precedence"]), ACTIONS)

    def test_the_shared_delay_correction_survives(self):
        """One shared delay pot, never a per-hazard sum."""
        self.assertIn("not a per-hazard sum", self.props["U2"]["deadline"])
        self.assertIn("NOT the sum", self.props["U4"]["correction_note"])

    def test_terminal_modes_are_not_called_safe(self):
        blob = json.dumps(self.p).lower()
        self.assertNotIn("safe state", blob)
        self.assertNotIn("proven", blob)


if __name__ == "__main__":
    unittest.main()
