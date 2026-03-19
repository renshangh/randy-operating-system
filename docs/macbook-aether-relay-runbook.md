# MacBook Aether Relay Runbook

## Purpose
Run the MacBook-side Aether relay ingress as a persistent LaunchAgent-backed service.

## Scope
This runbook covers only the MacBook ingress side for issue #187.

## Preconditions
- repo available at `~/.openclaw/workspace/randy-operating-system`
- relay secret chosen
- either:
  - a real Aether session id is known, or
  - the local OpenClaw session registry can resolve the desired inbox session
- Mac Mini relay path still disabled until explicit end-to-end test window

## Current operator note
On this MacBook, the session registry file `~/.openclaw/agents/main/sessions/sessions.json` may be present but still lack an entry that matches `aether-ops-inbox`. Auto-discovery fails with `missing_aether_session_id` when the label cannot be resolved automatically.

The current durable fallback is the **session registry file** at `~/.openclaw/workspace/aether_session_registry.json`. It maps `aether-ops-inbox` to the known working session (`6611226a-5a2a-4d08-af69-3c361259276c` at the time of the lesson learn). Instead of pinning `AETHER_SESSION_ID` in the plist, keep `AETHER_SESSION_ID` empty so the relay naturally looks up the registry and remains portable across machines/rotations.

### Updating the registry
When you have a new inbox session (for example, after creating a fresh session with `openclaw agent --session-id <new-id> --message "init aether inbox"`), update the registry with:

```bash
cd ~/.openclaw/workspace/randy-operating-system
python3 scripts/update_aether_session_registry.py aether-ops-inbox <new-session-id>
```

The relay now uses that session id when the repo's `aether_relay_ingress` process starts, avoiding the need to hardcode `AETHER_SESSION_ID` in the LaunchAgent.

## Files
- launcher script: `scripts/start_aether_relay_ingress.sh`
- LaunchAgent template: `deploy/launchagents/ai.openclaw.aether-relay-ingress.plist`
- ingress log: `/tmp/aether_relay_ingress.log`
- launchagent stdout: `/tmp/aether_relay_ingress.launchagent.stdout.log`
- launchagent stderr: `/tmp/aether_relay_ingress.launchagent.stderr.log`

## Required environment values
- `AETHER_RELAY_SECRET`
- one of:
  - `AETHER_SESSION_ID`, or
  - a working session-registry path that resolves `AETHER_SESSION_LABEL`

## Recommended defaults
- `AETHER_RELAY_HOST=0.0.0.0` for cross-host relay over the tailnet (do not expose publicly)
- `AETHER_RELAY_PORT=8791`
- `AETHER_RELAY_SENDER_ID=mac-mini`
- `AETHER_SESSION_LABEL=aether-ops-inbox`
- `OPENCLAW_BIN=/Users/renshan/.nvm/versions/node/v23.8.0/bin/openclaw`

## Install steps
1. Copy the template plist into `~/Library/LaunchAgents/ai.openclaw.aether-relay-ingress.plist`.
2. Replace `REPLACE_ME` for:
   - `AETHER_RELAY_SECRET`
3. Confirm `REPO_DIR`, `AETHER_RELAY_DEDUPE_DB`, and script path match the local checkout under `~/.openclaw/workspace/randy-operating-system`.
4. If the session registry does not resolve a live inbox session, add an explicit:
   - `AETHER_SESSION_ID=<known-live-main-session-id>`
5. Load the LaunchAgent:
   ```bash
   launchctl unload ~/Library/LaunchAgents/ai.openclaw.aether-relay-ingress.plist 2>/dev/null || true
   launchctl load ~/Library/LaunchAgents/ai.openclaw.aether-relay-ingress.plist
   launchctl kickstart -k gui/$(id -u)/ai.openclaw.aether-relay-ingress
   ```

## Verification
### Process-level
```bash
launchctl print gui/$(id -u)/ai.openclaw.aether-relay-ingress
```

### Log-level
```bash
tail -n 50 /tmp/aether_relay_ingress.log
```

Expected startup line:
```text
Starting Aether relay ingress host=127.0.0.1 port=8791 session_label=aether-ops-inbox
```

### RPC dry check
A request with bad auth should return `401 unauthorized`.
A request with valid auth but no valid session injection should fail safely and leave a ledger row.

### Proven-good validation state (2026-03-19)
After fixing the LaunchAgent paths and binding a known live session id, localhost probes progressed:
- `accepted` -> `acked`

Ledger probes that verified this path:
- `localhost-fix-probe-010`
- `localhost-fix-probe-011`

## Rollback
Disable the LaunchAgent:
```bash
launchctl unload ~/Library/LaunchAgents/ai.openclaw.aether-relay-ingress.plist
```

This rollback is clean because:
- Mac Mini relay remains config-gated
- Discord mirror path remains intact
- no GitHub webhook routing behavior changes until relay is explicitly enabled on the Mac Mini
