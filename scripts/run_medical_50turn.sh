#!/usr/bin/env bash
set -euo pipefail

run_id="${1:-medical_ts_pl_fewa_50turn_seed42}"
export AGEA_QUERY_MAX_TOKENS="${AGEA_QUERY_MAX_TOKENS:-3072}"

uv run mematk-extract \
  --config configs/extraction/medical/ts_pl_fewa_50turn.yaml \
  --run-id "$run_id"
