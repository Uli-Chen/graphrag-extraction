#!/usr/bin/env python3
"""Build a compact, auditable multi-seed TS-PL-FEWA result snapshot."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import statistics
from pathlib import Path
from typing import Any

import yaml


TRAJECTORY_FIELDS = (
    "evaluation_node_recall",
    "evaluation_edge_pair_recall",
    "evaluation_node_tsc_rank",
    "evaluation_node_tsc_raw",
    "evaluation_edge_tsc_rank",
    "evaluation_edge_tsc_raw",
    "evaluation_node_autc_rank",
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
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed-response", type=Path, required=True)
    parser.add_argument("--model", required=True)
    return parser.parse_args()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def mean_std(values: list[float]) -> tuple[float, float]:
    return statistics.mean(values), statistics.stdev(values)


def numeric_summary(rows: list[dict[str, Any]]) -> tuple[dict[str, float], dict[str, float]]:
    common = set.intersection(*(set(row) for row in rows))
    mean: dict[str, float] = {}
    std: dict[str, float] = {}
    for key in sorted(common):
        values = [row[key] for row in rows]
        if not all(
            isinstance(value, (int, float)) and not isinstance(value, bool)
            for value in values
        ):
            continue
        mean[key], std[key] = mean_std([float(value) for value in values])
    return mean, std


def f1(precision: float, recall: float) -> float:
    return 2.0 * precision * recall / (precision + recall) if precision + recall else 0.0


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
    seeds = sorted(runs)
    if len(seeds) < 2:
        raise SystemExit("multi-seed snapshot requires at least two seeds")
    if len(runs) != len(args.run):
        raise SystemExit("duplicate random seed")

    output = args.output.resolve()
    seed_response = args.seed_response.resolve()
    if output.exists():
        raise SystemExit(f"output already exists: {output}")
    if not seed_response.is_file():
        raise SystemExit(f"missing seed response: {seed_response}")
    output.mkdir(parents=True)

    summaries: dict[int, dict[str, Any]] = {}
    configs: dict[int, dict[str, Any]] = {}
    turns: dict[int, list[dict[str, str]]] = {}
    per_seed_final: dict[int, dict[str, Any]] = {}
    per_seed_trajectory: dict[int, dict[str, Any]] = {}
    per_seed_query: dict[int, dict[str, Any]] = {}
    per_seed_modes: dict[int, dict[str, Any]] = {}
    per_seed_anchor: dict[int, dict[str, Any]] = {}

    for seed in seeds:
        run_dir = runs[seed]
        summary = load_json(run_dir / "summary.json")
        config = load_json(run_dir / "config.json")
        turn_rows = read_csv(run_dir / "turn_metrics.csv")
        history = load_json(run_dir / "query_history.json")
        if (
            summary.get("dataset") != "medical"
            or summary.get("turns_completed") != 100
            or len(turn_rows) != 100
            or len(history) != 100
            or config.get("random_seed") != seed
            or config.get("anchor_sampling_policy") != "ts_pl_fewa"
            or config.get("disable_api_thinking") is not True
            or summary.get("formal_acceptance", {}).get("all_passed") is not True
        ):
            raise SystemExit(f"seed {seed} is not a complete accepted Medical FEWA run")

        final = dict(summary["final"])
        final["node_f1"] = f1(final["node_precision"], final["node_recall"])
        final["edge_pair_f1"] = f1(
            final["edge_pair_precision"], final["edge_pair_recall"]
        )
        summaries[seed] = summary
        configs[seed] = config
        turns[seed] = turn_rows
        per_seed_final[seed] = final
        per_seed_trajectory[seed] = summary["trajectory"]
        per_seed_query[seed] = summary["query_diagnostics"]
        per_seed_modes[seed] = summary["mode_diagnostics"]
        per_seed_anchor[seed] = summary["anchor_diagnostics"]

        seed_dir = output / f"seed{seed}"
        seed_dir.mkdir()
        for name in (
            "extracted_graph.graphml",
            "query_history.json",
            "turn_metrics.csv",
            "config.json",
            "EXPERIMENT_RESULTS.md",
        ):
            shutil.copy2(run_dir / name, seed_dir / name)
        shutil.copy2(run_dir / "summary.json", seed_dir / "summary.json")
        write_json(
            seed_dir / "metrics.json",
            {
                "designation": "official_fewa_multiseed_member",
                "source_run_id": summary["run_id"],
                "method": "ts_pl_fewa",
                "dataset": "medical",
                "query_budget": 100,
                "random_seed": seed,
                "truth": {
                    "nodes": summary["truth_nodes"],
                    "directed_edge_pairs": summary["truth_directed_edge_pairs"],
                },
                "final": final,
                "trajectory": summary["trajectory"],
                "query_diagnostics": summary["query_diagnostics"],
                "mode_diagnostics": summary["mode_diagnostics"],
                "anchor_diagnostics": summary["anchor_diagnostics"],
                "formal_acceptance": summary["formal_acceptance"],
            },
        )
        (seed_dir / "protocol.yaml").write_text(
            yaml.safe_dump(
                {
                    "dataset": "medical",
                    "run_id": summary["run_id"],
                    "method": "ts_pl_fewa",
                    "turns": 100,
                    "random_seed": seed,
                    "query_method": config["query_method"],
                    "llm_model": args.model,
                    "disable_api_thinking": True,
                    "enable_graph_filter": config["enable_graph_filter"],
                    "shared_seed_response": "../../seed_response.txt",
                    "initial_epsilon": config["initial_epsilon"],
                    "epsilon_decay": config["epsilon_decay"],
                    "min_epsilon": config["min_epsilon"],
                    "htsn_threshold": config["htsn_threshold"],
                    "adaptive_htsn_threshold": config["adaptive_htsn_threshold"],
                    "fewa_delta": config["fewa_delta"],
                    "fewa_max_arms": config["fewa_max_arms"],
                    "reward_normalizer": config["reward_normalizer"],
                },
                sort_keys=False,
            ),
            encoding="utf-8",
        )
        write_checksums(seed_dir, recursive=False)

    truth_nodes = {summary["truth_nodes"] for summary in summaries.values()}
    truth_edges = {summary["truth_directed_edge_pairs"] for summary in summaries.values()}
    if len(truth_nodes) != 1 or len(truth_edges) != 1:
        raise SystemExit("seed truth graphs differ")

    final_mean, final_std = numeric_summary(list(per_seed_final.values()))
    trajectory_mean, trajectory_std = numeric_summary(list(per_seed_trajectory.values()))
    query_mean, query_std = numeric_summary(list(per_seed_query.values()))
    mode_mean, mode_std = numeric_summary(list(per_seed_modes.values()))
    anchor_mean, anchor_std = numeric_summary(list(per_seed_anchor.values()))

    aggregate_turns: list[dict[str, Any]] = []
    for index in range(100):
        row: dict[str, Any] = {"turn": index + 1}
        for field in TRAJECTORY_FIELDS:
            values = [float(turns[seed][index][field]) for seed in seeds]
            row[field], row[f"{field}_std"] = mean_std(values)
        aggregate_turns.append(row)
    write_csv(output / "trajectory.csv", aggregate_turns)
    shutil.copy2(seed_response, output / "seed_response.txt")

    write_json(
        output / "metrics.json",
        {
            "designation": "official_fewa_3seed",
            "source_run_ids": {
                str(seed): summaries[seed]["run_id"] for seed in seeds
            },
            "method": "ts_pl_fewa",
            "dataset": "medical",
            "query_budget": 100,
            "seeds": seeds,
            "aggregation": {
                "center": "arithmetic_mean",
                "spread": "sample_standard_deviation",
                "ddof": 1,
            },
            "truth": {
                "nodes": next(iter(truth_nodes)),
                "directed_edge_pairs": next(iter(truth_edges)),
            },
            "final": final_mean,
            "final_std": final_std,
            "trajectory": trajectory_mean,
            "trajectory_std": trajectory_std,
            "query_diagnostics": query_mean,
            "query_diagnostics_std": query_std,
            "mode_diagnostics": mode_mean,
            "mode_diagnostics_std": mode_std,
            "anchor_diagnostics": anchor_mean,
            "anchor_diagnostics_std": anchor_std,
            "per_seed": {
                str(seed): {
                    "path": f"seed{seed}",
                    "final": per_seed_final[seed],
                    "trajectory": per_seed_trajectory[seed],
                    "query_diagnostics": per_seed_query[seed],
                    "mode_diagnostics": per_seed_modes[seed],
                    "anchor_diagnostics": per_seed_anchor[seed],
                    "formal_acceptance_all_passed": True,
                }
                for seed in seeds
            },
            "protocol": {
                "llm_model": args.model,
                "disable_api_thinking": True,
                "enable_graph_filter": False,
                "shared_seed_response": "seed_response.txt",
                "random_seeds": seeds,
            },
            "evaluation_note": (
                "All metrics are native outputs from the common MemATK evaluator. "
                "Aggregate values are the arithmetic mean and sample standard "
                "deviation across seeds."
            ),
        },
    )
    (output / "protocol.yaml").write_text(
        yaml.safe_dump(
            {
                "dataset": "medical",
                "designation": "official_fewa_3seed",
                "method": "ts_pl_fewa",
                "turns_per_seed": 100,
                "random_seeds": seeds,
                "query_method": "local",
                "llm_model": args.model,
                "disable_api_thinking": True,
                "enable_graph_filter": False,
                "shared_seed_response": "seed_response.txt",
                "initial_epsilon": configs[seeds[0]]["initial_epsilon"],
                "epsilon_decay": configs[seeds[0]]["epsilon_decay"],
                "min_epsilon": configs[seeds[0]]["min_epsilon"],
                "htsn_threshold": configs[seeds[0]]["htsn_threshold"],
                "adaptive_htsn_threshold": configs[seeds[0]][
                    "adaptive_htsn_threshold"
                ],
                "fewa_delta": configs[seeds[0]]["fewa_delta"],
                "fewa_max_arms": configs[seeds[0]]["fewa_max_arms"],
                "reward_normalizer": configs[seeds[0]]["reward_normalizer"],
                "aggregation": "mean_and_sample_standard_deviation",
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    (output / "README.md").write_text(
        "# Medical TS-PL-FEWA 3-seed formal snapshot\n\n"
        "This directory is the official 100-query TS-PL-FEWA result on Medical, "
        "aggregated over random seeds 40, 41, and 42. API thinking and graph "
        "filtering were disabled, and all seeds replayed the same frozen seed "
        "response. Root-level metrics and trajectory files contain the arithmetic "
        "mean and sample standard deviation; each `seed*/` directory preserves a "
        "compact auditable snapshot of one run. The previous important single-seed "
        "formal result is retained alongside this directory as "
        "`fewa_100turn_formal_1seed`.\n",
        encoding="utf-8",
    )
    write_checksums(output, recursive=True)
    print(f"built {output} for seeds {seeds}")


if __name__ == "__main__":
    main()
