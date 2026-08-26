#!/usr/bin/env python3
"""Audit and compare the formal novel AGEA/FEWA 100-round runs."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import yaml


EXPECTED_MODEL = "DeepSeek-V4-Flash"
THINKING_PATTERN = re.compile(r"<\s*/?\s*think\b|reasoning_content", re.IGNORECASE)
AGEA_DEFAULT_QUERIES = (
    "Discover new entity types and relationship categories in this dataset.",
    "Provide detailed information about high-degree entities and their direct relationships.",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agea-dir", type=Path, required=True)
    parser.add_argument("--fewa-dir", type=Path, required=True)
    parser.add_argument("--agea-log", type=Path, required=True)
    parser.add_argument("--fewa-log", type=Path, required=True)
    parser.add_argument("--graphrag-settings", type=Path, required=True)
    parser.add_argument("--index-manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--require-complete", action="store_true")
    return parser.parse_args()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def thinking_hits(paths: list[Path]) -> list[str]:
    hits = []
    for path in paths:
        if THINKING_PATTERN.search(path.read_text(encoding="utf-8", errors="replace")):
            hits.append(str(path))
    return hits


def main() -> None:
    args = parse_args()
    agea_history = load_json(args.agea_dir / "query_history.json")
    fewa_history = load_json(args.fewa_dir / "query_history.json")
    agea_analysis = load_json(args.agea_dir / "extraction_analysis.json")
    agea_uniform = load_json(args.agea_dir / "uniform_evaluation.json")
    fewa_summary = load_json(args.fewa_dir / "summary.json")
    fewa_turn_metrics = load_json(args.fewa_dir / "turn_metrics.json")
    index_manifest = load_json(args.index_manifest)
    settings = yaml.safe_load(args.graphrag_settings.read_text(encoding="utf-8"))
    fewa_config = load_json(args.fewa_dir / "config.json")

    agea_responses = sorted((args.agea_dir / "turn_logs" / "llm_response").glob("*.txt"))
    fewa_responses = sorted((args.fewa_dir / "turn_logs" / "llm_responses").glob("*.txt"))
    agea_fallbacks = [
        int(row.get("turn", 0))
        for row in agea_history
        if int(row.get("turn", 0)) > 1
        and str(row.get("query", "")).startswith(AGEA_DEFAULT_QUERIES)
    ]
    fewa_fallback_rows = [
        row
        for row in fewa_history
        if row.get("query_generation", {}).get("source") == "diversified_fallback"
    ]
    fewa_similarity_fallbacks = [
        int(row.get("turn", 0))
        for row in fewa_fallback_rows
        if row.get("query_generation", {}).get("fallback_reason") == "similarity_exhausted"
        and int(row.get("query_generation", {}).get("generation_error_attempts", 0)) == 0
    ]
    fewa_invalid_fallbacks = [
        int(row.get("turn", 0))
        for row in fewa_fallback_rows
        if int(row.get("turn", 0)) not in fewa_similarity_fallbacks
    ]
    agea_log = args.agea_log.read_text(encoding="utf-8", errors="replace")
    fewa_log = args.fewa_log.read_text(encoding="utf-8", errors="replace")
    agea_filter_statuses = {
        row.get("graph_filter_stats", {}).get("graph_filter_status")
        for row in agea_history
    }
    fewa_filter_statuses = {
        row.get("parser", {}).get("graph_filter_status") for row in fewa_turn_metrics
    }

    agea_final = agea_uniform.get("final", {})
    fewa_final = fewa_summary.get("final", {})

    comparable = {
        "final": {
            "AGEA": {
                key: agea_final.get(key)
                for key in (
                    "recovered_nodes",
                    "recovered_edge_pairs",
                    "matched_nodes",
                    "matched_directed_edge_pairs",
                    "node_precision",
                    "node_recall",
                    "edge_pair_precision",
                    "edge_pair_recall",
                    "node_tsc_rank",
                    "node_tsc_raw",
                    "edge_tsc_rank",
                    "edge_tsc_raw",
                )
            },
            "FEWA": {
                key: fewa_final.get(key)
                for key in (
                    "recovered_nodes",
                    "recovered_edge_pairs",
                    "matched_nodes",
                    "matched_directed_edge_pairs",
                    "node_precision",
                    "node_recall",
                    "edge_pair_precision",
                    "edge_pair_recall",
                    "node_tsc_rank",
                    "node_tsc_raw",
                    "edge_tsc_rank",
                    "edge_tsc_raw",
                )
            },
        },
        "trajectory_mean": {
            "AGEA": {
                key: agea_uniform.get("trajectory", {}).get(key)
                for key in (
                    "au_node_tsc_rank",
                    "au_node_tsc_raw",
                    "au_edge_tsc_rank",
                    "au_edge_tsc_raw",
                    "au_node_recall",
                    "au_edge_pair_recall",
                )
            },
            "FEWA": {
                key: fewa_summary.get("trajectory", {}).get(key)
                for key in (
                    "au_node_tsc_rank",
                    "au_node_tsc_raw",
                    "au_edge_tsc_rank",
                    "au_edge_tsc_raw",
                    "au_node_recall",
                    "au_edge_pair_recall",
                )
            },
        },
    }

    checks = {
        "index_complete": index_manifest.get("complete") is True,
        "agea_100_rounds": len(agea_history) == 100,
        "agea_uniform_replay_exact": agea_uniform.get("complete") is True,
        "fewa_100_rounds": len(fewa_history) == 100 and fewa_summary.get("turns_completed") == 100,
        "same_seed_query": bool(agea_history and fewa_history) and agea_history[0].get("query") == fewa_history[0].get("query"),
        "exact_graphrag_model": settings["models"]["default_chat_model"]["model"] == EXPECTED_MODEL,
        "exact_fewa_query_model": fewa_config.get("query_generator_model") == EXPECTED_MODEL,
        "no_0731_model": "0731" not in json.dumps({"settings": settings, "fewa": fewa_config}),
        "agea_no_filtering": agea_filter_statuses == {"disabled"},
        "fewa_no_filtering": fewa_config.get("enable_graph_filter") is False and fewa_filter_statuses == {"disabled"},
        "fewa_thinking_disabled": fewa_config.get("disable_api_thinking") is True,
        "agea_no_query_fallback": not agea_fallbacks and "Agentic query generation failed" not in agea_log,
        # Similarity-exhausted fallback is the configured 0.85 uniqueness
        # guard's terminal branch, not an API/model failure. The user excludes
        # retry attempts from the logical call budget, so only provider or
        # generation-error fallbacks invalidate the formal run.
        "fewa_no_generation_error_fallback": not fewa_invalid_fallbacks,
        "agea_response_count": len(agea_responses) == 100,
        "fewa_response_count": len(fewa_responses) == 100,
        "agea_no_thinking_tags": not thinking_hits(agea_responses),
        "fewa_no_thinking_tags": not thinking_hits(fewa_responses),
        "agea_exit_clean": "Traceback" not in agea_log and "RuntimeError" not in agea_log,
        "fewa_exit_clean": "Traceback" not in fewa_log and "RuntimeError" not in fewa_log,
    }
    result = {
        "complete": all(checks.values()),
        "checks": checks,
        "details": {
            "agea_turns": len(agea_history),
            "fewa_turns": len(fewa_history),
            "agea_fallback_turns": agea_fallbacks,
            "fewa_similarity_fallback_turns": fewa_similarity_fallbacks,
            "fewa_invalid_fallback_turns": fewa_invalid_fallbacks,
            "agea_filter_statuses": sorted(str(item) for item in agea_filter_statuses),
            "fewa_filter_statuses": sorted(str(item) for item in fewa_filter_statuses),
            "graph_digest": index_manifest.get("graph_digest"),
            "agea_reported_model": agea_analysis.get("llm_model"),
        },
        "comparison": comparable,
    }
    rendered = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    if args.require_complete and not result["complete"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
