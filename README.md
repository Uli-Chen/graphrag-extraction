# MemATK

MemATK implements topology-sensitive adaptive graph extraction over a prebuilt
GraphRAG index. The repository is organized around the formal 50-turn medical
experiment and its AGEA reference.

## Repository layout

```text
src/extraction/             extraction pipeline, metrics, control, and backend
src/evaluation/             graph-recovery and trajectory evaluation
baselines/AGEA/             vendored GraphRAG baseline and provenance
configs/extraction/medical/ formal 50-turn configuration
configs/graphrag/medical/   GraphRAG settings and prompts
data/{medical,novel}/       corpora and benchmark questions
results/medical/            compact formal-result snapshots
artifacts/graphrag/medical/ shared GraphRAG workspace used by all methods
artifacts/runs/             ignored complete experiment runs
scripts/                    formal experiment entry point
proposal.md                 implementation-aligned method proposal
```

## Setup

Python 3.10 and `uv` are required:

```bash
uv sync
cp .env.example .env
```

All methods load provider settings from the repository-level `.env`, which is
ignored by Git. AGEA-specific and GraphRAG-specific variables use separate
namespaces, so their query and victim models may use different providers. The
example configuration includes no real keys.

The GraphRAG index has one canonical runtime location:
`artifacts/graphrag/medical`. Both MemATK and the AGEA baseline resolve that
path directly; no dataset copy is kept below `baselines/AGEA`.

## Formal medical experiment

```bash
./scripts/run_medical_50turn.sh medical_ts_pl_fewa_50turn_seed42
```

The runner refuses to overwrite a non-empty directory. Complete output is saved
under `artifacts/runs/mematk`; the compact paper-facing snapshot is curated under
`results/medical/mematk_50turn_seed42`.

See [proposal.md](proposal.md) for the complete method definition and
[results/medical/README.md](results/medical/README.md) for the formal comparison.
