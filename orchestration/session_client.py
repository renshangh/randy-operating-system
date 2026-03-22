from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
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

    def handoff_target(self) -> dict[str, str | None]:
        return {
            "session_label": self.config.aether_session_label,
            "session_id": self._resolve_session_id(),
        }

    def send_event(self, packet: dict[str, Any]) -> SessionSendResult:
        if not self.config.enable_direct_session_wake:
            return SessionSendResult(
                ok=False,
                status="disabled",
                session_label=self.config.aether_session_label,
                error="direct_session_wake_disabled",
            )

        session_id = self._resolve_session_id()
        if not session_id:
            return SessionSendResult(
                ok=False,
                status="failed",
                session_label=self.config.aether_session_label,
                error="missing_aether_session_id",
            )

        message = self._format_message(packet)
        openclaw_bin = shutil.which("openclaw") or "openclaw"
        command = [
            openclaw_bin,
            "agent",
            "--session-id",
            session_id,
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
                session_id=session_id,
                error=str(exc),
            )

        stdout = (completed.stdout or "").strip()
        stderr = (completed.stderr or "").strip()
        if completed.returncode != 0:
            return SessionSendResult(
                ok=False,
                status="failed",
                session_label=self.config.aether_session_label,
                session_id=session_id,
                error=stderr or stdout or f"openclaw agent exit {completed.returncode}",
                stdout=stdout,
            )

        return SessionSendResult(
            ok=True,
            status="sent",
            session_label=self.config.aether_session_label,
            session_id=session_id,
            stdout=stdout,
        )

    def _resolve_session_id(self) -> str | None:
        if self.config.aether_session_id and self.config.aether_session_id != "REPLACE_ME":
            return self.config.aether_session_id

        registry_path = Path(os.path.expanduser(self.config.aether_session_registry))
        try:
            data = json.loads(registry_path.read_text())
        except Exception:
            return None

        entry = data.get(self.config.aether_session_label)
        if isinstance(entry, dict):
            return entry.get("sessionId")
        if isinstance(entry, str):
            return entry
        return None

    def _format_message(self, packet: dict[str, Any]) -> str:
        payload = json.dumps(packet, ensure_ascii=False, indent=2)
        return (
            "SYSTEM EVENT: GitHub webhook actionable event\n\n"
            "Process this event as an operations wake notification. "
            "Acknowledge receipt, decide whether follow-up is needed, and keep actions narrow to the issue context.\n\n"
            f"{payload}"
        )
