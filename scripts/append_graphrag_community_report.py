#!/usr/bin/env python3
"""Append one repaired GraphRAG community report and its embedding safely.

This is intentionally a targeted repair. Replaying the complete GraphRAG index
can change graph extraction/finalization output even when the LLM cache is warm.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import uuid
from pathlib import Path
from typing import Any

import lancedb
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from openai import OpenAI

from graphrag.index.operations.finalize_community_reports import (
    finalize_community_reports,
)
from graphrag.index.operations.summarize_communities.community_reports_extractor import (
    CommunityReportResponse,
)


VECTOR_TABLE = "default-community-full_content"
REPAIR_NAMESPACE = uuid.UUID("1b481e16-9f00-52b4-a321-494e03c91bd8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--cache-file", type=Path, required=True)
    parser.add_argument("--community-id", type=int, required=True)
    parser.add_argument(
        "--embedding-api-key",
        default=os.environ.get("GRAPHRAG_EMBEDDING_API_KEY"),
    )
    parser.add_argument(
        "--embedding-api-base",
        default=os.environ.get("GRAPHRAG_EMBEDDING_API_BASE"),
    )
    parser.add_argument(
        "--embedding-model",
        default=os.environ.get("GRAPHRAG_EMBEDDING_MODEL"),
    )
    return parser.parse_args()


def load_repaired_response(cache_file: Path) -> CommunityReportResponse:
    payload = json.loads(cache_file.read_text(encoding="utf-8"))
    result = payload.get("result", {})
    choices = result.get("choices", [])
    if len(choices) != 1:
        raise ValueError(f"Expected one cached choice, got {len(choices)}")
    message = choices[0].get("message", {})
    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise ValueError("Cached response has no non-empty message content")
    response = CommunityReportResponse.model_validate_json(content)

    model = result.get("model")
    if model != "DeepSeek-V4-Flash":
        raise ValueError(f"Unexpected repair model: {model!r}")
    reasoning_tokens = (
        result.get("usage", {})
        .get("completion_tokens_details", {})
        .get("reasoning_tokens")
    )
    if reasoning_tokens not in (None, 0):
        raise ValueError(f"Repair response used reasoning tokens: {reasoning_tokens}")
    return response


def text_output(report: CommunityReportResponse) -> str:
    sections = "\n\n".join(
        f"## {finding.summary}\n\n{finding.explanation}"
        for finding in report.findings
    )
    return f"# {report.title}\n\n{report.summary}\n\n{sections}"


def report_identifier(community_id: int) -> str:
    return uuid.uuid5(
        REPAIR_NAMESPACE,
        f"novel-community-report:{community_id}:DeepSeek-V4-Flash",
    ).hex


def make_report_row(
    communities: pd.DataFrame,
    community_id: int,
    response: CommunityReportResponse,
) -> pd.DataFrame:
    community = communities[communities["community"].astype(int) == community_id]
    if len(community) != 1:
        raise ValueError(
            f"Expected exactly one community {community_id}, got {len(community)}"
        )
    source = community.iloc[0]
    raw_report = pd.DataFrame([{
        "community": community_id,
        "title": response.title,
        "summary": response.summary,
        "full_content": text_output(response),
        "full_content_json": response.model_dump_json(indent=4),
        "rank": float(response.rating),
        "level": int(source["level"]),
        "rating_explanation": response.rating_explanation,
        "findings": [finding.model_dump() for finding in response.findings],
    }])
    finalized = finalize_community_reports(raw_report, communities)
    finalized.loc[:, "id"] = report_identifier(community_id)
    return finalized


def existing_vector_ids(table: Any) -> set[str]:
    return set(table.to_arrow().select(["id"]).column("id").to_pylist())


def embed(args: argparse.Namespace, text: str, expected_size: int) -> list[float]:
    missing = [
        name
        for name, value in (
            ("GRAPHRAG_EMBEDDING_API_KEY", args.embedding_api_key),
            ("GRAPHRAG_EMBEDDING_API_BASE", args.embedding_api_base),
            ("GRAPHRAG_EMBEDDING_MODEL", args.embedding_model),
        )
        if not value
    ]
    if missing:
        raise ValueError(f"Missing embedding settings: {', '.join(missing)}")
    client = OpenAI(
        api_key=args.embedding_api_key,
        base_url=args.embedding_api_base,
        max_retries=10,
        timeout=120.0,
    )
    result = client.embeddings.create(model=args.embedding_model, input=[text])
    if len(result.data) != 1:
        raise ValueError(f"Expected one embedding, got {len(result.data)}")
    vector = result.data[0].embedding
    if len(vector) != expected_size:
        raise ValueError(
            f"Embedding length mismatch: expected {expected_size}, got {len(vector)}"
        )
    return vector


def write_reports_atomically(
    reports_path: Path,
    reports: pd.DataFrame,
    new_row: pd.DataFrame,
) -> tuple[Path, Path]:
    existing_table = pq.read_table(reports_path)
    combined = pd.concat([reports, new_row], ignore_index=True)
    output_table = pa.Table.from_pandas(
        combined,
        schema=existing_table.schema,
        preserve_index=False,
        safe=True,
    )
    temporary = reports_path.with_suffix(".targeted-repair.tmp.parquet")
    backup_dir = reports_path.parent.parent / "repair_backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup = backup_dir / "community_reports.pre-targeted-repair.parquet"
    pq.write_table(output_table, temporary)
    if not backup.exists():
        shutil.copy2(reports_path, backup)
    return temporary, backup


def main() -> None:
    args = parse_args()
    output_dir = args.output_dir.resolve()
    reports_path = output_dir / "community_reports.parquet"
    communities_path = output_dir / "communities.parquet"
    communities = pd.read_parquet(communities_path)
    reports = pd.read_parquet(reports_path)
    response = load_repaired_response(args.cache_file)

    matches = reports[reports["community"].astype(int) == args.community_id]
    if len(matches) > 1:
        raise ValueError(f"Duplicate reports already exist for {args.community_id}")

    database = lancedb.connect(output_dir / "lancedb")
    table = database.open_table(VECTOR_TABLE)
    ids = existing_vector_ids(table)

    if len(matches) == 1:
        row = matches.iloc[[0]].copy()
        report_id = str(row.iloc[0]["id"])
    else:
        row = make_report_row(communities, args.community_id, response)
        report_id = str(row.iloc[0]["id"])

    vector_exists = report_id in ids
    if len(matches) == 1 and vector_exists:
        print(
            json.dumps({
                "status": "already_complete",
                "community": args.community_id,
                "report_id": report_id,
                "report_count": len(reports),
                "vector_count": table.count_rows(),
            }, indent=2)
        )
        return

    full_content = str(row.iloc[0]["full_content"])
    vector_type = table.schema.field("vector").type
    expected_size = int(vector_type.list_size)
    vector = None if vector_exists else embed(args, full_content, expected_size)

    temporary: Path | None = None
    backup: Path | None = None
    if len(matches) == 0:
        temporary, backup = write_reports_atomically(reports_path, reports, row)

    added_vector = False
    try:
        if not vector_exists:
            vector_row = pa.Table.from_pylist(
                [{
                    "id": report_id,
                    "text": full_content,
                    "vector": vector,
                    "attributes": json.dumps({"title": full_content}),
                }],
                schema=table.schema,
            )
            table.add(vector_row)
            added_vector = True
        if temporary is not None:
            os.replace(temporary, reports_path)
    except BaseException:
        if added_vector:
            table.delete(f"id = '{report_id}'")
        if temporary is not None and temporary.exists():
            temporary.unlink()
        raise

    refreshed_reports = pd.read_parquet(reports_path)
    refreshed_table = database.open_table(VECTOR_TABLE)
    report_matches = refreshed_reports[
        refreshed_reports["community"].astype(int) == args.community_id
    ]
    vector_matches = refreshed_table.to_arrow().select(["id"]).column("id").to_pylist().count(report_id)
    if len(report_matches) != 1 or vector_matches != 1:
        raise RuntimeError(
            "Targeted repair verification failed: "
            f"reports={len(report_matches)}, vectors={vector_matches}"
        )

    print(
        json.dumps({
            "status": "repaired",
            "community": args.community_id,
            "report_id": report_id,
            "embedding_model": args.embedding_model,
            "embedding_size": expected_size,
            "report_count": len(refreshed_reports),
            "vector_count": refreshed_table.count_rows(),
            "parquet_backup": str(backup) if backup else None,
        }, ensure_ascii=False, indent=2)
    )


if __name__ == "__main__":
    main()
