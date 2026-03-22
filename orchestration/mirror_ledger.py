from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


class MirrorLedger:
    def __init__(self, db_path: str | Path):
        self.db_path = str(db_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS mirror_deliveries (
                    dedupe_key TEXT PRIMARY KEY,
                    source_name TEXT NOT NULL,
                    source_session_id TEXT NOT NULL,
                    source_event_id TEXT NOT NULL,
                    source_role TEXT NOT NULL,
                    source_timestamp TEXT NOT NULL,
                    transcript_path TEXT NOT NULL,
                    transcript_offset INTEGER NOT NULL,
                    discord_status TEXT NOT NULL DEFAULT 'pending',
                    discord_http_status INTEGER,
                    discord_error TEXT,
                    delivered_at TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS mirror_cursors (
                    source_name TEXT NOT NULL,
                    transcript_path TEXT NOT NULL,
                    last_line_number INTEGER NOT NULL DEFAULT 0,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (source_name, transcript_path)
                )
                """
            )

    def has_delivery(self, dedupe_key: str) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM mirror_deliveries WHERE dedupe_key = ?",
                (dedupe_key,),
            ).fetchone()
            return row is not None

    def record_delivery_attempt(
        self,
        *,
        dedupe_key: str,
        source_name: str,
        source_session_id: str,
        source_event_id: str,
        source_role: str,
        source_timestamp: str,
        transcript_path: str,
        transcript_offset: int,
        discord_status: str,
        discord_http_status: int | None = None,
        discord_error: str | None = None,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO mirror_deliveries (
                    dedupe_key, source_name, source_session_id, source_event_id, source_role,
                    source_timestamp, transcript_path, transcript_offset, discord_status,
                    discord_http_status, discord_error, delivered_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CASE WHEN ? = 'sent' THEN CURRENT_TIMESTAMP ELSE NULL END)
                ON CONFLICT(dedupe_key) DO UPDATE SET
                    discord_status = excluded.discord_status,
                    discord_http_status = COALESCE(excluded.discord_http_status, mirror_deliveries.discord_http_status),
                    discord_error = COALESCE(excluded.discord_error, mirror_deliveries.discord_error),
                    delivered_at = CASE
                        WHEN excluded.discord_status = 'sent' THEN CURRENT_TIMESTAMP
                        ELSE mirror_deliveries.delivered_at
                    END,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    dedupe_key,
                    source_name,
                    source_session_id,
                    source_event_id,
                    source_role,
                    source_timestamp,
                    transcript_path,
                    transcript_offset,
                    discord_status,
                    discord_http_status,
                    discord_error,
                    discord_status,
                ),
            )

    def get_cursor(self, source_name: str, transcript_path: str) -> int:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT last_line_number FROM mirror_cursors WHERE source_name = ? AND transcript_path = ?",
                (source_name, transcript_path),
            ).fetchone()
            return int(row[0]) if row else 0

    def update_cursor(self, source_name: str, transcript_path: str, last_line_number: int) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO mirror_cursors (source_name, transcript_path, last_line_number)
                VALUES (?, ?, ?)
                ON CONFLICT(source_name, transcript_path) DO UPDATE SET
                    last_line_number = excluded.last_line_number,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (source_name, transcript_path, last_line_number),
            )
