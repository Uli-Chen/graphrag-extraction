from __future__ import annotations

import sys
import unittest
from pathlib import Path


ARTIFACT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ARTIFACT_ROOT / "src"))

from shadowmerge_eval.metrics import bool_rate, compute_rates, graph_diagnostics
from shadowmerge_eval.models import CaseEvaluation, MemoryRecord, Relation


class MetricTests(unittest.TestCase):
    def test_bool_rate_handles_empty_and_non_empty_inputs(self) -> None:
        self.assertEqual(bool_rate([]), 0.0)
        self.assertEqual(bool_rate([True, False, True]), 0.6667)

    def test_compute_rates_summarizes_case_results(self) -> None:
        cases = [
            CaseEvaluation("c1", "sample", "shadowmerge", True, True, True, True, True, 1, 2, {}),
            CaseEvaluation("c2", "sample", "shadowmerge", False, True, True, False, False, None, 1, {}),
        ]
        summary = compute_rates(cases)
        self.assertEqual(summary["num_cases"], 2)
        self.assertEqual(summary["asr"], 0.5)
        self.assertEqual(summary["utility"], 1.0)
        self.assertEqual(summary["materialization_rate"], 1.0)
        self.assertEqual(summary["merge_rate"], 0.5)
        self.assertEqual(summary["retrieval_rate"], 0.5)
        self.assertEqual(summary["mean_poison_rank"], 1.0)

    def test_graph_diagnostics_counts_relation_structure(self) -> None:
        records = [
            MemoryRecord("r1", Relation("alpha", "answers", "yes"), "alpha answers yes", "benign", "c1", "sample"),
            MemoryRecord("r2", Relation("alpha", "answers", "no"), "alpha answers no", "poison", "c1", "sample"),
        ]
        diagnostics = graph_diagnostics(records)
        self.assertEqual(diagnostics["node_count"], 3)
        self.assertEqual(diagnostics["edge_count"], 2)
        self.assertEqual(diagnostics["relation_type_count"], 1)
        self.assertEqual(diagnostics["connected_component_count"], 1)


if __name__ == "__main__":
    unittest.main()
