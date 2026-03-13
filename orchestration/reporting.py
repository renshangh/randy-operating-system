from __future__ import annotations

from orchestration.github_client import GitHubClient

RESULT_TO_LABEL = {
    "done": "dispatch:done",
    "blocked": "dispatch:blocked",
    "failed": "dispatch:failed",
}


def format_result_comment(result: dict) -> str:
    status = result.get("result_status", "unknown")
    agent = result.get("agent", "unknown")
    summary = result.get("summary", "")
    details = result.get("details", "")
    changed_files = result.get("changed_files") or []
    pr_url = result.get("pr_url")
    error_info = result.get("error_info")

    lines = [
        f"Status: {status}",
        f"Agent: {agent}",
        "",
        summary or "No summary provided.",
    ]

    if details:
        lines.extend(["", details])
    if changed_files:
        lines.extend(["", "Changed files:"] + [f"- {path}" for path in changed_files])
    if pr_url:
        lines.extend(["", f"PR: {pr_url}"])
    if error_info:
        lines.extend(["", f"Error: {error_info}"])

    return "\n".join(lines).strip()


def report_result(repository_full_name: str, issue_number: int, result: dict) -> dict:
    client = GitHubClient(repository_full_name)
    body = format_result_comment(result)
    client.comment_issue(issue_number, body)
    client.remove_labels(issue_number, ["dispatch:ready", "dispatch:running"])
    final_label = RESULT_TO_LABEL.get(result.get("result_status"))
    if final_label:
        client.add_labels(issue_number, [final_label])
    return {
        "comment_posted": True,
        "final_label": final_label,
    }
