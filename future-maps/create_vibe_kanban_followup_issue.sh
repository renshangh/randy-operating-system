gh issue create \
  --repo renshangh/randy-operating-system \
  --title "Adopt Vibe Kanban-style review/workspace concepts without replacing GitHub as source of truth" \
  --body "$(cat <<'EOF'
## Objective
Improve our agent orchestration system by borrowing the most useful concepts from Vibe Kanban — especially review clarity, execution visibility, and feedback loops — while **keeping GitHub as the durable source of truth** and preserving our existing webhook / Aether / OpenClaw orchestration architecture.

## Why this issue exists
We reviewed `BloopAI/vibe-kanban` and found that its biggest strengths are not its Kanban board itself, but its:
- clear workspace-per-task model
- strong human review flow
- better visibility into what an agent is doing
- better feedback loop for sending work back after review

Our system is stronger in:
- GitHub-native durability
- cross-surface orchestration
- flexible webhook/session-based routing
- specialist-agent coordination

The gap is not orchestration power — it is **review clarity and execution visibility**.

## Strategic direction
Do **not** replace GitHub with a new board/database as the workflow source of truth.

Instead:
- keep GitHub issues/labels/comments as durable workflow state
- keep webhook -> listener -> Aether wake as the orchestration backbone
- add Vibe Kanban-like clarity around:
  - review
  - workspace/session visibility
  - rework loops
  - per-issue execution history

## Scope
Explore and design a GitHub-native enhancement layer that adds:

### 1. Execution visibility
- per-issue execution context summary
- current owner agent
- current session target
- branch/worktree mapping if present
- latest wake result
- latest review/rework state

### 2. Review workflow improvements
- richer Aether review packet on `status:done`
- explicit review outcomes:
  - accept / close
  - request changes
  - relabel to `dispatch:ready`
  - escalate / handoff
- structured rework instructions for the next agent pass

### 3. Workspace/session clarity
- one issue -> one active execution context model
- branch/worktree/session conventions
- clearer mapping between issue, session, PR, and worktree

### 4. Observability
- durable per-issue execution log / timeline
- wake count, dispatch count, retry count
- last failure reason
- Aether inbox target validation
- clearer debugging surfaces for stale/misdirected session targets

## Non-goals
- do not replace GitHub issues with an app-owned Kanban board
- do not rebuild Vibe Kanban wholesale
- do not add a heavy UI before the control-plane/data model is clear
- do not weaken the current GitHub/webhook/session orchestration backbone

## Proposed phases

### Phase 1 — visibility and control
- issue execution status panel / summary
- durable per-issue execution log
- Aether inbox target validation

### Phase 2 — review loop
- structured Aether review packet
- explicit review outcome model
- structured rework instructions object

### Phase 3 — workspace/session model
- canonical issue -> execution context mapping
- branch/worktree naming conventions
- execution context summary command

### Phase 4 — review UX
- diff/review summary integration
- structured inline-review ingestion from GitHub PR comments
- derived “in review” state/dashboard

### Phase 5 — optional UI
- minimal orchestration dashboard
- session/workspace browser

## Acceptance criteria
- [ ] clear design direction documented for GitHub-native review/workspace improvements
- [ ] execution visibility requirements defined
- [ ] review outcome + rework loop model defined
- [ ] issue/session/worktree mapping model defined
- [ ] observability/debugging requirements defined
- [ ] follow-on implementation issues created in small executable packets

## Related context
- we compared our system against `BloopAI/vibe-kanban`
- takeaway: copy their **review/workspace clarity**, not their **source-of-truth model**
- keep:
  - GitHub as durable state
  - webhook/listener/Aether orchestration
- improve:
  - review clarity
  - workspace/session legibility
  - feedback loop quality

## Output expectation
Produce a practical roadmap and then break the work into small implementation issues rather than trying to design or build everything at once.
EOF
)"
