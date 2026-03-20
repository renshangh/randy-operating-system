# Mac Mini LanceDB RAG — Agent Query SOP

Related issue: `renshangh/randy-operating-system#193`

## Purpose
Define the first agent-facing SOP for Sarah and other agents to query the Mac Mini LanceDB RAG system.

This SOP covers the **query/use layer first**, before broader ingestion automation is expanded.

## Initial intended users
- Sarah
- Ember
- Sentinel
- Mark
- Amy
- other approved Mac Mini-side agent runtimes that need document/ops retrieval from the Mac Mini-hosted RAG store

## Initial use case
The first supported use case is **operations/document retrieval**.

Agents should use this RAG path to retrieve:
- runbooks
- SOPs
- architecture notes
- migration notes
- validation procedures
- issue-adjacent operational documents that have been ingested into the Mac Mini LanceDB store

## What this RAG is for
Use the Mac Mini LanceDB RAG query path when the agent needs:
- a specific operational procedure
- the current documented plan for a subsystem
- the canonical path or ownership for a repo/service/runtime
- architecture guidance grounded in stored docs
- retrieval from a known ingested document set

## What this RAG is NOT for
Do not use this RAG as the first tool for:
- live machine state checks
- current GitHub issue status unless the issue has been ingested as a document artifact
- ad hoc filesystem browsing when direct file read is more precise
- transient chat/session memory
- unverified assumptions about runtime state

If a direct file read, direct command, or direct GitHub check is more authoritative, prefer that.

## Query SOP
### Step 1 — decide whether RAG is the right tool
Use RAG only when the task is fundamentally a **retrieval question** against ingested documents.

Examples:
- "What is the current Phase 2 plan for Mac Mini RAG?"
- "Which doc explains the LaunchAgent problem?"
- "What is the validation path for the embedding service?"

### Step 2 — form a focused retrieval query
Write the query in plain language using the actual target concept, issue number, or document topic.

Good query examples:
- `Phase 2 Mac Mini RAG plan`
- `LaunchAgent LAN access diagnosis`
- `embedding service validation`
- `canonical repo path randy-operating-system`

Avoid vague queries like:
- `what is going on`
- `help`
- `memory`

### Step 3 — run the query
Initial query interface:
```bash
python3 scripts/rag_query.py "<query text>" --limit 5
```

Optional parameters may be added later, but the initial SOP is:
- plain-language query
- top-k results
- inspect source id, source type, score, and returned text chunk

### Step 4 — inspect returned chunks before acting
Before using a result operationally, verify:
- the result is from the expected source/doc family
- the returned chunk actually answers the question
- the chunk is not missing critical surrounding context

If needed, rerun with:
- a sharper query
- a more specific term
- a broader or narrower limit

### Step 5 — cite or follow the source document
When using RAG output to guide work:
- treat the returned chunk as a pointer to the source document
- if the action is important, read the source document directly after retrieval
- avoid treating one chunk as complete truth if the task is high-impact

## First approved query pattern
For the initial rollout, agents should primarily query the Mac Mini RAG for:
- operations docs
- architecture docs
- runbooks
- SOPs

This gives a controlled first usage pattern and avoids premature overloading of the system.

## Output interpretation
Each result should be interpreted as:
- **source_id** → which document/source it came from
- **source_type** → what class of source it is
- **chunk_index** → position within the source
- **text** → matched chunk
- **score** → retrieval distance/score signal
- **metadata_json** → structured metadata if present

Agents should not assume score alone means correctness; they should still inspect the text.

## Escalation / fallback rules
If the query result is weak or ambiguous:
1. refine the query and rerun
2. read the likely source document directly
3. fall back to direct file/GitHub inspection
4. if the document should exist but is not retrievable, flag ingestion/indexing gap

## Known boundaries (initial version)
- current interface is CLI-first
- current result quality depends on what has been ingested
- this SOP assumes the document set is controlled and curated
- this is not yet a general replacement for direct system inspection

## Recommended initial corpus for this SOP
Start with these doc families:
- `docs/mac_mini_lancedb_rag_phase2_plan.md`
- `docs/memory_embedding_phase1_mac_mini_plan.md`
- `docs/memory_embedding_phase1_plugin_patch_status.md`
- `docs/openclaw_gateway_lan_access_diagnosis.md`
- `docs/local_rag_macbook_baseline.md`

## Success criteria
This SOP is working if an agent can:
- ask a focused ops/document question
- retrieve the right document chunk
- identify the source document
- use retrieval as a pointer to the authoritative doc
- avoid unnecessary broad file exploration

## Next extension
After this SOP is proven against ops/architecture docs, extend it to:
- richer metadata filters
- broader document sets
- Sarah-specific workflow documents
- optional network/service wrapper for multi-runtime access
