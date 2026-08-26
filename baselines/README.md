# Baselines

This directory contains vendored implementations of the baselines used in the
project. Each snapshot is tracked by the parent repository rather than as a
nested Git repository. Upstream URLs and imported revisions are recorded in
the corresponding `UPSTREAM.md` files.

- `AGEA/`: topology-aware GraphRAG extraction baseline used by the formal
  medical comparison. The snapshot includes the compatibility changes listed
  in `AGEA/UPSTREAM.md`.
- `IKEA/`: implementation of *Silent Leaks: Implicit Knowledge Extraction
  Attack on RAG Systems Through Benign Queries* (ICLR 2026). See
  `IKEA/UPSTREAM.md`.
- `PIDE/`: implementation of *Follow My Instruction and Spill the Beans:
  Scalable Data Extraction from Retrieval-Augmented Generation Systems*
  (ICLR 2025). See `PIDE/UPSTREAM.md`.
