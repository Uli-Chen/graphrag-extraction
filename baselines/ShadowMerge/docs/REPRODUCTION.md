# Reproduction Notes

This package runs the ShadowMerge evaluation control flow on JSONL sample data:

1. Load evaluation cases.
2. Initialize the mock graph-memory backend.
3. Write benign graph anchors.
4. Write one poison memory per case through a selected adapter.
5. Run victim retrieval.
6. Compute ASR, utility, materialization, merge, retrieval, and poison-rank diagnostics.

The default configuration uses `mock_graph_memory`; it performs no network calls. The included adapters support ordinary interaction writes for comparing evaluation behavior across methods.

