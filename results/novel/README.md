# Novel GraphRAG: AGEA vs TS-PL-FEWA (100 rounds)

## Status

The formal comparison completed and passed every automated protocol and artifact check.

- GraphRAG chat/query model: `DeepSeek-V4-Flash` (no `0731` suffix)
- API thinking: disabled for GraphRAG and query-generator calls
- Graph filtering: disabled for both methods
- Budget: 100 logical rounds per method, with retry calls excluded as requested
- Seed: identical live seed prompt; each method made its own live model call
- Evaluation: both graphs were scored with the same `TruthData` and `evaluate_recovery` implementation

## Index

The audited Novel index contains 17,161 entities, 29,236 relationships, 2,922 communities, 2,922 community reports, and 1,038 text units. Its stable semantic graph digest is:

`46c42f479b6f30d32752ae06c35789cd1f3f51f17b3150e3b2773425401cc408`

## Final results

Percentages below are shown in percentage points. Relative change is `(FEWA - AGEA) / AGEA`.

| Metric | AGEA | TS-PL-FEWA | FEWA relative change |
|---|---:|---:|---:|
| Recovered nodes | 1,718 | **1,906** | **+10.94%** |
| Matched truth nodes | 1,468 | **1,636** | **+11.44%** |
| Node precision | 85.448% | **85.834%** | **+0.45%** |
| Node recall | 8.554% | **9.533%** | **+11.44%** |
| Node TSC (rank) | 14.633% | **17.178%** | **+17.39%** |
| Node TSC (raw) | 25.031% | **27.414%** | **+9.52%** |
| Recovered directed edge pairs | **2,267** | 2,168 | -4.37% |
| Matched truth edge pairs | 1,784 | **1,914** | **+7.29%** |
| Edge precision | 78.694% | **88.284%** | **+12.19%** |
| Edge recall | 6.102% | **6.547%** | **+7.29%** |
| Edge TSC (rank) | 6.216% | **6.598%** | **+6.16%** |
| Edge TSC (raw) | **6.437%** | 5.789% | -10.06% |

## 100-round trajectory means

| Metric | AGEA | TS-PL-FEWA | FEWA relative change |
|---|---:|---:|---:|
| AU node recall | 4.785% | **5.952%** | **+24.38%** |
| AU node TSC (rank) | 8.280% | **10.971%** | **+32.51%** |
| AU node TSC (raw) | 15.041% | **18.689%** | **+24.25%** |
| AU edge recall | 3.168% | **3.805%** | **+20.10%** |
| AU edge TSC (rank) | 3.244% | **3.829%** | **+18.01%** |
| AU edge TSC (raw) | **3.519%** | 3.403% | -3.29% |

## Interpretation

TS-PL-FEWA is stronger overall on this Novel run. It recovers 168 more true nodes and 130 more true directed edge pairs, despite emitting 99 fewer edge pairs in total. The edge result is especially informative: FEWA improves edge precision by 9.59 percentage points while also improving edge recall, indicating a materially cleaner recovered graph rather than a gain obtained by indiscriminately adding edges.

The trajectory metrics reinforce the final result. FEWA's average rank-weighted node TSC is 32.51% higher and its average node recall is 24.38% higher, so the advantage is present across the query budget rather than appearing only near round 100.

AGEA retains one clear advantage: raw-weighted edge TSC, both finally and over the trajectory. It also emits more total edge pairs. Thus the result supports FEWA on rank-sensitive coverage, recall, and precision, but does not establish dominance under every edge weighting.

AGEA used 9 post-seed explore rounds and 90 exploit rounds. FEWA used 23 post-seed explore rounds and 76 exploit rounds. FEWA recorded two configured `similarity_exhausted` query fallbacks (rounds 44 and 56); both had zero provider/generation errors and all 100 final queries remained unique. Retry attempts are excluded from the logical budget, following the requested protocol.

The formal FEWA rerun used a query-reformulation retry ceiling of 10 instead of 3 after the pilot repeatedly exhausted the 0.85 similarity gate. The similarity threshold, accepted-query rule, controller, seed, and extraction budget were unchanged. Even with the higher ceiling, rounds 44 and 56 reached the configured deterministic fallback; this is reported rather than silently removed.

## Audit evidence

- `fair_100round_audit.json`: all completion, model, seed, filtering, thinking-tag, response-count, and replay checks passed.
- AGEA's 100 responses were replayed turn by turn with the common evaluator. Every per-turn node/edge count and increment matched its recorded trajectory, and the reconstructed final node and edge sets exactly matched the stored formal graph.
- FEWA's built-in formal acceptance checks all passed: query uniqueness 100%, zero-gain rate 12%, maximum consecutive zero-gain 2, anchor-query adherence 100%, both post-seed modes observed, and non-empty response rate 100%.

The copied protocol snapshots are `agea_protocol.yaml` and `fewa_protocol.yaml`. Raw run artifacts remain under `artifacts/graphrag/novel/.../novel_agea_100round_no_thinking_fair` and `artifacts/runs/mematk/novel_ts_pl_fewa_100turn_no_thinking_fair_seed42`.
