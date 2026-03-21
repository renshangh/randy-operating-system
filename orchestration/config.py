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
    enable_direct_session_wake: bool = False
    aether_session_label: str = "aether-ops-inbox"
    aether_session_id: str = ""
    aether_session_registry: str = "~/.openclaw/workspace/aether_session_registry.json"
    session_send_timeout_seconds: int = 60
    session_ack_timeout_seconds: int = 120

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
        enable_direct_session_wake = os.environ.get("ENABLE_DIRECT_SESSION_WAKE", "0").lower() in {"1", "true", "yes", "on"}
        aether_session_label = os.environ.get("AETHER_SESSION_LABEL", "aether-ops-inbox")
        aether_session_id = os.environ.get("AETHER_SESSION_ID", "")
        aether_session_registry = os.environ.get("AETHER_SESSION_REGISTRY", "~/.openclaw/workspace/aether_session_registry.json")
        session_send_timeout_seconds = int(os.environ.get("SESSION_SEND_TIMEOUT_SECONDS", "60"))
        session_ack_timeout_seconds = int(os.environ.get("SESSION_ACK_TIMEOUT_SECONDS", "120"))
        return cls(
            github_webhook_secret=secret,
            allowed_repos=repos,
            host=host,
            port=port,
            discord_heartbeat_webhook_url=discord_webhook,
            discord_aether_user_id=discord_user_id,
            enable_direct_session_wake=enable_direct_session_wake,
            aether_session_label=aether_session_label,
            aether_session_id=aether_session_id,
            aether_session_registry=aether_session_registry,
            session_send_timeout_seconds=session_send_timeout_seconds,
            session_ack_timeout_seconds=session_ack_timeout_seconds,
        )
