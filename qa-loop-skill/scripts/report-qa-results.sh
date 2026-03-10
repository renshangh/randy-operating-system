#!/usr/bin/env bash
set -euo pipefail

# ------------------------------------------------------------
# report-qa-results.sh – Summarize QA run and update TASK.md
# ------------------------------------------------------------
# Arguments:
#   $1 – Path to the full QA log file.
#   $2 – PR number (optional, for linking).
# ------------------------------------------------------------

LOG_FILE="${1:-}"; PR_NUMBER="${2:-}";
if [[ -z "$LOG_FILE" ]]; then
  echo "Usage: $0 <log-file> [pr-number]"
  exit 1
fi

# Determine result (PASS/FAIL) from companion result file if present
RESULT_FILE="${LOG_FILE%.*}-result.txt"
if [[ -f "$RESULT_FILE" ]]; then
  RESULT=$(cat "$RESULT_FILE")
else
  RESULT="UNKNOWN"
fi

# Build summary
SUMMARY="QA Run for PR #${PR_NUMBER:-N/A}: $RESULT"

# Append summary to TASK.md (project root)
TASK_FILE="$(pwd)/TASK.md"
{
  echo "\n---\n"
  echo "## QA Summary – $(date)"
  echo "* PR: ${PR_NUMBER:-N/A}"
  echo "* Result: $RESULT"
  echo "* Log: $LOG_FILE"
  echo "\n$(head -n 20 "$LOG_FILE")"
  echo "\n---\n"
} >> "$TASK_FILE"

# Optionally post a comment back to the PR (if gh CLI is authenticated)
if [[ -n "$PR_NUMBER" && "$PR_NUMBER" != "N/A" ]]; then
  COMMENT="QA $RESULT – see logs in \\`$LOG_FILE\\`."
  gh pr comment "$PR_NUMBER" --repo renshangh/randy-operating-system --body "$COMMENT" || true
fi

# If failure, create an issue for investigation (optional)
if [[ "$RESULT" == "FAIL" ]]; then
  gh issue create --repo renshangh/randy-operating-system \
    --title "QA loop failure – PR #${PR_NUMBER}" \
    --body "The QA loop failed for PR #${PR_NUMBER}. See $LOG_FILE for details." || true
fi

echo "Report written to $TASK_FILE"
