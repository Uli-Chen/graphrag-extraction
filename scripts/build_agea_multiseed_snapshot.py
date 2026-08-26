#!/usr/bin/env python3
"""Build a compact, auditable multi-seed AGEA result snapshot."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import statistics
from pathlib import Path
from typing import Any

import yaml


FINAL_DERIVED_KEYS = ("node_f1", "edge_pair_f1")
NATIVE_FIELDS = (
    "nodes_added_to_graph",
    "edges_added_to_graph",
    "total_nodes_in_graph",
    "total_edges_in_graph",
    "native_node_precision",
    "native_node_recall",
    "native_edge_precision",
    "native_edge_recall",
    "native_degree_weighted_node_coverage",
)
EVALUATION_FIELDS = (
    "node_precision",
    "node_recall",
    "edge_pair_precision",
    "edge_pair_recall",
    "node_tsc_rank",
    "edge_tsc_rank",
    "node_autc_rank",
)


def parse_seed_path(value: str) -> tuple[int, Path]:
    seed_text, separator, path_text = value.partition("=")
    if not separator:
        raise argparse.ArgumentTypeError("expected SEED=PATH")
    try:
        seed = int(seed_text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid seed: {seed_text}") from exc
    return seed, Path(path_text).resolve()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="append", type=parse_seed_path, required=True)
    parser.add_argument(
        "--evaluation", action="append", type=parse_seed_path, required=True
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--truth-nodes", type=int, required=True)
    parser.add_argument("--truth-edges", type=int, required=True)
    return parser.parse_args()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def mean_std(values: list[float]) -> tuple[float, float]:
    return statistics.mean(values), statistics.stdev(values) if len(values) > 1 else 0.0


def numeric_summary(rows: list[dict[str, Any]]) -> tuple[dict[str, float], dict[str, float]]:
    common = set.intersection(*(set(row) for row in rows))
    mean: dict[str, float] = {}
    std: dict[str, float] = {}
    for key in sorted(common):
        values = [row[key] for row in rows]
        if not all(isinstance(value, (int, float)) and not isinstance(value, bool) for value in values):
            continue
        mean[key], std[key] = mean_std([float(value) for value in values])
    return mean, std


def f1(precision: float, recall: float) -> float:
    return 2.0 * precision * recall / (precision + recall) if precision + recall else 0.0


def query_signature(query: str) -> str:
    domain = query.split("\n\nFor my record", 1)[0]
    return " ".join(sorted(set(re.findall(r"[a-z0-9]+", domain.lower()))))


def query_diagnostics(history: list[dict[str, Any]]) -> dict[str, float | int]:
    signatures = [query_signature(str(record["query"])) for record in history]
    zero_gain = sum(
        not bool(
            record.get("nodes_added_to_graph", 0)
            or record.get("edges_added_to_graph", 0)
        )
        for record in history
    )
    total = len(history)
    return {
        "total_queries": total,
        "unique_queries": len(set(signatures)),
        "query_unique_rate": len(set(signatures)) / total if total else 0.0,
        "zero_gain_turns": zero_gain,
        "zero_gain_rate": zero_gain / total if total else 0.0,
    }


def mode_diagnostics(history: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "seed_turns": sum(record.get("mode") == "seed" for record in history),
        "post_seed_turns": sum(record.get("mode") != "seed" for record in history),
        "post_seed_explore_turns": sum(record.get("mode") == "explore" for record in history),
        "post_seed_exploit_turns": sum(record.get("mode") == "exploit" for record in history),
    }


def native_turn(record: dict[str, Any]) -> dict[str, float]:
    cumulative = record["cumulative_metrics"]
    return {
        "nodes_added_to_graph": float(record["nodes_added_to_graph"]),
        "edges_added_to_graph": float(record["edges_added_to_graph"]),
        "total_nodes_in_graph": float(record["total_nodes_in_graph"]),
        "total_edges_in_graph": float(record["total_edges_in_graph"]),
        "native_node_precision": float(cumulative["precision_nodes"]) / 100.0,
        "native_node_recall": float(cumulative["leakage_rate_nodes"]) / 100.0,
        "native_edge_precision": float(cumulative["precision_edges"]) / 100.0,
        "native_edge_recall": float(cumulative["leakage_rate_edges"]) / 100.0,
        "native_degree_weighted_node_coverage": float(
            cumulative["importance_leakage_rate_nodes_degree"]
        )
        / 100.0,
    }


def compact_trajectory(
    history: list[dict[str, Any]], evaluation: dict[str, Any]
) -> list[dict[str, Any]]:
    rows = []
    for turn, (record, evaluated) in enumerate(
        zip(history, evaluation["turn_metrics"], strict=True), start=1
    ):
        row: dict[str, Any] = {
            "turn": turn,
            "mode": record["mode"],
            "novelty": record.get("novelty", 0.0),
            **native_turn(record),
        }
        row.update({f"evaluation_{key}": evaluated[key] for key in EVALUATION_FIELDS})
        rows.append(row)
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_checksums(root: Path, *, recursive: bool) -> None:
    pattern = "**/*" if recursive else "*"
    paths = sorted(
        path for path in root.glob(pattern) if path.is_file() and path.name != "SHA256SUMS"
    )
    lines = []
    for path in paths:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.relative_to(root)}")
    (root / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    runs = dict(args.run)
    evaluations = dict(args.evaluation)
    if set(runs) != set(evaluations):
        raise SystemExit("run and evaluation seed sets differ")
    seeds = sorted(runs)
    if len(seeds) < 2:
        raise SystemExit("multi-seed snapshot requires at least two seeds")

    output = args.output.resolve()
    if output.exists():
        raise SystemExit(f"output already exists: {output}")
    output.mkdir(parents=True)

    histories: dict[int, list[dict[str, Any]]] = {}
    uniform: dict[int, dict[str, Any]] = {}
    per_seed_final: dict[int, dict[str, Any]] = {}
    per_seed_trajectory: dict[int, dict[str, Any]] = {}
    per_seed_query: dict[int, dict[str, Any]] = {}
    per_seed_modes: dict[int, dict[str, Any]] = {}
    compact_rows: dict[int, list[dict[str, Any]]] = {}

    for seed in seeds:
        run_dir = runs[seed]
        evaluation_path = evaluations[seed]
        history = load_json(run_dir / "query_history.json")
        result = load_json(evaluation_path)
        if len(history) != 100 or result.get("complete") is not True or result.get("turns") != 100:
            raise SystemExit(f"seed {seed} is not a complete audited 100-turn run")

        final = dict(result["final"])
        final["node_f1"] = f1(final["node_precision"], final["node_recall"])
        final["edge_pair_f1"] = f1(
            final["edge_pair_precision"], final["edge_pair_recall"]
        )
        histories[seed] = history
        uniform[seed] = result
        per_seed_final[seed] = final
        per_seed_trajectory[seed] = result["trajectory"]
        per_seed_query[seed] = query_diagnostics(history)
        per_seed_modes[seed] = mode_diagnostics(history)
        compact_rows[seed] = compact_trajectory(history, result)

        seed_dir = output / f"seed{seed}"
        seed_dir.mkdir()
        shutil.copy2(run_dir / "extracted_graph.graphml", seed_dir / "extracted_graph.graphml")
        shutil.copy2(run_dir / "extraction_analysis.json", seed_dir / "extraction_analysis.json")
        shutil.copy2(run_dir / "query_history.json", seed_dir / "query_history.json")
        shutil.copy2(evaluation_path, seed_dir / "uniform_evaluation.json")
        write_csv(seed_dir / "trajectory.csv", compact_rows[seed])
        write_json(
            seed_dir / "metrics.json",
            {
                "designation": "official_agea_multiseed_member",
                "source_run_id": run_dir.name,
                "method": "standalone_agea",
                "dataset": "medical",
                "query_budget": 100,
                "random_seed": seed,
                "truth": {
                    "nodes": args.truth_nodes,
                    "directed_edge_pairs": args.truth_edges,
                },
                "final": final,
                "trajectory": result["trajectory"],
                "query_diagnostics": per_seed_query[seed],
                "mode_diagnostics": per_seed_modes[seed],
                "replay_validation": {
                    "complete": result["complete"],
                    "failed_replay_turns": result["failed_replay_turns"],
                    "stored_graph_exact_node_match": result[
                        "stored_graph_exact_node_match"
                    ],
                    "stored_graph_exact_edge_match": result[
                        "stored_graph_exact_edge_match"
                    ],
                },
            },
        )
        (seed_dir / "protocol.yaml").write_text(
            yaml.safe_dump(
                {
                    "dataset": "medical",
                    "run_id": run_dir.name,
                    "method": "standalone_agea",
                    "turns": 100,
                    "random_seed": seed,
                    "query_method": "local",
                    "llm_model": args.model,
                    "disable_api_thinking": True,
                    "enable_graph_filter": False,
                    "initial_epsilon": 0.30,
                    "epsilon_decay": 0.98,
                    "min_epsilon": 0.05,
                    "novelty_threshold": 0.15,
                    "candidate_k": 6,
                    "seed_policy": "native_agea",
                },
                sort_keys=False,
            ),
            encoding="utf-8",
        )
        write_checksums(seed_dir, recursive=False)

    final_mean, final_std = numeric_summary(list(per_seed_final.values()))
    trajectory_mean, trajectory_std = numeric_summary(list(per_seed_trajectory.values()))
    query_mean, query_std = numeric_summary(list(per_seed_query.values()))
    mode_mean, mode_std = numeric_summary(list(per_seed_modes.values()))

    aggregate_turns: list[dict[str, Any]] = []
    numeric_turn_fields = NATIVE_FIELDS + tuple(
        f"evaluation_{key}" for key in EVALUATION_FIELDS
    )
    for index in range(100):
        row: dict[str, Any] = {"turn": index + 1}
        for field in numeric_turn_fields:
            values = [float(compact_rows[seed][index][field]) for seed in seeds]
            row[field], row[f"{field}_std"] = mean_std(values)
        aggregate_turns.append(row)
    write_csv(output / "trajectory.csv", aggregate_turns)

    write_json(
        output / "metrics.json",
        {
            "designation": "official_agea_3seed",
            "source_run_ids": {
                str(seed): runs[seed].name for seed in seeds
            },
            "method": "standalone_agea",
            "dataset": "medical",
            "query_budget": 100,
            "seeds": seeds,
            "aggregation": {
                "center": "arithmetic_mean",
                "spread": "sample_standard_deviation",
                "ddof": 1,
            },
            "truth": {
                "nodes": args.truth_nodes,
                "directed_edge_pairs": args.truth_edges,
            },
            "final": final_mean,
            "final_std": final_std,
            "trajectory": trajectory_mean,
            "trajectory_std": trajectory_std,
            "query_diagnostics": query_mean,
            "query_diagnostics_std": query_std,
            "mode_diagnostics": mode_mean,
            "mode_diagnostics_std": mode_std,
            "per_seed": {
                str(seed): {
                    "path": f"seed{seed}",
                    "final": per_seed_final[seed],
                    "trajectory": per_seed_trajectory[seed],
                    "query_diagnostics": per_seed_query[seed],
                    "mode_diagnostics": per_seed_modes[seed],
                }
                for seed in seeds
            },
            "protocol": {
                "llm_model": args.model,
                "disable_api_thinking": True,
                "enable_graph_filter": False,
                "seed_policy": "native AGEA seed query",
                "random_seeds": seeds,
            },
            "evaluation_note": (
                "All final and trajectory metrics were recomputed by replaying each "
                "AGEA response with MemATK's unified evaluator. Aggregate values are "
                "the arithmetic mean and sample standard deviation across seeds."
            ),
        },
    )
    (output / "protocol.yaml").write_text(
        yaml.safe_dump(
            {
                "dataset": "medical",
                "designation": "official_agea_3seed",
                "method": "standalone_agea",
                "turns_per_seed": 100,
                "random_seeds": seeds,
                "query_method": "local",
                "llm_model": args.model,
                "disable_api_thinking": True,
                "enable_graph_filter": False,
                "initial_epsilon": 0.30,
                "epsilon_decay": 0.98,
                "min_epsilon": 0.05,
                "novelty_threshold": 0.15,
                "candidate_k": 6,
                "seed_policy": "native_agea",
                "aggregation": "mean_and_sample_standard_deviation",
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    (output / "README.md").write_text(
        "# Medical AGEA 3-seed formal snapshot\n\n"
        "This directory is the official 100-query AGEA result on Medical, "
        "aggregated over random seeds 40, 41, and 42. API thinking and graph "
        "filtering were disabled. Root-level metrics and trajectory files contain "
        "the arithmetic mean and sample standard deviation; each `seed*/` directory "
        "contains the complete compact snapshot and unified replay evaluation for "
        "one run. There is intentionally no root-level graph or query history because "
        "a multi-seed aggregate has no single representative graph.\n",
        encoding="utf-8",
    )
    write_checksums(output, recursive=True)
    print(f"built {output} for seeds {seeds}")


if __name__ == "__main__":
    main()
