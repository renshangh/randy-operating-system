# Mac Mini LanceDB RAG — Phase 2 Plan

Related issue: `renshangh/randy-operating-system#193`

## Objective
Build a Mac Mini-hosted LanceDB-based RAG system for Sarah and the other agent runtimes.

This Phase 2 system is intentionally separate from the currently blocked MacBook OpenClaw memory-tool runtime path. The goal is to stand up a working agent-facing retrieval system on the Mac Mini first, then decide later how tightly to integrate it with OpenClaw memory tooling.

## Why Phase 2 exists
Phase 1 proved two useful things:
1. a local MacBook RAG baseline works
2. the current MacBook OpenClaw runtime has a Node/network mismatch that blocks the remote memory path even when the Mac Mini service itself is healthy

So Phase 2 shifts focus from fighting the MacBook runtime to building the RAG system directly where Sarah and the other agents are expected to benefit from it: the Mac Mini.

## Target architecture

### Core components
1. **Embedding service on the Mac Mini**
   - Python `sentence-transformers`
   - model: `BAAI/bge-small-en-v1.5`
   - normalized embeddings
   - existing service shape can be reused from `scripts/mac_mini_embedding_service.py`

2. **LanceDB store on the Mac Mini**
   - dedicated Phase 2 database path on the Mac Mini
   - fresh store using the 384-dim embedding space
   - tables for chunked documents / records plus metadata

3. **Ingestion path**
   - input text/documents are chunked
   - embeddings are generated locally on the Mac Mini
   - chunks + metadata + vectors are written into LanceDB

4. **Retrieval path**
   - query text embedded locally on the Mac Mini
   - LanceDB search returns top-k matches
   - include text, score, metadata, and source identifiers

5. **Agent-facing interface**
   - initial interface can be CLI-first
   - optional Phase 2.5 HTTP wrapper if needed later
   - Sarah/other agents should be able to call add/search predictably from their runtime

## Preferred Phase 2 operating model
### First implementation: CLI-first
Use small Python CLI scripts on the Mac Mini:
- `rag_ingest.py`
- `rag_query.py`
- optional `rag_stats.py`

Why CLI-first:
- simpler than another network hop
- easier to test directly on the Mac Mini
- avoids repeating the current remote-runtime failure mode too early
- good enough for Sarah and agent automation if invoked locally

### Later option: service wrapper
If multiple runtimes need a shared networked endpoint, add a small HTTP service only after the local CLI path is validated.

## Proposed file layout
Under `randy-operating-system/scripts/`:
- `rag_ingest.py`
- `rag_query.py`
- `rag_stats.py`
- `rag_common.py` (shared embedding/chunking/db helpers)

Under `randy-operating-system/docs/`:
- `mac_mini_lancedb_rag_phase2_plan.md` (this file)
- `mac_mini_lancedb_rag_phase2_runbook.md`

## Proposed Mac Mini storage paths
Examples:
- DB root: `~/.openclaw/memory/mac-mini-rag-lancedb`
- optional source snapshots: `~/.openclaw/memory/mac-mini-rag-sources`

Final path should be chosen explicitly during implementation and documented.

## Data model
Each chunk/record should include at minimum:
- `id`
- `source_id`
- `source_type`
- `text`
- `vector`
- `created_at`
- `updated_at`
- `tags` (optional)
- `metadata_json` (optional structured metadata)

## Chunking guidance
Start simple:
- chunk by paragraph / bounded text length
- preserve source id + chunk index
- avoid premature complexity

A simple fixed-size chunker with overlap is enough for the first validation build.

## Validation plan
### Phase 2 smoke test
1. ingest a small controlled corpus
2. query with exact token
3. query with paraphrase
4. confirm top results are sensible
5. verify LanceDB row counts and dimensions

### Agent validation
1. Sarah can run a local query on the Mac Mini
2. returned results are readable/actionable
3. query path is stable enough for repeated use

## Deliverables
- working Mac Mini-local LanceDB database
- working ingestion script
- working query script
- runbook for add/search/inspect flows
- verification evidence recorded on `#193`

## Out of scope for initial Phase 2 build
- full OpenClaw memory-tool integration
- distributed/shared auth model
- automatic sync between MacBook and Mac Mini stores
- multi-tenant isolation beyond basic metadata/source tagging

## Immediate next implementation step
Build the Mac Mini-local Python LanceDB CLI skeleton:
1. shared helper module
2. ingest command
3. query command
4. smoke-test corpus and runbook
