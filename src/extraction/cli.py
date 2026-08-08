"""CLI entry point for the medical GraphRAG extraction experiment."""

from __future__ import annotations

import argparse
import json

from .config import ExperimentConfig
from .pipeline import MedicalExtractionPipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", help="YAML configuration file")
    parser.add_argument("--run-id", help="Unique directory name under artifacts/runs/mematk")
    parser.add_argument("--turns", type=int, help="Number of GraphRAG query turns")
    parser.add_argument(
        "--enable-graph-filter",
        action="store_true",
        help="Enable AGEA's optional LLM graph filter (disabled by default)",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    config = ExperimentConfig.load(args.config)
    if args.run_id:
        config.run_id = args.run_id
    if args.turns is not None:
        config.turns = args.turns
    if args.enable_graph_filter:
        config.enable_graph_filter = True

    summary = MedicalExtractionPipeline(config).run()
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
