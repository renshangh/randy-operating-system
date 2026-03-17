# Aether-to-Mac-Mini Migration Checklist

Parent issue: #168

## Objective
Move Aether from the MacBook Pro to the Mac Mini as the **primary host** without losing routing, memory, tool access, or operator safety.

## Why
- free up the MacBook Pro
- make the system more deployable and customer-demo friendly
- reduce dependence on Randy's laptop as the long-term primary host

## Guiding Principle
Do **not** treat this as a one-shot folder move.

This is a **phased operational migration**:
1. audit
2. shadow deployment
3. controlled cutover
4. rollback-ready validation

---

## Migration Complexity Summary
- **Workspace copy only:** Low
- **Full operational migration:** Medium to High
- **Highest-risk areas:** auth/credentials, browser state, channel bindings, cutover confusion, hidden machine-local dependencies

---

## Success Criteria
Aether is considered successfully migrated when:
- primary Aether routing runs on the Mac Mini
- required workspaces, repos, memory, and docs are present on the Mac Mini
- main channel bindings route to the intended primary agent on the Mac Mini
- GitHub/tooling/auth workflows still work
- browser-dependent workflows are either migrated or explicitly deferred
- rollback to the MacBook is still possible until the Mac Mini proves stable

---

## Phase 1 — Current-State Audit

### 1.1 Workspace and repo inventory
- [ ] Inventory all repos Aether actively uses on the MacBook
- [ ] Inventory workspace-only files that matter for continuity
- [ ] Confirm which memory/docs/runbooks must exist on the Mac Mini
- [ ] Identify any local scripts or paths that assume MacBook-specific locations

### 1.2 OpenClaw configuration inventory
- [ ] Capture current MacBook `~/.openclaw/openclaw.json`
- [ ] Inventory agent definitions
- [ ] Inventory bindings
- [ ] Inventory active channels/accounts
- [ ] Inventory gateway settings, hooks, plugins, and model defaults
- [ ] Record any MacBook-only behavior not already represented on the Mac Mini

### 1.3 Credentials and auth inventory
- [ ] GitHub auth
- [ ] Discord bot tokens / account mappings
- [ ] Telegram bot tokens / account mappings
- [ ] Google / Gmail / Calendar auth if used
- [ ] browser login dependencies
- [ ] any local API keys or auth profiles
- [ ] separate copy-safe secrets from machine-bound auth that must be revalidated

### 1.4 Tool/runtime parity audit
- [ ] Confirm OpenClaw runtime is present and healthy on Mac Mini
- [ ] Confirm required CLI tools exist (`gh`, `git`, `python3`, `node`, etc.)
- [ ] Confirm required repo clones exist on Mac Mini
- [ ] Confirm required scripts run on Mac Mini
- [ ] Confirm any scheduled jobs / launch agents are understood

### 1.5 Operating dependency audit
- [ ] Identify what work Aether performs today that is still MacBook-only
- [ ] Identify browser-dependent tasks that may not migrate cleanly
- [ ] Identify anything that depends on local notifications, desktop state, or the laptop being physically present

---

## Phase 2 — Mac Mini Shadow Deployment

### 2.1 Prepare the Mac Mini as a candidate primary host
- [ ] Create or verify the main Aether agent definition on the Mac Mini
- [ ] Ensure workspace and repo paths are present and correct
- [ ] Sync required docs, memory, scripts, and runbooks
- [ ] Align model defaults and tool expectations with the intended Aether role

### 2.2 Recreate or validate required config
- [ ] Recreate missing bindings on Mac Mini
- [ ] Recreate missing channel account entries on Mac Mini
- [ ] Validate account-specific routing behavior
- [ ] Confirm no accidental fallback to the wrong agent/workspace

### 2.3 Validate auth and access
- [ ] Verify GitHub operations on Mac Mini
- [ ] Verify Discord account connectivity for required lanes
- [ ] Verify Telegram account connectivity for required lanes
- [ ] Verify any Google/browser-based auth that matters
- [ ] Document any auth that must remain on the MacBook for now

