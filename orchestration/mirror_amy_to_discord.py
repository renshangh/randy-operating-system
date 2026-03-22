from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from orchestration.amy_transcript_adapter import AmyTranscriptAdapter, DEFAULT_TRANSCRIPT_PATH
from orchestration.discord_output import DiscordWebhookOutput
from orchestration.mirror_ledger import MirrorLedger

DEFAULT_LEDGER_PATH = Path("orchestration/mirror_ledger.sqlite")


@dataclass(frozen=True)
class MirrorRunSummary:
    transcript_path: str
    start_line: int
    scanned_lines: int
    candidate_events: int
    delivered: int
    duplicates: int
    failed: int
    last_line_number: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mirror Amy transcript events into Discord.")
    parser.add_argument("--transcript-path", default=os.environ.get("AMY_TRANSCRIPT_PATH", str(DEFAULT_TRANSCRIPT_PATH)))
    parser.add_argument("--ledger-path", default=os.environ.get("MIRROR_LEDGER_PATH", str(DEFAULT_LEDGER_PATH)))
    parser.add_argument("--webhook-url", default=os.environ.get("DISCORD_REVIEW_WEBHOOK_URL") or os.environ.get("DISCORD_HEARTBEAT_WEBHOOK_URL", ""))
    parser.add_argument("--start-line", type=int, default=None, help="Override the saved cursor and start from this line number.")
    parser.add_argument("--max-events", type=int, default=10)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def run_once(*, transcript_path: str, ledger_path: str, webhook_url: str, start_line: int | None, max_events: int, dry_run: bool) -> MirrorRunSummary:
    adapter = AmyTranscriptAdapter(transcript_path)
    ledger = MirrorLedger(ledger_path)
    output = DiscordWebhookOutput(webhook_url)

    resume_line = start_line if start_line is not None else ledger.get_cursor("amy", str(adapter.transcript_path))
    scanned_lines = 0
    candidate_events = 0
    delivered = 0
    duplicates = 0
    failed = 0
    last_line_number = resume_line

    for event in adapter.iter_events(start_line=resume_line):
        if candidate_events >= max_events:
            break
        scanned_lines += 1
        last_line_number = event.transcript_line_number
        candidate_events += 1

        if ledger.has_delivery(event.dedupe_key):
            duplicates += 1
            ledger.update_cursor("amy", event.transcript_path, event.transcript_line_number)
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
            ledger.update_cursor("amy", event.transcript_path, event.transcript_line_number)
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
        ledger.update_cursor("amy", event.transcript_path, event.transcript_line_number)
        if result.ok:
            delivered += 1
        else:
            failed += 1

    return MirrorRunSummary(
        transcript_path=str(adapter.transcript_path),
        start_line=resume_line,
        scanned_lines=scanned_lines,
        candidate_events=min(candidate_events, max_events),
        delivered=delivered,
        duplicates=duplicates,
        failed=failed,
        last_line_number=last_line_number,
    )


def main() -> int:
    args = parse_args()
    summary = run_once(
        transcript_path=args.transcript_path,
        ledger_path=args.ledger_path,
        webhook_url=args.webhook_url,
        start_line=args.start_line,
        max_events=args.max_events,
        dry_run=args.dry_run,
    )
    print(json.dumps(asdict(summary), ensure_ascii=False, indent=2))
    return 0 if summary.failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
