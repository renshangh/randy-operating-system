# Orchestration

Phase 1 webhook-driven orchestration scaffold for `randy-operating-system`.

## Current components
- `config.py` — environment-backed listener configuration
- `webhook_listener.py` — stdlib GitHub webhook listener scaffold
- `router.py` — Phase 1 router with label checks, dedupe, and task-packet building
- `run_ledger.py` — local SQLite delivery/run ledger
- `task_packet.py` — compact task packet builder
- `adapters/base_runner.py` — runner result contract
- `adapters/ember_runner.py` — Ember adapter scaffold
- `github_client.py` — minimal GitHub issue comment/label wrapper
- `reporting.py` — result comment + label transition logic
- `amy_transcript_adapter.py` — Amy Mac Mini transcript JSONL adapter for mirror events
- `discord_output.py` — shared Discord webhook sender used by mirroring/notice flows
- `mirror_ledger.py` — SQLite dedupe + cursor state for transcript mirroring
- `mirror_amy_to_discord.py` — narrow validation-oriented Amy -> Discord mirror runner
- `sarah_telegram_adapter.py` — Sarah Telegram session discovery + transcript adapter
- `mirror_sarah_telegram_to_discord.py` — narrow validation-oriented Sarah Telegram -> Discord mirror runner

## Environment variables
- `GITHUB_WEBHOOK_SECRET` — required GitHub webhook HMAC secret
- `ALLOWED_REPOS` — comma-separated repo allowlist, default: `renshangh/real-estate-assistant,renshangh/openclaw-remote-deploy`
- `ORCHESTRATION_RETA_PATH` — optional explicit local path for `renshangh/real-estate-assistant`
- `ORCHESTRATION_REMOTE_DEPLOY_PATH` — optional explicit local path for `renshangh/openclaw-remote-deploy`
- `LISTENER_HOST` — default `127.0.0.1`
- `LISTENER_PORT` — default `8787`
- `ENABLE_DIRECT_SESSION_WAKE` — enable local direct OpenClaw wake path for accepted completion/command events
- `AETHER_SESSION_LABEL` — logical target label for ledger/audit, default `aether-ops-inbox`
- `AETHER_SESSION_ID` — concrete OpenClaw session id used by the local direct-wake transport
- `AETHER_SESSION_REGISTRY` — optional registry path used to resolve the active Aether session id when `AETHER_SESSION_ID` is unset, default `~/.openclaw/workspace/aether_session_registry.json`
- `SESSION_SEND_TIMEOUT_SECONDS` — timeout for direct wake send, default `60`
- `SESSION_ACK_TIMEOUT_SECONDS` — reserved for Phase 2 ack timeout handling, default `120`
- `AETHER_RELAY_HOST` — MacBook relay ingress bind host, default `127.0.0.1`
- `AETHER_RELAY_PORT` — MacBook relay ingress port, default `8791`
- `AETHER_RELAY_SECRET` — shared secret required by the MacBook relay ingress
- `AETHER_RELAY_SENDER_ID` — expected relay sender id, default `mac-mini`
- `AETHER_RELAY_DEDUPE_DB` — local SQLite path for relay dedupe/ack state, default `orchestration/aether_relay_ingress.sqlite`
- `AETHER_RELAY_TIMEOUT_SECONDS` — timeout for injecting into Aether from the MacBook ingress, default `30`
- `DISCORD_REVIEW_WEBHOOK_URL` — optional Discord webhook for the validation review surface; `mirror_amy_to_discord.py` falls back to `DISCORD_HEARTBEAT_WEBHOOK_URL` if unset
- `AMY_TRANSCRIPT_PATH` — optional override for the Amy transcript JSONL path, default: `~/.openclaw/agents/amy/sessions/4da4b59b-d945-43b6-8707-06e2cc2d88c2.jsonl`
- `SARAH_SESSIONS_INDEX_PATH` — optional override for Sarah session discovery index, default: `~/.openclaw/agents/sarah/sessions/sessions.json`
- `MIRROR_LEDGER_PATH` — optional SQLite path for mirror dedupe + cursor state, default: `orchestration/mirror_ledger.sqlite`

## Sarah Telegram mirror runner notes
- Run as a module from the repo root: `python3 -m orchestration.mirror_sarah_telegram_to_discord ...`
- Discovery prefers `agent:sarah:telegram:*` keys but also falls back to session metadata that identifies a Sarah-owned Telegram session.
- If runtime session keys differ from the expected prefix, pass one or more explicit `--session-key` values.
- Malformed/blank transcript lines are skipped instead of aborting the whole run.

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
- Phase 1 direct wake is wired for accepted completion comments and operator commands (`/retry`, `/status`, `/hold`) using `openclaw agent --session-id ...` when explicitly enabled.
- The Mac Mini -> MacBook relay experiment is no longer part of the active orchestration path; keep GitHub as durable state and Discord as the human-facing mirror/clarification layer.
- Background poller scripts should set an explicit PATH instead of relying on cron/launchd defaults; `issue_50_progress_bus_poll.sh` was hardened after repeated `gh: command not found` failures in background execution.
- Discord heartbeat remains a human-facing mirror; the direct wake path is the machine trigger when enabled.
- `run_ledger.sqlite` records routing plus direct wake / Discord mirror state for each accepted delivery.
- The Ember adapter boundary exists and writes local artifacts, but live runtime invocation is not yet wired.
- Reporting currently posts concise issue comments and applies result labels via `gh`.
