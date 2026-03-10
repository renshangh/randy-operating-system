## Summary
- add a first operator-grade SOP stack for heartbeat, scheduled jobs, config changes, service restarts, and model routing
- add an Issue #50 closeout checklist tied directly to acceptance criteria
- establish cross-links so future maintenance work follows one coherent operating path

## Problem
Issue #50 identified a real operating gap: the system had intent around heartbeat and local-model routing, but the runbook layer was too weak. Heartbeat behavior, scheduled work, config changes, and disruptive restarts were not documented as one safe operating system.

## Solution
This change introduces five focused SOP documents:
- `SOP_HEARTBEAT.md`
- `SOP_CRON_AND_SCHEDULED_JOBS.md`
- `SOP_CONFIG_CHANGES.md`
- `SOP_SERVICE_RESTARTS.md`
- `SOP_MODEL_ROUTING.md`

It also adds `ISSUE_50_CHECKLIST.md` so final closeout can be reviewed against the original acceptance criteria instead of memory or ad hoc judgment.

## Operational impact
- heartbeat is defined as lightweight awareness and triage, not pseudo-cron
- scheduled work now has a separate deterministic home
- config changes now require inspection, bounded edits, verification, and rollback thinking
- service restarts are explicitly treated as disruptive operations
- model-routing expectations are documented across control surfaces

## Follow-up
A final review should update any existing operator-facing docs that still imply the old heartbeat-as-scheduler pattern.
