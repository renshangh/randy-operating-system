from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib import request
from urllib.error import HTTPError, URLError

from orchestration.config import ListenerConfig


@dataclass(frozen=True)
class RelaySendResult:
    ok: bool
    status: str
    session_label: str
    session_id: str | None = None
    action: str | None = None
    error: str | None = None
    http_status: int | None = None
    response: dict[str, Any] | None = None


class RelayClient:
    def __init__(self, config: ListenerConfig):
        self.config = config

    def send_event(self, packet: dict[str, Any]) -> RelaySendResult:
        if not self.config.enable_aether_relay:
            return RelaySendResult(
                ok=False,
                status="disabled",
                session_label=self.config.aether_relay_label,
                error="aether_relay_disabled",
            )

        if not self.config.aether_relay_url or not self.config.aether_relay_secret:
            return RelaySendResult(
                ok=False,
                status="failed",
                session_label=self.config.aether_relay_label,
                error="missing_relay_url_or_secret",
            )

        payload = json.dumps(packet).encode("utf-8")
        req = request.Request(
            self.config.aether_relay_url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "X-Aether-Relay-Key": self.config.aether_relay_secret,
                "X-Aether-Relay-Id": self.config.aether_relay_sender_id,
                "X-Aether-Delivery-Id": str(packet.get("delivery_id") or ""),
            },
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self.config.aether_relay_timeout_seconds) as response:
                body = response.read().decode("utf-8", errors="replace")
                parsed = json.loads(body) if body else {}
                status_code = getattr(response, "status", response.getcode())
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            error = body or f"http_{exc.code}"
            return RelaySendResult(
                ok=False,
                status="failed",
                session_label=self.config.aether_relay_label,
                error=error,
                http_status=exc.code,
            )
        except (URLError, TimeoutError, json.JSONDecodeError) as exc:
            return RelaySendResult(
                ok=False,
                status="failed",
                session_label=self.config.aether_relay_label,
                error=str(exc),
            )

        relay_status = str(parsed.get("status") or "acked")
        ok = bool(parsed.get("ok", False))
        return RelaySendResult(
            ok=ok,
            status=relay_status,
            session_label=str(parsed.get("session_label") or self.config.aether_relay_label),
            session_id=parsed.get("session_id"),
            action=parsed.get("action"),
            http_status=status_code,
            response=parsed,
        )
