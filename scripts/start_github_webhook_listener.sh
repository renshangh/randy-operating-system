#!/bin/zsh
set -euo pipefail

REPO_DIR="${REPO_DIR:-$HOME/.openclaw/workspace/randy-operating-system}"
ENV_FILE="${ENV_FILE:-$REPO_DIR/deploy/aether_github_webhook_listener.env}"
LOG_FILE="${LOG_FILE:-/tmp/aether_github_webhook_listener.log}"

if [[ -f "$ENV_FILE" ]]; then
  set -a
  source "$ENV_FILE"
  set +a
fi

: "${GITHUB_WEBHOOK_SECRET:?GITHUB_WEBHOOK_SECRET is required}"
export PATH="${PATH:-/usr/bin:/bin:/usr/sbin:/sbin}:/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/local/sbin"
export PYTHONPATH="$REPO_DIR"
export ALLOWED_REPOS="${ALLOWED_REPOS:-renshangh/real-estate-assistant,renshangh/openclaw-remote-deploy,renshangh/marketing-ops,renshangh/randy-job-hunt-pipeline,renshangh/randy-operating-system,renshangh/knowledge-base}"
export LISTENER_HOST="${LISTENER_HOST:-127.0.0.1}"
export LISTENER_PORT="${LISTENER_PORT:-8787}"
export DISCORD_HEARTBEAT_WEBHOOK_URL="${DISCORD_HEARTBEAT_WEBHOOK_URL:-}"
export DISCORD_AETHER_USER_ID="${DISCORD_AETHER_USER_ID:-}"

cd "$REPO_DIR"
exec python3 -m orchestration.webhook_listener >>"$LOG_FILE" 2>&1
