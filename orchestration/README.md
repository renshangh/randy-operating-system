# Orchestration

Phase 1 webhook-driven orchestration scaffold for `randy-operating-system`.

## Current components
- `config.py` — environment-backed listener configuration
- `webhook_listener.py` — stdlib GitHub webhook listener scaffold
- `router.py` — Phase 1 router with label checks, dedupe, and task-packet building
- `run_ledger.py` — local SQLite delivery/run ledger
- `task_packet.py` — compact task packet builder
- `aether_relay_ingress.py` — MacBook-side relay ingress skeleton with auth, validation, dedupe, and ack behavior
- `adapters/base_runner.py` — runner result contract
- `adapters/ember_runner.py` — Ember adapter scaffold
- `github_client.py` — minimal GitHub issue comment/label wrapper
- `reporting.py` — result comment + label transition logic

## Environment variables
- `GITHUB_WEBHOOK_SECRET` — required GitHub webhook HMAC secret
- `ALLOWED_REPOS` — comma-separated repo allowlist, default: `renshangh/real-estate-assistant,renshangh/openclaw-remote-deploy`
- `ORCHESTRATION_RETA_PATH` — optional explicit local path for `renshangh/real-estate-assistant`
- `ORCHESTRATION_REMOTE_DEPLOY_PATH` — optional explicit local path for `renshangh/openclaw-remote-deploy`
- `LISTENER_HOST` — default `127.0.0.1`
- `LISTENER_PORT` — default `8787`
- `ENABLE_DIRECT_SESSION_WAKE` — enable direct OpenClaw wake path for accepted completion/command events
- `ENABLE_AETHER_RELAY` — enable Mac Mini -> MacBook relay delivery path for accepted completion/command events
- `AETHER_SESSION_LABEL` — logical target label for ledger/audit, default `aether-ops-inbox`
- `AETHER_SESSION_ID` — concrete OpenClaw session id used by the local direct-wake transport and MacBook ingress injector
- `AETHER_RELAY_URL` — MacBook relay ingress URL used by the Mac Mini relay client
- `AETHER_RELAY_SECRET` — shared secret used by the Mac Mini relay client
- `AETHER_RELAY_SENDER_ID` — sender id header used by the Mac Mini relay client, default `mac-mini`
- `AETHER_RELAY_LABEL` — logical relay target label for ledger/audit, default `aether-ops-inbox`
- `AETHER_RELAY_TIMEOUT_SECONDS` — timeout for the Mac Mini relay POST, default `20`
- `SESSION_SEND_TIMEOUT_SECONDS` — timeout for direct wake send, default `60`
- `SESSION_ACK_TIMEOUT_SECONDS` — reserved for Phase 2 ack timeout handling, default `120`
- `AETHER_RELAY_HOST` — MacBook relay ingress bind host, default `127.0.0.1`
- `AETHER_RELAY_PORT` — MacBook relay ingress port, default `8791`
- `AETHER_RELAY_SECRET` — shared secret required by the MacBook relay ingress
- `AETHER_RELAY_SENDER_ID` — expected relay sender id, default `mac-mini`
- `AETHER_RELAY_DEDUPE_DB` — local SQLite path for relay dedupe/ack state, default `orchestration/aether_relay_ingress.sqlite`
- `AETHER_RELAY_TIMEOUT_SECONDS` — timeout for injecting into Aether from the MacBook ingress, default `30`

## Start listener
```bash
export GITHUB_WEBHOOK_SECRET='replace-me'
export ALLOWED_REPOS='renshangh/real-estate-assistant,renshangh/openclaw-remote-deploy'
export ORCHESTRATION_REMOTE_DEPLOY_PATH="$HOME/.openclaw/workspace/openclaw-remote-deploy"
python -m orchestration.webhook_listener
```

## Notes
- The listener intentionally stays narrow: receive, verify, normalize, and hand off.
- Dispatch start remains label-driven via `dispatch:ready` + exactly one `agent:*` label.
- Specialist completion comments beginning with `Status: done`, `Status: blocked`, or `Status: failed` are treated as actionable completion events and recorded without redispatching work.
- Optional: set `DISCORD_HEARTBEAT_WEBHOOK_URL` (and `DISCORD_AETHER_USER_ID`) to auto-post completion notices to Discord.
- Phase 1 direct wake is now wired for accepted completion comments and operator commands (`/retry`, `/status`, `/hold`) using `openclaw agent --session-id ...`.
- The new `aether_relay_ingress.py` is the MacBook-side ingress skeleton for Phase 1 of issue #187; it accepts only narrow allowed classifications, dedupes on `delivery_id`, and returns a compact JSON ack.
- The new `relay_client.py` is the Mac Mini-side RPC sender for Phase 2 of issue #187; when `ENABLE_AETHER_RELAY=1`, the listener uses it for accepted completion/command events instead of the local direct-wake path.
- Discord heartbeat remains a human-facing mirror; the direct wake path is the machine trigger when enabled.
- `run_ledger.sqlite` now records routing plus direct wake / Discord mirror state for each accepted delivery.
- The Ember adapter boundary exists and writes local artifacts, but live runtime invocation is not yet wired.
- Reporting currently posts concise issue comments and applies result labels via `gh`.
