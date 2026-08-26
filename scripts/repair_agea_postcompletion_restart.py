#!/usr/bin/env python3
"""Repair AGEA runs that launchd restarted after their intended final turn.

The repair is deliberately conservative:

* retain the first ``--turns`` query-history records;
* identify post-completion nodes from the appended history;
* identify post-completion edges by combining per-turn add counts with intact
  response artifacts from the original run;
* restore the exact node/edge structure at the intended final turn;
* quarantine response artifacts overwritten by the accidental restart; and
* emit an auditable repair manifest.

A separate full backup must be supplied and is never modified by this script.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import networkx as nx

from utils import normalize_node_label, parse_llm_response_for_graph_items


RESPONSE_MARKER = "Full GraphRAG Response (including retrieved context):\n"
STDERR_MARKER = "\n" + "=" * 80 + "\nFull stderr:\n"
TURN_SUFFIX = re.compile(r"(\d+)(?=\.[^.]+$)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="append", type=Path, required=True)
    parser.add_argument("--backup-root", type=Path, required=True)
    parser.add_argument("--turns", type=int, default=1000)
    return parser.parse_args()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path, value: Any) -> None:
    temporary = path.with_suffix(path.suffix + ".repair-tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def atomic_graphml(path: Path, graph: nx.MultiDiGraph) -> None:
    temporary = path.with_suffix(path.suffix + ".repair-tmp")
    nx.write_graphml(graph, temporary)
    os.replace(temporary, path)


def response_text(path: Path) -> str:
    artifact = path.read_text(encoding="utf-8")
    if RESPONSE_MARKER not in artifact:
        raise ValueError(f"response marker missing: {path}")
    response = artifact.split(RESPONSE_MARKER, 1)[1]
    return response.split(STDERR_MARKER, 1)[0]


def edge_signature(edge: dict[str, Any]) -> tuple[str, str, str]:
    source = normalize_node_label(
        edge.get("source") or edge.get("src") or edge.get("s") or ""
    )
    target = normalize_node_label(
        edge.get("target") or edge.get("dst") or edge.get("t") or ""
    )
    relation = (
        edge.get("rel")
        or edge.get("relation")
        or edge.get("predicate")
        or edge.get("type")
        or edge.get("label")
        or "related_to"
    )
    return source, target, str(relation)


def graph_edge_signatures(graph: nx.MultiDiGraph) -> set[tuple[str, str, str]]:
    return {
        (
            str(source),
            str(target),
            str(attributes.get("rel", attributes.get("relation", "related_to"))),
        )
        for source, target, attributes in graph.edges(data=True)
    }


def parsed_edge_attributes(edge: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in edge.items()
        if key not in {"source", "target", "src", "dst"}
    }


def attributes_reflected(
    graph: nx.MultiDiGraph,
    signature: tuple[str, str, str],
    parsed: dict[str, Any],
) -> bool:
    source, target, relation = signature
    if source not in graph or not graph.has_edge(source, target):
        return False
    expected = parsed_edge_attributes(parsed)
    for attributes in graph[source][target].values():
        stored_relation = attributes.get("rel", attributes.get("relation", "related_to"))
        if str(stored_relation) != relation:
            continue
        if all(attributes.get(key) == value for key, value in expected.items()):
            return True
    return False


def remove_edge_signature(
    graph: nx.MultiDiGraph, signature: tuple[str, str, str]
) -> None:
    source, target, relation = signature
    matches = []
    if source in graph and graph.has_edge(source, target):
        for key, attributes in graph[source][target].items():
            stored_relation = attributes.get("rel", attributes.get("relation", "related_to"))
            if str(stored_relation) == relation:
                matches.append(key)
    if len(matches) != 1:
        raise ValueError(f"expected exactly one stored edge for {signature}, found {matches}")
    graph.remove_edge(source, target, matches[0])


def parse_turn(run_dir: Path, turn: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    path = (
        run_dir
        / "turn_logs"
        / "llm_response"
        / f"first_llm_response_query_{turn}.txt"
    )
    return parse_llm_response_for_graph_items(
        response_text(path), normalize_and_dedupe=True
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def quarantine_overwritten_artifacts(run_dir: Path, cutoff: int) -> dict[str, int]:
    quarantine = run_dir / "repair_quarantine" / "postcompletion_restart_artifacts"
    moved: dict[str, int] = {}
    for source_dir in sorted((run_dir / "turn_logs").iterdir()):
        if not source_dir.is_dir() or source_dir.name == "postcompletion_restart_artifacts":
            continue
        target_dir = quarantine / source_dir.name
        count = 0
        for path in sorted(source_dir.iterdir()):
            if not path.is_file():
                continue
            match = TURN_SUFFIX.search(path.name)
            if not match or int(match.group(1)) > cutoff:
                continue
            target_dir.mkdir(parents=True, exist_ok=True)
            target = target_dir / path.name
            if target.exists():
                raise FileExistsError(target)
            shutil.move(str(path), str(target))
            count += 1
        moved[source_dir.name] = count
    return moved


def repair_run(run_dir: Path, backup_root: Path, turns: int) -> dict[str, Any]:
    run_dir = run_dir.resolve()
    history_path = run_dir / "query_history.json"
    history = load_json(history_path)
    if len(history) <= turns:
        raise ValueError(f"{run_dir}: history has no appended records ({len(history)})")
    original_history = history[:turns]
    appended_history = history[turns:]
    cutoff = len(appended_history)
    appended_turns = [int(record.get("turn", -1)) for record in appended_history]
    if appended_turns != list(range(1, cutoff + 1)):
        raise ValueError(f"{run_dir}: appended turns are not 1..{cutoff}")

    backup_candidates = list(backup_root.glob(f"*{run_dir.name.split('seed')[-1].split('_')[0]}*"))
    if not backup_candidates:
        raise FileNotFoundError(f"no backup member found for {run_dir.name}")

    filtered = nx.node_link_graph(load_json(run_dir / "extracted_graph.json"), edges="links")
    raw = nx.node_link_graph(load_json(run_dir / "extracted_graph_raw.json"), edges="links")
    if set(filtered.nodes) != set(raw.nodes) or graph_edge_signatures(filtered) != graph_edge_signatures(raw):
        raise ValueError(f"{run_dir}: raw and filtered graphs differ despite disabled filtering")

    target_nodes = int(original_history[-1]["total_nodes_in_graph"])
    target_edges = int(original_history[-1]["total_edges_in_graph"])
    appended_nodes = {
        normalize_node_label(name)
        for record in appended_history
        for name in record.get("newly_discovered_entity_names", [])
    }
    reported_node_additions = sum(
        int(record.get("nodes_added_to_graph", 0)) for record in appended_history
    )
    reported_edge_additions = sum(
        int(record.get("edges_added_to_graph", 0)) for record in appended_history
    )
    if len(appended_nodes) != reported_node_additions:
        raise ValueError(
            f"{run_dir}: unique appended node names={len(appended_nodes)} "
            f"but reported additions={reported_node_additions}"
        )
    if filtered.number_of_nodes() != target_nodes + reported_node_additions:
        raise ValueError(f"{run_dir}: current/target node counts do not reconcile")
    if filtered.number_of_edges() != target_edges + reported_edge_additions:
        raise ValueError(f"{run_dir}: current/target edge counts do not reconcile")

    # Every response after the overwritten prefix belongs to the original run.
    # Any genuinely post-completion edge must therefore be absent from this set.
    intact_original_edges: set[tuple[str, str, str]] = set()
    original_last_node_values: dict[str, dict[str, Any]] = {}
    for turn in range(cutoff + 1, turns + 1):
        nodes, edges = parse_turn(run_dir, turn)
        intact_original_edges.update(edge_signature(edge) for edge in edges)
        for node in nodes:
            label = normalize_node_label(node.get("label", node.get("id", "")))
            values = {
                key: value
                for key, value in node.items()
                if key not in {"id", "label"}
            }
            original_last_node_values.setdefault(label, {}).update(values)

    selected_edges: set[tuple[str, str, str]] = set()
    selected_by_turn: dict[str, list[list[str]]] = {}
    seen_appended_edges: set[tuple[str, str, str]] = set()
    touched_node_keys: dict[str, set[str]] = {}
    for record in appended_history:
        turn = int(record["turn"])
        nodes, edges = parse_turn(run_dir, turn)
        for node in nodes:
            label = normalize_node_label(node.get("label", node.get("id", "")))
            touched_node_keys.setdefault(label, set()).update(
                key for key in node if key not in {"id", "label", "degree"}
            )

        first_seen: list[tuple[tuple[str, str, str], dict[str, Any]]] = []
        for edge in edges:
            signature = edge_signature(edge)
            if signature in seen_appended_edges:
                continue
            seen_appended_edges.add(signature)
            first_seen.append((signature, edge))

        needed = int(record.get("edges_added_to_graph", 0))
        if needed == 0:
            continue
        absent_from_intact = [
            pair for pair in first_seen if pair[0] not in intact_original_edges
        ]
        reflected = [
            pair
            for pair in absent_from_intact
            if attributes_reflected(filtered, pair[0], pair[1])
        ]
        if len(absent_from_intact) == needed:
            chosen = absent_from_intact
        elif len(reflected) == needed:
            chosen = reflected
        else:
            raise ValueError(
                f"{run_dir}: turn {turn} edge inversion is ambiguous: "
                f"needed={needed}, absent={len(absent_from_intact)}, "
                f"reflected={len(reflected)}"
            )
        chosen_signatures = {signature for signature, _ in chosen}
        if selected_edges & chosen_signatures:
            raise ValueError(f"{run_dir}: selected an appended edge more than once")
        selected_edges.update(chosen_signatures)
        selected_by_turn[str(turn)] = [list(value) for value in sorted(chosen_signatures)]

    if len(selected_edges) != reported_edge_additions:
        raise ValueError(
            f"{run_dir}: selected edges={len(selected_edges)} "
            f"but reported additions={reported_edge_additions}"
        )

    repaired = filtered.copy()
    for signature in sorted(selected_edges):
        remove_edge_signature(repaired, signature)
    missing_appended_nodes = sorted(appended_nodes - set(repaired.nodes))
    if missing_appended_nodes:
        raise ValueError(f"{run_dir}: appended nodes missing from graph: {missing_appended_nodes}")
    repaired.remove_nodes_from(sorted(appended_nodes))

    # Restore node metadata keys when the same node was observed later in the
    # intact portion of the original run. Structural metrics do not use these
    # descriptive fields, but restoring available values improves fidelity.
    restored_attribute_keys = 0
    unresolved_attribute_keys: dict[str, list[str]] = {}
    for node, keys in touched_node_keys.items():
        if node not in repaired:
            continue
        original_values = original_last_node_values.get(node, {})
        for key in sorted(keys):
            if key in original_values:
                repaired.nodes[node][key] = original_values[key]
                restored_attribute_keys += 1
            else:
                unresolved_attribute_keys.setdefault(node, []).append(key)

    for node in repaired.nodes:
        repaired.nodes[node]["degree"] = repaired.degree(node)

    if repaired.number_of_nodes() != target_nodes or repaired.number_of_edges() != target_edges:
        raise ValueError(
            f"{run_dir}: repaired counts={(repaired.number_of_nodes(), repaired.number_of_edges())} "
            f"target={(target_nodes, target_edges)}"
        )

    quarantine = run_dir / "repair_quarantine"
    quarantine.mkdir(exist_ok=True)
    atomic_json(quarantine / "postcompletion_query_history.json", appended_history)
    moved = quarantine_overwritten_artifacts(run_dir, cutoff)

    atomic_json(history_path, original_history)
    graph_data = nx.node_link_data(repaired, edges="links")
    atomic_json(run_dir / "extracted_graph.json", graph_data)
    atomic_json(run_dir / "extracted_graph_raw.json", graph_data)
    atomic_graphml(run_dir / "extracted_graph.graphml", repaired)
    atomic_graphml(run_dir / "extracted_graph_raw.graphml", repaired)

    manifest: dict[str, Any] = {
        "repair": "remove_launchd_postcompletion_restart_append",
        "repaired_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_dir": str(run_dir),
        "backup_root": str(backup_root.resolve()),
        "intended_turns": turns,
        "appended_turns_removed": cutoff,
        "target_graph": {"nodes": target_nodes, "edges": target_edges},
        "removed": {
            "nodes": len(appended_nodes),
            "edges": len(selected_edges),
            "node_names": sorted(appended_nodes),
            "edges_by_appended_turn": selected_by_turn,
        },
        "artifact_quarantine": {
            "path": str(quarantine / "postcompletion_restart_artifacts"),
            "moved_file_counts": moved,
            "note": (
                "The accidental restart overwrote the original artifacts for these "
                "turn numbers. They were removed from the primary turn-log directories; "
                "the pre-repair copies remain available in the full backup."
            ),
        },
        "node_attribute_recovery": {
            "restored_keys": restored_attribute_keys,
            "unresolved_node_count": len(unresolved_attribute_keys),
            "unresolved_keys": unresolved_attribute_keys,
            "note": (
                "Node/edge structure is exactly reconciled to the original turn-1000 "
                "counts and per-turn additions. Some descriptive node attributes touched "
                "by the restart cannot be proven identical when the node did not reappear "
                "in an intact later original response. Evaluation metrics ignore them."
            ),
        },
        "structural_recovery_note": (
            "Post-completion edges were uniquely identified from per-turn reported edge "
            "additions, first appearance in restart responses, absence from intact original "
            "responses after the overwritten prefix, and stored parsed attributes where "
            "needed."
        ),
    }
    core_files = (
        "query_history.json",
        "extracted_graph.json",
        "extracted_graph.graphml",
        "extracted_graph_raw.json",
        "extracted_graph_raw.graphml",
        "extraction_analysis.json",
    )
    manifest["sha256"] = {
        name: sha256(run_dir / name) for name in core_files if (run_dir / name).is_file()
    }
    atomic_json(run_dir / "REPAIR_MANIFEST.json", manifest)
    return manifest


def main() -> None:
    args = parse_args()
    backup_root = args.backup_root.resolve()
    if not backup_root.is_dir():
        raise FileNotFoundError(backup_root)
    results = [repair_run(path, backup_root, args.turns) for path in args.run]
    print(
        json.dumps(
            [
                {
                    "run_dir": result["run_dir"],
                    "appended_turns_removed": result["appended_turns_removed"],
                    "target_graph": result["target_graph"],
                    "removed": {
                        "nodes": result["removed"]["nodes"],
                        "edges": result["removed"]["edges"],
                    },
                    "unresolved_attribute_nodes": result["node_attribute_recovery"][
                        "unresolved_node_count"
                    ],
                }
                for result in results
            ],
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
