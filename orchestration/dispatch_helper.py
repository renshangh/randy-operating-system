from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from orchestration.github_client import GitHubClient

DISPATCH_READY_LABEL = "dispatch:ready"
DEFAULT_STALE_AFTER_MINUTES = 10
WATCHLIST_PATH = Path(__file__).with_name("active_dispatches.json")

AGENT_LABELS: dict[str, str] = {
    "mark": "agent:mark",
    "sarah": "agent:sarah",
    "ember": "agent:ember",
    "sentinel": "agent:sentinel",
}


@dataclass(frozen=True)
class DispatchResult:
    repo: str
    issue_number: int
    agent: str
    labels_added: tuple[str, ...]
    github_comment_posted: bool
    watchlist_updated: bool


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat()


def _default_issue_url(repo: str, issue_number: int) -> str:
    return f"https://github.com/{repo}/issues/{issue_number}"


def update_active_dispatch_watchlist(*, repo: str, issue_number: int, agent: str) -> bool:
    now = _now_iso()
    payload: dict[str, Any]
    if WATCHLIST_PATH.exists():
        payload = json.loads(WATCHLIST_PATH.read_text(encoding="utf-8"))
    else:
        payload = {
            "version": 1,
            "description": "Active delegated GitHub issues being tracked for the 10-minute stale hand-back SOP.",
            "updated_at": now,
            "items": [],
        }

    items = payload.get("items")
    if not isinstance(items, list):
        items = []
        payload["items"] = items

    entry = {
        "repo": repo,
        "issue_number": issue_number,
        "issue_url": _default_issue_url(repo, issue_number),
        "issue_title": "",
        "assigned_agent": agent,
        "agent_name": agent.capitalize(),
        "status": "active",
        "dispatch_started_at": now,
        "last_meaningful_update_at": now,
        "stale_after_minutes": DEFAULT_STALE_AFTER_MINUTES,
        "warning_sent_at": None,
    }

    updated = False
    for index, item in enumerate(items):
        if str(item.get("repo") or "").strip() == repo and int(item.get("issue_number") or 0) == issue_number:
            items[index] = entry
            updated = True
            break
    else:
        items.append(entry)
        updated = True

    payload["updated_at"] = now
    WATCHLIST_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return updated


def dispatch_issue(*, repo: str, issue_number: int, agent: str, dispatch_body: str = "") -> DispatchResult:
    client = GitHubClient(repo)
    agent_label = AGENT_LABELS[agent]
    labels = (agent_label, DISPATCH_READY_LABEL)
    client.add_labels(issue_number, labels)

    github_comment_posted = False
    body = dispatch_body.strip()
    if body:
        client.comment_issue(issue_number, body)
        github_comment_posted = True

    watchlist_updated = update_active_dispatch_watchlist(repo=repo, issue_number=issue_number, agent=agent)

    return DispatchResult(
        repo=repo,
        issue_number=issue_number,
        agent=agent,
        labels_added=labels,
        github_comment_posted=github_comment_posted,
        watchlist_updated=watchlist_updated,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Dispatch an issue by applying the agent label plus dispatch:ready.")
    parser.add_argument("--repo", required=True)
    parser.add_argument("--issue", required=True, type=int)
    parser.add_argument("--agent", required=True, choices=sorted(AGENT_LABELS))
    parser.add_argument("--body", default="")
    args = parser.parse_args()

    result = dispatch_issue(
        repo=args.repo,
        issue_number=args.issue,
        agent=args.agent,
        dispatch_body=args.body,
    )
    print(f"repo={result.repo}")
    print(f"issue={result.issue_number}")
    print(f"agent={result.agent}")
    print(f"labels_added={','.join(result.labels_added)}")
    print(f"github_comment_posted={result.github_comment_posted}")
    print(f"watchlist_updated={result.watchlist_updated}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
