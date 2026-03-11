# Scheduled Job Instruction Extraction Summary (#53)

This document consolidates all current pseudo-cron and recurring task instructions found within the repository.

## 1. Recurring Heartbeat Tasks (HEARTBEAT.md)
| Cadence | Command | Description | Source |
|---------|---------|-------------|--------|
| `every 5m` | `gh pr list --repo renshangh/real-estate-assistant --json number,title,state,updatedAt --limit 10` | Monitor all open PRs in real-estate-assistant | HEARTBEAT.md:7 |
| `every 30m` | `./qa-loop-skill/scripts/qa-heartbeat.sh` | Run QA heartbeat script | HEARTBEAT.md:10 |
| `every 30m` | `gh project item-list 2 --owner renshangh --format json` | Sync with Randy's Live Control Board | HEARTBEAT.md:14 |

## 2. Operational Recurring Tasks (RUNBOOK.md)
| Cadence | Command | Description | Source |
|---------|---------|-------------|--------|
| `every 5m` | `openclaw lead monitor --sources zillow,facebook,web` | Real-estate lead monitoring | RUNBOOK.md:24 |
| `every 1d` | `openclaw report leads --daily --email yourname@example.com` | Daily performance email (09:00) | RUNBOOK.md:27 |
| `every 30m` | `./qa-loop-skill/scripts/qa-heartbeat.sh` | QA Loop execution | RUNBOOK.md:30 |

## 3. General Scheduling Guidance (AGENTS.md)
| Cadence | Instruction | Source |
|---------|-------------|--------|
| `every ~30 min` | Timing can drift slightly; fine for heartbeats. | AGENTS.md:143 |
| `9:00 AM Monday` | Exact timing matters; use cron for these tasks. | AGENTS.md:148 |
| `every few days` | Use a heartbeat to read memory logs and update MEMORY.md. | AGENTS.md:199 |

## 4. Summary of Observed Behaviors
- Most recurring tasks are currently defined using pseudo-cron syntax (`every Xm/d`) within `HEARTBEAT.md` or `RUNBOOK.md`.
- There is overlap between `HEARTBEAT.md` and `RUNBOOK.md` regarding the QA heartbeat.
- Guidance in `AGENTS.md` distinguishes between drift-tolerant heartbeats and precise cron schedules.
