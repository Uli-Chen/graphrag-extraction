#!/usr/bin/env bash
set -uo pipefail

project_dir="/Users/chen/research/mematk"
runtime="/private/tmp/mematk-graphrag-py312/bin/python"
state_dir="$project_dir/artifacts/runs/novel_fair_orchestrator"
index_pid_file="$project_dir/artifacts/graphrag/novel/index.pid"
index_output="$project_dir/artifacts/graphrag/novel/output"
fewa_config="$project_dir/configs/extraction/novel/ts_pl_fewa_100turn_no_thinking_fair.yaml"
seed_queries="$project_dir/configs/extraction/novel/seed_queries.txt"
index_audit="$project_dir/scripts/audit_graphrag_index.py"
uniform_replay="$project_dir/scripts/replay_agea_uniform_metrics.py"
comparison_audit="$project_dir/scripts/audit_novel_fair_results.py"

mkdir -p "$state_dir"

set -a
source "$project_dir/.env"
set +a
export PYTHONPATH="$project_dir/src:$project_dir/baselines/AGEA"
export QUERY_GENERATOR="DeepSeek-V4-Flash"
export AGEA_CHAT_MODEL="DeepSeek-V4-Flash"
export GRAPHRAG_CHAT_MODEL="DeepSeek-V4-Flash"

if [[ -s "$index_pid_file" ]]; then
  index_pid="$(cat "$index_pid_file")"
  if kill -0 "$index_pid" 2>/dev/null; then
    echo "Waiting for GraphRAG index PID $index_pid"
    while kill -0 "$index_pid" 2>/dev/null; do
      sleep 30
    done
  fi
fi

validate_index() {
  "$runtime" - "$index_output" <<'PY'
import sys
from pathlib import Path

import pandas as pd

output = Path(sys.argv[1])
required = (
    "entities.parquet",
    "relationships.parquet",
    "communities.parquet",
    "community_reports.parquet",
    "text_units.parquet",
)
missing_files = [name for name in required if not (output / name).is_file() or (output / name).stat().st_size == 0]
if missing_files:
    print(f"Index is missing required files: {missing_files}", file=sys.stderr)
    raise SystemExit(1)

communities = pd.read_parquet(output / "communities.parquet", columns=["community"])
reports = pd.read_parquet(output / "community_reports.parquet", columns=["community"])
community_ids = set(communities["community"].astype(str))
report_ids = set(reports["community"].astype(str))
missing_reports = sorted(community_ids - report_ids)
extra_reports = sorted(report_ids - community_ids)
if missing_reports or extra_reports:
    print(
        "Community report coverage mismatch: "
        f"communities={len(community_ids)}, reports={len(report_ids)}, "
        f"missing={missing_reports[:20]}, extra={extra_reports[:20]}",
        file=sys.stderr,
    )
    raise SystemExit(1)

print(
    "Index validation passed: "
    f"communities={len(community_ids)}, reports={len(report_ids)}"
)
PY
}

if ! validate_index; then
  "$runtime" "$index_audit" \
    --output-dir "$index_output" \
    --manifest "$state_dir/incomplete_index_manifest.json" \
    > "$state_dir/incomplete_index_audit.log" 2>&1
  echo "GraphRAG index is incomplete; refusing a nondeterministic full replay" >&2
  echo "Run the targeted community-report repair before experiments" >&2
  exit 20
fi
if ! "$runtime" "$index_audit" \
  --output-dir "$index_output" \
  --manifest "$state_dir/validated_index_manifest.json" \
  --require-complete \
  > "$state_dir/validated_index_audit.log" 2>&1; then
  echo "GraphRAG index failed parquet/vector completeness audit" >&2
  exit 20
fi

echo "Running two-round AGEA smoke test"
"$runtime" "$project_dir/baselines/AGEA/graphrag/run_agea.py" \
  --dataset novel \
  --turns 2 \
  --seed-queries "$seed_queries" \
  --initial-epsilon 0.30 \
  --epsilon-decay 0.98 \
  --min-epsilon 0.05 \
  --novelty-threshold 0.15 \
  --novelty-window 5 \
  --novelty-threshold-mode adaptive \
  --output-suffix novel_agea_smoke_2round \
  --disable-graph-filter \
  --query-generator-model DeepSeek-V4-Flash \
  --query-method local \
  --disable-api-thinking \
  --query-retries 2 \
  > "$state_dir/agea_smoke.log" 2>&1
agea_smoke_status=$?

echo "Running two-round FEWA smoke test"
"$runtime" -m extraction.cli \
  --config "$fewa_config" \
  --run-id novel_fewa_smoke_2round \
  --turns 2 \
  > "$state_dir/fewa_smoke.log" 2>&1
fewa_smoke_status=$?

