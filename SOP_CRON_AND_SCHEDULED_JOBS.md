# SOP: Cron and Scheduled Jobs

**Owner:** Aether  
**Status:** Draft  
**Review Cadence:** Monthly or after any job failure pattern change

## Objective
Define which workloads belong in deterministic scheduling and what each scheduled job must declare.

## What belongs in scheduled jobs
Use cron, CI, or another deterministic scheduler for work that needs:
1. exact cadence
2. reproducible execution
3. durable logs
4. explicit retry and failure policy

Typical examples:
- recurring PR checks
- board synchronization
- job crawls
- refresh or validation scripts

## What does not belong in scheduled jobs
Do not schedule work here if it is primarily:
1. awareness and triage
2. user-facing conversational follow-up
3. ad hoc investigation
4. ambiguous work needing judgment at each run

Those belong in heartbeat or direct operator flow.

## Required declaration for every scheduled job
Each job must document:
- owner
- command
- cadence
- expected output
- failure path
- notification target
- whether retries are allowed

## Failure handling and retries
1. Log failures where the operator can retrieve them quickly.
2. Alert on repeated failure or high-impact single failure.
3. Keep retries bounded.
4. Escalate instead of looping forever.
5. If a job becomes noisy or unreliable, disable or narrow it until fixed.

## Validation checklist
Before enabling or changing a scheduled job:
1. verify the command manually
2. verify permissions and paths
3. verify alert destination
4. verify logs are readable
5. verify the job is not better expressed as heartbeat awareness

## Cross-links
- `SOP_HEARTBEAT.md`
- `SOP_CONFIG_CHANGES.md`
- `SOP_MODEL_ROUTING.md`
