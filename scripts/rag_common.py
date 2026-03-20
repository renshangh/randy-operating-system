#!/usr/bin/env python3
"""Shared helpers for Mac Mini LanceDB RAG Phase 2.

CLI-first RAG utilities intended to run locally on the Mac Mini.
This module intentionally keeps imports lazy where practical so the file can
exist in the repo even if LanceDB / sentence-transformers are not installed on
this MacBook runtime.
"""

from __future__ import annotations

import argparse
import json
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_MODEL = os.environ.get("RAG_EMBED_MODEL", "BAAI/bge-small-en-v1.5")
DEFAULT_DB_PATH = os.environ.get(
    "RAG_DB_PATH",
    str(Path.home() / ".openclaw" / "memory" / "mac-mini-rag-lancedb"),
)
DEFAULT_TABLE = os.environ.get("RAG_TABLE", "documents")
DEFAULT_CHUNK_SIZE = int(os.environ.get("RAG_CHUNK_SIZE", "900"))
DEFAULT_CHUNK_OVERLAP = int(os.environ.get("RAG_CHUNK_OVERLAP", "150"))
DEFAULT_TOP_K = int(os.environ.get("RAG_TOP_K", "5"))
DEFAULT_NORMALIZE = os.environ.get("RAG_NORMALIZE", "1") != "0"
VECTOR_DIMENSIONS = {"BAAI/bge-small-en-v1.5": 384}


@dataclass
class RagConfig:
    db_path: str = DEFAULT_DB_PATH
    table_name: str = DEFAULT_TABLE
    model: str = DEFAULT_MODEL
    chunk_size: int = DEFAULT_CHUNK_SIZE
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP
    normalize: bool = DEFAULT_NORMALIZE

    @property
    def vector_dim(self) -> int:
        dims = VECTOR_DIMENSIONS.get(self.model)
        if not dims:
            raise ValueError(f"Unsupported embedding model: {self.model}")
        return dims


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_parent_dir(path: str) -> None:
    Path(path).expanduser().mkdir(parents=True, exist_ok=True)


def load_sentence_transformer(model_name: str):
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(model_name)


def embed_texts(texts: list[str], cfg: RagConfig) -> list[list[float]]:
    model = load_sentence_transformer(cfg.model)
    vectors = model.encode(texts, normalize_embeddings=cfg.normalize)
    return [list(map(float, row)) for row in vectors]


def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    normalized = " ".join(text.split())
    if not normalized:
        return []
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if chunk_overlap < 0:
        raise ValueError("chunk_overlap must be >= 0")
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    chunks: list[str] = []
    start = 0
    step = chunk_size - chunk_overlap
    while start < len(normalized):
        chunk = normalized[start : start + chunk_size].strip()
        if chunk:
            chunks.append(chunk)
        if start + chunk_size >= len(normalized):
            break
        start += step
    return chunks


def build_records(
    *,
    source_id: str,
    source_type: str,
    text: str,
    cfg: RagConfig,
    metadata: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    metadata = metadata or {}
    chunks = chunk_text(text, cfg.chunk_size, cfg.chunk_overlap)
    if not chunks:
        return []
    vectors = embed_texts(chunks, cfg)
    created_at = utc_now_iso()
    records: list[dict[str, Any]] = []
    for idx, (chunk, vector) in enumerate(zip(chunks, vectors)):
        records.append(
            {
                "id": str(uuid.uuid4()),
                "source_id": source_id,
                "source_type": source_type,
                "chunk_index": idx,
                "text": chunk,
                "vector": vector,
                "created_at": created_at,
                "updated_at": created_at,
                "metadata_json": json.dumps(metadata, sort_keys=True),
            }
        )
    return records


def connect_lancedb(cfg: RagConfig):
    import lancedb

    ensure_parent_dir(cfg.db_path)
    return lancedb.connect(cfg.db_path)


def open_or_create_table(cfg: RagConfig):
    db = connect_lancedb(cfg)
    table_names = set(db.table_names())
    if cfg.table_name in table_names:
        return db, db.open_table(cfg.table_name)

    schema_row = {
        "id": "__schema__",
        "source_id": "__schema__",
        "source_type": "schema",
        "chunk_index": -1,
        "text": "",
        "vector": [0.0] * cfg.vector_dim,
        "created_at": utc_now_iso(),
        "updated_at": utc_now_iso(),
        "metadata_json": "{}",
    }
    table = db.create_table(cfg.table_name, [schema_row])
    table.delete('id = "__schema__"')
    return db, table


def add_records(records: list[dict[str, Any]], cfg: RagConfig) -> dict[str, Any]:
    db, table = open_or_create_table(cfg)
    if records:
        table.add(records)
    return {
        "db_path": cfg.db_path,
        "table_name": cfg.table_name,
        "inserted": len(records),
        "source_ids": sorted({r["source_id"] for r in records}),
        "table_names": list(db.table_names()),
    }


def query_records(query: str, cfg: RagConfig, limit: int = DEFAULT_TOP_K) -> list[dict[str, Any]]:
    _db, table = open_or_create_table(cfg)
    vector = embed_texts([query], cfg)[0]
    results = table.search(vector).limit(limit).to_list()
    normalized: list[dict[str, Any]] = []
    for item in results:
        normalized.append(
            {
                "id": item.get("id"),
                "source_id": item.get("source_id"),
                "source_type": item.get("source_type"),
                "chunk_index": item.get("chunk_index"),
                "text": item.get("text"),
                "score": item.get("_distance"),
                "metadata_json": item.get("metadata_json"),
            }
        )
    return normalized


def _table_rows(table) -> list[dict[str, Any]]:
    if hasattr(table, "to_list"):
        return table.to_list()
    if hasattr(table, "search"):
        try:
            return table.search().limit(10_000).to_list()
        except TypeError:
            pass
    if hasattr(table, "to_arrow"):
        arrow = table.to_arrow()
        return [dict(zip(arrow.column_names, row)) for row in zip(*[col.to_pylist() for col in arrow.columns])]
    raise AttributeError("Unable to materialize LanceDB rows for stats")


def table_stats(cfg: RagConfig) -> dict[str, Any]:
    db, table = open_or_create_table(cfg)
    rows = _table_rows(table)
    return {
        "db_path": cfg.db_path,
        "table_name": cfg.table_name,
        "table_names": list(db.table_names()),
        "rows": len(rows),
        "source_ids": sorted({row.get("source_id") for row in rows if row.get("source_id")}),
        "source_types": sorted({row.get("source_type") for row in rows if row.get("source_type")}),
        "model": cfg.model,
        "vector_dim": cfg.vector_dim,
    }


def read_text_input(text_arg: str | None, file_path: str | None) -> str:
    if text_arg and file_path:
        raise ValueError("Provide either --text or --file, not both")
    if file_path:
        return Path(file_path).expanduser().read_text(encoding="utf-8")
    if text_arg:
        return text_arg
    raise ValueError("One of --text or --file is required")


def parse_metadata(raw: str | None) -> dict[str, Any]:
    if not raw:
        return {}
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("--metadata-json must decode to a JSON object")
    return value


def common_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--db-path", default=DEFAULT_DB_PATH)
    parser.add_argument("--table", default=DEFAULT_TABLE)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK_SIZE)
    parser.add_argument("--chunk-overlap", type=int, default=DEFAULT_CHUNK_OVERLAP)
    parser.add_argument("--no-normalize", action="store_true")
    return parser


def cfg_from_args(args: argparse.Namespace) -> RagConfig:
    return RagConfig(
        db_path=args.db_path,
        table_name=args.table,
        model=args.model,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        normalize=not args.no_normalize,
    )
