# Medical GraphRAG results

Both directories use a 50-query budget and the same frozen medical GraphRAG
truth (1,178 nodes and 3,046 directed edge pairs).

| Method | Nodes | Edges | Node precision | Node recall | Edge precision | Edge recall |
|---|---:|---:|---:|---:|---:|---:|
| AGEA reference | 697 | 871 | 0.7633 | 0.4516 | 0.9472 | 0.2708 |
| MemATK seed 42 | 614 | 910 | 0.9153 | 0.4771 | 0.9901 | 0.2958 |

`mematk_50turn_seed42` includes its formal protocol, aggregate metrics, per-turn
recovery trajectory, paper-facing report, and final graph. The AGEA snapshot
preserves the upstream-style extraction analysis, query history, and final graph.
Full response/context artifacts remain local under `artifacts/`.
