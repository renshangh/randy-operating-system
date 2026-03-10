---
name: qa-loop-skill
description: Run the reusable QA loop for compile, test, lint, and heartbeat checks on a PR. Use when you need automated QA verification (e.g., on PR open, on demand via `openclaw exec`, or from CI). Trigger on any request that mentions “run QA”, “QA loop”, or similar.
---

# QA Loop Skill

## When to use
- A new pull request is opened and you want to automatically verify compilation, tests, and lint.
- A developer invokes `openclaw exec qa-loop-skill` to get an on‑demand QA run.
- CI needs to run the QA checklist as a reusable step.

## How it works
1. Executes `scripts/run-qa-loop.sh` which:
   - Cleans the workspace.
   - Compiles the `api` package.
   - Runs the test suite (`pytest`).
   - Runs the linter (`flake8`).
   - Optionally runs heartbeat health checks via `scripts/qa-heartbeat.sh`.
2. The script writes logs to `logs/qa-<timestamp>.txt` and a result flag (`PASS`/`FAIL`).
3. `scripts/report-qa-results.sh` aggregates the logs, updates `TASK.md`, posts a comment to the PR, and creates a failure issue if needed.

## Invocation
```bash
# From the repository root
openclaw exec qa-loop-skill            # runs the default QA loop
openclaw exec qa-loop-skill --pr 123   # target a specific PR number (optional)
```

## Resources
- `scripts/run-qa-loop.sh` – main driver.
- `scripts/report-qa-results.sh` – summarises and posts results.
- `scripts/qa-heartbeat.sh` – reusable heartbeat checks.
- `references/qa-checklist.md` – detailed step‑by‑step checklist.
- `references/qa-criteria.md` – pass/fail criteria and escalation policy.

## Packaging & Validation
- Run `scripts/package_skill.py qa-loop-skill` to produce `qa-loop-skill.skill`.
- Verify the skill can be invoked via `openclaw exec qa-loop-skill` and that logs appear under `logs/`.
