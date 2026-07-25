from __future__ import annotations

from typing import Any, Dict, Iterable, List

from .metrics import bool_rate, mean_optional


def parse_graph_gate_event(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "case_id": str(payload.get("case_id") or ""),
        "materialized": bool(payload.get("materialized")),
        "merged": bool(payload.get("merged")),
        "retrieved": bool(payload.get("retrieved")),
        "rank": payload.get("rank") if payload.get("rank") is not None else None,
        "gate_passed": bool(payload.get("gate_passed")),
    }


def summarize_graph_gate_events(events: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    parsed: List[Dict[str, Any]] = [parse_graph_gate_event(event) for event in events]
    return {
        "event_count": len(parsed),
        "materialized_rate": bool_rate(event["materialized"] for event in parsed),
        "merge_rate": bool_rate(event["merged"] for event in parsed),
        "retrieval_rate": bool_rate(event["retrieved"] for event in parsed),
        "gate_pass_rate": bool_rate(event["gate_passed"] for event in parsed),
        "mean_rank": mean_optional(event["rank"] for event in parsed),
    }

