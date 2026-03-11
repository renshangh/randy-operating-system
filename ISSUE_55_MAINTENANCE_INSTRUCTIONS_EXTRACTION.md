# Issue #55 — Restart + config-change instruction extraction (current state)

**Issue:** #55 (child of #50)

## Objective
Identify current guidance, if any, for:
- service restarts (gateway / agent / system services)
- config edits / config-change workflows
- post-change verification and rollback

## Findings (docs in this repo)
### 1) No explicit restart SOP exists in the current docs
A scan of the current markdown docs in `randy-operating-system/` did **not** find any documented procedure for:
- when it is safe to restart services
- how to communicate before restarts
- how to verify after restarts
- how to record restart-related incidents

**Evidence:** no references found for:
- `openclaw gateway restart|start|stop`
- “service restart”
- “disruptive action”
- “restart approval”

### 2) No explicit config-change SOP exists in the current docs
A scan of the current docs did **not** find documented procedures for:
- pre-change inspection / capturing baseline values
- making minimal config edits
- verification-first before restarting
- rollback procedures

**Evidence:** no references found for:
- `openclaw config set|get`
- “config change”
- “rollback”

### 3) The only adjacent guidance is a generic execution safety pattern (not OpenClaw-specific)
`task-110-workflow.md` contains a generic runbook pattern emphasizing:
- **dry-run → execute → verify → log**
- “backup policy” (copy file before destructive steps)

This is useful as a *general safety mindset*, but it does **not** define how to safely execute OpenClaw config changes or service restarts.

**Source:** `task-110-workflow.md`

## Output: maintenance-procedure note (current state)
- **Restarts:** not documented (gap)
- **Config changes:** not documented (gap)
- **Verification / rollback:** not documented (gap)
- **General safety pattern present:** dry-run/execute/verify/log + backup-before-destructive in `task-110-workflow.md`

## Acceptance check
- Explicitly calls out missing guidance: **Yes**
- Summarizes any existing guidance: **Yes** (generic safety pattern only)

## Notes / follow-ups
- This extraction confirms the need for the planned SOP docs under #50:
  - `SOP_CONFIG_CHANGES.md`
  - `SOP_SERVICE_RESTARTS.md`
