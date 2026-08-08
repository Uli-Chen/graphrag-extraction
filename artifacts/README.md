# Runtime artifacts

This directory holds local GraphRAG indices, caches, logs, raw LLM responses,
retrieved contexts, and complete run directories. Its contents are intentionally
ignored by Git; only this README is tracked.

Expected local layout:

```text
artifacts/
├── graphrag/medical/       # shared input, output index, cache, and logs
└── runs/mematk/            # complete extraction runs
```

Provider credentials are shared through the repository-level `.env`; runtime
workspaces do not own independent configuration.

Compact, paper-auditable result snapshots belong under `results/`.
