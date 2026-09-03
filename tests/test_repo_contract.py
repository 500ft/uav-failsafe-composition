from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RepositoryContractTests(unittest.TestCase):
    def test_contract_script_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(ROOT / "scripts/check_repo_contract.py")],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def test_example_is_unambiguously_not_a_result(self) -> None:
        example = json.loads(
            (ROOT / "protocols/example-configuration-manifest.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(example["evidence_state"], "planned-example")
        self.assertIn("not-executed", example["run_id"])


if __name__ == "__main__":
    unittest.main()
