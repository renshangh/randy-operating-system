# GitHub Webhook → Mac Mini Endpoint Runbook

## Purpose
This runbook documents the full setup for delivering GitHub webhook events to the Mac Mini over a public Tailscale Funnel endpoint and forwarding them into the local orchestration listener.

It covers:
- local listener startup
- Tailscale Serve/Funnel setup
- GitHub webhook configuration
- secret alignment
- validation and troubleshooting

## Architecture

```text
GitHub Webhook
  -> public HTTPS endpoint via Tailscale Funnel
  -> Mac Mini Tailscale Serve proxy
  -> local listener on 127.0.0.1:8787
  -> orchestration router
  -> Ember runtime
  -> GitHub issue comment / label updates
```

## Current Known-Good Endpoint Pattern
- Public base URL:
  - `https://daniels-mac-mini-1.tail807add.ts.net`
- Webhook path:
  - `https://daniels-mac-mini-1.tail807add.ts.net/github/webhook`
- Local listener target:
  - `http://127.0.0.1:8787`

## Prerequisites
- Mac Mini reachable via SSH
- Tailscale installed and logged in on the Mac Mini
- Tailscale Funnel enabled for the tailnet/account
- GitHub CLI authenticated on the Mac Mini if reporting back to GitHub is required
- Local orchestration repo present on the Mac Mini at:
  - `~/.openclaw/workspace-ember/randy-operating-system`

## 1. Connect to the Mac Mini
From the operator machine:

```bash
ssh danielshan@192.168.1.44
```

## 2. Start the local webhook listener
From the Mac Mini:

```bash
cd ~/.openclaw/workspace-ember/randy-operating-system
export PYTHONPATH=$PWD
export GITHUB_WEBHOOK_SECRET='reta-webhook-2026'
export ALLOWED_REPOS='renshangh/real-estate-assistant'
export LISTENER_HOST='127.0.0.1'
export LISTENER_PORT='8787'
nohup python3 -m orchestration.webhook_listener >/tmp/ember_webhook_listener.log 2>&1 &
```

### Verify listener is bound
```bash
lsof -iTCP:8787 -sTCP:LISTEN -n -P
```

Expected:
- Python listening on `127.0.0.1:8787`

### If the port is already in use
Find/stop the previous listener:

```bash
ps aux | grep orchestration.webhook_listener | grep -v grep
kill <pid>
```

Then restart the listener.

## 3. Publish the local listener inside Tailscale
From the Mac Mini:

```bash
tailscale serve --bg http://127.0.0.1:8787
```

### Verify Serve
```bash
tailscale serve status
```

Expected pattern:

```text
https://<machine>.tail<tailnet>.ts.net/
|-- proxy http://127.0.0.1:8787
```

## 4. Expose the endpoint publicly with Funnel
From the Mac Mini:

```bash
tailscale funnel --bg http://127.0.0.1:8787
```

### Verify Funnel
```bash
tailscale funnel status
```

Expected pattern:

```text
https://<machine>.tail<tailnet>.ts.net (Funnel on)
|-- / proxy http://127.0.0.1:8787
```

## 5. Configure the GitHub webhook
In the target repository:
- `Settings`
- `Webhooks`
- `Add webhook`

Use:

### Payload URL
```text
https://daniels-mac-mini-1.tail807add.ts.net/github/webhook
```

### Content type
```text
application/json
```

### Secret
Use the exact same string configured on the listener, for example:

```text
reta-webhook-2026
```

### SSL verification
- **Enable SSL verification**

### Events
Recommended minimum:
- Issues
- Issue comments

## 6. Validate delivery
### A. GitHub-side validation
After saving the webhook:
- open the webhook
- inspect `Recent Deliveries`
- trigger a redelivery or create a fresh issue/label event

Expected:
- green checkmark
- HTTP 200

### B. Listener-side validation
Check the listener log:

```bash
sed -n '1,260p' /tmp/ember_webhook_listener.log
```

Expected examples:
- `Accepted event ... event=issues action=labeled issue=157`
- `Ignoring unsupported event ... event=ping`

### C. Ember artifact validation
Check recent Ember artifacts:

```bash
ls -lt ~/.openclaw/workspace-ember/randy-operating-system/orchestration/logs/ember | head
```

## 7. Trigger a safe end-to-end test
Use either:
- an existing safe test issue, or
- a new throwaway issue

Recommended dispatch labels:
- `agent:ember`
- `dispatch:ready`

### Important label exactness
The router currently expects:

```text
agent:ember
```

not:

```text
agent: ember
```

A label with a space after the colon will be blocked as `unsupported_agent`.

## 8. Known-good troubleshooting patterns

### Problem: `invalid_signature`
GitHub delivery body:

```json
{"error": "invalid_signature"}
```

Cause:
- webhook secret in GitHub does not match `GITHUB_WEBHOOK_SECRET` on the Mac Mini listener

Fix:
- set both sides to the exact same secret string
- restart the listener if needed

### Problem: `tailscale serve --bg 443 http://127.0.0.1:8787` fails with `invalid argument format`
Cause:
- local Tailscale CLI expects the target URL without explicit `443` positional syntax

Fix:

```bash
tailscale serve --bg http://127.0.0.1:8787
```

### Problem: `tailscale funnel --bg on` fails with `non-localhost target "http://on" must include a scheme`
Cause:
- local Tailscale CLI expects the target URL in the funnel command as well

Fix:

```bash
tailscale funnel --bg http://127.0.0.1:8787
```

### Problem: Webhook delivery succeeds but issue does not update
Possible causes:
- router blocked dispatch due to unsupported labels
- issue label mismatch such as `agent: ember` vs `agent:ember`
- downstream reporting/label update error

Checks:

```bash
sed -n '1,260p' /tmp/ember_webhook_listener.log
ls -lt ~/.openclaw/workspace-ember/randy-operating-system/orchestration/logs/ember | head
sqlite3 ~/.openclaw/workspace-ember/randy-operating-system/orchestration/run_ledger.sqlite ".tables"
sqlite3 -header -column ~/.openclaw/workspace-ember/randy-operating-system/orchestration/run_ledger.sqlite "select delivery_id, repository_full_name, issue_number, seen_at, dispatch_decision, run_id, note from run_ledger order by seen_at desc limit 20;"
```

### Problem: listener fails to start with `Address already in use`
Cause:
- old listener still bound to port 8787

Fix:

```bash
ps aux | grep orchestration.webhook_listener | grep -v grep
kill <pid>
```

Then restart the listener.

## 9. Operational notes
- Webhook transport can be healthy even when workflow dispatch is blocked by labels.
- Green GitHub deliveries only prove ingress and request acceptance, not full task execution.
- The cleanest first validation sequence is:
  1. webhook delivery 200
  2. listener accepted event
  3. run artifact created
  4. GitHub issue comment posted
  5. labels updated correctly

## 10. Recommended next hardening steps
- replace shell-export listener startup with a durable launch script/service definition
- persist the webhook secret in a managed env file or LaunchAgent config
- normalize supported label parsing so trivial formatting differences are less brittle
- make label cleanup/reporting idempotent and explicit
- document expected label taxonomy in the repo
