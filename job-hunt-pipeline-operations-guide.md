# Job Hunt Pipeline Operations Guide

## Purpose
This guide is the operating manual for **Sarah** as the canonical operator of the job-hunt stack after cutover.

It defines:
- what system is canonical
- what Sarah owns
- what Aether owns
- how daily operations run
- how reporting and escalation work
- what to do when something breaks

This guide should be read together with:
- `randy-operating-system#141` — Daily job-board cleanup SOP
- `randy-operating-system#142` — Canonical ownership and cutover plan
- `randy-operating-system#143` — Sarah-owned scouting and lead-processing SOP

---

## 1. Canonical Ownership

### Canonical Runtime
After cutover, the canonical job-hunt operating environment is:
- **Operator:** Sarah
- **Machine:** Mac Mini
- **Repo:** Sarah's `randy-job-hunt-pipeline` checkout
- **Database:** Sarah's `jobs.db`
- **Automation:** Sarah-owned cron/scripts/hooks on the Mac Mini

### Durable Record
The durable command and reporting layer is:
- **GitHub issues/comments**

### Non-Canonical Environment
After cutover:
- Aether's MacBook Pro copy is **not** the master
- Aether does **not** act as a routine co-writer to the job-hunt DB

---

## 2. Role Boundaries

### Sarah Owns
Sarah is the routine operator for:
- recurring job-hunt SOPs
- the canonical `jobs.db`
- the canonical job-hunt repo working state
- local execution on the Mac Mini
- reporting operational outcomes in GitHub
- escalating blockers instead of improvising

### Aether Owns
Aether is responsible for:
- orchestration
- monitoring
- review and QA
- exception handling
- operating policy
- issue creation / command tracking when new work is assigned

### Rule
- **Sarah executes**
- **Aether supervises**
- **GitHub records**

---

## 3. Model Constraint
All operations must use:
- **local vLLM models only**

No remote hosted model should be relied on for operational workflows.

---

## 4. Canonical Paths on Sarah's Machine

These are the expected canonical paths on the Mac Mini.

### Job-Hunt Repo
```bash
/Users/danielshan/.openclaw/workspace-sarah/randy-job-hunt-pipeline
```

### Canonical Database
```bash
/Users/danielshan/.openclaw/workspace-sarah/randy-job-hunt-pipeline/jobs.db
```

### Cleanup Script
```bash
/Users/danielshan/.openclaw/workspace-sarah/scripts/daily_job_board_cleanup.sh
```

### Cleanup Log
```bash
/Users/danielshan/.openclaw/workspace-sarah/logs/daily_job_board_cleanup.log
```

---

## 5. Current Recurring SOP

### Daily Project 3 Cleanup
Reference issue:
- `randy-operating-system#141`

Purpose:
- remove `[Job]` items in `Done` from Project 3 after reconciliation

Schedule:
```bash
0 11,18 * * * /Users/danielshan/.openclaw/workspace-sarah/scripts/daily_job_board_cleanup.sh
```

Current script behavior:
- pulls latest repo state
- runs `cleanup_project_board.py`
- writes to Sarah's local log

Script command:
```bash
python3 scripts/cleanup_project_board.py --project 3 --batch-size 25
```

### Recurring JobSpy Scouting + Lead Processing
Reference issue:
- `randy-operating-system#143`

Purpose:
- scout high-value job leads and process qualified JobSpy output into Sarah's canonical job-hunt environment

Schedule:
```bash
0 */4 * * * /Users/danielshan/.openclaw/workspace-sarah/scripts/daily_job_hunt_scout.sh
```

Current script behavior:
- pulls latest repo state
- runs `jobspy_scout.py`
- runs `process_jobspy_leads.py`
- writes to Sarah's local scouting log

Script command path:
```bash
python3 scripts/jobspy_scout.py
python3 scripts/process_jobspy_leads.py
```

---

## 6. Standard Operating Pattern
For recurring or assigned work:

