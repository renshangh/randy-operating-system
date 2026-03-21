# RAG Inventory — MacBook vs Mac Mini

> Scope: inventory of RAG-related configurations across both machines as of 2026-03-21.
> Source: repo docs + GitHub issues (#190/#193/#195) + local MacBook inspection.

---

## 1) MacBook (Aether runtime)

### OpenClaw memory plugin
- **Plugin:** `memory-lancedb-hybrid`
- **Status:** registered (lazy init)
- **Embedding provider:** `local-hash`
- **Reranker:** `rrf`
- **DB path:** `/Users/renshan/.openclaw/memory/lancedb-local-hash-512`

### Local LanceDB stores present on disk
- `/Users/renshan/.openclaw/memory/lancedb/`
- `/Users/renshan/.openclaw/memory/lancedb-bge-small-en-v15/`
- `/Users/renshan/.openclaw/memory/lancedb-localhash/`
- `/Users/renshan/.openclaw/memory/lancedb-local-hash-512/`
  - table dir: `memories.lance/`
  - contains `_indices`, `_transactions`, `_versions`, `data/*.lance`

### MacBook local RAG baseline (Phase 1 workaround)
- **Purpose:** local smoke baseline independent of remote embeddings
- **Files:**
  - `scripts/local_rag_smoke.js`
  - `docs/local_rag_macbook_baseline.md`
- **Store:** JSON-backed local smoke store (see `local-rag-smoke-store.json` in `~/.openclaw/memory/`)

### Notes / constraints
- Python `lancedb` is not installed in system Python on MacBook.
- Primary access should use OpenClaw Node plugin path.

---

## 2) Mac Mini (shared agent runtime)

### Phase 2 LanceDB RAG (Mac Mini-hosted)
- **DB path (canonical):** `~/.openclaw/memory/mac-mini-rag-lancedb`
- **Table:** `documents`
- **Embedding model:** `BAAI/bge-small-en-v1.5` (384 dims)
- **CLI-first scripts (repo):**
  - `scripts/rag_common.py`
  - `scripts/rag_ingest.py`
  - `scripts/rag_query.py`
  - `scripts/rag_stats.py`
- **SOP:** `docs/mac_mini_lancedb_rag_agent_sop.md`
- **Plan:** `docs/mac_mini_lancedb_rag_phase2_plan.md`

### Phase 2 test DB (validation)
- **Test DB path:** `~/.openclaw/memory/mac-mini-rag-lancedb-test`
- **Status note:** test DB not clean in #195 (contained rows from `test-195-phase2-plan`).

### Embedding service (Phase 1 memory path)
- **Canonical host:** Mac Mini
- **Service script:** `scripts/mac_mini_embedding_service.py`
- **Expected port:** `8011`
- **Client:** MacBook OpenClaw memory plugin (remote-http)
- **Old/stale path:** `127.0.0.1:18011` (prior SSH tunnel)

---

## 3) Related Issues / References
- **#190** — Parent knowledge architecture issue
- **#193** — Phase 1 embedding connectivity / Phase 2 Mac Mini RAG
- **#195** — Validation/testing cases (test DB + query protocol)
- **#196** — Bug: missing `sentence_transformers` in Mac Mini test env

---

## 4) Open Questions / To Verify
- Confirm current Mac Mini embedding service health + binding interface.
- Confirm per-agent memory store paths on Mac Mini (if any additional beyond Phase 2 store).
- Decide whether MacBook should keep `lancedb-bge-small-en-v1.5` store active or deprecated.

---

## 5) Change Log
- 2026-03-21: Initial inventory drafted from repo + runtime checks.
