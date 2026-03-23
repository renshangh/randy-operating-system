from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

DEFAULT_WATCHLIST_PATH = Path(__file__).with_name("active_dispatches.json")
ACTIVE_STATES = {"active", "delegated", "in_progress", "in-progress", "ready"}
INACTIVE_STATES = {"accepted", "closed", "returned", "reassigned", "done", "inactive"}
MESSAGE_MODES = {"checkpoint", "final"}


@dataclass(frozen=True)
class DispatchStatus:
    repo: str
    issue_number: int
    issue_url: str
    issue_title: str
    assigned_agent: str
    agent_name: str
    state: str
    channel_id: str | None
    mention: str | None
    dispatch_started_at: str | None
    last_meaningful_update_at: str | None
    stale_after_minutes: int
    age_minutes: float
    stale: bool
    recommended_message_mode: str
    discord_followup_message: str | None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check active delegated issues for stale watchlist entries.")
    parser.add_argument("--watchlist", default=str(DEFAULT_WATCHLIST_PATH), help="Path to active_dispatches.json")
    parser.add_argument("--now", help="Override current time in ISO-8601 format")
    parser.add_argument("--stale-only", action="store_true", help="Print only stale entries")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of human-readable text")
    parser.add_argument(
        "--message-mode",
        choices=sorted(MESSAGE_MODES),
        default="final",
        help="Template to generate for stale follow-up messages",
    )
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


def format_repo_issue(repo: str, issue_number: int) -> str:
    return f"{repo} issue #{issue_number}" if repo and issue_number else f"issue #{issue_number}" if issue_number else repo or "the issue"


def build_followup_message(
    *,
    mention: str | None,
    agent_name: str,
    repo: str,
    issue_number: int,
    issue_url: str,
    mode: str,
) -> str | None:
    if not mention:
        return None

    resolved_agent_name = agent_name or "Agent"
    repo_issue = format_repo_issue(repo, issue_number)

    if mode == "checkpoint":
        return (
            f"{mention} {resolved_agent_name} — quick check on {repo_issue}.\n\n"
            "If you’re still actively working, post a substantive GitHub progress update now with current status, blocker if any, and next step.\n\n"
            "If not, release it back now through the normal return path:\n"
            "- remove `dispatch:ready`\n"
            "- add `status:done`\n"
            f"- post a concise `Author: {resolved_agent_name}` GitHub comment with what you attempted, the exact blocker, and the next step\n\n"
            f"Issue: {issue_url}"
        )

    return (
        f"{mention} {resolved_agent_name} — stop active work on {repo_issue} and hand it back now.\n\n"
        "Use the normal return path:\n"
        "- remove `dispatch:ready`\n"
        "- add `status:done`\n"
        f"- post a substantive `Author: {resolved_agent_name}` GitHub comment with what you completed, the exact blocker/error, and the next debugging step\n\n"
        f"Issue: {issue_url}"
    )


def evaluate_entry(entry: dict[str, Any], now: datetime, *, message_mode: str) -> DispatchStatus:
    state = str(entry.get("status") or "active")
    dispatch_started_at = parse_timestamp(entry.get("dispatch_started_at"))
    last_update_at = parse_timestamp(entry.get("last_meaningful_update_at")) or dispatch_started_at
    stale_after_minutes = int(entry.get("stale_after_minutes") or 10)
    discord = entry.get("discord") or {}
    issue_url = str(entry.get("issue_url") or "").strip()
    agent_name = str((discord.get("agent_name") if isinstance(discord, dict) else None) or entry.get("agent_name") or entry.get("assigned_agent") or "Agent").strip()

    if last_update_at is None:
        age_minutes = float("inf")
    else:
        age_minutes = max((now - last_update_at).total_seconds() / 60.0, 0.0)

    stale = is_active_state(state) and age_minutes >= stale_after_minutes
    mention = (discord.get("mention") if isinstance(discord, dict) else None)
    discord_followup_message = None
    if stale:
        discord_followup_message = build_followup_message(
            mention=mention,
            agent_name=agent_name,
            repo=str(entry.get("repo") or "").strip(),
            issue_number=int(entry.get("issue_number") or 0),
            issue_url=issue_url,
            mode=message_mode,
        )

    return DispatchStatus(
        repo=str(entry.get("repo") or "").strip(),
        issue_number=int(entry.get("issue_number") or 0),
        issue_url=issue_url,
        issue_title=str(entry.get("issue_title") or "").strip(),
        assigned_agent=str(entry.get("assigned_agent") or "").strip(),
        agent_name=agent_name,
        state=state,
        channel_id=(discord.get("channel_id") if isinstance(discord, dict) else None),
        mention=mention,
        dispatch_started_at=entry.get("dispatch_started_at"),
        last_meaningful_update_at=entry.get("last_meaningful_update_at"),
        stale_after_minutes=stale_after_minutes,
        age_minutes=age_minutes,
        stale=stale,
        recommended_message_mode=message_mode,
        discord_followup_message=discord_followup_message,
    )


def render_text(results: list[DispatchStatus], stale_only: bool) -> str:
    filtered = [result for result in results if result.stale] if stale_only else results
    if not filtered:
        return "ACTIVE_DISPATCHES_OK no stale delegated issues"

    lines: list[str] = []
    stale_count = sum(1 for result in filtered if result.stale)
    total_count = len(filtered)
    header = (
        f"ACTIVE_DISPATCHES_ALERT stale={stale_count} tracked={total_count}"
        if stale_count
        else f"ACTIVE_DISPATCHES_STATUS tracked={total_count} stale=0"
    )
    lines.append(header)
    for result in filtered:
        state = "STALE" if result.stale else "OK"
        age = "unknown" if result.age_minutes == float("inf") else f"{result.age_minutes:.1f}m"
        title_part = f" | {result.issue_title}" if result.issue_title else ""
        agent_part = f" | agent={result.agent_name or result.assigned_agent}" if (result.agent_name or result.assigned_agent) else ""
        mention_part = f" | mention={result.mention}" if result.mention else ""
        channel_part = f" | channel={result.channel_id}" if result.channel_id else ""
        lines.append(
            f"- {state} | {result.repo}#{result.issue_number}{title_part}{agent_part} | age={age} | threshold={result.stale_after_minutes}m | state={result.state}{channel_part}{mention_part}"
        )
        if result.discord_followup_message:
            lines.append("  followup_message:")
            for message_line in result.discord_followup_message.splitlines():
                lines.append(f"    {message_line}")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    watchlist_path = Path(args.watchlist).expanduser().resolve()
    payload = load_watchlist(watchlist_path)
    now = parse_timestamp(args.now) if args.now else datetime.now().astimezone()
    if now is None:
        raise SystemExit("Invalid --now value")

    items = payload.get("items") or []
    results = [evaluate_entry(item, now, message_mode=args.message_mode) for item in items]
    filtered = [result for result in results if result.stale] if args.stale_only else results

    if args.json:
        print(
            json.dumps(
                {
                    "watchlist": str(watchlist_path),
                    "checked_at": now.isoformat(),
                    "tracked_count": len(results),
                    "stale_count": sum(1 for result in results if result.stale),
                    "message_mode": args.message_mode,
                    "items": [asdict(result) for result in filtered],
                },
                indent=2,
            )
        )
    else:
        print(render_text(results, args.stale_only))

    return 1 if any(result.stale for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
