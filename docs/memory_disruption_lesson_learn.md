# Memory Disruption #176 – Lesson Learn Runbook 2026-03-19

**Purpose:** capture the runtime lesson-learn takeaways after stabilizing the Mac Mini relay → MacBook ingress path and the related automation scripts so future operators can restart/resume the flow with confidence.

## 1. Context
- Weekend workstream #176 focused on the Memory Disruption operator relay experiments: building a durable **Mac Mini ingress** that forwards actionable GitHub webhook events into the **MacBook-hosted Aether** runtime. 
- Key artifacts: `orchestration/aether_relay_ingress.py`, `scripts/start_aether_relay_ingress.sh`, `deploy/launchagents/ai.openclaw.aether-relay-ingress.plist`, and `scripts/issue_50_progress_bus_poll.sh` for the cron-style progress bus.
- After the sprint the relay should safely inject via `agent --session-id`, record ledger entries, and tolerate session locking.

## 2. What went well
1. **Background poller stability:** hardening `issue_50_progress_bus_poll.sh` with an explicit `PATH` plus `gh`/`jq` preflight checks removed the noisy `command not found: gh` failures when LaunchAgents/cron hit the script.
2. **Relay injection resilience:** MacBook ingress now retries on session locks/timeouts (configurable via `AETHER_RELAY_RETRY_ATTEMPTS`/`DELAY`) and records the successful `acked` ack sequence in `orchestration/aether_relay_ingress.sqlite`.
3. **Live validation:** the MacBook LaunchAgent was fixed to point at `~/.openclaw/workspace/randy-operating-system` and the correct `orchestration` SQLite path, and a known working `AETHER_SESSION_ID` was temporarily bound so probes `localhost-fix-probe-010/011` now progress to `acked`.
4. **Documentation sync:** runbooks/README now reference the actual workspace path, session discovery caveat, injected retries, PATH notes, and committed runbook updates (`docs/macbook-aether-relay-runbook.md`, `docs/mac-mini-to-macbook-aether-relay-design.md`, `orchestration/README.md`).
5. **Operational housekeeping:** the Live Control Board cron (`gh project item-list`) was disabled as requested, keeping the heartbeat console lean.

## 3. What did not go well
1. **Session registry gap:** `~/.openclaw/agents/main/sessions/sessions.json` was empty; auto-discovery couldn’t locate the inbox session, which triggered `missing_aether_session_id` failures and forced a temporary session ID pin in the LaunchAgent.
2. **LaunchAgent drift:** the installed plist still referenced `/Users/renshan/repo/...` and the wrong dedupe DB path. The deployed service had to be re-edited manually before it could run correctly.
3. **Relay noise:** incomplete PATH + missing `openclaw` binary produced repeated `Broken pipe`/`FileNotFoundError: openclaw` logs during probe attempts until `OPENCLAW_BIN`/PATH were explicitly set.
4. **Visibility noise:** the Live Control Board poller kept running even though the board wasn’t used, consuming cycles until it was disabled.

## 4. Action items (next cleanup pass)
1. **Durable inbox session:** create/mark a persistent Aether inbox session (e.g., `agent:main:discord:...` or `aether-ops-inbox`) and update the relay injector to find it through the actual transcript files rather than `sessions.json`. Document steps in this doc once done.
2. **Document missing session symptoms:** add a short note (maybe into `docs/macbook-aether-relay-runbook.md`) describing the `missing_aether_session_id` error and how to recover by either pinning a session ID or restarting the session registry.
3. **Confirm `openclaw` path in plist:** ensure the installed LaunchAgent always sets `OPENCLAW_BIN`/`PATH`; track this in the runbook if new systems are provisioned.
4. **Optionally re-enable Live Board cron** when the board is needed again; otherwise keep it idle.
5. **Reference material:** link to runbook commits `5386164` (code fix) and `6e5480b` (docs cleanup) plus this lesson doc in the main issue (#176 or the parent). 

## 5. References
- GitHub commits: `5386164` (code hardening), `6e5480b` (docs cleanup)
- Issues: `#176` (Memory Disruption relay work), `#140` (agent coordination), `#187` (Aether relay ingress)
- Probes: `localhost-fix-probe-009/010/011` (ledger records) recorded in `orchestration/aether_relay_ingress.sqlite`
- Logs: `/tmp/aether_relay_ingress.log`, `logs/issue_120_reporter_bus.log`
- Current LaunchAgent: `~/Library/LaunchAgents/ai.openclaw.aether-relay-ingress.plist`

If you want me to keep this doc updated with the final inbox session discovery path or new lessons, just say so.