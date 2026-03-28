# Mac Mini Relay Sync Check

## Why this exists
The Mac Mini repositories and agent workspaces can accumulate local edits or commits before they are relayed back into GitHub master branches. This script performs a twice-daily OpenClaw-managed check from the MacBook side to flag any local drift and keep Aether aware of the canonical production vs. local split.

## What the script does
1. `scripts/macmini_relay_check.py` runs on the MacBook. It inspects both the shared Mac Mini agent workspaces (`workspace-<agent>`) and the checked-out repos (`randy-operating-system` and `randy-job-hunt-pipeline`).
2. For each target, it verifies the path exists, fetches the latest upstream refs, reports the branch, and runs `git status --short` plus ahead/behind counts.
3. It classifies each target as either clean or needing relay attention based on untracked/dirty files or local commits ahead/behind the tracked upstream.
4. Outputs are logged to `~/.openclaw/logs/macmini-relay-check.log` and a JSON payload at the same location so the run history is durable.
5. A structured summary message is posted to Discord `#general` (channel `1483085404675772469`) via the `openclaw message` workflow so Aether and the team can quickly see which targets still need relay action.

## Detection details
| Marker | Meaning |
| --- | --- |
| `git status --short` | detects uncommitted files or worktree drift |
| `rev-list --count @{u}..HEAD` | identifies local commits that have not yet been pushed |
| `rev-list --count HEAD..@{u}` | identifies local branch falling behind upstream (might require a pull before commit) |
| missing repo or `.git` directory | indicates the workspace is offline and should be investigated |

If any target needs attention, the summary includes the branch name, the nature of the drift (uncommitted changes, ahead/behind), and the first five `git status` lines for context.

## Schedule (OpenClaw—no crontab)
1. Create an OpenClaw cron job on the MacBook:
   ```bash
   openclaw cron create --name macmini-relay-check \ 
     --schedule "0 9 * * *" \ 
     --schedule "0 21 * * *" \ 
     --command "/usr/bin/python3 /Users/danielshan/repo/renshangh/randy-operating-system/scripts/macmini_relay_check.py"
   ```
   This runs the check twice a day (09:00 and 21:00 America/Chicago) inside the managed OpenClaw scheduler.
2. The same job can be manually triggered with:
   ```bash
   openclaw cron run macmini-relay-check
   ```
3. If the job cannot reach the workspaces (e.g., SSH failure), OpenClaw surfaces the failure so it can be investigated without the scheduler being blocked.

## Output and follow-up
- A Markdown-style summary (Clean workspaces + relay-needed workspaces) is sent to `#general`, giving Aether a quick read of the state.
- Logs are archived at `~/.openclaw/logs/macmini-relay-check.log` and `~/.openclaw/logs/macmini-relay-check.json` for auditing and comparison between runs.
- When a target needs attention, the summary message is the cue for Aether or the assigned specialist to `git status`/`git push` the appropriate repo/workspace before the next check.

## Operational notes
- To adjust monitored directories, update the `MONITORED` list inside `scripts/macmini_relay_check.py` and re-run the job manually once.
- The message uses the `openclaw message` suite so it reuses the existing relay channel authentication without exposing tokens in the script.
- Because the cron job lives inside OpenClaw, we can schedule it without touching macOS crontab and keep the run history inside the OpenClaw workspace.
