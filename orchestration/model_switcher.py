from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, time, timezone
from pathlib import Path
from typing import Any


DEFAULT_STATE_PATH = ".state/model_switcher_state.json"
DEFAULT_IDLE_THRESHOLD_SECONDS = 300
DEFAULT_IDLE_MODEL = "vllm/openai/gpt-oss-120b"
DEFAULT_ACTIVE_MODEL = "google-gemini-cli/gemini-3-pro-preview"
DEFAULT_OFF_HOURS_START = "18:00"
DEFAULT_OFF_HOURS_END = "08:00"


@dataclass
class SwitchDecision:
    timestamp: str
    mode: str
    target_model: str
    reason: str
    idle_threshold_seconds: int
    idle_seconds: float | None
    now_local: str
    last_activity_at: str | None
    state_path: str
    dry_run: bool
    changed: bool


@dataclass
class SwitchState:
    last_activity_at: str | None = None
    current_mode: str | None = None
    current_model: str | None = None
    last_decision_at: str | None = None
    last_reason: str | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Phase-1 scaffold for idle/off-hours model switching. "
            "Reads a small JSON state file, decides whether the system should be "
            "in active or idle mode, and emits structured decision logs."
        )
    )
    parser.add_argument("--state-path", default=os.environ.get("MODEL_SWITCHER_STATE_PATH", DEFAULT_STATE_PATH))
    parser.add_argument(
        "--idle-threshold-seconds",
        type=int,
        default=int(os.environ.get("MODEL_SWITCHER_IDLE_THRESHOLD_SECONDS", DEFAULT_IDLE_THRESHOLD_SECONDS)),
    )
    parser.add_argument("--idle-model", default=os.environ.get("MODEL_SWITCHER_IDLE_MODEL", DEFAULT_IDLE_MODEL))
    parser.add_argument("--active-model", default=os.environ.get("MODEL_SWITCHER_ACTIVE_MODEL", DEFAULT_ACTIVE_MODEL))
    parser.add_argument(
        "--off-hours-start",
        default=os.environ.get("MODEL_SWITCHER_OFF_HOURS_START", DEFAULT_OFF_HOURS_START),
        help="Local time in HH:MM (24h)",
    )
    parser.add_argument(
        "--off-hours-end",
        default=os.environ.get("MODEL_SWITCHER_OFF_HOURS_END", DEFAULT_OFF_HOURS_END),
        help="Local time in HH:MM (24h)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Emit decision only; do not persist state changes")
    parser.add_argument(
        "--wake",
        action="store_true",
        help="Force active mode and stamp last_activity_at=now. Intended wake path for webhook/router integration.",
    )
    return parser.parse_args()


def parse_local_hhmm(value: str) -> time:
    hour_str, minute_str = value.split(":", 1)
    return time(hour=int(hour_str), minute=int(minute_str))


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def load_state(path: Path) -> SwitchState:
    if not path.exists():
        return SwitchState()
    raw = json.loads(path.read_text())
    return SwitchState(
        last_activity_at=raw.get("last_activity_at"),
        current_mode=raw.get("current_mode"),
        current_model=raw.get("current_model"),
        last_decision_at=raw.get("last_decision_at"),
        last_reason=raw.get("last_reason"),
    )


def save_state(path: Path, state: SwitchState) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(state), indent=2, sort_keys=True) + "\n")


def parse_iso8601(value: str | None) -> datetime | None:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    dt = datetime.fromisoformat(normalized)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def in_off_hours(now_local: datetime, start: time, end: time) -> bool:
    current = now_local.timetz().replace(tzinfo=None)
    if start == end:
        return True
    if start < end:
        return start <= current < end
    return current >= start or current < end


def decide_mode(
    state: SwitchState,
    *,
    now_utc: datetime,
    idle_threshold_seconds: int,
    off_hours_start: time,
    off_hours_end: time,
    idle_model: str,
    active_model: str,
    wake: bool,
    dry_run: bool,
    state_path: Path,
) -> tuple[SwitchDecision, SwitchState]:
    now_local = now_utc.astimezone()
    previous_last_activity = parse_iso8601(state.last_activity_at)

    if wake:
        last_activity = now_utc
        mode = "active"
        target_model = active_model
        reason = "forced_wake"
        idle_seconds = 0.0
    else:
        last_activity = previous_last_activity
        idle_seconds = None
        if last_activity is not None:
            idle_seconds = max((now_utc - last_activity).total_seconds(), 0.0)

        off_hours = in_off_hours(now_local, off_hours_start, off_hours_end)
        idle_threshold_hit = idle_seconds is not None and idle_seconds >= idle_threshold_seconds

        if off_hours and idle_threshold_hit:
            mode = "idle"
            target_model = idle_model
            reason = "off_hours_and_idle_threshold"
        elif off_hours:
            mode = "idle"
            target_model = idle_model
            reason = "off_hours"
        elif idle_threshold_hit:
            mode = "idle"
            target_model = idle_model
            reason = "idle_threshold"
        else:
            mode = "active"
            target_model = active_model
            reason = "recent_activity"

    changed = state.current_mode != mode or state.current_model != target_model or wake
    next_state = SwitchState(
        last_activity_at=(last_activity or now_utc if wake else last_activity).isoformat().replace("+00:00", "Z")
        if (last_activity or wake)
        else None,
        current_mode=mode,
        current_model=target_model,
        last_decision_at=now_utc.isoformat().replace("+00:00", "Z"),
        last_reason=reason,
    )

    decision = SwitchDecision(
        timestamp=now_utc.isoformat().replace("+00:00", "Z"),
        mode=mode,
        target_model=target_model,
        reason=reason,
        idle_threshold_seconds=idle_threshold_seconds,
        idle_seconds=idle_seconds,
        now_local=now_local.isoformat(),
        last_activity_at=state.last_activity_at,
        state_path=str(state_path),
        dry_run=dry_run,
        changed=changed,
    )
    return decision, next_state


def emit_structured_log(decision: SwitchDecision) -> None:
    payload: dict[str, Any] = {"event": "model_switch_decision", **asdict(decision)}
    print(json.dumps(payload, sort_keys=True))


def main() -> int:
    args = parse_args()
    state_path = Path(args.state_path)
    state = load_state(state_path)
    now_utc = utc_now()
    decision, next_state = decide_mode(
        state,
        now_utc=now_utc,
        idle_threshold_seconds=args.idle_threshold_seconds,
        off_hours_start=parse_local_hhmm(args.off_hours_start),
        off_hours_end=parse_local_hhmm(args.off_hours_end),
        idle_model=args.idle_model,
        active_model=args.active_model,
        wake=args.wake,
        dry_run=args.dry_run,
        state_path=state_path,
    )
    emit_structured_log(decision)
    if not args.dry_run:
        save_state(state_path, next_state)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
