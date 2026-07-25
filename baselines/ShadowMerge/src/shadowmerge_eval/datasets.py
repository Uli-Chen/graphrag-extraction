from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List, Sequence

from .models import DatasetCase


def load_jsonl_cases(path: Path) -> List[DatasetCase]:
    cases: List[DatasetCase] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                payload = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at {path}:{line_number}") from exc
            cases.append(DatasetCase.from_dict(payload))
    return cases


def load_cases(paths: Sequence[Path]) -> List[DatasetCase]:
    loaded: List[DatasetCase] = []
    for path in paths:
        loaded.extend(load_jsonl_cases(path))
    return loaded


def resolve_dataset_paths(config_root: Path, values: Iterable[str]) -> List[Path]:
    paths: List[Path] = []
    for value in values:
        candidate = Path(value)
        if not candidate.is_absolute():
            candidate = config_root / candidate
        paths.append(candidate)
    return paths
