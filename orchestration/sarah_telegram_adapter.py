from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

DEFAULT_SARAH_SESSIONS_INDEX = Path.home() / ".openclaw/agents/sarah/sessions/sessions.json"
DEFAULT_SARAH_SESSIONS_DIR = Path.home() / ".openclaw/agents/sarah/sessions"
SARAH_AGENT_ID = "sarah"
DEFAULT_SESSION_KEY_PREFIXES = ("agent:sarah:telegram:",)


@dataclass(frozen=True)
class SarahTelegramSource:
    session_key: str
    session_id: str
    transcript_path: str
    account_id: str
    chat_id: str
    chat_type: str
    subject: str


@dataclass(frozen=True)
class SarahMirrorEvent:
    source_name: str
    source_session_key: str
    source_session_id: str
    source_account_id: str
    source_chat_id: str
    source_chat_type: str
    source_subject: str
    source_event_id: str
    source_role: str
    source_timestamp: str
    transcript_path: str
    transcript_line_number: int
    text: str
    dedupe_key: str

    def to_discord_message(self) -> str:
        header = (
            "Sarah telegram mirror\n"
            f"session: {self.source_session_key}\n"
            f"account: {self.source_account_id}\n"
            f"chat: {self.source_chat_id}\n"
            f"chat_type: {self.source_chat_type}\n"
            f"subject: {self.source_subject or '-'}\n"
            f"role: {self.source_role}\n"
            f"event: {self.source_event_id}\n"
            f"timestamp: {self.source_timestamp}"
        )
        body = self.text.strip() or "(no visible text)"
        return f"{header}\n```\n{body[:1600]}\n```"


class SarahTelegramAdapter:
    def __init__(self, sessions_index_path: str | Path = DEFAULT_SARAH_SESSIONS_INDEX):
        self.sessions_index_path = Path(sessions_index_path).expanduser()

    def discover_sources(
        self,
        *,
        session_key_prefixes: tuple[str, ...] = DEFAULT_SESSION_KEY_PREFIXES,
        explicit_session_keys: set[str] | None = None,
    ) -> list[SarahTelegramSource]:
        payload = json.loads(self.sessions_index_path.read_text(encoding="utf-8"))
        sources: list[SarahTelegramSource] = []
        explicit_session_keys = explicit_session_keys or set()
        for session_key, entry in payload.items():
            if not self._should_include_session(
                session_key,
                entry,
                session_key_prefixes=session_key_prefixes,
                explicit_session_keys=explicit_session_keys,
            ):
                continue
            session_id = str(entry.get("sessionId") or "").strip()
            session_file = str(entry.get("sessionFile") or "").strip()
            origin = entry.get("origin") or {}
            delivery_context = entry.get("deliveryContext") or {}
            if not session_id or not session_file:
                continue
            sources.append(
                SarahTelegramSource(
                    session_key=session_key,
                    session_id=session_id,
                    transcript_path=session_file,
                    account_id=str(
                        origin.get("accountId")
                        or delivery_context.get("accountId")
                        or entry.get("lastAccountId")
                        or ""
                    ),
                    chat_id=str(
                        entry.get("groupId")
                        or origin.get("to")
                        or delivery_context.get("to")
                        or ""
                    ),
                    chat_type=str(
                        entry.get("chatType")
                        or origin.get("chatType")
                        or delivery_context.get("chatType")
                        or delivery_context.get("channel")
                        or entry.get("lastChannel")
                        or ""
                    ),
                    subject=str(entry.get("subject") or entry.get("displayName") or ""),
                )
            )
        return sorted(sources, key=lambda item: item.session_key)

    def iter_events(self, source: SarahTelegramSource, *, start_line: int = 0) -> Iterable[SarahMirrorEvent]:
        transcript_path = Path(source.transcript_path).expanduser()
        with transcript_path.open("r", encoding="utf-8") as handle:
            for line_number, raw_line in enumerate(handle, start=1):
                if line_number <= start_line:
                    continue
                raw_line = raw_line.strip()
                if not raw_line:
                    continue
                try:
                    entry = json.loads(raw_line)
                except json.JSONDecodeError:
                    continue
                event = self._normalize_event(source, transcript_path, entry, line_number)
                if event is not None:
                    yield event

    def _should_include_session(
        self,
        session_key: str,
        entry: dict[str, Any],
        *,
        session_key_prefixes: tuple[str, ...],
        explicit_session_keys: set[str],
    ) -> bool:
        if session_key in explicit_session_keys:
            return True
        if any(session_key.startswith(prefix) for prefix in session_key_prefixes):
            return True
        channel_candidates = {
            str(entry.get("channel") or "").strip().lower(),
            str(entry.get("lastChannel") or "").strip().lower(),
            str((entry.get("origin") or {}).get("channel") or "").strip().lower(),
            str((entry.get("origin") or {}).get("chatType") or "").strip().lower(),
            str((entry.get("deliveryContext") or {}).get("channel") or "").strip().lower(),
            str(entry.get("chatType") or "").strip().lower(),
        }
        if "telegram" not in channel_candidates:
            return False
        agent_candidates = {
            session_key.lower(),
            str(entry.get("displayName") or "").strip().lower(),
            str(entry.get("subject") or "").strip().lower(),
            str(entry.get("label") or "").strip().lower(),
        }
        return any("sarah" in candidate for candidate in agent_candidates if candidate)

    def _normalize_event(
        self,
        source: SarahTelegramSource,
        transcript_path: Path,
        entry: dict[str, Any],
        line_number: int,
    ) -> SarahMirrorEvent | None:
        if entry.get("type") != "message":
            return None
        message = entry.get("message") or {}
        role = str(message.get("role") or "").strip().lower()
        if role not in {"user", "assistant"}:
            return None
        text = self._extract_visible_text(message.get("content") or [])
        if not text:
            return None
        source_event_id = str(entry.get("id") or f"line-{line_number}")
        source_timestamp = str(entry.get("timestamp") or message.get("timestamp") or "")
        dedupe_seed = "|".join([
            SARAH_AGENT_ID,
            source.session_id,
            source_event_id,
            role,
            source_timestamp,
        ])
        return SarahMirrorEvent(
            source_name=SARAH_AGENT_ID,
            source_session_key=source.session_key,
            source_session_id=source.session_id,
            source_account_id=source.account_id,
            source_chat_id=source.chat_id,
            source_chat_type=source.chat_type,
            source_subject=source.subject,
            source_event_id=source_event_id,
            source_role=role,
            source_timestamp=source_timestamp,
            transcript_path=str(transcript_path),
            transcript_line_number=line_number,
            text=text,
            dedupe_key=hashlib.sha256(dedupe_seed.encode("utf-8")).hexdigest(),
        )

    def _extract_visible_text(self, content: list[dict[str, Any]]) -> str:
        parts: list[str] = []
        for item in content:
            if item.get("type") != "text":
                continue
            text = str(item.get("text") or "").strip()
            if text:
                parts.append(text)
        return "\n\n".join(parts).strip()
