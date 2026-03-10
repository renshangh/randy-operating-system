# SOP: Heartbeat

**Owner:** Aether  
**Status:** Draft  
**Review Cadence:** Monthly or after any heartbeat-related incident

## Objective
Define heartbeat as a lightweight awareness and triage mechanism. It is not a full scheduler and should not be used to hide heavy recurring automation behind pseudo-cron language.

## What heartbeat is for
Heartbeat is appropriate for:
1. quick status checks
2. lightweight inbox, board, or service awareness
3. escalation when something important changed
4. low-noise proactive nudges when the user needs to know

## What heartbeat is not for
Heartbeat is not the right place for:
1. exact recurring job execution such as every-5-minute or every-4-hour commands
2. heavy crawls, large sync jobs, or long-running scripts
3. repeated status spam when nothing materially changed
4. hidden automation that should live in cron, CI, or another deterministic scheduler

## Response rules
1. If nothing needs attention, reply with the configured quiet acknowledgement only.
2. If something changed and requires awareness, send a concise alert with impact and next step.
3. Prefer silence over noise.
4. During quiet hours, only interrupt for urgent items.

## Good examples
- Check whether a critical PR queue is suddenly non-empty.
- Check whether a board sync is failing and alert if it is.
- Check whether an expected service is down and escalate.

## Anti-examples
- Run a crawler every 4 hours from heartbeat instructions.
- Perform a bulk project sync on every heartbeat.
- Re-send the same healthy status repeatedly when nothing changed.

## Escalation
Escalate immediately when:
- a P0 workflow is blocked
- a service outage affects live operations
- a direct-chat experience is degraded by maintenance or model-routing failures

## Cross-links
- `SOP_CRON_AND_SCHEDULED_JOBS.md`
- `SOP_MODEL_ROUTING.md`
- `SOP_SERVICE_RESTARTS.md`
