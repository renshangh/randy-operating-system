# Memory Disruption SOP

**Purpose:** Maintain continuity when session memory is lost or compacted, and prevent recurrence.

---
## A) Immediate Recovery Checklist (first 5 minutes)
1. Read `SOUL.md` (identity + operating rules).
2. Read `USER.md` (user profile + priorities).
3. Read `memory/YYYY-MM-DD.md` (today + yesterday).
4. Read `MEMORY.md` (long-term state).
5. Review last 24h GitHub activity (issues/PRs/comments) for key decisions.

---
## B) Durable-First Rules (prevent recurrence)
1. **GitHub is the source of truth.** Every material decision goes to an issue/comment.
2. **Daily Memory Gate:** append to `memory/YYYY-MM-DD.md` before end of day.
3. **Checkpoint Notes:** for long sessions, add mid-session checkpoints to daily memory.
4. **Artifact-first acceptance:** “done” only when files/commits exist.

---
## C) Recovery Workflow (if memory loss occurs)
1. Reconstruct from GitHub + daily memory files.
2. Summarize recovered state in the current day’s memory file.
3. Call out **unknowns** explicitly (what could not be recovered).
4. Validate against actual artifacts (files, commits, issues).

---
## D) Backup & Health Controls
- Nightly backup of:
  - `.openclaw/memory/`
  - `MEMORY.md`
- Weekly audit: ensure daily memory files exist and are readable.

---
## E) Post-Incident Retro Template
**Incident:** Memory disruption / session loss

- **Impact:** (what was lost)
- **Root cause:** (why it happened)
- **Immediate fixes:** (what was done today)
- **Preventive fixes:** (what will stop it next time)
- **Owner:** Aether
- **Status:** Open / In-progress / Done
