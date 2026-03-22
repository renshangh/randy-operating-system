from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from zoneinfo import ZoneInfo

AMY_AGENT_ID = "amy"
AMY_ACCOUNT_ID = "amy-tg"
AMY_CHAT_ID = "5507785599"
AMY_SESSION_KEY = "agent:amy:main"
LOCAL_TIMEZONE = ZoneInfo("America/Chicago")
SESSIONS_DIR = Path.home() / ".openclaw/agents/amy/sessions"
SESSIONS_INDEX_PATH = SESSIONS_DIR / "sessions.json"


def _extract_session_id_from_sessions_index(payload: Any) -> str | None:
    candidates: list[dict[str, Any]] = []

    if isinstance(payload, dict):
        for key in ("sessions", "items", "data"):
            value = payload.get(key)
            if isinstance(value, list):
                candidates.extend(item for item in value if isinstance(item, dict))
        if all(not isinstance(v, list) for v in payload.values()):
            candidates.append(payload)
    elif isinstance(payload, list):
        candidates.extend(item for item in payload if isinstance(item, dict))

    def score(item: dict[str, Any]) -> tuple[int, str]:
        session_id = str(item.get("id") or item.get("sessionId") or item.get("session_id") or "")
        timestamp = str(
            item.get("updatedAt")
            or item.get("updated_at")
            or item.get("lastActivityAt")
            or item.get("last_activity_at")
            or item.get("createdAt")
            or item.get("created_at")
            or ""
        )
        active = item.get("active") is True or str(item.get("status") or "").lower() in {"active", "running", "open"}
        return (1 if active else 0, timestamp + session_id)

    best_session_id: str | None = None
    best_score: tuple[int, str] | None = None
    for item in candidates:
        session_id = str(item.get("id") or item.get("sessionId") or item.get("session_id") or "").strip()
        if not session_id:
            continue
        item_score = score(item)
        if best_score is None or item_score > best_score:
            best_score = item_score
            best_session_id = session_id
    return best_session_id


def resolve_current_amy_transcript() -> Path:
    if SESSIONS_INDEX_PATH.exists():
        try:
            payload = json.loads(SESSIONS_INDEX_PATH.read_text(encoding="utf-8"))
            session_id = _extract_session_id_from_sessions_index(payload)
            if session_id:
                candidate = SESSIONS_DIR / f"{session_id}.jsonl"
                if candidate.exists():
                    return candidate
        except Exception:
            pass

    candidates = [
        path
        for path in SESSIONS_DIR.glob("*.jsonl")
        if path.is_file() and ".reset." not in path.name
    ]
    if not candidates:
        raise FileNotFoundError(f"No Amy transcript .jsonl files found in {SESSIONS_DIR}")
    return max(candidates, key=lambda path: path.stat().st_mtime)


def _format_local_timestamp(raw_timestamp: str) -> str:
    if not raw_timestamp:
        return ""
    normalized = raw_timestamp.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return raw_timestamp
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    local_dt = parsed.astimezone(LOCAL_TIMEZONE)
    return local_dt.strftime("%Y-%m-%d %H:%M %Z")


DEFAULT_TRANSCRIPT_PATH = resolve_current_amy_transcript()


@dataclass(frozen=True)
class MirrorEvent:
    source_name: str
    source_session_id: str
    source_session_key: str
    source_account_id: str
    source_chat_id: str
    source_event_id: str
    source_role: str
    source_timestamp: str
    transcript_path: str
    transcript_line_number: int
    text: str
    dedupe_key: str

    def to_discord_message(self) -> str:
        header = (
            "Amy transcript mirror\n"
            f"session: {self.source_session_key}\n"
            f"account: {self.source_account_id}\n"
            f"chat: {self.source_chat_id}\n"
            f"role: {self.source_role}\n"
            f"event: {self.source_event_id}\n"
            f"timestamp: {_format_local_timestamp(self.source_timestamp)}"
        )
        body = self.text.strip() or "(no visible text)"
        return f"{header}\n```\n{body[:1600]}\n```"


class AmyTranscriptAdapter:
    def __init__(self, transcript_path: str | Path | None = None):
        resolved_path = transcript_path if transcript_path is not None else resolve_current_amy_transcript()
        self.transcript_path = Path(resolved_path).expanduser()
        self.source_session_id = self.transcript_path.stem

    def iter_events(self, *, start_line: int = 0) -> Iterable[MirrorEvent]:
        with self.transcript_path.open("r", encoding="utf-8") as handle:
            for line_number, raw_line in enumerate(handle, start=1):
                if line_number <= start_line:
                    continue
                parsed = json.loads(raw_line)
                event = self._normalize_event(parsed, line_number)
                if event is not None:
                    yield event

    def _normalize_event(self, entry: dict[str, Any], line_number: int) -> MirrorEvent | None:
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
        dedupe_seed = "|".join(
            [
                AMY_AGENT_ID,
                self.source_session_id,
                source_event_id,
                role,
                source_timestamp,
            ]
        )
        dedupe_key = hashlib.sha256(dedupe_seed.encode("utf-8")).hexdigest()
        return MirrorEvent(
            source_name=AMY_AGENT_ID,
            source_session_id=self.source_session_id,
            source_session_key=AMY_SESSION_KEY,
            source_account_id=AMY_ACCOUNT_ID,
            source_chat_id=AMY_CHAT_ID,
            source_event_id=source_event_id,
            source_role=role,
            source_timestamp=source_timestamp,
            transcript_path=str(self.transcript_path),
            transcript_line_number=line_number,
            text=text,
            dedupe_key=dedupe_key,
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
