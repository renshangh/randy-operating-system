# AI Agent Randy Dashboard

AI Agent operating system for Randy (AI Agent avatar) across GitHub, Gmail, Calendar, and OpenClaw.

## Idle Model Switcher

The Phase 1 idle-model switcher lives at `orchestration/model_switcher.py`.

### What it does
This script helps move an agent onto a lower-cost local model when the agent is idle or outside business hours, then move it back toward the active model when new work arrives.

In plain terms:
- **Idle / off-hours** → prefer the local vLLM model
- **New work arrives** → wake the agent back to the active model

### Current behavior
The switcher currently makes and logs decisions. It is scaffold-first, so it does not yet fully rewire the whole runtime by itself. It is meant to be called by a scheduler/heartbeat for idle checks and by the webhook/router for wake-up.

### Quick start
Run a safe dry-run idle check:

```bash
python3 orchestration/model_switcher.py --dry-run
```

Run a safe dry-run wake check:

```bash
python3 orchestration/model_switcher.py --dry-run --wake
```

Compile check:

```bash
python3 -m py_compile orchestration/model_switcher.py
```

### How an operator would use it
#### 1) Periodic idle check
Have a scheduler, cron job, or heartbeat call:

```bash
python3 orchestration/model_switcher.py
```

This evaluates whether the system should stay on the active model or be pushed toward the idle local model.

#### 2) Wake when work arrives
When a webhook listener, router, or dispatch entrypoint receives a new task, call:

```bash
python3 orchestration/model_switcher.py --wake
```

That forces the decision path back toward the configured active model.

### State file
By default, the script reads and writes:

```bash
.state/model_switcher_state.json
```

Expected fields include:
- `last_activity_at`
- `current_mode`
- `current_model`
- `last_decision_at`
- `last_reason`

Example:

```json
{
  "last_activity_at": "2026-03-17T02:45:00Z",
  "current_mode": "idle",
  "current_model": "vllm/openai/gpt-oss-120b",
  "last_decision_at": "2026-03-17T02:45:00Z",
  "last_reason": "off_hours"
}
```

### Configuration
You can control behavior with environment variables:
- `MODEL_SWITCHER_STATE_PATH` → state file path
- `MODEL_SWITCHER_IDLE_THRESHOLD_SECONDS` → idle timeout, default `300`
- `MODEL_SWITCHER_IDLE_MODEL` → model to prefer during idle/off-hours
- `MODEL_SWITCHER_ACTIVE_MODEL` → model to prefer when active
- `MODEL_SWITCHER_OFF_HOURS_START` → off-hours start in `HH:MM`, default `18:00`
- `MODEL_SWITCHER_OFF_HOURS_END` → off-hours end in `HH:MM`, default `08:00`

### Example commands
Use a custom state file:

```bash
python3 orchestration/model_switcher.py --state-path .state/model_switcher_state.json --dry-run
```

Set custom models inline:

```bash
MODEL_SWITCHER_IDLE_MODEL=vllm/openai/gpt-oss-120b \
MODEL_SWITCHER_ACTIVE_MODEL=google-gemini-cli/gemini-3-pro-preview \
python3 orchestration/model_switcher.py --dry-run
```

### Operational note
For production use, the intended flow is:
1. a periodic scheduler/heartbeat runs the script for idle/off-hours checks
2. the webhook/router runs the script with `--wake` when new work arrives
3. downstream runtime hooks use the decision output to apply the actual model change

## Single Operating Playbook

### 1) System of Record
- GitHub Projects: task execution and prioritization
- Gmail: inbound communication and alerts
- Google Calendar: commitments and focus blocks
- OpenClaw: orchestration and daily summaries

### 2) GitHub Projects Setup
Create one project: **Randy Operating System**

Fields:
- Priority (P0/P1/P2/P3)
- Type (Bug/Feature/Ops/Decision)
- Effort (S/M/L)
- Status (Inbox/Ready/Doing/Blocked/Done)
- Repo (source repo)
- Due Date
- Owner

Views:
- Exec Queue
- Needs Decision
- Blocked
- This Week

### 3) Gmail Setup
Labels:
- Action/Today
- Action/ThisWeek
- Waiting/External
- GitHub/PR
- GitHub/Issue
- Calendar/Prep

Filters:
- GitHub review requests -> GitHub/PR + Action/Today
- GitHub assigned/mentioned -> GitHub/Issue + Action/Today
- Calendar invites/changes -> Calendar/Prep

### 4) Calendar Rhythm
Daily blocks:
- 08:30-09:00 Triage
- 09:00-11:00 Deep Work (P0/P1)
- 13:30-14:00 Review/Follow-up
- 16:30-16:45 Closeout

### 5) OpenClaw Daily Protocol
1. Pull top GitHub items
2. Pull Gmail urgent queues
3. Pull next 24h calendar events
4. Publish top priorities + decisions + next actions

### 6) Weekly Cadence
- Monday: backlog reprioritization
- Wednesday: midweek correction
- Friday: close loops and set next week focus

### 7) Mobile Rules
- Use Gmail app + Google Calendar app on iPhone
- Use GitHub app for triage/status updates
- Avoid deep execution on phone; assign/plan only

### 8) Operating Rules
- If it matters, it must be in GitHub Project or Calendar
- Blocked items need owner + next action within 24h
- Empty Action/Today by end of day
