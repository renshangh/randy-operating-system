#!/usr/bin/env python3
"""Check Mac mini repos and workspaces for drift and post a two-times-daily summary."""
from __future__ import annotations

import datetime
import json
import os
import subprocess
from pathlib import Path
from typing import Iterable, Mapping, Sequence

BASE = Path.home() / ".openclaw"
LOG_PATH = BASE / "logs" / "macmini-relay-check.log"
CONSOLE_JSON = LOG_PATH.with_suffix(".json")
OPENCLAW_CMD = os.getenv("OPENCLAW_PATH", "openclaw")
RESULT_CHANNEL = "channel:1483085404675772469"  # #general

MONITORED: Sequence[tuple[str, Path]] = (
    ("workspace-sarah", BASE / "workspace-sarah"),
    ("workspace-ember", BASE / "workspace-ember"),
    ("workspace-sentinel", BASE / "workspace-sentinel"),
    ("workspace-market", BASE / "workspace-market"),
    ("workspace-social", BASE / "workspace-social"),
    ("repo-randy-operating-system", Path.home() / "repo" / "randy-operating-system"),
    ("repo-randy-job-hunt-pipeline", Path.home() / "repo" / "randy-job-hunt-pipeline"),
)


def run_git(cwd: Path, *args: str) -> str:
    proc = subprocess.run(
        ("git",) + args,
        cwd=cwd,
        capture_output=True,
        text=True,
        env=os.environ,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"git {args} failed in {cwd} (code {proc.returncode}): {proc.stderr.strip()}"
        )
    return proc.stdout.strip()


def gather_status(name: str, path: Path) -> Mapping[str, object]:
    info = {
        "name": name,
        "path": str(path),
        "exists": path.exists(),
        "git": (path / ".git").exists(),
        "branch": "",
        "upstream": "",
        "dirty": False,
        "status_lines": [],
        "ahead": 0,
        "behind": 0,
        "needs_relay": False,
        "errors": [],
    }

    if not info["exists"] or not info["git"]:
        return info

    try:
        run_git(path, "fetch", "--dry-run")
    except RuntimeError as exc:
        info["errors"].append(str(exc))

    try:
        info["branch"] = run_git(path, "rev-parse", "--abbrev-ref", "HEAD")
    except RuntimeError as exc:
        info["errors"].append(str(exc))
        info["branch"] = "(unknown)"

    try:
        upstream = run_git(path, "rev-parse", "--abbrev-ref", "@{u}")
        info["upstream"] = upstream
    except RuntimeError:
        info["upstream"] = "no upstream"

    try:
        status = run_git(path, "status", "--short")
    except RuntimeError as exc:
        info["errors"].append(str(exc))
        status = ""
    status_lines = [line for line in status.splitlines() if line.strip()]
    info["status_lines"] = status_lines
    info["dirty"] = bool(status_lines)

    if info["upstream"] not in ("", "no upstream"):
        try:
            ahead = run_git(path, "rev-list", "--count", f"{info['upstream']}..HEAD")
            behind = run_git(path, "rev-list", "--count", f"HEAD..{info['upstream']}")
            info["ahead"] = int(ahead)
            info["behind"] = int(behind)
        except RuntimeError as exc:
            info["errors"].append(str(exc))

    info["needs_relay"] = bool(info["dirty"] or info["ahead"] or info["behind"])
    return info


def format_detail(entry: Mapping[str, object]) -> list[str]:
    lines = []
    status = []
    if entry.get("dirty"):
        status.append("uncommitted changes")
    ahead = entry.get("ahead") or 0
    behind = entry.get("behind") or 0
    if ahead:
        status.append(f"ahead {ahead} commits")
    if behind:
        status.append(f"behind {behind} commits")
    if not status:
        status.append("git status flagged")
    lines.append(f"- {entry['name']} ({entry.get('branch') or 'unknown branch'}): {', '.join(status)}")
    for raw in entry.get("status_lines", [])[:5]:
        lines.append(f"    {raw}")
    if len(entry.get("status_lines", [])) > 5:
        lines.append("    ...")
    return lines


def summarize(entries: Sequence[Mapping[str, object]]) -> str:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M %Z")
    clean = [e for e in entries if e["exists"] and e["git"] and not e["needs_relay"]]
    attention = [e for e in entries if e["needs_relay"]]
    missing = [e for e in entries if not e["exists"] or not e["git"]]

    text = [f"Mac mini relay sync check — {timestamp}"]
    if missing:
        text.append("\nMissing git workspaces:")
        for entry in missing:
            text.append(f"- {entry['name']} (path: {entry['path']}): git repo not present")
    if clean:
        text.append("\nClean workspaces:")
        for entry in clean:
            text.append(f"- {entry['name']} ({entry.get('branch')})")
    if attention:
        text.append("\nWorkspaces needing relay attention:")
        for entry in attention:
            text.extend(format_detail(entry))
    else:
        text.append("\nNo drift detected — all monitored workspaces are in sync.")
    return "\n".join(text)


def persist_logs(text: str, entries: Sequence[Mapping[str, object]]) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(f"{datetime.datetime.now().isoformat()} - relay check\n")
        handle.write(text)
        handle.write("\n\n")
    payload = {
        "timestamp": datetime.datetime.now().isoformat(),
        "entries": [dict(entry) for entry in entries],
        "summary": text,
    }
    with CONSOLE_JSON.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def post_message(text: str) -> None:
    try:
        subprocess.run(
            [
                OPENCLAW_CMD,
                "message",
                "send",
                "--account",
                "sarah",
                "--channel",
                "discord",
                "--target",
                RESULT_CHANNEL,
                "--message",
                text,
                "--silent",
            ],
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        raise RuntimeError("failed to send relay summary") from exc


def main() -> None:
    entries = [gather_status(name, path) for name, path in MONITORED]
    summary = summarize(entries)
    persist_logs(summary, entries)
    try:
        post_message(summary)
    except RuntimeError as exc:
        print("Relay delivery failed:", exc)


if __name__ == "__main__":
    main()
