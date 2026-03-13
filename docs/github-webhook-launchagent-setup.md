# GitHub Webhook Listener LaunchAgent Setup

## Purpose
This document converts the GitHub webhook listener on the Mac Mini from a manual shell-started process into a persistent macOS LaunchAgent service.

Use this after the webhook path has already been validated manually.

## Files
- Startup script:
  - `scripts/start_github_webhook_listener.sh`
- LaunchAgent template:
  - `deploy/launchagents/ai.openclaw.github-webhook-listener.plist`

## What this service does
At login / LaunchAgent load time it:
- sets the required environment variables
- sets `PYTHONPATH` to the orchestration repo root
- starts `python3 -m orchestration.webhook_listener`
- keeps the listener alive if it exits

## Important assumptions
Current template assumes:
- Mac Mini user: `danielshan`
- repo path:
  - `/Users/danielshan/.openclaw/workspace-ember/randy-operating-system`
- listener log:
  - `/tmp/ember_webhook_listener.log`
- listener bind:
  - `127.0.0.1:8787`

## 1. Copy the files to the Mac Mini repo
From the operator machine:

```bash
rsync -av \
  scripts/start_github_webhook_listener.sh \
  deploy/launchagents/ai.openclaw.github-webhook-listener.plist \
  danielshan@192.168.1.44:/Users/danielshan/.openclaw/workspace-ember/randy-operating-system/
```

If the deploy directory does not already exist remotely, copy with explicit destinations:

```bash
ssh danielshan@192.168.1.44 'mkdir -p ~/.openclaw/workspace-ember/randy-operating-system/deploy/launchagents'
rsync -av scripts/start_github_webhook_listener.sh danielshan@192.168.1.44:/Users/danielshan/.openclaw/workspace-ember/randy-operating-system/scripts/
rsync -av deploy/launchagents/ai.openclaw.github-webhook-listener.plist danielshan@192.168.1.44:/Users/danielshan/.openclaw/workspace-ember/randy-operating-system/deploy/launchagents/
```

## 2. Make the startup script executable
On the Mac Mini:

```bash
chmod +x ~/.openclaw/workspace-ember/randy-operating-system/scripts/start_github_webhook_listener.sh
```

## 3. Review the LaunchAgent template
Open and verify the values in:

```bash
~/.openclaw/workspace-ember/randy-operating-system/deploy/launchagents/ai.openclaw.github-webhook-listener.plist
```

Pay special attention to:
- `GITHUB_WEBHOOK_SECRET`
- `REPO_DIR`
- `ALLOWED_REPOS`
- `LISTENER_HOST`
- `LISTENER_PORT`

## 4. Install the LaunchAgent into the user LaunchAgents directory
On the Mac Mini:

```bash
mkdir -p ~/Library/LaunchAgents
cp ~/.openclaw/workspace-ember/randy-operating-system/deploy/launchagents/ai.openclaw.github-webhook-listener.plist ~/Library/LaunchAgents/
```

## 5. Unload any old instance first (safe if absent)
```bash
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/ai.openclaw.github-webhook-listener.plist 2>/dev/null || true
```

## 6. Load the service
```bash
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.openclaw.github-webhook-listener.plist
launchctl enable gui/$(id -u)/ai.openclaw.github-webhook-listener
launchctl kickstart -k gui/$(id -u)/ai.openclaw.github-webhook-listener
```

## 7. Verify the service
### LaunchAgent state
```bash
launchctl print gui/$(id -u)/ai.openclaw.github-webhook-listener | sed -n '1,160p'
```

### Listener bind
```bash
lsof -iTCP:8787 -sTCP:LISTEN -n -P
```

### Listener log
```bash
sed -n '1,120p' /tmp/ember_webhook_listener.log
```

### LaunchAgent stdout/stderr
```bash
sed -n '1,120p' /tmp/ember_webhook_listener.launchagent.stdout.log
sed -n '1,120p' /tmp/ember_webhook_listener.launchagent.stderr.log
```

## 8. Service management commands
### Restart
```bash
launchctl kickstart -k gui/$(id -u)/ai.openclaw.github-webhook-listener
```

### Stop/unload
```bash
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/ai.openclaw.github-webhook-listener.plist
```

### Disable
```bash
launchctl disable gui/$(id -u)/ai.openclaw.github-webhook-listener
```

### Re-enable
```bash
launchctl enable gui/$(id -u)/ai.openclaw.github-webhook-listener
```

## 9. Interaction with Tailscale Serve/Funnel
This LaunchAgent only keeps the local listener alive.

Public ingress still depends on Tailscale:

```bash
tailscale serve --bg http://127.0.0.1:8787
tailscale funnel --bg http://127.0.0.1:8787
```

Check status with:

```bash
tailscale serve status
tailscale funnel status
```

## 10. Security note
The template currently stores the webhook secret directly in the plist for simplicity and repeatability.

For stronger hardening later, move the secret into:
- a protected env file sourced by the start script, or
- a secrets manager / Keychain-backed retrieval step

## 11. Recommended operational state
For stable operation on the Mac Mini:
- LaunchAgent manages the local listener lifecycle
- Tailscale Serve/Funnel manages HTTPS ingress
- GitHub webhook sends to the Funnel URL
- issue labels must use exact supported values such as `agent:ember`
