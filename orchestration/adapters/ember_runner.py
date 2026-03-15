from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from orchestration.adapters.base_runner import BaseRunner, RunnerResult


class EmberRunner(BaseRunner):
    agent_name = "ember"

    def __init__(self, logs_dir: str | Path | None = None, timeout_seconds: int = 600):
        base_dir = Path(__file__).resolve().parent.parent
        self.logs_dir = Path(logs_dir or (base_dir / "logs" / self.agent_name))
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.timeout_seconds = timeout_seconds

    def run(self, task_packet: dict[str, Any]) -> RunnerResult:
        run_id = task_packet["run_id"]
        log_path = self.logs_dir / f"{run_id}.json"
        prompt = self._build_prompt(task_packet)
        command = [
            "zsh",
            "-lc",
            f'cd {self._shell_quote(task_packet["local_repo_path"])} && openclaw agent --agent {self._shell_quote(self.agent_name)} --message {self._shell_quote(prompt)} --json',
        ]

        try:
            completed = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
            )
            raw = completed.stdout.strip()
            log_path.write_text(raw or completed.stderr, encoding="utf-8")
            parsed = json.loads(raw)
            text = self._extract_text(parsed)
            return RunnerResult(
                run_id=run_id,
                agent=self.agent_name,
                result_status="done",
                summary=(text[:500] if text else "Ember completed with no text payload."),
                details="Real Ember runtime invocation succeeded.",
                raw_output_path=str(log_path),
            )
        except subprocess.TimeoutExpired as exc:
            log_path.write_text(f"TIMEOUT\n{exc}", encoding="utf-8")
            return RunnerResult(
                run_id=run_id,
                agent=self.agent_name,
                result_status="failed",
                summary="Ember runtime invocation timed out.",
                error_info=str(exc),
                raw_output_path=str(log_path),
            )
        except subprocess.CalledProcessError as exc:
            body = (exc.stdout or "") + ("\n" + exc.stderr if exc.stderr else "")
            log_path.write_text(body, encoding="utf-8")
            return RunnerResult(
                run_id=run_id,
                agent=self.agent_name,
                result_status="failed",
                summary="Ember runtime invocation failed.",
                error_info=(exc.stderr or exc.stdout or str(exc))[:1000],
                raw_output_path=str(log_path),
            )
        except Exception as exc:  # noqa: BLE001
            log_path.write_text(str(exc), encoding="utf-8")
            return RunnerResult(
                run_id=run_id,
                agent=self.agent_name,
                result_status="failed",
                summary="Ember adapter crashed while invoking the runtime.",
                error_info=str(exc),
                raw_output_path=str(log_path),
            )

    def _build_prompt(self, task_packet: dict[str, Any]) -> str:
        return (
            f"Issue #{task_packet['issue_number']}: {task_packet['issue_title']}\n\n"
            f"Objective:\n{task_packet['objective']}\n\n"
            f"Constraints:\n{task_packet['scope_constraints']}\n\n"
            f"Acceptance criteria:\n{task_packet['acceptance_criteria']}\n\n"
            f"Output expectation:\n{task_packet['output_expectation']}"
        )

    def _extract_text(self, payload: dict[str, Any]) -> str:
        result = payload.get("result") or {}
        payloads = result.get("payloads") or []
        texts = [item.get("text", "") for item in payloads if item.get("text")]
        return "\n".join(texts).strip()

    def _shell_quote(self, value: str) -> str:
        return "'" + value.replace("'", "'\"'\"'") + "'"


class SarahRunner(EmberRunner):
    agent_name = "sarah"


class SentinelRunner(EmberRunner):
    agent_name = "sentinel"
