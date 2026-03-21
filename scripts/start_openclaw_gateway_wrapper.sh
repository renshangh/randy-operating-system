#!/bin/bash
set -euo pipefail
export HOME="/Users/renshan"
export PATH="/Users/renshan/.nvm:/Users/renshan/.local/bin:/Users/renshan/.npm-global/bin:/Users/renshan/bin:/Users/renshan/.volta/bin:/Users/renshan/.asdf/shims:/Users/renshan/.bun/bin:/Users/renshan/Library/Application Support/fnm/aliases/default/bin:/Users/renshan/.fnm/aliases/default/bin:/Users/renshan/Library/pnpm:/Users/renshan/.local/share/pnpm:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
export NODE_EXTRA_CA_CERTS="/etc/ssl/cert.pem"
export NODE_USE_SYSTEM_CA="1"
export OPENCLAW_GATEWAY_PORT="18789"
export OPENCLAW_LAUNCHD_LABEL="ai.openclaw.gateway"
export OPENCLAW_SYSTEMD_UNIT="openclaw-gateway.service"
export OPENCLAW_WINDOWS_TASK_NAME="OpenClaw Gateway"
export OPENCLAW_SERVICE_MARKER="openclaw"
export OPENCLAW_SERVICE_KIND="gateway"
export OPENCLAW_SERVICE_VERSION="2026.3.13"
exec /bin/bash -lc '/Users/renshan/.nvm/versions/node/v23.8.0/bin/node /Users/renshan/.nvm/versions/node/v23.8.0/lib/node_modules/openclaw/dist/index.js gateway --port 18789'
