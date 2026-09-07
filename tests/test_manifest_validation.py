"""Regression cases derived from the declared manifest schema, not study evidence."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("repo_contract_under_test", ROOT / "scripts/check_repo_contract.py")
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)
EXAMPLE = ROOT / "protocols/example-configuration-manifest.json"


class ManifestValidationTests(unittest.TestCase):
    def errors_for(self, example):
        original_read = Path.read_text
        def read(path, *args, **kwargs):
            if path.resolve() == EXAMPLE:
                return json.dumps(example)
            return original_read(path, *args, **kwargs)
        with patch.object(Path, "read_text", read):
            return checker.run_checks()

    def test_declared_example_remains_valid(self):
        self.assertEqual(self.errors_for(json.loads(EXAMPLE.read_text())), [])

    def test_schema_rejects_invalid_nested_values(self):
        original = json.loads(EXAMPLE.read_text())
        cases = [[["autopilot"],"NOT_AN_AUTOPILOT"],[["initial_condition","battery_fraction"],2],[["recording","sample_rate_hz"],-1],[["authority_loss_event","scheduled_time_s"],-0.1],[["test_environment","seed"],"seed"],[["initial_condition","horizontal_speed_mps"],True],[["recording","sample_rate_hz"],"NaN"],[["recording","sample_rate_hz"],"Infinity"]]
        for keys, value in cases:
            if value == "NaN":
                value = float("nan")
            elif value == "Infinity":
                value = float("inf")
            with self.subTest(field=keys, value=value):
                example = copy.deepcopy(original)
                parent = example
                for key in keys[:-1]:
                    parent = parent[key]
                parent[keys[-1]] = value
                self.assertTrue(self.errors_for(example), "invalid manifest was admitted")

    def test_nested_required_field_is_enforced(self):
        example = json.loads(EXAMPLE.read_text())
        del example["recording"]["log_path"]
        self.assertTrue(self.errors_for(example))

    def test_unknown_top_level_field_is_rejected(self):
        example = json.loads(EXAMPLE.read_text())
        example["invented_measurement"] = 10
        self.assertTrue(self.errors_for(example))


if __name__ == "__main__":
    unittest.main()
