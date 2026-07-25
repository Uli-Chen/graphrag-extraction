#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ARTIFACT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ARTIFACT_ROOT / "src"))

from shadowmerge_eval.harness import run_evaluation


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the ShadowMerge evaluation package.")
    parser.add_argument("--config", required=True, help="Path to a YAML config file.")
    parser.add_argument("--output-dir", default=None, help="Optional output directory override.")
    parser.add_argument("--mock", action="store_true", help="Use the included mock graph-memory backend.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = Path.cwd() / config_path
    output_dir = Path(args.output_dir) if args.output_dir else None
    result = run_evaluation(
        config_path,
        root=ARTIFACT_ROOT,
        output_dir=output_dir,
        mock=True if args.mock else True,
    )
    print(json.dumps(result.summary, indent=2, sort_keys=True))
    if output_dir is not None:
        print(f"wrote_outputs={output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
