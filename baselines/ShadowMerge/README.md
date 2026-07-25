# ShadowMerge Evaluation Package

## Purpose

This package contains the runnable ShadowMerge evaluation workflow used for graph-memory interaction tests. It supports smoke checks, metric computation, graph-gate diagnostics, and baseline comparison through a local mock graph-memory backend.

Included components:

- Dataset loading for JSONL evaluation cases.
- Mock graph-memory writes and retrieval.
- Adapters for ShadowMerge, Naive Text Poisoning, MINJA-adapt, and GRAGPoison-adapt.
- ASR, utility, materialization, merge, retrieval, poison-rank, and graph-gate diagnostic metrics.
- Unit tests and a no-network smoke test.

## Environment Setup

Use Python 3.10 or newer.

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

Credentials are not stored in files. If a real model backend is added locally, provide credentials through environment variables named in `configs/config.example.yaml`. The default smoke test uses mock mode and does not call external services.

## Quick Start

From this directory:

```bash
bash scripts/run_smoke_test.sh
python -m tests.test_metrics
python scripts/run_eval.py --config configs/config.example.yaml --mock
```

From the parent repository:

```bash
bash ShadowMerge_anonymous/scripts/run_smoke_test.sh
python -m pytest ShadowMerge_anonymous/tests
python ShadowMerge_anonymous/scripts/run_eval.py --config ShadowMerge_anonymous/configs/config.example.yaml --mock
```

## Expected Outputs

The smoke test prints a JSON summary with:

- ASR and utility.
- Materialization, merge, and retrieval rates.
- Mean poison rank on graph-memory retrieval.
- Graph diagnostic counts for nodes, edges, relation types, and graph-gate stages.

`scripts/run_eval.py` writes `summary.json` and `case_results.jsonl` to the configured output directory.

## Data

The files under `data/samples/` provide JSONL evaluation cases shaped for PubMedQA-style, WebShop-style, and ToolEmu-style runs. They do not contain raw model traces, credentials, private paths, or production logs.

## Security Note

The package executes local evaluation logic by default. Credentials must be supplied through environment variables when using non-mock extensions.
