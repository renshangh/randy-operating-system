# User Guide: Randy Live Control Board

**Owner:** Aether  
**Audience:** Randy  
**Review Cadence:** Monthly

This guide explains how to operate and maintain your unified command center (GitHub Project #2).

## Related SOPs
- `SOP_HEARTBEAT.md`
- `SOP_CRON_AND_SCHEDULED_JOBS.md`
- `BLOCKER_PROTOCOL.md`

## 1. Accessing the Board
- **Web:** [https://github.com/users/renshangh/projects/2](https://github.com/users/renshangh/projects/2)
- **Mobile:** Open the **GitHub mobile app** and navigate to your profile -> Projects -> Randy Live Control Board.

## 2. The Core Workflow (Inbox to Done)
We use a standard Kanban-style flow to move items from idea to completion:
1. **Inbox:** New items land here automatically when added.
2. **Ready:** Items that are fully defined (have Priority, Type, and Next Action).
3. **Doing:** Active items being worked on (max 3 at a time).
4. **Blocked:** Items waiting on external input or decisions.
5. **Done:** Completed items.

## 3. Managing Items
### Adding New Items
- **From this repo:** Click "Add item" at the bottom of any column and type the title, or create an Issue in the `randy-operating-system` repo.
- **From other repos:** 
  - Open any Issue/PR in any of your repositories.
  - In the right-hand sidebar, click **Projects**.
  - Select **Randy Live Control Board**.

### Required Fields for Every Item
To keep the dashboard meaningful, ensure every item has:
- **Priority:** P0 (Urgent), P1 (This Week), P2 (Important), P3 (Backlog).
- **Type:** Bug, Feature, Ops (Task), or Decision.
- **Owner:** Who is responsible (Randy or Aether).
- **Due Date:** When it needs to be finished.

## 4. Daily Operating Rhythm
- **08:30 – Triage (30 min):**
  - Randy & Aether review the **Exec Queue** view.
  - Pick the **Top 3** items for the day and move them to **Doing**.
  - Clear the **Gmail Action/Today** label.
- **13:30 – Midday Review (30 min):**
  - Check progress on "Doing" items.
  - Resolve any immediate blockers.
- **16:30 – Closeout (15 min):**
  - Move completed items to **Done**.
  - Update **Blocked** items with a "Next Action" and new date.
  - Plan the Top 3 for tomorrow.

## 5. Saved Views
The board is pre-configured with specialized views (tabs at the top):
- **Exec Queue:** Your high-priority, ready-to-work items.
- **Needs Decision:** Items waiting for Randy’s choice to proceed.
- **Blocked:** Transparency into what is stuck and why.
- **This Week:** Items due by Sunday.

## 6. Role of Aether (OpenClaw)
Aether acts as your operator:
- **Morning Brief:** Posts a summary of priorities, decisions, and calendar events.
- **Triage Support:** Automatically labels and categorizes new items based on your rules.
- **Execution:** Directly completes "Ops" type items assigned to Aether.
- **Reporting:** Provides cycle status updates and logs incidents to GitHub Issues.
