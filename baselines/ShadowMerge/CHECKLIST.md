# Package Checklist

## Scope

- Created `ShadowMerge_anonymous/` as a standalone ShadowMerge evaluation package.
- Included evaluation code, metric computation, mock graph-memory behavior, baseline adapters, tests, sample data, configuration, and documentation.
- No runtime byproducts, credentials, private data, or repository history are present.

## Scan Results

- Marker scan: no findings.
- Credential pattern scan: no findings.
- Local path scan: no findings.
- Provider env reference scan: only the three environment-variable names in `configs/config.example.yaml`; no source or script findings.
- CJK character scan: no findings.
- Bytecode and cache scan: no findings after cleanup.

## Verification

- `python -m pytest ShadowMerge_anonymous/tests`: passed, 4 tests.
- `bash ShadowMerge_anonymous/scripts/run_smoke_test.sh`: passed.
- `python -m tests.test_metrics` from the package root: passed, 3 tests.
- `python scripts/run_eval.py --config configs/config.example.yaml --mock` with a temporary output directory: passed.

Smoke-test summary:

```json
{
  "asr": 1.0,
  "materialization_rate": 1.0,
  "mean_poison_rank": 1.0,
  "merge_rate": 1.0,
  "num_cases": 6,
  "retrieval_rate": 1.0,
  "utility": 1.0
}
```

## Package Listing

```text
ShadowMerge_anonymous/.gitignore
ShadowMerge_anonymous/CHECKLIST.md
ShadowMerge_anonymous/LICENSE
ShadowMerge_anonymous/README.md
ShadowMerge_anonymous/configs/config.example.yaml
ShadowMerge_anonymous/data/samples/pubmedqa_samples.jsonl
ShadowMerge_anonymous/data/samples/toolemu_samples.jsonl
ShadowMerge_anonymous/data/samples/webshop_samples.jsonl
ShadowMerge_anonymous/docs/DATA.md
ShadowMerge_anonymous/docs/REPRODUCTION.md
ShadowMerge_anonymous/requirements.txt
ShadowMerge_anonymous/scripts/run_eval.py
ShadowMerge_anonymous/scripts/run_smoke_test.sh
ShadowMerge_anonymous/src/shadowmerge_eval/__init__.py
ShadowMerge_anonymous/src/shadowmerge_eval/baselines.py
ShadowMerge_anonymous/src/shadowmerge_eval/datasets.py
ShadowMerge_anonymous/src/shadowmerge_eval/diagnostics.py
ShadowMerge_anonymous/src/shadowmerge_eval/harness.py
ShadowMerge_anonymous/src/shadowmerge_eval/metrics.py
ShadowMerge_anonymous/src/shadowmerge_eval/mock_memory.py
ShadowMerge_anonymous/src/shadowmerge_eval/models.py
ShadowMerge_anonymous/src/shadowmerge_eval/prompts.py
ShadowMerge_anonymous/tests/__init__.py
ShadowMerge_anonymous/tests/test_metrics.py
ShadowMerge_anonymous/tests/test_smoke.py
```

## Manual Confirmation

- No additional files were flagged by the scans above.
