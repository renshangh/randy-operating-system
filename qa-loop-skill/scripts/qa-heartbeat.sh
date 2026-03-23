#!/usr/bin/env bash
set -euo pipefail

# ------------------------------------------------------------
# qa-heartbeat.sh – Run the heartbeat checks used by the QA loop.
# ------------------------------------------------------------
# This script can be called from run-qa-loop.sh or manually.
# ------------------------------------------------------------

log() {
  echo "[heartbeat] $*"
}

log "Running OpenClaw status"
openclaw status || log "OpenClaw status returned a non‑zero code"

log "Checking active delegated issue watchlist"
python3 orchestration/check_active_dispatches.py --stale-only || log "Active dispatch watchlist reported stale delegated issues"

# Add any additional heartbeat commands defined in HEARTBEAT.md here.
# Example: check GPU health, disk usage, etc.
# openclaw exec "some health command"

log "Heartbeat checks completed"
