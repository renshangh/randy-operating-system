from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path

from orchestration.discord_output import DiscordWebhookOutput
from orchestration.mirror_ledger import MirrorLedger
from orchestration.sarah_telegram_adapter import (
    DEFAULT_SARAH_SESSIONS_INDEX,
    DEFAULT_SESSION_KEY_PREFIXES,
    SarahTelegramAdapter,
)

DEFAULT_LEDGER_PATH = Path("orchestration/mirror_ledger.sqlite")


@dataclass(frozen=True)
class SarahMirrorRunSummary:
    sessions_index_path: str
    selected_sources: list[str]
    candidate_events: int
    delivered: int
    duplicates: int
    failed: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mirror Sarah Telegram transcript events into Discord.")
    parser.add_argument("--sessions-index-path", default=os.environ.get("SARAH_SESSIONS_INDEX_PATH", str(DEFAULT_SARAH_SESSIONS_INDEX)))
    parser.add_argument("--ledger-path", default=os.environ.get("MIRROR_LEDGER_PATH", str(DEFAULT_LEDGER_PATH)))
    parser.add_argument("--webhook-url", default=os.environ.get("DISCORD_REVIEW_WEBHOOK_URL") or os.environ.get("DISCORD_HEARTBEAT_WEBHOOK_URL", ""))
    parser.add_argument(
        "--session-key-prefix",
        action="append",
        dest="session_key_prefixes",
        help="Repeatable session-key prefix filter. Defaults to known Sarah Telegram prefixes plus metadata-based telegram detection.",
    )
    parser.add_argument(
        "--session-key",
        action="append",
        dest="session_keys",
        help="Explicit session key(s) to include even if they do not match the default prefix.",
    )
    parser.add_argument("--max-events-per-source", type=int, default=5)
    parser.add_argument("--start-line", type=int, default=None, help="Override saved cursors and start every selected source from this line.")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def run_once(*, sessions_index_path: str, ledger_path: str, webhook_url: str, session_key_prefixes: tuple[str, ...], explicit_session_keys: set[str], max_events_per_source: int, start_line: int | None, dry_run: bool) -> SarahMirrorRunSummary:
    adapter = SarahTelegramAdapter(sessions_index_path)
    ledger = MirrorLedger(ledger_path)
    output = DiscordWebhookOutput(webhook_url)

    sources = adapter.discover_sources(session_key_prefixes=session_key_prefixes, explicit_session_keys=explicit_session_keys)
    candidate_events = delivered = duplicates = failed = 0

    for source in sources:
        start_line = start_line if start_line is not None else ledger.get_cursor(source.session_key, source.transcript_path)
        emitted = 0
        for event in adapter.iter_events(source, start_line=start_line):
            if emitted >= max_events_per_source:
                break
            emitted += 1
            candidate_events += 1

            if ledger.has_delivery(event.dedupe_key):
                duplicates += 1
                ledger.update_cursor(source.session_key, event.transcript_path, event.transcript_line_number)
                continue

            if dry_run:
                print(json.dumps({"dry_run_event": asdict(event)}, ensure_ascii=False))
                ledger.record_delivery_attempt(
                    dedupe_key=event.dedupe_key,
                    source_name=event.source_name,
                    source_session_id=event.source_session_id,
                    source_event_id=event.source_event_id,
                    source_role=event.source_role,
                    source_timestamp=event.source_timestamp,
                    transcript_path=event.transcript_path,
                    transcript_offset=event.transcript_line_number,
                    discord_status="dry_run",
                )
                ledger.update_cursor(source.session_key, event.transcript_path, event.transcript_line_number)
                delivered += 1
                continue

            result = output.send_content(event.to_discord_message())
            ledger.record_delivery_attempt(
                dedupe_key=event.dedupe_key,
                source_name=event.source_name,
                source_session_id=event.source_session_id,
                source_event_id=event.source_event_id,
                source_role=event.source_role,
                source_timestamp=event.source_timestamp,
                transcript_path=event.transcript_path,
                transcript_offset=event.transcript_line_number,
                discord_status=result.status,
                discord_http_status=result.http_status,
                discord_error=result.error,
            )
            ledger.update_cursor(source.session_key, event.transcript_path, event.transcript_line_number)
            if result.ok:
                delivered += 1
            else:
                failed += 1

    return SarahMirrorRunSummary(
        sessions_index_path=sessions_index_path,
        selected_sources=[source.session_key for source in sources],
        candidate_events=candidate_events,
        delivered=delivered,
        duplicates=duplicates,
        failed=failed,
    )


def main() -> int:
    args = parse_args()
    session_key_prefixes = tuple(args.session_key_prefixes or DEFAULT_SESSION_KEY_PREFIXES)
    explicit_session_keys = set(args.session_keys or [])
    summary = run_once(
        sessions_index_path=args.sessions_index_path,
        ledger_path=args.ledger_path,
        webhook_url=args.webhook_url,
        session_key_prefixes=session_key_prefixes,
        explicit_session_keys=explicit_session_keys,
        max_events_per_source=args.max_events_per_source,
        start_line=args.start_line,
        dry_run=args.dry_run,
    )
    print(json.dumps(asdict(summary), ensure_ascii=False, indent=2))
    return 0 if summary.failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
