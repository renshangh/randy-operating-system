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
                    event_type TEXT,
                    event_action TEXT,
                    classification TEXT,
                    target_agent TEXT,
                    target_session_label TEXT,
                    target_session_key TEXT,
                    accepted INTEGER NOT NULL DEFAULT 0,
                    dispatch_decision TEXT NOT NULL,
                    run_id TEXT,
                    note TEXT,
                    session_send_status TEXT NOT NULL DEFAULT 'not_attempted',
                    session_send_error TEXT,
                    session_sent_at TEXT,
                    ack_status TEXT NOT NULL DEFAULT 'not_expected',
                    ack_action TEXT,
                    ack_message TEXT,
                    ack_received_at TEXT,
                    discord_notice_status TEXT NOT NULL DEFAULT 'not_attempted',
                    discord_notice_error TEXT,
                    discord_notice_at TEXT,
                    seen_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_run_ledger_repo_issue ON run_ledger(repository_full_name, issue_number)"
            )

    def has_delivery(self, delivery_id: str) -> bool:
        with self._connect() as conn:
            row = conn.execute("SELECT 1 FROM run_ledger WHERE delivery_id = ?", (delivery_id,)).fetchone()
            return row is not None

    def count_runs(self, repository_full_name: str, issue_number: int) -> int:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT COUNT(*) FROM run_ledger WHERE repository_full_name = ? AND issue_number = ? AND dispatch_decision IN ('running', 'done', 'failed')",
                (repository_full_name, issue_number),
            ).fetchone()
            return int(row[0] if row else 0)

    def record(
        self,
        delivery_id: str,
        repository_full_name: str,
        issue_number: int,
        dispatch_decision: str,
        *,
        event_type: str | None = None,
        event_action: str | None = None,
        classification: str | None = None,
        target_agent: str | None = None,
        target_session_label: str | None = None,
        target_session_key: str | None = None,
        accepted: bool = False,
        run_id: str | None = None,
        note: str | None = None,
        ack_status: str | None = None,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO run_ledger (
                    delivery_id, repository_full_name, issue_number, event_type, event_action,
                    classification, target_agent, target_session_label, target_session_key,
                    accepted, dispatch_decision, run_id, note, ack_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, COALESCE(?, 'not_expected'))
                ON CONFLICT(delivery_id) DO UPDATE SET
                    repository_full_name=excluded.repository_full_name,
                    issue_number=excluded.issue_number,
                    event_type=COALESCE(excluded.event_type, run_ledger.event_type),
                    event_action=COALESCE(excluded.event_action, run_ledger.event_action),
                    classification=COALESCE(excluded.classification, run_ledger.classification),
                    target_agent=COALESCE(excluded.target_agent, run_ledger.target_agent),
                    target_session_label=COALESCE(excluded.target_session_label, run_ledger.target_session_label),
                    target_session_key=COALESCE(excluded.target_session_key, run_ledger.target_session_key),
                    accepted=excluded.accepted,
                    dispatch_decision=excluded.dispatch_decision,
                    run_id=COALESCE(excluded.run_id, run_ledger.run_id),
                    note=COALESCE(excluded.note, run_ledger.note),
                    ack_status=COALESCE(excluded.ack_status, run_ledger.ack_status),
                    updated_at=CURRENT_TIMESTAMP
                """,
                (
                    delivery_id,
                    repository_full_name,
                    issue_number,
                    event_type,
                    event_action,
                    classification,
                    target_agent,
                    target_session_label,
                    target_session_key,
                    int(accepted),
                    dispatch_decision,
                    run_id,
                    note,
                    ack_status,
                ),
            )

    def mark_session_send(
        self,
        delivery_id: str,
        status: str,
        *,
        session_label: str | None = None,
        session_key: str | None = None,
        error: str | None = None,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE run_ledger
                SET session_send_status = ?,
                    target_session_label = COALESCE(?, target_session_label),
                    target_session_key = COALESCE(?, target_session_key),
                    session_send_error = ?,
                    session_sent_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE delivery_id = ?
                """,
                (status, session_label, session_key, error, delivery_id),
            )

    def mark_ack_status(self, delivery_id: str, status: str, *, action: str | None = None, message: str | None = None) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE run_ledger
                SET ack_status = ?,
                    ack_action = ?,
                    ack_message = ?,
                    ack_received_at = CASE WHEN ? = 'acked' THEN CURRENT_TIMESTAMP ELSE ack_received_at END,
                    updated_at = CURRENT_TIMESTAMP
                WHERE delivery_id = ?
                """,
                (status, action, message, status, delivery_id),
            )

    def mark_discord_notice(self, delivery_id: str, status: str, *, error: str | None = None) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE run_ledger
                SET discord_notice_status = ?,
                    discord_notice_error = ?,
                    discord_notice_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE delivery_id = ?
                """,
                (status, error, delivery_id),
            )
