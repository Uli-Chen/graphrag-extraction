#!/usr/bin/env python3
"""Audit GraphRAG parquet/vector completeness and emit stable semantic digests."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import lancedb
import numpy as np
import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--require-complete", action="store_true")
    return parser.parse_args()


def normalize(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        value = value.tolist()
    if isinstance(value, (list, tuple, set)):
        return sorted((normalize(item) for item in value), key=repr)
    if isinstance(value, dict):
        return {str(key): normalize(item) for key, item in sorted(value.items())}
    if value is None:
        return None
    try:
        if bool(pd.isna(value)):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        number = float(value)
        if math.isfinite(number):
            return number
        return str(number)
    if isinstance(value, (str, int, bool)):
        return value
    return str(value)


def digest_rows(rows: list[Any]) -> str:
    serialized = [
        json.dumps(normalize(row), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        for row in rows
    ]
    serialized.sort()
    digest = hashlib.sha256()
    for row in serialized:
        digest.update(row.encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()


def selected_rows(frame: pd.DataFrame, columns: list[str]) -> list[dict[str, Any]]:
    available = [column for column in columns if column in frame.columns]
    return frame.loc[:, available].to_dict(orient="records")


def vector_counts(output_dir: Path) -> dict[str, int | None]:
    database = lancedb.connect(output_dir / "lancedb")
    names = set(database.list_tables().tables)
    expected = (
        "default-entity-description",
        "default-community-full_content",
        "default-text_unit-text",
    )
    return {
        name: database.open_table(name).count_rows() if name in names else None
        for name in expected
    }


def build_manifest(output_dir: Path) -> dict[str, Any]:
    required = (
        "entities",
        "relationships",
        "communities",
        "community_reports",
        "text_units",
    )
    frames = {
        name: pd.read_parquet(output_dir / f"{name}.parquet") for name in required
    }
    entities = frames["entities"]
    relationships = frames["relationships"]
    communities = frames["communities"]
    reports = frames["community_reports"]
    text_units = frames["text_units"]

    entity_title_by_id = {
        str(identifier): str(title)
        for identifier, title in zip(entities["id"], entities["title"], strict=True)
    }
    community_rows = []
    for row in communities.itertuples(index=False):
        member_titles = sorted(
            entity_title_by_id.get(str(identifier), f"<missing:{identifier}>")
            for identifier in row.entity_ids
        )
        community_rows.append({
            "level": int(row.level),
            "size": int(row.size),
            "members": member_titles,
        })

    community_ids = set(communities["community"].astype(str))
    report_ids = set(reports["community"].astype(str))
    missing_reports = sorted(community_ids - report_ids)
    extra_reports = sorted(report_ids - community_ids)
    vectors = vector_counts(output_dir)

    counts = {name: len(frame) for name, frame in frames.items()}
    expected_vector_counts = {
        "default-entity-description": counts["entities"],
        "default-community-full_content": counts["community_reports"],
        "default-text_unit-text": counts["text_units"],
    }
    vector_mismatches = {
        name: {"actual": vectors[name], "expected": expected}
        for name, expected in expected_vector_counts.items()
        if vectors[name] != expected
    }

    semantic_digests = {
        "entities": digest_rows(selected_rows(
            entities,
            ["title", "type", "description", "frequency", "degree"],
        )),
        "relationships": digest_rows(selected_rows(
            relationships,
            ["source", "target", "description", "weight", "combined_degree"],
        )),
        "communities": digest_rows(community_rows),
        "text_units": digest_rows(selected_rows(
            text_units,
            ["text", "n_tokens", "document_ids"],
        )),
    }
    graph_digest = digest_rows([
        {"name": name, "digest": digest}
        for name, digest in semantic_digests.items()
    ])

    return {
        "counts": counts,
        "community_levels": {
            str(level): int(count)
            for level, count in communities["level"].value_counts().sort_index().items()
        },
        "missing_reports": missing_reports,
        "extra_reports": extra_reports,
        "vector_counts": vectors,
        "vector_mismatches": vector_mismatches,
        "semantic_digests": semantic_digests,
        "graph_digest": graph_digest,
        "complete": not missing_reports and not extra_reports and not vector_mismatches,
    }


def main() -> None:
    args = parse_args()
    manifest = build_manifest(args.output_dir)
    rendered = json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True)
    if args.manifest:
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    if args.require_complete and not manifest["complete"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
