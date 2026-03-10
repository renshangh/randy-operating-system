# RUNBOOK – Real Estate AI Assistant (Ember)

## Overview
Ember now operates as a **real‑estate AI assistant** that helps Dallas real‑estate teams automate lead handling, scheduling, document processing, and client communication using OpenClaw.

## Daily / Recurring Tasks
| Frequency | Task | Command / Tool | Notes |
|-----------|------|----------------|-------|
| Every 5 min | Check for new leads in connected lead sources (Zillow, website forms, Facebook leads) and auto‑respond via OpenClaw | `openclaw lead monitor --sources zillow,facebook,web --response-template lead_response.txt` | Trigger AI Lead Response Bot |
| Every 15 min | Sync appointments from AI Scheduler to Google Calendar / Outlook | `openclaw calendar sync --provider google` | Keep agent calendars up‑to‑date |
| Hourly | Summarize inbox and generate draft replies for pending emails | `openclaw email summarize --inbox` | Review drafts before sending |
| Daily (9 am) | Generate Daily Lead Report (new leads, response rate, scheduled showings) and send to team Slack channel | `openclaw report leads --daily --output slack` | Use Slack webhook defined in `TOOLS.md` |
| Weekly (Monday 10 am) | Push weekly performance metrics to team dashboard (conversion rate, hours saved) | `openclaw analytics push --period week` | Update KPI board |

## On‑Demand Actions
- **Run a live demo** for a prospect: `openclaw demo run --scenario lead_response`.
- **Create a new automation workflow**: `openclaw workflow create --name "Zillow Lead Bot" --steps lead_capture,auto_reply,schedule_showing`.
- **Generate a free AI audit** for a prospect: `openclaw audit generate --client <name>`.

## Alerts & Notifications (Heartbeats)
Add the following entries to `HEARTBEAT.md` to automate checks:
```
# Real‑estate lead monitoring (every 5 minutes)
- every 5m: openclaw lead monitor --sources zillow,facebook,web

# Daily performance email (every day at 09:00)
- every 1d: openclaw report leads --daily --email yourname@example.com

# QA Loop (every 30 minutes)
- every 30m: ./qa-loop-skill/scripts/qa-heartbeat.sh
```

## SOP for New Client Onboarding
1. **Initial Contact** – Use outreach script (see `real_estate_strategy.txt`).
2. **Free Audit** – Run `openclaw audit generate` and share PDF.
3. **Proposal** – Draft using the package templates (Starter, Growth, Enterprise).
4. **Setup** – Execute `openclaw install --config <client-config>`.
5. **Training** – Schedule Zoom walkthrough, record and store in `training/`.
6. **Support** – Daily health check via heartbeat; weekly check‑in call.

---
*Update this RUNBOOK as new workflows or tools are added.*