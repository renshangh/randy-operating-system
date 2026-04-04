# Orchestration Anti-Drift SOP

## Purpose

Prevent orchestration drift between:
- local specialist workspaces
- canonical repo state on the execution host
- GitHub issue/review state
- Discord wake/routing state

This SOP defines the required transitions and verification gates so work does not appear complete before the durable system of record actually reflects it.

---

## Core Rule

No task is considered truly complete unless these layers are aligned:
1. specialist work output exists
2. canonical repo copy exists in the correct path
3. GitHub issue reflects the correct workflow state
4. Discord wake/follow-up is sent to the correct specialist channel when needed
5. GitHub-visible proof exists when the deliverable is expected to be durable upstream

---

## 1. Canonical Issue State Machine

Only use these workflow meanings:

### Active dispatch
- label: `dispatch:ready`
- meaning: issue is currently assigned out for active specialist work

### Returned to Aether
- label: `status:done`
- meaning: specialist turn is over and issue is back with Aether for review
- important: this does **not** mean accepted or complete

### Accepted / closed
- issue is closed by Aether after verification
- remove any no-longer-relevant active dispatch labels first

---

## 2. Required Label Transitions

### Send to specialist
When dispatching an issue to a specialist:
- add `dispatch:ready`
- set or confirm the correct `agent:<name>` label
- remove `status:done` if present

### Specialist return
When a specialist completes a pass:
- remove `dispatch:ready`
- add `status:done`
- post a substantive GitHub return comment

### Aether sends back for rework
When Aether determines another specialist pass is needed:
- remove `status:done`
- add `dispatch:ready`
- post exact rework instructions on the GitHub issue
- send short Discord follow-up telling the specialist to check GitHub

### Aether accepts/closes
When work is actually complete:
- verify deliverables
- remove `dispatch:ready` if still present
- optionally remove stale specialist label if appropriate to the repo workflow
- close the issue if the task is complete

---

## 3. Relay Gate (Pre-Review Requirement)

Do **not** review local-only claims.

Before routing to reviewer or accepting specialist output, verify:
1. the specialist identified the exact changed file path(s)
2. the artifact exists in the specialist/local workspace if that is where it was produced
3. the artifact has been relayed into the canonical repo path when required
4. the canonical repo copy is the version being reviewed

If the artifact only exists in a local workspace but not in the canonical repo path, the issue is **not review-ready**.

---

## 4. Canonical Repo -> GitHub Durability Gate

Canonical local repo state is not enough for durable completion.

When a task is supposed to land in GitHub truth, verify:
1. file exists in canonical repo path
2. git status reflects the intended change
3. commit is made if needed
4. push is made if needed
5. GitHub-visible proof or link is returned on the issue

If GitHub cannot see the result, the task should not be represented as durably complete.

---

## 5. Discord Channel Routing Rule

Never rely on memory alone for specialist wake-ups.

Maintain and use a canonical specialist-to-channel map.
Before every follow-up/wake:
1. confirm the assigned specialist
2. confirm the mapped Discord channel id
3. send the follow-up only to that mapped channel

If the wrong channel was used:
- correct it immediately
- resend to the right channel
- do not assume the prior wake was sufficient

---

## 6. GitHub Comment Content Rule

A specialist return must be substantive.
A valid return comment should include, as applicable:
- what was done
- exact file path(s)
- exact artifact location(s)
- blocker, if incomplete
- next step, if blocked or partial
- proof link, if pushed/published

Avoid vague comments like:
- “done”
- “ready”
- “updated”
without artifact paths or evidence.

---

## 7. Parent / Child Issue Rule

For parent control issues and child execution issues:

### Parent issue
- used for backlog, control, and roll-up state
- should remain open only if more child work remains
- should not drift into ambiguous specialist-return state without a clear next parent-level decision

### Child issue
- used for one concrete execution unit
- should be routed, reviewed, and closed based on the actual deliverable

If a child completes, update the parent explicitly so it reflects:
- what child completed
- what remains next
- whether parent stays open for more subtasks

---

## 8. Wake Semantics Rule

Do not assume any arbitrary GitHub comment will trigger the Discord wake path.
Use the expected workflow signals:
- `status:done` event when returning work
- recognized completion-style comment shape when a fresh wake is intentionally required

If a wake fails unexpectedly, verify router expectations before assuming specialist silence.

---

## 9. Aether Review Checklist

Before accepting any return, check:
- is the latest GitHub comment substantive?
- are exact file/artifact paths present?
- does the canonical repo copy actually exist?
- if required, is there GitHub-visible proof?
- does the label state match the actual workflow state?
- is the issue blocked, partial, or truly complete?

---

## 10. Aether Dispatch Checklist

Before dispatching or re-dispatching:
- correct issue number
- correct specialist label
- `dispatch:ready` present
- `status:done` removed
- GitHub comment contains exact instructions
- Discord wake goes to the correct mapped specialist channel

---

## 11. Anti-Drift Principle

The system must not allow these layers to drift apart:
- local artifact truth
- canonical repo truth
- GitHub issue truth
- Discord routing truth

If they disagree, trust order is:
1. GitHub issue + canonical repo verification
2. canonical local repo state
3. specialist local workspace state
4. Discord wake text alone

Discord is the wake path.
GitHub is the durable work record.
Canonical repo verification is the relay gate between them.
