# Issue #59 — Restart-safety gap list

**Issue:** #59 (child of #50)

## Objective
Identify what is currently missing around disruptive operations (service restarts).

## Gaps (current state)
### 1) Warning + approval
- **Gap:** No documented requirement to warn the operator/user before restarting the OpenClaw gateway or other services.
- **Gap:** No rule for when approval is required (e.g., restarting during an active direct chat).

### 2) Restart risk classification
- **Gap:** No documented classification of restart types (e.g., “safe/reload” vs “disruptive/full restart”).
- **Gap:** No statement that gateway restarts can interrupt active sessions.

### 3) Safe timing rules
- **Gap:** No “do not restart during active direct chat” rule.
- **Gap:** No maintenance window / quiet-hours rule for disruptive restarts.
- **Gap:** No guidance for deferring restarts until a safe moment when user-facing impact is minimized.

### 4) Pre-restart checklist
- **Gap:** No preflight checklist (capture current status, active sessions, pending queues, current model routing, current config values).
- **Gap:** No explicit rule to ensure you can rollback quickly (e.g., verify a backup/restore path for config changes that motivate the restart).

### 5) Post-restart verification
- **Gap:** No required verification steps after restart (gateway health, bot connectivity, session continuity expectations, model routing verification, auth validity).
- **Gap:** No “verify before declaring done” standard checklist.

### 6) Recovery + rollback
- **Gap:** No documented recovery plan if restart causes degraded behavior (how to restore previous config, how to revert the last change, how to validate recovery).

### 7) Incident capture
- **Gap:** No documented requirement to capture restart-related incidents (trigger, impact, resolution, lesson learned).
- **Gap:** No defined location/format for restart incident notes.

### 8) Operator communication channel
- **Gap:** No defined channel/format for communicating planned disruptive maintenance (e.g., “I’m about to restart the gateway; expect X seconds downtime”).

## Acceptance check
- Includes warning gaps: **Yes**
- Includes approval gaps: **Yes**
- Includes timing gaps: **Yes**
- Includes recovery gaps: **Yes**
- Includes verification gaps: **Yes**

## Notes
This gap list is intended to feed drafting for `SOP_SERVICE_RESTARTS.md` (issues #82–#88).
