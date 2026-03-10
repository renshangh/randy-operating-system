# QA Loop Pass/Fail Criteria

The QA skill uses the following criteria to decide whether a PR passes the QA loop.

## Success Conditions
1. **Compilation**
   - `python -m compileall api` returns exit code **0**.
   - No error messages appear in the output.
2. **Test Suite**
   - `pytest` completes with exit code **0**.
   - All test cases pass (no failures or errors).  Warnings are allowed.
3. **Linting**
   - `flake8` (or the project's configured linter) returns exit code **0**.
   - No linting **errors** are reported.  Warning‑level messages do not cause a failure.
4. **Heartbeat Checks**
   - All health‑check commands defined in `HEARTBEAT.md` succeed (exit code **0**).
   - Any non‑zero exit from a heartbeat command is recorded as a **warning**, not an outright failure, unless the command is marked critical in the checklist.

## Failure Conditions
- Any step listed under **Success Conditions** returns a non‑zero exit code.
- The compiled log contains any `Traceback` or `SyntaxError` entries.
- Test output shows `FAILED` or `ERROR` lines.
- Linter output includes lines prefixed with `E` (error) – warnings (`W`) are tolerated.
- Critical heartbeat commands (e.g., service health probes) exit non‑zero.

## Reporting
- On success, the skill emits a concise summary:
  ```
  ✅ QA passed – all checks succeeded.
  ```
- On failure, the skill emits a detailed report listing the failed step(s), exit codes, and a snippet of the relevant log (first 20 lines of each failing command).
- All logs are persisted under `logs/qa-<timestamp>.txt` and a reference is added to `TASK.md` or the repository’s memory store.

## Escalation
- If a failure is due to flaky tests (detected via repeated runs or known flaky markers), the skill adds a label `flaky` to the PR and posts a comment suggesting a rerun.
- Critical failures (compilation or lint errors) automatically trigger a GitHub issue titled `QA loop failure – <PR‑number>` for further investigation.
