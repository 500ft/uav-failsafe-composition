"""URC-03: the trace schema admits the valid fixture and rejects each invalid variant."""
import copy, json, unittest
from pathlib import Path
from jsonschema.validators import validator_for

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "protocols/trace-schema.json").read_text())
VALID = json.loads((ROOT / "protocols/fixtures/trace-valid.json").read_text())
V = validator_for(SCHEMA); V.check_schema(SCHEMA); VALIDATOR = V(SCHEMA)


def errors(instance):
    return [e.message for e in VALIDATOR.iter_errors(instance)]


class TraceSchemaTests(unittest.TestCase):
    def test_valid_fixture_is_admitted(self):
        self.assertEqual(errors(VALID), [])

    def test_invalid_variants_are_rejected(self):
        variants = {
            "unknown event name": (["events", 0, "name"], "lost_the_plot"),
            "injection class outside vocabulary": (["manifest", "injection", "class"], "gremlin"),
            "firmware commit not a full sha": (["manifest", "firmware_commit"], "d6f12ad"),
            "evidence state claims measurement": (["manifest", "evidence_state"], "measured"),
            "negative vehicle time": (["samples", 0, "t_vehicle_s"], -1.0),
            "battery fraction above one": (["samples", 0, "battery_remaining"], 1.5),
            "validity reason outside vocabulary": (["validity", "reasons"], ["bad_vibes"]),
            "position with two components": (["samples", 0, "pos_ned_m"], [1.0, 2.0]),
        }
        for label, (path, value) in variants.items():
            with self.subTest(label):
                inst = copy.deepcopy(VALID); parent = inst
                for key in path[:-1]:
                    parent = parent[key]
                parent[path[-1]] = value
                self.assertTrue(errors(inst), label)

    def test_missing_required_block_is_rejected(self):
        for block in ("manifest", "clock", "events", "samples", "validity"):
            with self.subTest(block):
                inst = copy.deepcopy(VALID); del inst[block]
                self.assertTrue(errors(inst))

    def test_unknown_top_level_field_is_rejected(self):
        inst = copy.deepcopy(VALID); inst["result"] = "safe"
        self.assertTrue(errors(inst))


if __name__ == "__main__":
    unittest.main()
