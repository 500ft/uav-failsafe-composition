"""URC-02: matrix rows are reproducible from the model tables and their hashes; the example manifest still validates."""
import hashlib, json, subprocess, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model.px4_failsafe import configured_action, DEFAULTS, ACTIONS  # noqa: E402


class ConfigurationMatrixTests(unittest.TestCase):
    def setUp(self):
        self.m = json.loads((ROOT / "protocols/configuration-matrix.json").read_text())

    def test_model_self_check_runs(self):
        self.assertEqual(subprocess.run([sys.executable, str(ROOT / "model/px4_failsafe.py")], capture_output=True, text=True).returncode, 0)

    def test_realised_actions_and_hashes_reproduce(self):
        for r in self.m["rows"]:
            params = dict(DEFAULTS, **r["deltas_from_defaults"])
            for cls, action in r["realised_action_per_class"].items():
                self.assertEqual(configured_action(cls, params), action, (r["configuration_id"], cls))
                self.assertIn(action, ACTIONS)
            full = dict(sorted({**self.m["common_params"], **params}.items()))
            self.assertEqual(hashlib.sha256(json.dumps(full, sort_keys=True).encode()).hexdigest(), r["parameters_sha256"], r["configuration_id"])

    def test_intention_rows_realise_their_intention_on_supported_classes(self):
        for r in self.m["rows"]:
            if r["intention"] == "vendor_defaults":
                continue
            for cls, action in r["realised_action_per_class"].items():
                if cls not in r["unsupported_for_intention"]:
                    self.assertEqual(action, r["intention"], (r["configuration_id"], cls))

    def test_identity_is_pinned(self):
        self.assertRegex(self.m["firmware"]["commit"], r"^[0-9a-f]{40}$")
        self.assertTrue(self.m["vehicle"]["lockstep"])
        self.assertEqual(self.m["common_params"]["SYS_FAILURE_EN"], 1)
        ids = [r["configuration_id"] for r in self.m["rows"]]
        self.assertEqual(len(ids), len(set(ids)))


if __name__ == "__main__":
    unittest.main()
