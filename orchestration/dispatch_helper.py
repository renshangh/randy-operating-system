from __future__ import annotations

import argparse
from dataclasses import dataclass

from orchestration.github_client import GitHubClient

DISPATCH_READY_LABEL = "dispatch:ready"

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

    return DispatchResult(
        repo=repo,
        issue_number=issue_number,
        agent=agent,
        labels_added=labels,
        github_comment_posted=github_comment_posted,
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
