# Memory Embedding Phase 1 — Plugin Patch Status

Related issue: `renshangh/randy-operating-system#191`

## Purpose
Record the exact Phase 1 memory plugin/config changes applied locally on the MacBook for the Mac Mini embedding backend, even though the plugin skill directory itself is not under a tracked git repository in this workspace.

## Local files changed
### Memory plugin skill
- `~/.openclaw/workspace/skills/memory-lancedb-hybrid/plugin/config.ts`
- `~/.openclaw/workspace/skills/memory-lancedb-hybrid/plugin/index.ts`
- `~/.openclaw/workspace/skills/memory-lancedb-hybrid/plugin/openclaw.plugin.json`

### OpenClaw config
- `~/.openclaw/openclaw.json`

## What changed
### 1. Added `remote-http` embedding provider support
The plugin now supports a third embedding backend option in addition to:
- `openai`
- `local-hash`

New provider:
- `remote-http`

### 2. Added remote embedding config fields
New embedding config fields supported:
- `baseUrl`
- `timeoutMs`

### 3. Added BGE model dimension mapping
Added support for:
- `BAAI/bge-small-en-v1.5` → `384` dims

### 4. Added remote HTTP embedding client behavior
The plugin now supports:
- `POST {baseUrl}/embed`
- JSON input with text payload
- response validation for:
  - payload shape
  - declared dimensions
  - actual vector length
  - expected model vector dimension

### 5. Updated local OpenClaw memory config
Current local target config is:
- provider: `remote-http`
- model: `BAAI/bge-small-en-v1.5`
- baseUrl: `http://192.168.1.4:8011`
- timeoutMs: `30000`
- dbPath: `~/.openclaw/memory/lancedb-bge-small-en-v15`

## Current live status
These changes are **implemented locally but not live yet**.

Reason:
- gateway restart surfaced an OpenClaw runtime/config mismatch
- config token differs from service token
- CLI indicated `openclaw gateway install --force` is required before a clean restart

## Operator guardrail
Per operator instruction:
- do **not** perform future gateway restart/install steps silently
- notify before any gateway restart or gateway install step

## Memory backup / migration status
### Backup completed
Legacy LanceDB backup created at:
- `~/.openclaw/memory/backups/lancedb-1536-backup-20260320-082945`

### LanceDB row inspection
Direct inspection found:
- legacy LanceDB store: `0` rows
- temporary local-hash store: `0` rows
- new BGE store path: `0` rows

### Implication
There may be no legacy LanceDB memories requiring migration. If confirmed after the gateway path is restored, Phase 1 can move directly to live memory tool validation.

## Next action
After operator-approved gateway install/restart:
1. bring the patched plugin live
2. validate `memory_store`
3. validate `memory_recall`
4. validate `memory_forget`
5. confirm whether any migration is still required
