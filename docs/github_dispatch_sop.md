# GitHub Dispatch SOP

## Purpose
Define the GitHub-first operating model for dispatching work to specialists, routing QA, and recording decisions in a durable way.

## Core Rule
- **GitHub is the persistent source of truth** for task definition, task packets, deliverables, QA, and decisions.
- **Discord is only for short live notice / heads-up**, not the primary record.

## Roles
- **Aether** — orchestrator, reviewer, sequencing owner
- **Sarah** — planning, architecture, workflow design
- **Ember** — implementation, coding, technical execution
- **Sentinel** — QA, validation, bug checking

## Labeling Rule
Every routed issue should use explicit GitHub routing labels.

### Agent label
Use one of:
- `agent:sarah`
- `agent:ember`
- `agent:sentinel`

This is the **agent column / agent assignment signal**.

### Dispatch label
Use:
- `dispatch:ready`

Without `dispatch:ready`, the specialist may not see or pick up the issue.

### Review/return label
Use:
- `status:done`

`status:done` means the specialist believes the work is complete and the issue is ready for Aether review.

## Standard GitHub Task Packet
When dispatching an issue, the task packet on GitHub should explicitly include:

### 1. Goal / Objectives
What the specialist is being asked to accomplish.

### 2. Context / Inputs
What background, parent issue, constraints, dependencies, files, or assumptions they need.

### 3. Required Deliverables / Outputs
Exactly what they must produce.
Examples:
- design draft
- schema proposal
- implementation notes
- script changes
- QA verdict
- checklist
- runbook

### 4. Acceptance Criteria
How the work will be judged.
This is the review standard Aether will use to:
- accept it
- reject it
- send it back for revision
- request expansion

## Dispatch Flow

### Step 1 — Define the issue on GitHub
The issue body should be human-readable and include:
- Goal / Objectives
- Context / Inputs
- Required Deliverables / Outputs
- Acceptance Criteria

### Step 2 — Add routing labels
Add:
- the correct `agent:*` label
- `dispatch:ready`

### Step 3 — Add the GitHub task packet
Post a comment on the issue that says:
- what the specialist must do
- what output format is expected
- what outcome is needed for the issue to move forward

### Step 4 — Send short Discord notice
Send a brief notice in the specialist lane pointing back to the GitHub issue.
Do **not** rely on Discord as the durable record.

## QA / Reroute Flow
If work needs QA:

### Step 5 — Reroute on GitHub first
Update the GitHub issue:
- replace or change the `agent:*` label to the QA specialist (usually `agent:sentinel`)
- add or confirm `dispatch:ready`

### Step 6 — Post the QA packet on GitHub
The QA comment should explicitly state:
- Objective
- What to review
- Required QA output format
- Expected outcome

### Standard QA output format
- **QA Status:** PASS or FAIL
- **Findings:** short bullet list
- **Required fixes:** only if FAIL
- **Recommendation:** accept as-is, revise, or expand

### Step 7 — Send short QA notice in Discord
Send only a brief heads-up in the QA lane, pointing back to the GitHub issue.

## Active Dispatch Watchlist + 10-Minute Rule
Aether must maintain a small, always-reachable watchlist of active delegated issues.

### Purpose
This prevents delegated work from sitting silently in `dispatch:ready` without a clean return.

### What belongs on the watchlist
Each active delegated issue should track at least:
- repository
- issue number
- assigned agent
- dispatch time
- last meaningful update time
- Discord follow-up channel
- current state

### When to add an issue
Add the issue to the watchlist when Aether dispatches it to a specialist using:
- `agent:<agentname>`
- `dispatch:ready`

### 10-minute stale check
Aether should check the watchlist on a repeating heartbeat/poll workflow.

If an issue has remained actively delegated for about 10 minutes without a clean verified return, Aether should intervene.

Meaningful progress that resets the clock includes:
- a substantive GitHub progress comment
- a concrete pass/fail checkpoint
- a valid return to Aether using `status:done`

### Intervention when stale
If a tracked issue is stale:
1. Post a GitHub comment instructing the specialist to stop active work for now and release the issue back to Aether.
2. Send a Discord follow-up to the assigned agent with an explicit @mention.
3. The specialist should hand the issue back using the normal return path:
   - remove `dispatch:ready`
   - add `status:done`
   - leave a concise GitHub comment with:
     - what was attempted
     - the exact error/blocker
     - the next debugging step

### When to remove an issue from the watchlist
Remove the issue from the watchlist when any of the following happen:
- Aether accepts the work
- the issue is closed
- Aether fully takes the issue back and it is no longer actively delegated
- ownership changes to a different agent (remove the old entry and create a new one)

## Label-State Loop
This is the canonical closed-loop dispatch pattern.

### Aether -> Specialist
When Aether dispatches an issue, apply:
- `agent:<agentname>`
- `dispatch:ready`

This means the issue is waiting on specialist action.

### Specialist -> Aether
When the specialist believes the work is complete, they should:
- remove `dispatch:ready`
- add `status:done`
- post a substantive GitHub comment with the actual result/update

This means the issue is now waiting on Aether review.

### Aether review outcome
If Aether accepts the work:
- verify the output
- relay/close/update as needed

If Aether wants rework:
- remove `status:done`
- restore `dispatch:ready`
- keep `agent:<agentname>` unless ownership changes
- post a GitHub comment explaining what must be revised

Then the issue loops back to the specialist.

### State rule
`dispatch:ready` and `status:done` should not both be present at the same time.

### Meaning of the state labels
- `dispatch:ready` = waiting on specialist
- `status:done` = waiting on Aether review

## Review Gate
Aether reviews only after the specialist or QA specialist has posted the required output on GitHub and the issue has been returned in the review state.

Then Aether decides:
- accept
- revise
- expand
- move to next issue
- close

## Practical Rules
- Keep GitHub content human-readable
- Use proper line breaks and readable formatting
- Avoid relying on Discord for important instructions
- Keep Discord messages short; keep GitHub comments complete
- If the issue is rerouted, the new GitHub task packet must explain the reroute and expected output

## Default Pattern
1. Define issue clearly
2. Add `agent:*` + `dispatch:ready`
3. Post GitHub task packet
4. Send Discord heads-up
5. Wait for GitHub deliverable
6. Route QA on GitHub if needed
7. Send QA heads-up in Discord
8. Review on GitHub
9. Decide and record next step on GitHub
