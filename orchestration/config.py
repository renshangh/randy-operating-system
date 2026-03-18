from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ListenerConfig:
    github_webhook_secret: str
    allowed_repos: tuple[str, ...]
    host: str = "127.0.0.1"
    port: int = 8787
    discord_heartbeat_webhook_url: str = ""
    discord_aether_user_id: str = ""

    @classmethod
    def from_env(cls) -> "ListenerConfig":
        secret = os.environ.get("GITHUB_WEBHOOK_SECRET", "")
        repos_raw = os.environ.get(
            "ALLOWED_REPOS",
            "renshangh/real-estate-assistant,renshangh/openclaw-remote-deploy",
        )
        repos = tuple(r.strip() for r in repos_raw.split(",") if r.strip())
        host = os.environ.get("LISTENER_HOST", "127.0.0.1")
        port = int(os.environ.get("LISTENER_PORT", "8787"))
        discord_webhook = os.environ.get("DISCORD_HEARTBEAT_WEBHOOK_URL", "")
        discord_user_id = os.environ.get("DISCORD_AETHER_USER_ID", "")
        return cls(
            github_webhook_secret=secret,
            allowed_repos=repos,
            host=host,
            port=port,
            discord_heartbeat_webhook_url=discord_webhook,
            discord_aether_user_id=discord_user_id,
        )
