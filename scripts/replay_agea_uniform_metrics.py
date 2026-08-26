#!/usr/bin/env python3
"""Replay AGEA responses and score every turn with MEMATK's unified evaluator."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path
from typing import Any

import networkx as nx

from evaluation.graph_recovery import TruthData, aggregate_trajectory, evaluate_recovery
from graph_extractor_memory import GraphExtractorMemory
from utils import parse_llm_response_for_graph_items


RESPONSE_MARKER = "Full GraphRAG Response (including retrieved context):\n"
STDERR_MARKER = "\n" + "=" * 80 + "\nFull stderr:\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agea-dir", type=Path, required=True)
    parser.add_argument("--truth-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def turn_number(path: Path) -> int:
    match = re.search(r"(\d+)$", path.stem)
    if not match:
        raise ValueError(f"Cannot derive turn number from {path}")
    return int(match.group(1))


def response_text(path: Path) -> str:
    artifact = path.read_text(encoding="utf-8")
    if RESPONSE_MARKER not in artifact:
        raise ValueError(f"Response marker missing from {path}")
    response = artifact.split(RESPONSE_MARKER, 1)[1]
    return response.split(STDERR_MARKER, 1)[0]


def edge_signatures(graph: nx.MultiDiGraph) -> set[tuple[str, str, str]]:
    return {
        (
            str(source),
            str(target),
            str(attributes.get("rel", attributes.get("relation", "related_to"))),
        )
        for source, target, attributes in graph.edges(data=True)
    }


def main() -> None:
    args = parse_args()
    agea_dir = args.agea_dir.resolve()
    history = json.loads((agea_dir / "query_history.json").read_text(encoding="utf-8"))
    response_paths = sorted(
        (agea_dir / "turn_logs" / "llm_response").glob("first_llm_response_query_*.txt"),
        key=turn_number,
    )
    if len(response_paths) != len(history):
        raise ValueError(
            f"Response/history mismatch: responses={len(response_paths)}, history={len(history)}"
        )

    truth = TruthData.load(args.truth_dir)
    with tempfile.TemporaryDirectory(prefix="mematk-agea-replay-") as temporary:
        memory = GraphExtractorMemory(
            str(Path(temporary) / "replay.graphml"),
            str(Path(temporary) / "replay.json"),
        )
        turn_metrics: list[dict[str, Any]] = []
        replay_checks: list[dict[str, Any]] = []
        for expected_turn, (record, path) in enumerate(
            zip(history, response_paths, strict=True), start=1
        ):
            actual_turn = int(record.get("turn", -1))
            if actual_turn != expected_turn or turn_number(path) != expected_turn:
                raise ValueError(
                    f"Turn ordering mismatch at {expected_turn}: history={actual_turn}, file={path}"
                )
            nodes, edges = parse_llm_response_for_graph_items(
                response_text(path),
                normalize_and_dedupe=True,
            )
            added_nodes, added_edges, _ = memory.merge_turn_subgraph(nodes, edges)
            expected_nodes = int(record.get("total_nodes_in_graph", -1))
            expected_edges = int(record.get("total_edges_in_graph", -1))
            actual_nodes = memory.G.number_of_nodes()
            actual_edges = memory.G.number_of_edges()
            check = {
                "turn": expected_turn,
                "expected_nodes": expected_nodes,
                "actual_nodes": actual_nodes,
                "expected_edges": expected_edges,
                "actual_edges": actual_edges,
                "reported_added_nodes": int(record.get("nodes_added_to_graph", -1)),
                "replayed_added_nodes": added_nodes,
                "reported_added_edges": int(record.get("edges_added_to_graph", -1)),
                "replayed_added_edges": added_edges,
            }
            check["passed"] = (
                actual_nodes == expected_nodes
                and actual_edges == expected_edges
                and added_nodes == check["reported_added_nodes"]
                and added_edges == check["reported_added_edges"]
            )
            replay_checks.append(check)
            turn_metrics.append(evaluate_recovery(memory.G, truth))

        stored_data = json.loads((agea_dir / "extracted_graph.json").read_text(encoding="utf-8"))
        stored_graph = nx.node_link_graph(stored_data)
        exact_nodes = set(memory.G.nodes) == set(stored_graph.nodes)
        exact_edges = edge_signatures(memory.G) == edge_signatures(stored_graph)
        failed_turns = [check["turn"] for check in replay_checks if not check["passed"]]
        result = {
            "complete": not failed_turns and exact_nodes and exact_edges,
            "turns": len(turn_metrics),
            "failed_replay_turns": failed_turns,
            "stored_graph_exact_node_match": exact_nodes,
            "stored_graph_exact_edge_match": exact_edges,
            "final": turn_metrics[-1] if turn_metrics else {},
            "trajectory": aggregate_trajectory(turn_metrics),
            "turn_metrics": turn_metrics,
            "replay_checks": replay_checks,
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({key: value for key, value in result.items() if key not in {"turn_metrics", "replay_checks"}}, ensure_ascii=False, indent=2))
    if not result["complete"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