### 2.4 Run Aether in shadow mode
- [ ] Perform non-destructive test tasks from the Mac Mini
- [ ] Compare Mac Mini results against expected Aether behavior
- [ ] Confirm memory/docs/context availability feels complete enough
- [ ] Record missing dependencies discovered during shadow tests

---

## Phase 3 — Readiness Gate Before Cutover

Do **not** cut over until the following are true:
- [ ] Mac Mini can complete core Aether tasks reliably
- [ ] required bindings are correct and stable
- [ ] primary channels are tested
- [ ] no critical workflow still depends solely on the MacBook
- [ ] rollback steps are documented and ready
- [ ] Randy agrees to a controlled cutover window

---

## Phase 4 — Controlled Cutover

### 4.1 Pre-cutover safety steps
- [ ] Back up MacBook OpenClaw config
- [ ] Back up Mac Mini OpenClaw config
- [ ] Save a clear before/after routing map
- [ ] Freeze non-essential config changes during cutover window

### 4.2 Move primary routing to Mac Mini
- [ ] Update main channel/account bindings to the intended Mac Mini-hosted primary agent
- [ ] Restart gateway/services in a controlled sequence
- [ ] Verify only one primary Aether path is active
- [ ] Prevent split-brain behavior between MacBook and Mac Mini

### 4.3 Smoke-test immediately after cutover
- [ ] test inbound message routing
- [ ] test outbound reply path
- [ ] test GitHub operation
- [ ] test one specialist handoff path
- [ ] test one documentation/runbook retrieval path
- [ ] test one safe operational task end-to-end

---

## Phase 5 — Stabilization
- [ ] Watch for reconnect instability
- [ ] Watch for wrong-agent replies or fallback to main/default unexpectedly
- [ ] Watch for missing credentials or browser failures
- [ ] Watch for path mismatches or repo drift
- [ ] Keep MacBook available as rollback host until stability is proven

Suggested stabilization rule:
- no final decommission of MacBook-as-primary until the Mac Mini runs cleanly for a defined soak period

---

## Rollback Plan
If cutover fails, be ready to:
- [ ] restore prior MacBook bindings
- [ ] restore prior MacBook config snapshot
- [ ] restart the MacBook-side gateway/services if needed
- [ ] disable the conflicting Mac Mini primary binding
- [ ] confirm the MacBook is primary again before resuming operations

Rollback success condition:
- primary routing is restored quickly with no ambiguity about which host is live

---

## Known Risk Areas
- machine-local browser state does not migrate cleanly
- Discord/Telegram account routing can silently fall back if bindings are incomplete
- copied config may contain paths or assumptions that only work on the MacBook
- dual-host cutover can create split-brain confusion if both primary paths stay active
- hidden tool or auth dependencies may only appear under live usage

---

## Recommended Workstreams
1. **Environment audit**
2. **Workspace + repo sync**
3. **Config + bindings migration**
4. **Credentials/auth validation**
5. **Browser/tool parity validation**
6. **Shadow deployment testing**
7. **Controlled cutover**
8. **Rollback-ready stabilization**

---

## Suggested First Practical Actions
- [ ] Diff MacBook vs Mac Mini `openclaw.json`
- [ ] Inventory Aether-specific bindings and channels on the MacBook
- [ ] List required repos/workspaces/scripts for Aether
- [ ] Identify which current Aether workflows are browser-dependent
- [ ] Define what “minimum viable Aether on Mac Mini” means before full cutover

---

## Definition of "Minimum Viable Aether on Mac Mini"
A reasonable first cut is:
- core chat routing works
- GitHub operations work
- Discord/Telegram primary lane works
- memory/docs/runbooks are available
- specialist orchestration works
- browser-heavy or machine-local edge cases can be deferred if clearly documented

This allows a phased migration without requiring every edge workflow on day one.
