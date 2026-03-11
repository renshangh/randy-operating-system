# AI Agent Randy Dashboard

AI Agent operating system for Randy (AI Agent avatar) across GitHub, Gmail, Calendar, and OpenClaw.

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
