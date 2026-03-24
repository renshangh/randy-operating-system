from __future__ import annotations

import os
import re
import uuid
from pathlib import Path
from typing import Any

from orchestration.adapters.ember_runner import EmberRunner, SarahRunner, SentinelRunner
from orchestration.reporting import report_result
from orchestration.run_ledger import RunLedger
from orchestration.task_packet import build_task_packet

SUPPORTED_AGENT_LABELS = {"agent:ember": "ember", "agent:sarah": "sarah", "agent:sentinel": "sentinel"}
RESULT_LABELS = {"dispatch:running", "dispatch:done", "dispatch:blocked", "dispatch:failed"}
STATUS_DONE_LABEL = "status:done"


def _default_repo_paths() -> dict[str, str]:
    home = Path.home()

    def resolve_repo_path(env_var: str, canonical_name: str) -> str:
        env_path = os.environ.get(env_var)
        if env_path:
            return env_path
        return str(home / "repo" / canonical_name)

    return {
        "renshangh/real-estate-assistant": resolve_repo_path(
            "ORCHESTRATION_RETA_PATH",
            "real-estate-assistant",
        ),
        "renshangh/openclaw-remote-deploy": resolve_repo_path(
            "ORCHESTRATION_REMOTE_DEPLOY_PATH",
            "openclaw-remote-deploy",
        ),
        "renshangh/marketing-ops": resolve_repo_path(
            "ORCHESTRATION_MARKETING_OPS_PATH",
            "marketing-ops",
        ),
        "renshangh/randy-operating-system": resolve_repo_path(
            "ORCHESTRATION_RANDY_OPERATING_SYSTEM_PATH",
            "randy-operating-system",
        ),
        "renshangh/knowledge-base": resolve_repo_path(
            "ORCHESTRATION_KNOWLEDGE_BASE_PATH",
            "knowledge-base",
        ),
    }


