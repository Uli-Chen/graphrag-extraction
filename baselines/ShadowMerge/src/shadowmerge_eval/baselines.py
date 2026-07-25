from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Type

from .models import DatasetCase, MemoryRecord, Relation


@dataclass(frozen=True)
class BaselineAdapter:
    name: str

    def build_poison_write(self, case: DatasetCase) -> MemoryRecord:
        raise NotImplementedError

    def _record(self, case: DatasetCase, relation: Relation, content: str) -> MemoryRecord:
        return MemoryRecord(
            record_id=f"{case.case_id}:{self.name}:poison",
            relation=relation,
            content=content,
            kind="poison",
            case_id=case.case_id,
            dataset=case.dataset,
            metadata={
                "baseline": self.name,
                "phase": "evaluation_poison",
                "target_entity": case.target_entity,
            },
        )


class ShadowMergeAdapter(BaselineAdapter):
    def __init__(self) -> None:
        super().__init__(name="shadowmerge")

    def build_poison_write(self, case: DatasetCase) -> MemoryRecord:
        content = (
            "Graph-memory write for evaluation. "
            f"{case.poison_relation.source} {case.poison_relation.relation} "
            f"{case.poison_relation.target}."
        )
        return self._record(case, case.poison_relation, content)


class NaiveTextPoisoningAdapter(BaselineAdapter):
    def __init__(self) -> None:
        super().__init__(name="naive_text_poisoning")

    def build_poison_write(self, case: DatasetCase) -> MemoryRecord:
        relation = Relation(
            source=case.target_entity,
            relation="mentions",
            target=case.expected_malicious_answer,
        )
        content = (
            "Text-memory write for evaluation. "
            f"{case.target_entity}: {case.expected_malicious_answer}."
        )
        return self._record(case, relation, content)


class MinjaAdaptAdapter(BaselineAdapter):
    def __init__(self) -> None:
        super().__init__(name="minja_adapt")

    def build_poison_write(self, case: DatasetCase) -> MemoryRecord:
        hint = str(case.baseline_hints.get("query_surface") or case.victim_query)
        relation = Relation(
            source=case.target_entity,
            relation="query_aligned_answer",
            target=case.expected_malicious_answer,
        )
        content = (
            "MINJA-adapt write for ordinary interaction evaluation. "
            f"Query surface: {hint}. Candidate answer: {case.expected_malicious_answer}."
        )
        return self._record(case, relation, content)


class GragPoisonAdaptAdapter(BaselineAdapter):
    def __init__(self) -> None:
        super().__init__(name="gragpoison_adapt")

    def build_poison_write(self, case: DatasetCase) -> MemoryRecord:
        support = str(case.baseline_hints.get("support_node") or "support_node")
        relation = Relation(
            source=case.target_entity,
            relation=case.poison_relation.relation,
            target=case.poison_relation.target,
        )
        content = (
            "GRAGPoison-adapt graph write for evaluation. "
            f"Support node: {support}. Relation: {relation.source} "
            f"{relation.relation} {relation.target}."
        )
        return self._record(case, relation, content)


ADAPTERS: Dict[str, Type[BaselineAdapter]] = {
    "shadowmerge": ShadowMergeAdapter,
    "naive_text_poisoning": NaiveTextPoisoningAdapter,
    "minja_adapt": MinjaAdaptAdapter,
    "gragpoison_adapt": GragPoisonAdaptAdapter,
}


def create_adapter(name: str) -> BaselineAdapter:
    normalized = str(name or "shadowmerge").strip().lower()
    if normalized not in ADAPTERS:
        available = ", ".join(sorted(ADAPTERS))
        raise ValueError(f"Unknown baseline '{name}'. Available baselines: {available}")
    return ADAPTERS[normalized]()
