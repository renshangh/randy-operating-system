# Issue #54 — Model routing instruction extraction (current state)

**Issue:** #54 (child of #50)

## Objective
Identify and summarize current instructions about which models should be used for:
- direct chat
- heartbeat
- scheduled/cron jobs
- micro-workloads / sub-workloads

## Findings (docs in this repo)
### 1) No explicit model-routing policy is documented in the current SOP/runbook set
A scan of the current documentation in `randy-operating-system/` did **not** find any explicit statements defining which model(s) should be used for chat vs heartbeat vs cron, nor a fallback policy.

**Evidence:**
- No references to `gpt-oss`, `gpt-5`, `openai-codex`, `gemini`, `vllm/openai/*`, or `heartbeat.model` in this repo’s markdown docs.

### 2) HEARTBEAT.md defines scheduled commands, but not model selection
`HEARTBEAT.md` currently contains pseudo-scheduled entries like:
- `gh pr list ...` every 5m
- `./qa-loop-skill/scripts/qa-heartbeat.sh` every 30m
- `gh project item-list ...` every 30m

…but it does not specify which model should execute heartbeat work.

**Source:** `HEARTBEAT.md`

### 3) QA heartbeat script calls `openclaw status`, but does not set routing
`qa-loop-skill/scripts/qa-heartbeat.sh` runs `openclaw status` and notes that additional commands may be added, but it contains no model routing instructions.

**Source:** `qa-loop-skill/scripts/qa-heartbeat.sh`

## Findings (config references)
### 4) Model-routing intent is currently implied by OpenClaw config, not repo docs
Issue #50 notes the intended heartbeat routing in OpenClaw config:
- `heartbeat.model = "vllm/openai/gpt-oss-120b"`

This repo does not currently store that config snapshot; it is referenced as an operational config value.

**Source:** Issue #50 body (notes)

## Output: current-state model-routing matrix (based on docs + known config note)
| Surface | Documented policy in repo? | Current known intent / reference |
|---|---:|---|
| Direct chat | No | Not defined in repo docs (operationally implied by OpenClaw agent/session config) |
| Heartbeat | No | Intended via config: `heartbeat.model = vllm/openai/gpt-oss-120b` (per #50 note) |
| Scheduled/cron | No | Not defined in repo docs |
| Micro-tasks / subtasks | No | Not defined in repo docs |
| Fallback policy | No | Not defined in repo docs |

## Acceptance check
- Captures docs references: **Yes** (explicitly notes absence + cites files scanned)
- Captures config references: **Partially** (only the known `heartbeat.model` value referenced in #50; full baseline snapshot belongs to Aether-owned #56)

## Notes / follow-ups
- The absence of explicit model-routing policy in this repo confirms the need for the planned `SOP_MODEL_ROUTING.md` workstream under #50.
- Aether-owned issue #56 should capture the definitive baseline config values so this extraction can be updated from “known intent” → “verified config snapshot.”
