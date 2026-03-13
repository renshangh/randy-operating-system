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

## Environment variables
- `GITHUB_WEBHOOK_SECRET` — required GitHub webhook HMAC secret
- `ALLOWED_REPOS` — comma-separated repo allowlist, default: `renshangh/real-estate-assistant`
- `LISTENER_HOST` — default `127.0.0.1`
- `LISTENER_PORT` — default `8787`

## Start listener
```bash
export GITHUB_WEBHOOK_SECRET='replace-me'
export ALLOWED_REPOS='renshangh/real-estate-assistant'
python -m orchestration.webhook_listener
```

## Notes
- The listener intentionally stays narrow: receive, verify, normalize, and hand off.
- The router currently resolves only `agent:ember` for `renshangh/real-estate-assistant`.
- The Ember adapter boundary exists and writes local artifacts, but live runtime invocation is not yet wired.
- Reporting currently posts concise issue comments and applies result labels via `gh`.
