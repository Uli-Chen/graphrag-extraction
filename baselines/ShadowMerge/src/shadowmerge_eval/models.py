from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class Relation:
    source: str
    relation: str
    target: str

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "Relation":
        return cls(
            source=str(payload.get("source") or ""),
            relation=str(payload.get("relation") or ""),
            target=str(payload.get("target") or ""),
        )

    def as_dict(self) -> Dict[str, str]:
        return {
            "source": self.source,
            "relation": self.relation,
            "target": self.target,
        }


@dataclass(frozen=True)
class DatasetCase:
    case_id: str
    dataset: str
    target_entity: str
    benign_relation: Relation
    poison_relation: Relation
    benign_query: str
    victim_query: str
    expected_benign_answer: str
    expected_malicious_answer: str
    baseline_hints: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "DatasetCase":
        return cls(
            case_id=str(payload["case_id"]),
            dataset=str(payload["dataset"]),
            target_entity=str(payload["target_entity"]),
            benign_relation=Relation.from_dict(dict(payload["benign_relation"])),
            poison_relation=Relation.from_dict(dict(payload["poison_relation"])),
            benign_query=str(payload["benign_query"]),
            victim_query=str(payload["victim_query"]),
            expected_benign_answer=str(payload["expected_benign_answer"]),
            expected_malicious_answer=str(payload["expected_malicious_answer"]),
            baseline_hints=dict(payload.get("baseline_hints") or {}),
        )


@dataclass
class MemoryRecord:
    record_id: str
    relation: Relation
    content: str
    kind: str
    case_id: str
    dataset: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    score: Optional[float] = None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "record_id": self.record_id,
            "source": self.relation.source,
            "relationship": self.relation.relation,
            "target": self.relation.target,
            "content": self.content,
            "kind": self.kind,
            "case_id": self.case_id,
            "dataset": self.dataset,
            "metadata": dict(self.metadata),
            "score": self.score,
        }


@dataclass(frozen=True)
class CaseEvaluation:
    case_id: str
    dataset: str
    baseline: str
    attack_success: bool
    utility_success: bool
    materialized: bool
    merged: bool
    poison_retrieved: bool
    poison_rank: Optional[int]
    retrieved_count: int
    diagnostics: Dict[str, Any]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "case_id": self.case_id,
            "dataset": self.dataset,
            "baseline": self.baseline,
            "attack_success": self.attack_success,
            "utility_success": self.utility_success,
            "materialized": self.materialized,
            "merged": self.merged,
            "poison_retrieved": self.poison_retrieved,
            "poison_rank": self.poison_rank,
            "retrieved_count": self.retrieved_count,
            "diagnostics": dict(self.diagnostics),
        }


@dataclass(frozen=True)
class EvaluationResult:
    summary: Dict[str, Any]
    cases: List[CaseEvaluation]
    graph_diagnostics: Dict[str, Any]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "summary": dict(self.summary),
            "cases": [case.as_dict() for case in self.cases],
            "graph_diagnostics": dict(self.graph_diagnostics),
        }
