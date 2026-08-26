#!/usr/bin/env bash
set -euo pipefail

run_id="${1:-medical_uniform_fresh_50turn_seed42}"
export AGEA_QUERY_MAX_TOKENS="${AGEA_QUERY_MAX_TOKENS:-3072}"

uv run mematk-extract \
  --config configs/extraction/medical/uniform_fresh_50turn.yaml \
  --run-id "$run_id"
