from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib import request
from urllib.error import HTTPError, URLError


@dataclass(frozen=True)
class DiscordSendResult:
    ok: bool
    status: str
    http_status: int | None = None
    error: str | None = None
    response_body: str | None = None


class DiscordWebhookOutput:
    def __init__(self, webhook_url: str, *, timeout_seconds: int = 10):
        self.webhook_url = webhook_url.strip()
        self.timeout_seconds = timeout_seconds

    def send_content(self, content: str) -> DiscordSendResult:
        if not self.webhook_url:
            return DiscordSendResult(ok=False, status="disabled", error="webhook_not_configured")

        payload = json.dumps({"content": content}).encode("utf-8")
        req = request.Request(
            self.webhook_url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "randy-operating-system/discord-output/1.0",
            },
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as response:
                body = response.read().decode("utf-8", errors="replace")
                status_code = getattr(response, "status", response.getcode())
            return DiscordSendResult(
                ok=True,
                status="sent",
                http_status=status_code,
                response_body=body or None,
            )
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            return DiscordSendResult(
                ok=False,
                status="failed",
                http_status=exc.code,
                error=body or f"http_{exc.code}",
                response_body=body or None,
            )
        except URLError as exc:
            return DiscordSendResult(ok=False, status="failed", error=str(exc))
