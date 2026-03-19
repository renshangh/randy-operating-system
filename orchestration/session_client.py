from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from typing import Any

from orchestration.config import ListenerConfig


@dataclass(frozen=True)
class SessionSendResult:
    ok: bool
    status: str
    session_label: str
    session_id: str | None = None
    error: str | None = None
    stdout: str | None = None


class SessionClient:
    def __init__(self, config: ListenerConfig):
        self.config = config

    def send_event(self, packet: dict[str, Any]) -> SessionSendResult:
        if not self.config.enable_direct_session_wake:
            return SessionSendResult(
                ok=False,
                status="disabled",
                session_label=self.config.aether_session_label,
                error="direct_session_wake_disabled",
            )

        if not self.config.aether_session_id:
            return SessionSendResult(
                ok=False,
                status="failed",
                session_label=self.config.aether_session_label,
                error="missing_aether_session_id",
            )

        message = self._format_message(packet)
        command = [
            "openclaw",
            "agent",
            "--session-id",
            self.config.aether_session_id,
            "--message",
            message,
            "--timeout",
            str(self.config.session_send_timeout_seconds),
            "--json",
        ]
        try:
            completed = subprocess.run(command, capture_output=True, text=True, check=False)
        except Exception as exc:  # noqa: BLE001
            return SessionSendResult(
                ok=False,
                status="failed",
                session_label=self.config.aether_session_label,
                session_id=self.config.aether_session_id,
                error=str(exc),
            )

        stdout = (completed.stdout or "").strip()
        stderr = (completed.stderr or "").strip()
        if completed.returncode != 0:
            return SessionSendResult(
                ok=False,
                status="failed",
                session_label=self.config.aether_session_label,
                session_id=self.config.aether_session_id,
                error=stderr or stdout or f"openclaw agent exit {completed.returncode}",
                stdout=stdout,
            )

        return SessionSendResult(
            ok=True,
            status="sent",
            session_label=self.config.aether_session_label,
            session_id=self.config.aether_session_id,
            stdout=stdout,
        )

    def _format_message(self, packet: dict[str, Any]) -> str:
        payload = json.dumps(packet, ensure_ascii=False, indent=2)
        return (
            "SYSTEM EVENT: GitHub webhook actionable event\n\n"
            "Process this event as an operations wake notification. "
            "Acknowledge receipt, decide whether follow-up is needed, and keep actions narrow to the issue context.\n\n"
            f"{payload}"
        )
