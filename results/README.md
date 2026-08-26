# Results

This directory contains compact, reviewable snapshots of formal experiments.
Raw LLM responses, retrieved contexts, caches, and controller state normally
belong in the ignored `artifacts/` tree. A snapshot may retain a frozen seed
response or upstream query history when either is needed to audit or reproduce
the formal protocol.

Each snapshot identifies its protocol and preserves aggregate metrics, a
per-turn recovery curve, extracted graphs, and checksums. Multi-seed snapshots
store aggregate files at the root and auditable run artifacts in `seed*/`
subdirectories. Method-specific reports or upstream analysis files are retained
where available.

The Novel 100-round AGEA/TS-PL-FEWA comparison and its unified evaluation are
documented in [`novel/README.md`](novel/README.md).
