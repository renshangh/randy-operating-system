from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

DEFAULT_WATCHLIST_PATH = Path(__file__).with_name("active_dispatches.json")
ACTIVE_STATES = {"active", "delegated", "in_progress", "in-progress", "ready"}
INACTIVE_STATES = {"accepted", "closed", "returned", "reassigned", "done", "inactive"}


@dataclass(frozen=True)
class DispatchStatus:
    repo: str
    issue_number: int
    issue_title: str
    assigned_agent: str
    state: str
    channel_id: str | None
    mention: str | None
    dispatch_started_at: str | None
    last_meaningful_update_at: str | None
    stale_after_minutes: int
    age_minutes: float
    stale: bool


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check active delegated issues for stale watchlist entries.")
    parser.add_argument("--watchlist", default=str(DEFAULT_WATCHLIST_PATH), help="Path to active_dispatches.json")
    parser.add_argument("--now", help="Override current time in ISO-8601 format")
    parser.add_argument("--stale-only", action="store_true", help="Print only stale entries")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of human-readable text")
    return parser.parse_args()


def parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    normalized = value.strip()
    if not normalized:
        return None
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    return datetime.fromisoformat(normalized)


def load_watchlist(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def is_active_state(state: str) -> bool:
    normalized = (state or "").strip().lower()
    if normalized in INACTIVE_STATES:
        return False
    return normalized in ACTIVE_STATES or normalized == ""


def evaluate_entry(entry: dict[str, Any], now: datetime) -> DispatchStatus:
    state = str(entry.get("status") or "active")
    dispatch_started_at = parse_timestamp(entry.get("dispatch_started_at"))
    last_update_at = parse_timestamp(entry.get("last_meaningful_update_at")) or dispatch_started_at
    stale_after_minutes = int(entry.get("stale_after_minutes") or 10)

    if last_update_at is None:
        age_minutes = float("inf")
    else:
        age_minutes = max((now - last_update_at).total_seconds() / 60.0, 0.0)

    stale = is_active_state(state) and age_minutes >= stale_after_minutes

    return DispatchStatus(
        repo=str(entry.get("repo") or ""),
        issue_number=int(entry.get("issue_number") or 0),
        issue_title=str(entry.get("issue_title") or "").strip(),
        assigned_agent=str(entry.get("assigned_agent") or "").strip(),
        state=state,
        channel_id=((entry.get("discord") or {}).get("channel_id") if isinstance(entry.get("discord"), dict) else None),
        mention=((entry.get("discord") or {}).get("mention") if isinstance(entry.get("discord"), dict) else None),
        dispatch_started_at=entry.get("dispatch_started_at"),
        last_meaningful_update_at=entry.get("last_meaningful_update_at"),
        stale_after_minutes=stale_after_minutes,
        age_minutes=age_minutes,
        stale=stale,
    )


def render_text(results: list[DispatchStatus], stale_only: bool) -> str:
    filtered = [result for result in results if result.stale] if stale_only else results
    if not filtered:
        return "ACTIVE_DISPATCHES_OK no stale delegated issues"

    lines: list[str] = []
    stale_count = sum(1 for result in filtered if result.stale)
    total_count = len(filtered)
    header = f"ACTIVE_DISPATCHES_ALERT stale={stale_count} tracked={total_count}" if stale_count else f"ACTIVE_DISPATCHES_STATUS tracked={total_count} stale=0"
    lines.append(header)
    for result in filtered:
        state = "STALE" if result.stale else "OK"
        age = "unknown" if result.age_minutes == float("inf") else f"{result.age_minutes:.1f}m"
        title_part = f" | {result.issue_title}" if result.issue_title else ""
        agent_part = f" | agent={result.assigned_agent}" if result.assigned_agent else ""
        mention_part = f" | mention={result.mention}" if result.mention else ""
        channel_part = f" | channel={result.channel_id}" if result.channel_id else ""
        lines.append(
            f"- {state} | {result.repo}#{result.issue_number}{title_part}{agent_part} | age={age} | threshold={result.stale_after_minutes}m | state={result.state}{channel_part}{mention_part}"
        )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    watchlist_path = Path(args.watchlist).expanduser().resolve()
    payload = load_watchlist(watchlist_path)
    now = parse_timestamp(args.now) if args.now else datetime.now().astimezone()
    if now is None:
        raise SystemExit("Invalid --now value")

    items = payload.get("items") or []
    results = [evaluate_entry(item, now) for item in items]
    filtered = [result for result in results if result.stale] if args.stale_only else results

    if args.json:
        print(
            json.dumps(
                {
                    "watchlist": str(watchlist_path),
                    "checked_at": now.isoformat(),
                    "tracked_count": len(results),
                    "stale_count": sum(1 for result in results if result.stale),
                    "items": [result.__dict__ for result in filtered],
                },
                indent=2,
            )
        )
    else:
        print(render_text(results, args.stale_only))

    return 1 if any(result.stale for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
