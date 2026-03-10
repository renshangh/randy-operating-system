# Issue #57 — Conflicts between current HEARTBEAT.md and desired heartbeat behavior

**Issue:** #57 (child of #50)

## Desired heartbeat behavior (from #50)
Heartbeat should be:
- a **lightweight awareness / triage / escalation** mechanism
- **not** a pseudo-scheduler for heavy recurring work
- safe and non-disruptive (no surprise restarts during active chat)

## Conflicts
### Conflict 1 — HEARTBEAT.md is used as a scheduler (“every 5m / every 30m”)
- **Current behavior:** `HEARTBEAT.md` contains entries like `- every 5m: ...` and `- every 30m: ...`.
- **Desired behavior:** heartbeat should be a lightweight checklist/decision file, not a cron-like schedule.
- **Why this is a problem:** it encourages heavy work to run on heartbeat cadence, conflates awareness with deterministic execution, and increases the chance of noisy/expensive/interruptive actions running while a user session is active.

**Source:** `HEARTBEAT.md`

### Conflict 2 — Heavy / external API calls are scheduled via heartbeat
- **Current behavior:** heartbeat schedules `gh pr list` every 5 minutes and `gh project item-list ... --format json` every 30 minutes.
- **Desired behavior:** heavy recurring work should move to deterministic scheduling (cron or equivalent), with explicit failure handling and observability.
- **Why this is a problem:** repeated GitHub API polling via heartbeat can create rate-limit risk, tool noise, and can run in the wrong operational context.

**Source:** `HEARTBEAT.md`

### Conflict 3 — HEARTBEAT.md implies “bot triggers deeper checks” without an explicit gating rule
- **Current behavior:** comment states detailed status checks “can be triggered by the bot” based on the list above, but does not define conditions, thresholds, or escalation rules.
- **Desired behavior:** heartbeat should include explicit rules for when to notify/escalate vs stay quiet.
- **Why this is a problem:** ambiguous triggers increase the risk of unnecessary tool actions and noisy alerts.

**Source:** `HEARTBEAT.md` (comment block)

### Conflict 4 — Heartbeat content mixes unrelated domains (PR monitoring, QA, board sync)
- **Current behavior:** heartbeat mixes PR polling, QA loop checks, and project-board sync in one file.
- **Desired behavior:** heartbeat should focus on awareness/triage; scheduled operational jobs should be documented and managed via the scheduled-jobs SOP.
- **Why this is a problem:** it makes the heartbeat surface act like a general scheduler, which hides ownership/cadence/failure policy and makes changes risky.

**Source:** `HEARTBEAT.md`

### Conflict 5 — No documented quiet-hours / “no-noise” policy in heartbeat instructions
- **Current behavior:** heartbeat entries are unconditional; no rule exists for quiet hours or when to avoid messaging.
- **Desired behavior:** heartbeat should explicitly encode when to remain silent unless urgent.
- **Why this is a problem:** without a quiet/noise policy, heartbeat can spam updates and break the “lightweight awareness” intent.

**Source:** `HEARTBEAT.md`

### Conflict 6 — No explicit separation between “awareness checks” and “execution actions”
- **Current behavior:** scheduled commands could evolve into performing actions, but the file has no guardrails about read-only checks vs write/disruptive operations.
- **Desired behavior:** heartbeat should prioritize safe awareness checks; disruptive actions should require explicit approval/workflow.
- **Why this is a problem:** operationally dangerous actions can be accidentally scheduled or expanded into heartbeat scope.

**Source:** `HEARTBEAT.md`

## Acceptance check
- Each conflict states current behavior, desired behavior, and why it is a problem: **Met**

## Notes
This conflict list is intended to feed:
- Ember’s classification work (#58)
- Aether’s refactor plan for `HEARTBEAT.md` (#97) and replacement `HEARTBEAT.md` drafting (#98)
