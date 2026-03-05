# Blocker Escalation Protocol & Response SLA

## Objective
Ensure that blockers do not stall the operating system for more than 24 hours.

## Blocker Definitions
- **Internal Blocker:** Aether needs a decision, credential, or approval from Randy.
- **External Blocker:** Aether is waiting on a third party (e.g., recruiter, technical outage).

## Protocol
1. **Detection:** When a task cannot proceed, mark the Project status as `Blocked`.
2. **Logging:** Comment on the GitHub Issue with:
   - **Impact:** What is stalled.
   - **Evidence:** Error message or reason.
   - **Next Step:** What is needed to clear it.
3. **Escalation:**
   - If `P0`: Telegram Randy immediately.
   - If `P1/P2`: Include in the next **Daily Briefing**.
4. **Fallback:** If a blocker persists >24h without resolution, Aether must propose a "Plan B" or alternative path in the issue comments.

## Response SLA
- **Randy:** Target 4-hour response for `P0` decisions; 24-hour for `P1`.
- **Aether:** Implement resolution within 2 hours of blocker clearing.
