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

    def test_research_dependency_graph_has_no_dangling_endpoints(self) -> None:
        graph = json.loads(
            (ROOT / "docs/research-dependency-graph.json").read_text(encoding="utf-8")
        )
        node_ids = {node["id"] for node in graph["nodes"]}
        self.assertTrue(graph["directed"])
        self.assertEqual(graph["token_usage"]["status"], "unavailable")
        self.assertIsNone(graph["token_usage"]["input_tokens"])
        self.assertIsNone(graph["token_usage"]["output_tokens"])
        for edge in graph["edges"]:
            self.assertIn(edge["source"], node_ids)
            self.assertIn(edge["target"], node_ids)


if __name__ == "__main__":
    unittest.main()
