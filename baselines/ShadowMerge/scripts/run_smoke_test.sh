#!/usr/bin/env bash
set -euo pipefail

ARTIFACT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="$(mktemp -d "${TMPDIR:-/tmp}/shadowmerge_smoke.XXXXXX")"

python "$ARTIFACT_ROOT/scripts/run_eval.py" \
  --config "$ARTIFACT_ROOT/configs/config.example.yaml" \
  --output-dir "$OUTPUT_DIR" \
  --mock

echo "smoke_output_dir=$OUTPUT_DIR"
