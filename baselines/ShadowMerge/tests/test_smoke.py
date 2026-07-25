from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ARTIFACT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ARTIFACT_ROOT / "src"))

from shadowmerge_eval.harness import run_evaluation


class SmokeHarnessTests(unittest.TestCase):
    def test_evaluation_completes_with_mock_backend(self) -> None:
        config_path = ARTIFACT_ROOT / "configs" / "config.example.yaml"
        with tempfile.TemporaryDirectory() as tmpdir:
            result = run_evaluation(config_path, root=ARTIFACT_ROOT, output_dir=Path(tmpdir), mock=True)
            self.assertGreaterEqual(result.summary["num_cases"], 3)
            self.assertEqual(result.summary["materialization_rate"], 1.0)
            self.assertEqual(result.summary["retrieval_rate"], 1.0)
            self.assertIn("graph_gate", result.graph_diagnostics)
            self.assertTrue((Path(tmpdir) / "summary.json").exists())
            self.assertTrue((Path(tmpdir) / "case_results.jsonl").exists())


if __name__ == "__main__":
    unittest.main()
