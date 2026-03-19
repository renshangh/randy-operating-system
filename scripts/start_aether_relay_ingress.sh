#!/bin/zsh
set -euo pipefail

REPO_DIR="${REPO_DIR:-$HOME/repo/randy-operating-system}"
LOG_FILE="${LOG_FILE:-/tmp/aether_relay_ingress.log}"
: "${AETHER_RELAY_SECRET:?AETHER_RELAY_SECRET is required}"
: "${AETHER_SESSION_ID:?AETHER_SESSION_ID is required}"
export PATH="${PATH:-/usr/bin:/bin:/usr/sbin:/sbin}:/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/local/sbin"
export PYTHONPATH="$REPO_DIR"
export AETHER_RELAY_HOST="${AETHER_RELAY_HOST:-127.0.0.1}"
export AETHER_RELAY_PORT="${AETHER_RELAY_PORT:-8791}"
export AETHER_RELAY_SENDER_ID="${AETHER_RELAY_SENDER_ID:-mac-mini}"
export AETHER_RELAY_DEDUPE_DB="${AETHER_RELAY_DEDUPE_DB:-$REPO_DIR/orchestration/aether_relay_ingress.sqlite}"
export AETHER_RELAY_TIMEOUT_SECONDS="${AETHER_RELAY_TIMEOUT_SECONDS:-30}"
export AETHER_SESSION_LABEL="${AETHER_SESSION_LABEL:-aether-ops-inbox}"

cd "$REPO_DIR"
exec python3 -m orchestration.aether_relay_ingress >>"$LOG_FILE" 2>&1