class Router:
    def __init__(self, ledger_path: str | Path | None = None, repo_paths: dict[str, str] | None = None):
        base_dir = Path(__file__).resolve().parent
        self.ledger = RunLedger(ledger_path or (base_dir / "run_ledger.sqlite"))
        self.repo_paths = repo_paths or _default_repo_paths()
        self.runners = {
            "ember": EmberRunner(),
            "sarah": SarahRunner(),
            "sentinel": SentinelRunner(),
        }

    def handle_event(self, normalized_event: dict[str, Any]) -> dict[str, Any]:
        if normalized_event.get("event_type") == "issue_comment":
            return self._handle_completion_event(normalized_event)
        if normalized_event.get("event_type") == "issues" and normalized_event.get("action") == "labeled":
            event_label = str(normalized_event.get("event_label") or "").strip().lower()
            if event_label == STATUS_DONE_LABEL:
                return self._handle_completion_label_event(normalized_event, event_label)
        return self._handle_dispatch_event(normalized_event)

    def _handle_dispatch_event(self, normalized_event: dict[str, Any]) -> dict[str, Any]:
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

        if STATUS_DONE_LABEL in labels:
            return self._ignore(delivery_id, repo, issue_number, "already_done")

        local_repo_path = self.repo_paths.get(repo)
        if not local_repo_path:
            return self._blocked(delivery_id, repo, issue_number, "repo_path_not_configured")

        run_id = str(uuid.uuid4())
        task_packet = build_task_packet(normalized_event, local_repo_path)
        task_packet["run_id"] = run_id
        agent = SUPPORTED_AGENT_LABELS[agent_label]

        run_count = self.ledger.count_runs(repo, issue_number)
        if run_count >= 3 and agent == "ember":
            return self._blocked(delivery_id, repo, issue_number, f"max_retries_exceeded:{agent}:{run_count}")

        self.ledger.record(
            delivery_id,
            repo,
            issue_number,
            "running",
            event_type=normalized_event.get("event_type"),
            event_action=normalized_event.get("action"),
            classification="dispatch:ready",
            target_agent=agent,
            accepted=True,
            run_id=run_id,
            note="dispatch_eligible",
        )
        runner_result = self.runners[agent].run(task_packet)
        self.ledger.record(
            delivery_id,
            repo,
            issue_number,
            runner_result.result_status,
            event_type=normalized_event.get("event_type"),
            event_action=normalized_event.get("action"),
            classification=runner_result.result_status,
            target_agent=agent,
            accepted=True,
            run_id=run_id,
            note=runner_result.summary,
        )

        report_result(
            repo,
            issue_number,
            {
                "result_status": runner_result.result_status,
                "agent": runner_result.agent,
                "summary": runner_result.summary,
                "details": runner_result.details,
                "changed_files": runner_result.changed_files,
                "pr_url": runner_result.pr_url,
                "error_info": runner_result.error_info,
            },
        )

        return {
            "accepted": True,
            "status": runner_result.result_status,
            "run_id": run_id,
            "agent": agent,
            "repository_full_name": repo,
            "issue_number": issue_number,
        }

    def _handle_completion_event(self, normalized_event: dict[str, Any]) -> dict[str, Any]:
        delivery_id = normalized_event.get("delivery_id")
        repo = normalized_event.get("repository_full_name")
        issue_number = int(normalized_event.get("issue_number") or 0)
        issue_state = normalized_event.get("issue_state")
        comment_body = (normalized_event.get("comment_body") or "").strip()
        labels = set(normalized_event.get("labels") or [])

        if self.ledger.has_delivery(delivery_id):
            return self._ignore(delivery_id, repo, issue_number, "duplicate_delivery")
        if issue_state != "open":
            return self._ignore(delivery_id, repo, issue_number, "issue_not_open")

        parsed_completion = self._parse_completion_comment(comment_body)
        if parsed_completion:
            status, agent, summary = parsed_completion
            has_valid_return_state = STATUS_DONE_LABEL in labels and "dispatch:ready" not in labels
            has_substantive_comment = self._is_substantive_completion_comment(comment_body)
            return self._accept_completion_event(
                normalized_event,
                status=status,
                agent=agent,
                summary=summary,
                note=f"agent={agent}; summary={summary}",
                requires_discord_wake=has_valid_return_state and has_substantive_comment,
                validation_reason=(
                    "valid_specialist_return"
                    if has_valid_return_state and has_substantive_comment
                    else "completion_comment_without_valid_return_state"
                ),
            )

        parsed_command = self._parse_operator_command(comment_body)
        if parsed_command:
            command = parsed_command
            decision = f"command:{command}"
            self.ledger.record(
                delivery_id,
                repo,
                issue_number,
                decision,
                event_type=normalized_event.get("event_type"),
                event_action=normalized_event.get("action"),
                classification=decision,
                target_agent="aether",
                accepted=True,
                note=f"operator_command={command}",
                ack_status="pending",
            )
            return {
                "accepted": True,
                "status": decision,
                "classification": decision,
                "agent": "aether",
                "repository_full_name": repo,
                "issue_number": issue_number,
                "summary": f"operator command received ({command})",
                "notice_only": True,
                "requires_aether_wake": True,
            }

        return self._ignore(delivery_id, repo, issue_number, "non_actionable_comment")

    def _handle_completion_label_event(self, normalized_event: dict[str, Any], event_label: str) -> dict[str, Any]:
        delivery_id = normalized_event.get("delivery_id")
        repo = normalized_event.get("repository_full_name")
        issue_number = int(normalized_event.get("issue_number") or 0)
        issue_state = normalized_event.get("issue_state")
        labels = set(normalized_event.get("labels") or [])

        if self.ledger.has_delivery(delivery_id):
            return self._ignore(delivery_id, repo, issue_number, "duplicate_delivery")
        if issue_state != "open":
            return self._ignore(delivery_id, repo, issue_number, "issue_not_open")

        if event_label != STATUS_DONE_LABEL:
            return self._ignore(delivery_id, repo, issue_number, "non_actionable_label")

        agent_labels = sorted(label for label in labels if label.startswith("agent:"))
        agent = SUPPORTED_AGENT_LABELS.get(agent_labels[0], agent_labels[0].split(":", 1)[-1]) if agent_labels else "unknown"
        summary = f"completion label received ({event_label})"
        return self._accept_completion_event(
            normalized_event,
            status="done",
            agent=agent,
            summary=summary,
            note=f"label={event_label}; agent={agent}",
            requires_discord_wake=False,
            validation_reason=(
                "awaiting_substantive_completion_comment"
                if "dispatch:ready" not in labels
                else "dispatch_ready_still_present"
            ),
        )

    def _accept_completion_event(
        self,
        normalized_event: dict[str, Any],
        *,
        status: str,
        agent: str,
        summary: str,
        note: str,
        requires_discord_wake: bool,
        validation_reason: str,
    ) -> dict[str, Any]:
        delivery_id = normalized_event.get("delivery_id")
        repo = normalized_event.get("repository_full_name")
        issue_number = int(normalized_event.get("issue_number") or 0)
        decision = f"completion:{status}"
        self.ledger.record(
            delivery_id,
            repo,
            issue_number,
            decision,
            event_type=normalized_event.get("event_type"),
            event_action=normalized_event.get("action"),
            classification=decision,
            target_agent=agent,
            accepted=True,
            note=note,
            ack_status="pending",
        )
        return {
            "accepted": True,
            "status": decision,
            "classification": decision,
            "agent": agent,
            "repository_full_name": repo,
            "issue_number": issue_number,
            "summary": summary,
            "notice_only": True,
            "requires_aether_wake": True,
            "requires_discord_wake": requires_discord_wake,
            "validation_reason": validation_reason,
        }

    def _parse_completion_comment(self, comment_body: str) -> tuple[str, str, str] | None:
        status_match = re.search(r"^Status:\s*(done|blocked|failed)\b", comment_body, re.IGNORECASE | re.MULTILINE)
        agent_match = re.search(r"^Agent:\s*([a-zA-Z0-9:_-]+)\b", comment_body, re.IGNORECASE | re.MULTILINE)
        if not status_match or not agent_match:
            return None

        status = status_match.group(1).lower()
        agent = agent_match.group(1).lower()
        lines = [line.strip() for line in comment_body.splitlines() if line.strip()]
        summary = ""
        for line in lines:
            lower = line.lower()
            if lower.startswith("status:") or lower.startswith("agent:"):
                continue
            summary = line
            break
        summary = summary or f"completion comment received ({status})"
        return status, agent, summary

    def _is_substantive_completion_comment(self, comment_body: str) -> bool:
        lines = [line.strip() for line in comment_body.splitlines() if line.strip()]
        content_lines = []
        for line in lines:
            lower = line.lower()
            if lower.startswith("status:") or lower.startswith("agent:") or lower.startswith("author:"):
                continue
            content_lines.append(line)
        substantive_text = " ".join(content_lines).strip()
        return len(substantive_text) >= 12

    def _parse_operator_command(self, comment_body: str) -> str | None:
        stripped = comment_body.strip().lower()
        if stripped.startswith("/retry"):
            return "retry"
        if stripped.startswith("/status"):
            return "status"
        if stripped.startswith("/hold"):
            return "hold"
        return None

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