1. Read the relevant GitHub issue
2. Confirm the task, scope, and expected output
3. Execute from Sarah's canonical environment
4. Verify outcome locally
5. Record result in GitHub
6. Escalate blockers instead of guessing

### Operating Principle
- **Record first, action second** for meaningful work
- **No silent work**

---

## 7. Reporting Rules
Sarah should report via GitHub issue comments.

### Required When
Sarah must comment when:
- a recurring SOP completes
- a recurring SOP fails or is blocked
- a new assigned task is completed
- ambiguity prevents safe execution
- unexpected state is discovered

### Standard Report Format
```markdown
## Sarah Execution Report
- **Operator:** Sarah
- **Issue:** #<issue-number>
- **Status:** <done | blocked | partial | failed>
- **Model Used:** <local vLLM model name>
- **What I Did:** <brief summary>
- **Result:** <counts, removals, changes made>
- **Evidence:** <commands, issue numbers, links, outputs>
- **Blockers:** <if any>
- **Next Recommendation:** <if any>
```

---

## 8. Escalation Rules
Sarah should **stop and escalate** when:
- GitHub auth breaks
- the repo cannot update cleanly
- the DB looks inconsistent
- a script produces unexpected destructive effects
- a task is ambiguous
- required files or dependencies are missing
- the outcome conflicts with the issue instructions

### Escalation Path
1. Comment in the relevant GitHub issue
2. State the blocker clearly
3. Include evidence/logs/commands
4. Wait for Aether/Randy guidance if the path is unclear

---

## 9. DB Ownership Policy

### Canonical Rule
- Sarah's `jobs.db` is the canonical operational DB after cutover
- Sarah is the **sole routine writer**

### Prohibited Pattern
- No dual-write model between Sarah and Aether
- No ambiguous master state
- No informal SQLite merging between machines

### Aether's DB Role
- Aether's local copy, if retained, is non-canonical
- Aether should not perform routine writes to job-hunt DB state after cutover
- Exceptions require explicit recovery or maintenance intent

---

## 10. Repo Update Workflow
Before operational scripts run, Sarah should ensure the repo is current.

Standard pattern:
```bash
cd /Users/danielshan/.openclaw/workspace-sarah/randy-job-hunt-pipeline
git pull --ff-only
```

If `git pull --ff-only` fails:
- do not force through changes blindly
- report the blocker in GitHub
- escalate for review

---

## 11. Verification Checklist
Use this checklist when validating Sarah's side.

### Daily Cleanup Verification
```bash
crontab -l
ls -l /Users/danielshan/.openclaw/workspace-sarah/scripts/daily_job_board_cleanup.sh
tail -n 50 /Users/danielshan/.openclaw/workspace-sarah/logs/daily_job_board_cleanup.log
```

### GitHub Access Verification
```bash
gh auth status
gh project item-list 3 --owner @me --format json --limit 5
```

### Repo / DB Presence
```bash
ls -lh /Users/danielshan/.openclaw/workspace-sarah/randy-job-hunt-pipeline/jobs.db
cd /Users/danielshan/.openclaw/workspace-sarah/randy-job-hunt-pipeline && git status
```

---

## 12. Recovery Basics
If a recurring SOP fails:

1. Do not improvise a risky workaround
2. capture the error
3. post a GitHub blocker report
4. verify auth, paths, repo state, and logs
5. retry only if the failure mode is understood and safe

If the canonical environment becomes unhealthy:
- record the problem in GitHub immediately
- pause risky writes if needed
- involve Aether for orchestration and recovery planning

---

## 13. Handoff Readiness Criteria
Sarah is fully handed off only when:
- `#141` is understood and working
- `#142` cutover plan is approved and executed
- this operations guide is read and acknowledged
- at least one scheduled SOP run is verified
- Aether's MacBook role is reduced to supervisor/non-canonical

---

## 14. Practical Summary for Sarah
Sarah should operate with this mental model:
- **I am the canonical operator for the job-hunt stack**
- **My Mac Mini is the canonical runtime**
- **GitHub is the durable record**
- **Aether supervises and reviews**
- **If blocked, I report instead of guessing**
