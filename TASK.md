# TASK.md — Randy Personal Dashboard Execution Queue

Owner: Randy Shan  
Operator: Aether
Repo: `renshangh/randy-personal-dashboard`

## Objective
Operationalize a unified dashboard workflow across GitHub Projects, Gmail, Google Calendar, and OpenClaw so daily work is prioritized and executed from one control plane.

## Execution Rules
1. Every task must have: priority, owner, next action, due date.
2. Work in small increments; one shippable outcome per issue.
3. Keep statuses strict: `Inbox -> Ready -> Doing -> Blocked/Done`.
4. If blocked >24h, log blocker and propose fallback.

## Priority Scale
- **P0** = urgent/system-blocking
- **P1** = high impact, should complete this week
- **P2** = important but not urgent
- **P3** = nice to have

## Current Sprint (Initial 10 Issues)
1. [P0] Create and configure GitHub Project: Randy Operating System
2. [P0] Define project fields and status workflow
3. [P1] Create saved project views (Exec Queue, Needs Decision, Blocked, This Week)
4. [P1] Configure Gmail labels for action triage
5. [P1] Configure Gmail filters for GitHub and calendar notifications
6. [P1] Define Google Calendar daily operating blocks
7. [P1] Install and verify iPhone app stack (Gmail, Google Calendar, GitHub)
8. [P2] Define OpenClaw daily briefing template
9. [P2] Define weekly review checklist and cadence
10. [P2] Define blocker/escalation protocol and response SLA

## Done Criteria
- Initial control plane is operational on Mac and iPhone.
- Daily top-3 workflow is executable without ad-hoc decisions.
- OpenClaw can produce concise daily action brief from system inputs.
