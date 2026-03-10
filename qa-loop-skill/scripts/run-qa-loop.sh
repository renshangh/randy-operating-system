#!/usr/bin/env bash
set -euo pipefail

# ------------------------------------------------------------
# run-qa-loop.sh – Execute the QA checklist for a PR.
# ------------------------------------------------------------
# Expected environment variables (optional):
#   PR_NUMBER – PR identifier (used for log naming).
#   REPO_ROOT – Path to the repository root (default: current dir).
# ------------------------------------------------------------

PR_NUMBER="${PR_NUMBER:-unknown}"
REPO_ROOT="${REPO_ROOT:-$(pwd)}"
TIMESTAMP=$(date +%Y%m%d%H%M%S)
LOG_DIR="$REPO_ROOT/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/qa-${PR_NUMBER}-${TIMESTAMP}.txt"

log() {
  echo "[${PR_NUMBER}] $*" | tee -a "$LOG_FILE"
}

log "=== QA Loop Start (PR #$PR_NUMBER) ==="

# 1. Workspace preparation
log "Cleaning workspace"
git clean -fdx || true
rm -rf __pycache__ build/ || true

# 2. Compile step
log "Compiling api package"
if python -m compileall api; then
  log "Compile succeeded"
else
  log "Compile failed"
  echo "FAIL" > "$LOG_DIR/qa-result-${PR_NUMBER}.txt"
  exit 1
fi

# 3. Test suite
log "Running pytest"
if pytest -q; then
  log "Tests passed"
else
  log "Tests failed"
  echo "FAIL" > "$LOG_DIR/qa-result-${PR_NUMBER}.txt"
  exit 1
fi

# 4. Lint/static analysis (flake8 as example)
log "Running flake8 lint"
if flake8 .; then
  log "Lint passed"
else
  log "Lint errors detected"
  echo "FAIL" > "$LOG_DIR/qa-result-${PR_NUMBER}.txt"
  exit 1
fi

# 5. Heartbeat verification – optional, run generic openclaw status
log "Running heartbeat verification"
if openclaw status; then
  log "Heartbeat checks passed"
else
  log "Heartbeat warnings detected"
  # Not a hard stop – continue but note warning
fi

log "=== QA Loop Completed Successfully ==="

echo "PASS" > "$LOG_DIR/qa-result-${PR_NUMBER}.txt"

# Hand off to reporting script
if [[ -x "$REPO_ROOT/scripts/report-qa-results.sh" ]]; then
  "$REPO_ROOT/scripts/report-qa-results.sh" "$LOG_FILE" "$PR_NUMBER"
else
  log "Report script not found – skipping"
fi
