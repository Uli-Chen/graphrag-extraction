# AGEA GraphRAG baseline

This directory contains the AGEA components required for the formal medical
GraphRAG comparison. Upstream provenance and retained provider-compatibility
changes are documented in `UPSTREAM.md`.

The medical GraphRAG workspace is stored once at
`artifacts/graphrag/medical`. The runner resolves this repository-level path
directly; the baseline directory contains no dataset copy or compatibility
symlink.

Configure the query generator in the repository-level `.env`:

```bash
AGEA_LLM_PROVIDER=openai_compatible
AGEA_API_BASE=https://llmapi.paratera.com/v1/
AGEA_API_KEY=replace-me
QUERY_GENERATOR=DeepSeek-V4-Flash-0731
```

The retained GraphRAG runner can execute the 50-turn reference protocol with:

```bash
uv run python baselines/AGEA/graphrag/run_agea.py \
  --dataset medical \
  --turns 50 \
  --query-method local \
  --disable-graph-filter
```
