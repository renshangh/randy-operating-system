# Local RAG MacBook Baseline

Related issue: `renshangh/randy-operating-system#193`

## Purpose
Provide a MacBook-local RAG smoke harness that does not depend on the OpenClaw gateway or the remote embedding service path.

## Implementation
Script:
- `scripts/local_rag_smoke.js`

Characteristics:
- fully local on the MacBook
- no remote HTTP dependency
- deterministic local hash embeddings (`512` dims)
- JSON-backed local store at `~/.openclaw/memory/local-rag-smoke-store.json`
- basic add/search flow for fast validation

## Usage
Reset store:
```bash
node scripts/local_rag_smoke.js reset
```

Add text:
```bash
node scripts/local_rag_smoke.js add "Local MacBook RAG baseline test. Token: local-rag-hash-baseline."
```

Search:
```bash
node scripts/local_rag_smoke.js search "local-rag-hash-baseline" 3
```

Stats:
```bash
node scripts/local_rag_smoke.js stats
```

## Validation result
Validated on the MacBook:
- add succeeded
- search succeeded
- stored token was returned from the top result

## Interpretation
This proves a purely local MacBook RAG baseline can work even while the current OpenClaw memory tool path remains blocked by the Node/runtime network mismatch affecting the remote embedding configuration.
