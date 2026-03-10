# QA Loop Checklist

This checklist defines the exact steps the QA skill will execute for each PR.

## 1. Workspace preparation
- Ensure a clean git checkout of the PR branch.
- Remove any previous build artifacts (`rm -rf __pycache__` and `build/` if present).

## 2. Compile step
- Run: `python -m compileall api`
- Verify that the command exits with status `0` (no compilation errors).

## 3. Test suite
- Execute the repository's test suite (adjust as needed for the project):
  ```bash
  pytest -q
  ```
- Capture the exit code; any non‑zero code marks the QA run as **failed**.

## 4. Lint / static analysis
- Run the configured linter (example using `flake8`):
  ```bash
  flake8 .
  ```
- The linter must return exit code `0`. Warnings can be tolerated but errors will fail the run.

## 5. Heartbeat verification (optional but recommended)
- Re‑run any heartbeat commands that monitor long‑running services, e.g.:
  - `openclaw status`
  - Custom health checks defined in `HEARTBEAT.md`
- Ensure these commands succeed; otherwise record a warning.

## 6. Reporting
- Collect the logs from steps 2‑5 and store them under `logs/qa-<timestamp>.txt`.
- Pass the summary to `scripts/report-qa-results.sh` (implemented in M2).

**Note:** The checklist is deliberately linear; each step aborts on failure to avoid cascading errors.
