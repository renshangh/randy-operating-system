from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Any

from orchestration.adapters.ember_runner import EmberRunner
from orchestration.run_ledger import RunLedger
from orchestration.task_packet import build_task_packet

SUPPORTED_AGENT_LABELS = {"agent:ember": "ember"}
RESULT_LABELS = {"dispatch:running", "dispatch:done", "dispatch:blocked", "dispatch:failed"}


def _default_repo_paths() -> dict[str, str]:
    env_reta = os.environ.get("ORCHESTRATION_RETA_PATH")
    if env_reta:
        return {"renshangh/real-estate-assistant": env_reta}

    home = Path.home()
    ember_reta = home / ".openclaw" / "workspace-ember" / "real-estate-assistant"
    if ember_reta.exists():
        return {"renshangh/real-estate-assistant": str(ember_reta)}

    main_reta = home / ".openclaw" / "workspace" / "real-estate-assistant"
    return {"renshangh/real-estate-assistant": str(main_reta)}


class Router:
    def __init__(self, ledger_path: str | Path | None = None, repo_paths: dict[str, str] | None = None):
        base_dir = Path(__file__).resolve().parent
        self.ledger = RunLedger(ledger_path or (base_dir / "run_ledger.sqlite"))
        self.repo_paths = repo_paths or _default_repo_paths()
        self.runners = {
            "ember": EmberRunner(),
        }

    def handle_event(self, normalized_event: dict[str, Any]) -> dict[str, Any]:
        delivery_id = normalized_event.get("delivery_id")
        repo = normalized_event.get("repository_full_name")
        issue_number = int(normalized_event.get("issue_number") or 0)
        labels = set(normalized_event.get("labels") or [])
        issue_state = normalized_event.get("issue_state")

        if self.ledger.has_delivery(delivery_id):
            return self._ignore(delivery_id, repo, issue_number, "duplicate_delivery")

        if issue_state != "open":
            return self._ignore(delivery_id, repo, issue_number, "issue_not_open")

        agent_labels = sorted(label for label in labels if label.startswith("agent:"))
        if len(agent_labels) != 1:
            return self._blocked(delivery_id, repo, issue_number, "invalid_agent_label_state")

        agent_label = agent_labels[0]
        if agent_label not in SUPPORTED_AGENT_LABELS:
            return self._blocked(delivery_id, repo, issue_number, "unsupported_agent")

        if "dispatch:ready" not in labels:
            return self._ignore(delivery_id, repo, issue_number, "dispatch_not_ready")

        if "dispatch:running" in labels or "dispatch:done" in labels:
            return self._ignore(delivery_id, repo, issue_number, "already_running_or_done")

        conflicting = RESULT_LABELS.intersection(labels) - {"dispatch:running", "dispatch:done"}
        if conflicting:
            return self._blocked(delivery_id, repo, issue_number, f"conflicting_result_labels:{','.join(sorted(conflicting))}")

        local_repo_path = self.repo_paths.get(repo)
        if not local_repo_path:
            return self._blocked(delivery_id, repo, issue_number, "repo_path_not_configured")

        run_id = str(uuid.uuid4())
        task_packet = build_task_packet(normalized_event, local_repo_path)
        task_packet["run_id"] = run_id
        agent = SUPPORTED_AGENT_LABELS[agent_label]
        self.ledger.record(delivery_id, repo, issue_number, "running", run_id=run_id, note="dispatch_eligible")
        runner_result = self.runners[agent].run(task_packet)
        self.ledger.record(delivery_id, repo, issue_number, runner_result.result_status, run_id=run_id, note=runner_result.summary)
        return {
            "accepted": True,
            "status": runner_result.result_status,
            "run_id": run_id,
            "agent": agent,
            "repository_full_name": repo,
            "issue_number": issue_number,
            "task_packet": task_packet,
            "runner_result": {
                "run_id": runner_result.run_id,
                "agent": runner_result.agent,
                "result_status": runner_result.result_status,
                "summary": runner_result.summary,
                "details": runner_result.details,
                "changed_files": runner_result.changed_files,
                "pr_url": runner_result.pr_url,
                "error_info": runner_result.error_info,
                "raw_output_path": runner_result.raw_output_path,
            },
        }

    def _ignore(self, delivery_id: str, repo: str, issue_number: int, note: str) -> dict[str, Any]:
        self.ledger.record(delivery_id, repo, issue_number, "ignored", note=note)
        return {
            "accepted": False,
            "status": "ignored",
            "repository_full_name": repo,
            "issue_number": issue_number,
            "reason": note,
        }

    def _blocked(self, delivery_id: str, repo: str, issue_number: int, note: str) -> dict[str, Any]:
        self.ledger.record(delivery_id, repo, issue_number, "blocked", note=note)
        return {
            "accepted": False,
            "status": "blocked",
            "repository_full_name": repo,
            "issue_number": issue_number,
            "reason": note,
        }
