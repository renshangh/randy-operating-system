from __future__ import annotations

import json
import os
import shutil
import sqlite3
import subprocess
import threading
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
import time

ALLOWED_CLASSIFICATIONS = {
    "completion:done",
    "completion:blocked",
    "completion:failed",
    "command:retry",
    "command:status",
    "command:hold",
}
REQUIRED_FIELDS = {
    "kind",
    "delivery_id",
    "repository_full_name",
    "issue_number",
    "classification",
    "summary",
    "sent_at",
}


@dataclass(frozen=True)
class RelayIngressConfig:
    host: str = "127.0.0.1"
    port: int = 8791
    relay_secret: str = ""
    relay_sender_id: str = "mac-mini"
    aether_agent_id: str = "main"
    aether_session_label: str = "aether-ops-inbox"
    aether_session_id: str = ""
    session_store_path: str = ""
    session_registry_path: str = "~/.openclaw/workspace/aether_session_registry.json"
    openclaw_bin: str = ""
    inject_timeout_seconds: int = 30
    inject_retry_attempts: int = 4
    inject_retry_delay_seconds: float = 2.0
    dedupe_db_path: str = "orchestration/aether_relay_ingress.sqlite"

    @classmethod
    def from_env(cls) -> "RelayIngressConfig":
        return cls(
            host=os.environ.get("AETHER_RELAY_HOST", "127.0.0.1"),
            port=int(os.environ.get("AETHER_RELAY_PORT", "8791")),
            relay_secret=os.environ.get("AETHER_RELAY_SECRET", ""),
            relay_sender_id=os.environ.get("AETHER_RELAY_SENDER_ID", "mac-mini"),
            aether_agent_id=os.environ.get("AETHER_AGENT_ID", "main"),
            aether_session_label=os.environ.get("AETHER_SESSION_LABEL", "aether-ops-inbox"),
            aether_session_id=os.environ.get("AETHER_SESSION_ID", ""),
            session_registry_path=os.environ.get("AETHER_SESSION_REGISTRY", "~/.openclaw/workspace/aether_session_registry.json"),
            session_store_path=os.environ.get("AETHER_SESSION_STORE", ""),
            openclaw_bin=os.environ.get("OPENCLAW_BIN", shutil.which("openclaw") or "openclaw"),
            inject_timeout_seconds=int(os.environ.get("AETHER_RELAY_TIMEOUT_SECONDS", "30")),
            inject_retry_attempts=int(os.environ.get("AETHER_RELAY_RETRY_ATTEMPTS", "4")),
            inject_retry_delay_seconds=float(os.environ.get("AETHER_RELAY_RETRY_DELAY_SECONDS", "2")),
            dedupe_db_path=os.environ.get(
                "AETHER_RELAY_DEDUPE_DB", "orchestration/aether_relay_ingress.sqlite"
            ),
        )


