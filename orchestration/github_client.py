from __future__ import annotations

import shutil
import subprocess
from typing import Iterable


class GitHubClient:
    def __init__(self, repo: str):
        self.repo = repo
        self.gh = shutil.which("gh") or "/opt/homebrew/bin/gh"

    def comment_issue(self, issue_number: int, body: str) -> None:
        subprocess.run(
            [self.gh, "issue", "comment", str(issue_number), "--repo", self.repo, "--body", body],
            check=True,
            capture_output=True,
            text=True,
        )

    def add_labels(self, issue_number: int, labels: Iterable[str]) -> None:
        labels = [label for label in labels if label]
        if not labels:
            return
        for label in labels:
            subprocess.run(
                [self.gh, "issue", "edit", str(issue_number), "--repo", self.repo, "--add-label", label],
                check=False,
                capture_output=True,
                text=True,
            )

    def remove_labels(self, issue_number: int, labels: Iterable[str]) -> None:
        labels = [label for label in labels if label]
        if not labels:
            return
        # GitHub CLI returns status 1 if any label to be removed is not present.
        # We wrap this to ignore failures on removal.
        for label in labels:
            subprocess.run(
                [self.gh, "issue", "edit", str(issue_number), "--repo", self.repo, "--remove-label", label],
                check=False,
                capture_output=True,
                text=True,
            )
