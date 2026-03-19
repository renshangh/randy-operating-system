#!/bin/zsh
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <session-id>"
  echo "Example: $0 6611226a-5a2a-4d08-af69-3c361259276c"
  exit 1
fi

SESSION_ID=$1
REGISTRY=${AETHER_SESSION_REGISTRY:-~/.openclaw/workspace/aether_session_registry.json}
LAUNCH_AGENT=~/Library/LaunchAgents/ai.openclaw.aether-relay-ingress.plist
SCRIPT_DIR=$(dirname "$0")

python3 "${SCRIPT_DIR}/update_aether_session_registry.py" aether-ops-inbox "$SESSION_ID" --registry "$REGISTRY"

launchctl unload "$LAUNCH_AGENT" 2>/dev/null || true
launchctl load "$LAUNCH_AGENT"
launchctl kickstart -k "gui/$(id -u)/ai.openclaw.aether-relay-ingress"

"${SCRIPT_DIR}/start_aether_relay_ingress.sh"
