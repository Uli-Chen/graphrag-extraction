from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import yaml

from .baselines import create_adapter
from .datasets import load_cases, resolve_dataset_paths
from .diagnostics import summarize_graph_gate_events
from .metrics import (
    compute_rates,
    graph_diagnostics,
    graph_gate_case_diagnostics,
    is_merged,
    is_materialized,
    poison_retrieval_hit,
)
from .mock_memory import MockGraphMemory, first_poison_rank
from .models import CaseEvaluation, DatasetCase, EvaluationResult, MemoryRecord


def load_config(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}
    if not isinstance(loaded, dict):
        raise ValueError(f"Configuration must be a mapping: {path}")
    return loaded


class EvaluationHarness:
    def __init__(self, config: Dict[str, Any], *, root: Path, mock: bool = True) -> None:
        self.config = config
        self.root = root
        self.mock = bool(mock)
        memory_config = dict(config.get("memory") or {})
        if memory_config.get("backend") != "mock_graph_memory":
            raise ValueError("This evaluation package uses mock_graph_memory by default.")
        self.top_k = int(memory_config.get("retrieval_top_k", 10))
        evaluation_config = dict(config.get("evaluation") or {})
        self.seed = int(evaluation_config.get("seed", 42))
        self.num_background_writes = int(evaluation_config.get("num_background_writes", 2))
        self.baseline = str(evaluation_config.get("baseline") or "shadowmerge")
        self.memory = MockGraphMemory()

    def load_dataset_cases(self) -> List[DatasetCase]:
        evaluation_config = dict(self.config.get("evaluation") or {})
        dataset_values = list(evaluation_config.get("datasets") or [])
        paths = resolve_dataset_paths(self.root, dataset_values)
        return load_cases(paths)

    def run(self, *, output_dir: Optional[Path] = None) -> EvaluationResult:
        random.seed(self.seed)
        cases = self.load_dataset_cases()
        adapter = create_adapter(self.baseline)
        evaluations: List[CaseEvaluation] = []
        gate_events: List[Dict[str, Any]] = []

        for index, case in enumerate(cases):
            for background_case in self._background_cases(cases, index):
                self.memory.write_benign_anchor(background_case)

            self.memory.write_benign_anchor(case)
            benign_retrieved = self.memory.retrieve(case.benign_query, top_k=self.top_k, case_id=case.case_id)
            utility_success = self._mock_utility_success(case, benign_retrieved)

            poison_record = adapter.build_poison_write(case)
            self.memory.write(poison_record)
            victim_retrieved = self.memory.retrieve(case.victim_query, top_k=self.top_k, case_id=case.case_id)

            records = self.memory.records
            poison_rank = first_poison_rank(victim_retrieved, case_id=case.case_id)
            materialized = is_materialized(records, poison_record.relation, case_id=case.case_id)
            merged = is_merged(records, case)
            retrieved_hit = poison_retrieval_hit(victim_retrieved, case_id=case.case_id)
            attack_success = bool(materialized and merged and retrieved_hit)
            gate = graph_gate_case_diagnostics(
                case=case,
                records=records,
                retrieved=victim_retrieved,
                poison_relation=poison_record.relation,
            )
            gate_events.append({"case_id": case.case_id, **gate})

            evaluations.append(
                CaseEvaluation(
                    case_id=case.case_id,
                    dataset=case.dataset,
                    baseline=adapter.name,
                    attack_success=attack_success,
                    utility_success=utility_success,
                    materialized=materialized,
                    merged=merged,
                    poison_retrieved=retrieved_hit,
                    poison_rank=poison_rank,
                    retrieved_count=len(victim_retrieved),
                    diagnostics={
                        **gate,
                        "victim_retrieved": [record.as_dict() for record in victim_retrieved],
                    },
                )
            )

        graph_summary = {
            **graph_diagnostics(self.memory.records),
            "graph_gate": summarize_graph_gate_events(gate_events),
        }
        result = EvaluationResult(
            summary=compute_rates(evaluations),
            cases=evaluations,
            graph_diagnostics=graph_summary,
        )
        if output_dir is not None:
            write_outputs(result, output_dir)
        return result

    def _background_cases(self, cases: Sequence[DatasetCase], current_index: int) -> List[DatasetCase]:
        candidates = [case for index, case in enumerate(cases) if index != current_index]
        return candidates[: max(self.num_background_writes, 0)]

    def _mock_utility_success(self, case: DatasetCase, retrieved: Sequence[MemoryRecord]) -> bool:
        for record in retrieved:
            if record.case_id == case.case_id and record.kind == "benign":
                return record.relation.target == case.expected_benign_answer
        return False


def write_outputs(result: EvaluationResult, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / "summary.json"
    cases_path = output_dir / "case_results.jsonl"
    with summary_path.open("w", encoding="utf-8") as handle:
        json.dump(
            {
                "summary": result.summary,
                "graph_diagnostics": result.graph_diagnostics,
            },
            handle,
            indent=2,
            sort_keys=True,
        )
        handle.write("\n")
    with cases_path.open("w", encoding="utf-8") as handle:
        for case in result.cases:
            handle.write(json.dumps(case.as_dict(), sort_keys=True) + "\n")


def run_evaluation(config_path: Path, *, root: Path, output_dir: Optional[Path] = None, mock: bool = True) -> EvaluationResult:
    config = load_config(config_path)
    harness = EvaluationHarness(config, root=root, mock=mock)
    if output_dir is None:
        evaluation_config = dict(config.get("evaluation") or {})
        configured_output = evaluation_config.get("output_dir")
        if configured_output:
            output_dir = Path(str(configured_output))
            if not output_dir.is_absolute():
                output_dir = root / output_dir
    return harness.run(output_dir=output_dir)
