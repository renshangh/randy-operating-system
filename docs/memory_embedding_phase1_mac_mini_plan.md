# Memory Embedding Phase 1 Plan — Mac Mini

Related issue: `renshangh/randy-operating-system#191`

## Objective
Stand up a local embedding backend on the Mac Mini and wire OpenClaw memory to use it instead of the broken OpenAI-dependent path.

## Decision
For **Phase 1**, use:

- **Host:** Mac Mini
- **Runtime:** Python `sentence-transformers`
- **Model:** `BAAI/bge-small-en-v1.5`
- **Embedding dimension:** `384`
- **Memory store:** fresh LanceDB path dedicated to the new embedding dimension

## Why this choice
`BAAI/bge-small-en-v1.5` is the best first production candidate because it gives a practical balance of:

- solid retrieval quality
- lower resource usage than larger models
- easy local deployment
- no API key requirement
- compatible with the already-available Python ML stack on the Mac Mini

## Validation performed
Mac Mini direct smoke test succeeded:

- Python environment has `sentence_transformers`, `transformers`, and `torch`
- `SentenceTransformer("BAAI/bge-small-en-v1.5")` loaded successfully
- test encode returned shape `(1, 384)`

## Architecture
### Phase 1 target flow
1. OpenClaw memory plugin sends text to a Mac Mini embedding helper
2. Mac Mini helper returns a `384`-dim embedding vector
3. OpenClaw stores and queries memory in LanceDB using that vector
4. Hybrid retrieval remains enabled:
   - vector similarity
   - BM25 / full-text search
   - RRF reranking

## Scope for Phase 1
### In scope
- choose and validate the local embedding model
- build a Mac Mini embedding helper/service
- repoint OpenClaw memory embedding calls to that helper
- keep old 1536-dim memory store intact
- create a fresh 384-dim store
- migrate old memory text into the new store by re-embedding
- verify `memory_store`, `memory_recall`, and `memory_forget`

### Out of scope
- DGX Spark hosting (Phase 2)
- destructive rebuild of the old memory store
- multi-tenant or shared memory service design

## Implementation outline
### Step 1 — model and runtime selection
- complete

### Step 2 — Mac Mini embedding helper
Preferred first implementation:
- a lightweight Python helper script or HTTP microservice running on Mac Mini
- accepts text input
- returns embedding JSON
- uses `SentenceTransformer("BAAI/bge-small-en-v1.5")`

### Step 3 — OpenClaw memory plugin integration
- patch the memory plugin so embedding provider can call the Mac Mini helper
- preserve current LanceDB + hybrid retrieval behavior
- do not mutate the old 1536-dim store in place

### Step 4 — backup and migration
- back up old LanceDB memory directory
- extract existing memories
- re-embed old memory text into the new 384-dim space
- write migrated entries into the new store
- verify counts and spot-check recall quality

### Step 5 — validation
- store new fact
- recall by paraphrase and exact term
- forget by query and by id
- confirm no dependency on OpenAI API key

## Risks
- old and new memory stores can split if migration is incomplete
- remote helper reliability depends on Mac Mini reachability
- some exact recall may still rely more on BM25 than embeddings
- service/auth design should stay simple for Phase 1

## Rollback
If Phase 1 causes issues:
1. disable the Mac Mini embedding backend
2. revert plugin config to the prior temporary fallback
3. keep old LanceDB memory store untouched
4. restore prior plugin/config from git or config backup

## Next action
Build the Mac Mini embedding helper and wire the plugin to call it.
