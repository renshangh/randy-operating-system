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
