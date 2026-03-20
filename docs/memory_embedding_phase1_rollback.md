# Memory Embedding Phase 1 Rollback Path

Related issue: `renshangh/randy-operating-system#191`

## Objective
Provide a safe rollback procedure for Phase 1 memory embeddings if the Mac Mini embedding backend becomes unavailable, degrades recall quality, or causes OpenClaw instability.

## Current Phase 1 target state
- Memory plugin: `memory-lancedb-hybrid`
- Embedding provider: `remote-http`
- Embedding model: `BAAI/bge-small-en-v1.5`
- Embedding service endpoint: `http://127.0.0.1:18011`
- Active memory DB path: `~/.openclaw/memory/lancedb-bge-small-en-v15`
- Mac Mini service source: `scripts/mac_mini_embedding_service.py`

## Known preserved assets
- Legacy LanceDB backup:
  - `~/.openclaw/memory/backups/lancedb-1536-backup-20260320-082945`
- Legacy LanceDB path:
  - `~/.openclaw/memory/lancedb`
- Temporary fallback path:
  - `~/.openclaw/memory/lancedb-localhash`

## Rollback triggers
Rollback is appropriate if any of the following happen:
- memory tool calls fail repeatedly
- remote embedding endpoint becomes unreachable
- gateway startup becomes unstable due to memory config
- recall quality is materially worse than acceptable
- SSH tunnel path on `127.0.0.1:18011` is not reliable

## Rollback levels

### Level 1 — keep plugin, switch to local-hash fallback
Use this when the remote embedding service is unstable but you need memory tools to keep functioning locally.

#### Config change
In `~/.openclaw/openclaw.json` change:
- `plugins.entries.memory-lancedb-hybrid.config.embedding.provider` → `local-hash`
- `plugins.entries.memory-lancedb-hybrid.config.embedding.model` → `local-hash-512`
- remove `baseUrl`
- keep DB path on a dedicated fallback store such as:
  - `~/.openclaw/memory/lancedb-localhash`

#### Effect
- memory tools continue working locally
- no external API key needed
- lower semantic quality than BGE
- safest fast fallback if the network/service path breaks

### Level 2 — disable Phase 1 BGE path and revert to legacy OpenAI-style config shape
Use this only if there is a valid OpenAI embedding path available again.

#### Config change
Repoint embedding config back to an OpenAI-compatible provider/model and the legacy DB path.

#### Caution
- only use this if a valid embedding provider/key exists
- do not point OpenAI-style embeddings at invalid placeholder keys

### Level 3 — disable memory plugin entirely
Use this if memory itself is causing runtime instability and must be removed from the critical path.

#### Config change
- disable `plugins.entries.memory-lancedb-hybrid`
- or clear the memory slot assignment if required by runtime behavior

#### Effect
- OpenClaw will run without long-term memory
- lowest capability, highest stability fallback

## Recommended rollback sequence
1. Confirm the failure mode:
   - endpoint unreachable
   - bad recall results
   - gateway/plugin startup errors
2. Preserve current state:
   - do not delete any LanceDB directory
   - do not overwrite backup paths
3. Apply the smallest rollback needed:
   - prefer Level 1 first
4. Restart the gateway only after config is saved and inspected
5. Re-test:
   - `memory_store`
   - `memory_recall`
   - `memory_forget`
6. Record the rollback in `#191`

## Fast rollback target
If immediate stabilization is needed, the fastest practical rollback is:
- provider: `local-hash`
- model: `local-hash-512`
- dbPath: `~/.openclaw/memory/lancedb-localhash`

## Do not do
- do not delete `~/.openclaw/memory/lancedb`
- do not destroy backup directories
- do not mix vector dimensions inside the same LanceDB table
- do not silently restart the gateway without operator notice

## Verification after rollback
A rollback is considered successful only if:
- gateway is healthy
- memory tool calls stop failing
- memory store/recall/forget behave consistently for the chosen fallback mode

## Follow-up after rollback
If rollback is used, open a follow-up note in `#191` capturing:
- what failed
- which rollback level was used
- whether the Mac Mini service or SSH tunnel was the fault domain
- whether Phase 2 DGX Spark should be accelerated
