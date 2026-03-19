# MacBook Aether Relay Runbook

## Purpose
Run the MacBook-side Aether relay ingress as a persistent LaunchAgent-backed service.

## Scope
This runbook covers only the MacBook ingress side for issue #187.

## Preconditions
- repo available at `~/repo/randy-operating-system`
- real Aether session id known
- relay secret chosen
- Mac Mini relay path still disabled until explicit end-to-end test window

## Files
- launcher script: `scripts/start_aether_relay_ingress.sh`
- LaunchAgent template: `deploy/launchagents/ai.openclaw.aether-relay-ingress.plist`
- ingress log: `/tmp/aether_relay_ingress.log`
- launchagent stdout: `/tmp/aether_relay_ingress.launchagent.stdout.log`
- launchagent stderr: `/tmp/aether_relay_ingress.launchagent.stderr.log`

## Required environment values
- `AETHER_RELAY_SECRET`
- `AETHER_SESSION_ID`

## Recommended defaults
- `AETHER_RELAY_HOST=0.0.0.0` for cross-host relay over the tailnet (do not expose publicly)
- `AETHER_RELAY_PORT=8791`
- `AETHER_RELAY_SENDER_ID=mac-mini`
- `AETHER_SESSION_LABEL=aether-ops-inbox`

## Install steps
1. Copy the template plist into `~/Library/LaunchAgents/ai.openclaw.aether-relay-ingress.plist`.
2. Replace both `REPLACE_ME` values:
   - `AETHER_RELAY_SECRET`
   - `AETHER_SESSION_ID`
3. Confirm `REPO_DIR` and script path match the local checkout.
4. Load the LaunchAgent:
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

## Rollback
Disable the LaunchAgent:
```bash
launchctl unload ~/Library/LaunchAgents/ai.openclaw.aether-relay-ingress.plist
```

This rollback is clean because:
- Mac Mini relay remains config-gated
- Discord mirror path remains intact
- no GitHub webhook routing behavior changes until relay is explicitly enabled on the Mac Mini
