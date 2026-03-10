# SOP: Model Routing

**Owner:** Aether  
**Status:** Draft  
**Review Cadence:** Monthly or after routing/config incidents

## Objective
Define model-selection policy for direct chat, heartbeat, scheduled jobs, and decomposed task execution.

## Direct chat policy
Direct chat optimizes for responsiveness, quality, and user trust. Do not silently swap models when the change affects behavior materially; if fallback is required and user impact is meaningful, call it out.

## Heartbeat policy
Heartbeat should prefer a lightweight, stable model path aligned with its awareness role. If the operational intent is local-model-first, the heartbeat path must be explicitly configured and verified rather than assumed.

## Scheduled jobs policy
Deterministic jobs should favor stability, bounded cost, and reproducibility. Model choice must match the job's tolerance for latency, token budget, and failure recovery.

## Micro-task and subtask policy
Decomposed work should default to small, tightly scoped tasks so local models such as `vllm/openai/gpt-oss-120b` can execute reliably. Keep prompts short, outputs bounded, and acceptance criteria explicit.

## Fallback policy
If the local model is unavailable:
1. determine whether the task can wait
2. decide whether fallback is safe for that workload
3. avoid silent policy drift for sensitive or cost-constrained flows
4. record the exception when a stronger or external model is used

## Verification checklist
To verify intended routing:
1. inspect config values
2. verify runtime behavior where possible
3. confirm the right model is used on the target control surface
4. capture exceptions explicitly

## Cross-links
- `SOP_HEARTBEAT.md`
- `SOP_CRON_AND_SCHEDULED_JOBS.md`
- `SOP_CONFIG_CHANGES.md`
- `SOP_SERVICE_RESTARTS.md`
