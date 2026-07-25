from __future__ import annotations

import re
from collections import Counter
from typing import Any, Dict, Iterable, List, Optional

from .models import DatasetCase, MemoryRecord, Relation


def normalize_text(value: Any) -> str:
    return " ".join(str(value or "").casefold().split())


def split_terms(value: Any) -> List[str]:
    return re.findall(r"[a-z0-9]+", normalize_text(value))


def relation_text(record: MemoryRecord) -> str:
    return " ".join(
        [
            record.relation.source,
            record.relation.relation,
            record.relation.target,
            record.content,
        ]
    )


class MockGraphMemory:
    def __init__(self) -> None:
        self._records: List[MemoryRecord] = []

    @property
    def records(self) -> List[MemoryRecord]:
        return list(self._records)

    def write(self, record: MemoryRecord) -> MemoryRecord:
        self._records.append(record)
        return record

    def write_benign_anchor(self, case: DatasetCase) -> MemoryRecord:
        record = MemoryRecord(
            record_id=f"{case.case_id}:anchor",
            relation=case.benign_relation,
            content=(
                "Benign graph-memory anchor. "
                f"{case.benign_relation.source} {case.benign_relation.relation} "
                f"{case.benign_relation.target}."
            ),
            kind="benign",
            case_id=case.case_id,
            dataset=case.dataset,
            metadata={
                "phase": "evaluation_anchor",
                "target_entity": case.target_entity,
            },
        )
        return self.write(record)

    def retrieve(self, query: str, *, top_k: int = 10, case_id: Optional[str] = None) -> List[MemoryRecord]:
        query_terms = Counter(split_terms(query))
        ranked: List[MemoryRecord] = []
        for index, record in enumerate(self._records):
            record_terms = Counter(split_terms(relation_text(record)))
            overlap = sum(min(query_terms[term], record_terms[term]) for term in query_terms)
            case_bonus = 0.25 if case_id and record.case_id == case_id else 0.0
            kind_bonus = 0.05 if record.kind == "poison" else 0.0
            score = float(overlap) + case_bonus + kind_bonus
            if score <= 0:
                continue
            ranked_record = MemoryRecord(
                record_id=record.record_id,
                relation=record.relation,
                content=record.content,
                kind=record.kind,
                case_id=record.case_id,
                dataset=record.dataset,
                metadata=dict(record.metadata),
                score=round(score, 6),
            )
            ranked.append(ranked_record)
        ranked.sort(key=lambda item: (-(item.score or 0.0), item.kind != "poison", item.record_id))
        return ranked[: max(int(top_k), 0)]

    def snapshot(self) -> Dict[str, Any]:
        return {
            "records": [record.as_dict() for record in self._records],
            "relations": [
                {
                    "source": record.relation.source,
                    "relationship": record.relation.relation,
                    "target": record.relation.target,
                    "kind": record.kind,
                    "case_id": record.case_id,
                    "dataset": record.dataset,
                    "metadata": dict(record.metadata),
                }
                for record in self._records
            ],
        }

    def has_relation(self, relation: Relation, *, kind: Optional[str] = None, case_id: Optional[str] = None) -> bool:
        for record in self._records:
            if kind and record.kind != kind:
                continue
            if case_id and record.case_id != case_id:
                continue
            if relations_match(record.relation, relation):
                return True
        return False


def relations_match(left: Relation, right: Relation) -> bool:
    return (
        normalize_text(left.source) == normalize_text(right.source)
        and normalize_text(left.relation) == normalize_text(right.relation)
        and normalize_text(left.target) == normalize_text(right.target)
    )


def relation_channel_match(left: Relation, right: Relation) -> bool:
    return (
        normalize_text(left.source) == normalize_text(right.source)
        and normalize_text(left.relation) == normalize_text(right.relation)
    )


def first_poison_rank(records: Iterable[MemoryRecord], *, case_id: str) -> Optional[int]:
    for index, record in enumerate(records, start=1):
        if record.kind == "poison" and record.case_id == case_id:
            return index
    return None
