from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RunnerResult:
    run_id: str
    agent: str
    result_status: str
    summary: str
    details: str = ""
    changed_files: list[str] = field(default_factory=list)
    pr_url: str | None = None
    error_info: str | None = None
    raw_output_path: str | None = None


class BaseRunner:
    agent_name: str = "base"

    def run(self, task_packet: dict[str, Any]) -> RunnerResult:  # pragma: no cover
        raise NotImplementedError
