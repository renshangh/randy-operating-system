from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


class RunLedger:
    def __init__(self, db_path: str | Path):
        self.db_path = str(db_path)
        self._init_db()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS run_ledger (
                    delivery_id TEXT PRIMARY KEY,
                    repository_full_name TEXT NOT NULL,
                    issue_number INTEGER NOT NULL,
                    seen_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    dispatch_decision TEXT NOT NULL,
                    run_id TEXT,
                    note TEXT
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_run_ledger_repo_issue ON run_ledger(repository_full_name, issue_number)"
            )

    def has_delivery(self, delivery_id: str) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM run_ledger WHERE delivery_id = ?", (delivery_id,)
            ).fetchone()
            return row is not None

    def record(self, delivery_id: str, repository_full_name: str, issue_number: int, dispatch_decision: str, run_id: str | None = None, note: str | None = None) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO run_ledger
                (delivery_id, repository_full_name, issue_number, dispatch_decision, run_id, note)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (delivery_id, repository_full_name, issue_number, dispatch_decision, run_id, note),
            )