class RelayIngressLedger:
    def __init__(self, db_path: str | Path):
        self.db_path = str(db_path)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS relay_events (
                    delivery_id TEXT PRIMARY KEY,
                    sender_id TEXT NOT NULL,
                    repository_full_name TEXT NOT NULL,
                    issue_number INTEGER NOT NULL,
                    classification TEXT NOT NULL,
                    status TEXT NOT NULL,
                    session_label TEXT,
                    session_id TEXT,
                    note TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def get(self, delivery_id: str) -> sqlite3.Row | None:
        with self._connect() as conn:
            return conn.execute(
                "SELECT * FROM relay_events WHERE delivery_id = ?", (delivery_id,)
            ).fetchone()

    def record(
        self,
        delivery_id: str,
        *,
        sender_id: str,
        repository_full_name: str,
        issue_number: int,
        classification: str,
        status: str,
        session_label: str | None = None,
        session_id: str | None = None,
        note: str | None = None,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO relay_events (
                    delivery_id, sender_id, repository_full_name, issue_number,
                    classification, status, session_label, session_id, note
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(delivery_id) DO UPDATE SET
                    status = excluded.status,
                    session_label = COALESCE(excluded.session_label, relay_events.session_label),
                    session_id = COALESCE(excluded.session_id, relay_events.session_id),
                    note = COALESCE(excluded.note, relay_events.note),
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    delivery_id,
                    sender_id,
                    repository_full_name,
                    issue_number,
                    classification,
                    status,
                    session_label,
                    session_id,
                    note,
                ),
            )


class AetherSessionInjector:
    def __init__(self, config: RelayIngressConfig):
        self.config = config

    def inject(self, packet: dict[str, Any]) -> dict[str, Any]:
        session_id = self._resolve_session_id()
        if not session_id:
            return {
                "ok": False,
                "error": "missing_aether_session_id",
            }

        message = self._format_message(packet)
        command = [
            self.config.openclaw_bin,
            "agent",
            "--session-id",
            session_id,
            "--message",
            message,
            "--timeout",
            str(self.config.inject_timeout_seconds),
            "--json",
        ]

        last_error = "session_injection_failed"
        attempts = max(1, self.config.inject_retry_attempts)
        for attempt in range(1, attempts + 1):
            try:
                completed = subprocess.run(command, capture_output=True, text=True, check=False)
            except Exception as exc:  # noqa: BLE001
                last_error = str(exc)
                completed = None
            else:
                stdout = (completed.stdout or "").strip()
                stderr = (completed.stderr or "").strip()
                if completed.returncode == 0:
                    return {
                        "ok": True,
                        "session_label": self.config.aether_session_label,
                        "session_id": session_id,
                        "stdout": stdout,
                    }
                last_error = stderr or stdout or f"openclaw agent exit {completed.returncode}"

            if attempt < attempts and self._is_retryable_error(last_error):
                time.sleep(self.config.inject_retry_delay_seconds * attempt)
                continue
            break

        return {
            "ok": False,
            "error": last_error,
        }

    def resolve_session_id(self) -> str | None:
        return self._resolve_session_id()

    def _resolve_session_id(self) -> str | None:
        if self.config.aether_session_id and self.config.aether_session_id != "REPLACE_ME":
            return self.config.aether_session_id
        session_store_path = self.config.session_store_path or os.path.expanduser(
            f"~/.openclaw/agents/{self.config.aether_agent_id}/sessions/sessions.json"
        )
        try:
            data = json.loads(Path(session_store_path).read_text())
        except Exception:
            return self._resolve_from_registry(self.config.aether_session_label)
        sessions = data.get("sessions", [])
        candidates = [
            session
            for session in sessions
            if session.get("agentId") == self.config.aether_agent_id
            and session.get("kind") == "direct"
        ]
        label = self.config.aether_session_label
        if label:
            exact = [session for session in candidates if session.get("key") == label]
            if exact:
                return max(exact, key=lambda s: s.get("updatedAt", 0)).get("sessionId")
            partial = [
                session for session in candidates if label in (session.get("key") or "")
            ]
            if partial:
                return max(partial, key=lambda s: s.get("updatedAt", 0)).get("sessionId")
        if candidates:
            return max(candidates, key=lambda s: s.get("updatedAt", 0)).get("sessionId")
        return self._resolve_from_registry(label)

    def _resolve_from_registry(self, label: str | None) -> str | None:
        if not label:
            return None
        registry_path = Path(os.path.expanduser(self.config.session_registry_path))
        try:
            data = json.loads(registry_path.read_text())
        except Exception:
            return None
        entry = data.get(label)
        if isinstance(entry, dict):
            return entry.get("sessionId")
        if isinstance(entry, str):
            return entry
        return None

    def _is_retryable_error(self, error: str) -> bool:
        lowered = error.lower()
        return "session file locked" in lowered or "timeout" in lowered

    def _format_message(self, packet: dict[str, Any]) -> str:
        payload = json.dumps(packet, ensure_ascii=False, indent=2)
        return (
            "GitHub relay event received.\n\n"
            "Inject this event into Aether's operations context. "
            "Acknowledge receipt and keep actions narrow to the referenced issue context.\n\n"
            f"{payload}"
        )


class RelayHandler(BaseHTTPRequestHandler):
    server: "RelayIngressServer"

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/aether-relay/v1/events":
            self._respond(HTTPStatus.NOT_FOUND, {"ok": False, "error": "not_found"})
            return

        if not self.server.config.relay_secret:
            self._respond(HTTPStatus.SERVICE_UNAVAILABLE, {"ok": False, "error": "relay_secret_not_configured"})
            return

        relay_key = self.headers.get("X-Aether-Relay-Key", "")
        relay_sender_id = self.headers.get("X-Aether-Relay-Id", "")
        delivery_id = self.headers.get("X-Aether-Delivery-Id", "")
        if relay_key != self.server.config.relay_secret or relay_sender_id != self.server.config.relay_sender_id:
            self._respond(HTTPStatus.UNAUTHORIZED, {"ok": False, "error": "unauthorized"})
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._respond(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "invalid_content_length"})
            return

        raw_body = self.rfile.read(content_length)
        try:
            packet = json.loads(raw_body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._respond(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "invalid_json"})
            return

        validation_error = self._validate_packet(packet, delivery_id)
        if validation_error:
            self._respond(HTTPStatus.UNPROCESSABLE_ENTITY, validation_error)
            return

        existing = self.server.ledger.get(delivery_id)
        if existing is not None:
            self._respond(
                HTTPStatus.OK,
                {
                    "ok": True,
                    "delivery_id": delivery_id,
                    "status": "duplicate",
                    "action": "none",
                    "target": "aether",
                    "session_label": existing["session_label"] or self.server.config.aether_session_label,
                },
            )
            return

        self._respond(
            HTTPStatus.ACCEPTED,
            {
                "ok": True,
                "delivery_id": delivery_id,
                "status": "accepted",
                "action": "queued",
                "target": "aether",
                "session_label": self.server.config.aether_session_label,
            },
        )
        self.server.accept_async(delivery_id, relay_sender_id, packet)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        return

    def _validate_packet(self, packet: dict[str, Any], delivery_id: str) -> dict[str, Any] | None:
        missing = sorted(field for field in REQUIRED_FIELDS if packet.get(field) in (None, ""))
        if missing:
            return {"ok": False, "error": "invalid_payload", "details": [f"missing: {', '.join(missing)}"]}
        if packet.get("kind") != "github_webhook_event":
            return {"ok": False, "error": "invalid_payload", "details": ["kind must be github_webhook_event"]}
        if packet.get("delivery_id") != delivery_id:
            return {"ok": False, "error": "invalid_payload", "details": ["delivery_id header/body mismatch"]}
        if packet.get("classification") not in ALLOWED_CLASSIFICATIONS:
            return {
                "ok": False,
                "error": "invalid_payload",
                "details": ["classification is not allowed"],
            }
        return None

    def _respond(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        try:
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except BrokenPipeError:
            return


class RelayIngressServer(ThreadingHTTPServer):
    def __init__(self, config: RelayIngressConfig):
        self.config = config
        self.ledger = RelayIngressLedger(config.dedupe_db_path)
        self.injector = AetherSessionInjector(config)
        super().__init__((config.host, config.port), RelayHandler)

    def accept_async(self, delivery_id: str, relay_sender_id: str, packet: dict[str, Any]) -> None:
        worker = threading.Thread(
            target=self._record_and_inject,
            args=(delivery_id, relay_sender_id, packet),
            daemon=True,
        )
        worker.start()

    def _record_and_inject(self, delivery_id: str, relay_sender_id: str, packet: dict[str, Any]) -> None:
        session_id = self.injector.resolve_session_id()
        self.ledger.record(
            delivery_id,
            sender_id=relay_sender_id,
            repository_full_name=packet["repository_full_name"],
            issue_number=int(packet["issue_number"]),
            classification=packet["classification"],
            status="accepted",
            session_label=self.config.aether_session_label,
            session_id=session_id or None,
        )
        self._inject_and_record(delivery_id, relay_sender_id, packet)

    def _inject_and_record(self, delivery_id: str, relay_sender_id: str, packet: dict[str, Any]) -> None:
        injection = self.injector.inject(packet)
        if not injection.get("ok"):
            self.ledger.record(
                delivery_id,
                sender_id=relay_sender_id,
                repository_full_name=packet["repository_full_name"],
                issue_number=int(packet["issue_number"]),
                classification=packet["classification"],
                status="failed",
                session_label=self.config.aether_session_label,
                session_id=self.injector.resolve_session_id() or None,
                note=str(injection.get("error") or "session_injection_failed"),
            )
            return
        self.ledger.record(
            delivery_id,
            sender_id=relay_sender_id,
            repository_full_name=packet["repository_full_name"],
            issue_number=int(packet["issue_number"]),
            classification=packet["classification"],
            status="acked",
            session_label=injection.get("session_label") or self.config.aether_session_label,
            session_id=injection.get("session_id") or self.config.aether_session_id or None,
        )


def main() -> None:
    config = RelayIngressConfig.from_env()
    Path(config.dedupe_db_path).parent.mkdir(parents=True, exist_ok=True)
    server = RelayIngressServer(config)
    print(
        f"Starting Aether relay ingress host={config.host} port={config.port} session_label={config.aether_session_label}",
        flush=True,
    )
    server.serve_forever()


if __name__ == "__main__":
    main()