agea_base="$project_dir/artifacts/graphrag/novel/init_eps_0.3_eps_decay_0.98_min_eps_0.05_thres_0.15_no_graph_filter/DeepSeek_V4_Flash/local"
agea_smoke_history="$agea_base/novel_agea_smoke_2round/query_history.json"
fewa_smoke_summary="$project_dir/artifacts/runs/mematk/novel_fewa_smoke_2round/summary.json"

if [[ $agea_smoke_status -ne 0 ]] || ! jq -e 'length == 2' "$agea_smoke_history" >/dev/null; then
  echo "AGEA smoke test failed" >&2
  exit 21
fi
if rg -q 'Agentic query generation failed' "$state_dir/agea_smoke.log"; then
  echo "AGEA smoke test used a query-generation fallback" >&2
  exit 21
fi
if [[ $fewa_smoke_status -ne 0 ]] || ! jq -e \
  '.turns_completed == 2 and .query_diagnostics.query_generator_fallback_turns == 0' \
  "$fewa_smoke_summary" >/dev/null; then
  echo "FEWA smoke test failed" >&2
  exit 22
fi

echo "Launching formal AGEA and FEWA runs in parallel"
"$runtime" "$project_dir/baselines/AGEA/graphrag/run_agea.py" \
  --dataset novel \
  --turns 100 \
  --seed-queries "$seed_queries" \
  --initial-epsilon 0.30 \
  --epsilon-decay 0.98 \
  --min-epsilon 0.05 \
  --novelty-threshold 0.15 \
  --novelty-window 5 \
  --novelty-threshold-mode adaptive \
  --output-suffix novel_agea_100round_no_thinking_fair \
  --disable-graph-filter \
  --query-generator-model DeepSeek-V4-Flash \
  --query-method local \
  --disable-api-thinking \
  --query-retries 2 \
  > "$state_dir/agea_100round.log" 2>&1 &
agea_pid=$!
printf '%s\n' "$agea_pid" > "$state_dir/agea.pid"

"$runtime" -m extraction.cli \
  --config "$fewa_config" \
  > "$state_dir/fewa_100round.log" 2>&1 &
fewa_pid=$!
printf '%s\n' "$fewa_pid" > "$state_dir/fewa.pid"

set +e
wait "$agea_pid"
agea_status=$?
wait "$fewa_pid"
fewa_status=$?
set -e

agea_history="$agea_base/novel_agea_100round_no_thinking_fair/query_history.json"
fewa_summary="$project_dir/artifacts/runs/mematk/novel_ts_pl_fewa_100turn_no_thinking_fair_seed42/summary.json"
agea_turns="$(jq 'length' "$agea_history" 2>/dev/null || echo 0)"
fewa_turns="$(jq '.turns_completed // 0' "$fewa_summary" 2>/dev/null || echo 0)"

jq -n \
  --argjson agea_status "$agea_status" \
  --argjson fewa_status "$fewa_status" \
  --argjson agea_turns "$agea_turns" \
  --argjson fewa_turns "$fewa_turns" \
  '{agea_exit_status:$agea_status,fewa_exit_status:$fewa_status,agea_turns:$agea_turns,fewa_turns:$fewa_turns}' \
  > "$state_dir/comparison_status.json"

if [[ $agea_status -ne 0 || $fewa_status -ne 0 || $agea_turns -ne 100 || $fewa_turns -ne 100 ]]; then
  echo "Formal comparison did not complete successfully" >&2
  exit 23
fi

agea_dir="$agea_base/novel_agea_100round_no_thinking_fair"
fewa_dir="$project_dir/artifacts/runs/mematk/novel_ts_pl_fewa_100turn_no_thinking_fair_seed42"
if ! "$runtime" "$uniform_replay" \
  --agea-dir "$agea_dir" \
  --truth-dir "$index_output" \
  --output "$agea_dir/uniform_evaluation.json" \
  > "$state_dir/agea_uniform_replay.log" 2>&1; then
  echo "AGEA uniform-evaluator replay failed" >&2
  exit 24
fi
if ! "$runtime" "$comparison_audit" \
  --agea-dir "$agea_dir" \
  --fewa-dir "$fewa_dir" \
  --agea-log "$state_dir/agea_100round.log" \
  --fewa-log "$state_dir/fewa_100round.log" \
  --graphrag-settings "$project_dir/configs/graphrag/novel/settings.yaml" \
  --index-manifest "$state_dir/validated_index_manifest.json" \
  --output "$state_dir/final_comparison_audit.json" \
  --require-complete \
  > "$state_dir/final_comparison_audit.log" 2>&1; then
  echo "Formal comparison audit failed" >&2
  exit 25
fi

echo "Novel 100-round fair comparison completed"
