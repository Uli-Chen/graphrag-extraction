# Data Notes

The datasets in `data/samples/` are JSONL evaluation cases for local runs. They do not contain raw benchmark dumps, model traces, user data, private paths, or run logs.

Files:

- `pubmedqa_samples.jsonl`: PubMedQA-style biomedical question cases.
- `webshop_samples.jsonl`: WebShop-style shopping recommendation cases.
- `toolemu_samples.jsonl`: ToolEmu-style tool-use safety cases.

Each JSONL row contains the target entity, benign relation, poison relation, benign query, victim query, and expected answers.

