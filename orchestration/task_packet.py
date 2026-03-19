from __future__ import annotations

from typing import Any


def build_task_packet(normalized_event: dict[str, Any], local_repo_path: str) -> dict[str, Any]:
    issue_body = (normalized_event.get("issue_body") or "").strip()
    compact_body = issue_body[:4000]
    return {
        "repository_full_name": normalized_event.get("repository_full_name"),
        "local_repo_path": local_repo_path,
        "issue_number": normalized_event.get("issue_number"),
        "issue_title": normalized_event.get("issue_title"),
        "objective": compact_body,
        "scope_constraints": "Follow issue scope exactly; keep work narrow.",
        "acceptance_criteria": "Use the issue checklist and latest comments as acceptance criteria.",
        "recent_relevant_comments": [],
        "output_expectation": "Return concise done/blocked/failed result for GitHub reporting.",
    }


def build_session_event_packet(normalized_event: dict[str, Any], router_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "kind": "github_webhook_event",
        "delivery_id": normalized_event.get("delivery_id"),
        "event_type": normalized_event.get("event_type"),
        "action": normalized_event.get("action"),
        "repository_full_name": normalized_event.get("repository_full_name"),
        "issue_number": normalized_event.get("issue_number"),
        "issue_title": normalized_event.get("issue_title"),
        "issue_url": normalized_event.get("issue_url"),
        "issue_state": normalized_event.get("issue_state"),
        "sender_login": normalized_event.get("sender_login"),
        "labels": normalized_event.get("labels") or [],
        "classification": router_result.get("classification") or router_result.get("status"),
        "target_agent": router_result.get("agent"),
        "summary": router_result.get("summary") or "",
        "comment_body": normalized_event.get("comment_body") or "",
        "notice_only": bool(router_result.get("notice_only")),
    }
