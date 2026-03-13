#!/bin/zsh
set -euo pipefail

REPO_DIR="${REPO_DIR:-$HOME/.openclaw/workspace-ember/randy-operating-system}"
LOG_FILE="${LOG_FILE:-/tmp/ember_webhook_listener.log}"
: "${GITHUB_WEBHOOK_SECRET:?GITHUB_WEBHOOK_SECRET is required}"
export PATH="${PATH:-/usr/bin:/bin:/usr/sbin:/sbin}:/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/local/sbin"
export PYTHONPATH="$REPO_DIR"
export ALLOWED_REPOS="${ALLOWED_REPOS:-renshangh/real-estate-assistant}"
export LISTENER_HOST="${LISTENER_HOST:-127.0.0.1}"
export LISTENER_PORT="${LISTENER_PORT:-8787}"

cd "$REPO_DIR"
exec python3 -m orchestration.webhook_listener >>"$LOG_FILE" 2>&1
