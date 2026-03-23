# Wekan integration roadmap

## Principle
Use Wekan as a **visual operational board and planning layer**, while keeping:
- GitHub as source of truth
- webhook/listener/Aether as orchestration backbone
- OpenClaw/session ledger as execution truth

So the integration goal is **visibility first, control second**.

---

# Phase 1 — One-way GitHub -> Wekan sync
**Goal:** make Wekan a live board view of our orchestration state.

## What to build
A small sync service that:
- consumes normalized GitHub events from our existing webhook flow
- upserts a Wekan card for each tracked GitHub issue
- maps GitHub state into Wekan lists / labels / fields

## Identity model
Use:
- `repo + issue_number`
as the stable identity

Store that on every Wekan card so reconciliation is deterministic.

## Suggested Wekan board
Board:
- **Agent Ops**

Lists:
- Backlog
- Ready for Agent
- Running
- Awaiting Aether Review
- Needs Rework
- Done
- Failed

## Suggested mapping
### From GitHub / ledger -> Wekan
- issue title -> card title
- issue body/objective -> card description
- issue URL -> card link / description field
- `agent:<name>` -> Wekan label or custom field
- `dispatch:ready` -> **Ready for Agent**
- active run / running state -> **Running**
- `status:done` -> **Awaiting Aether Review**
- returned for another pass -> **Needs Rework**
- closed/accepted -> **Done**
- hard failures / repeated routing failures -> **Failed**

## Custom fields to include
- repo
- issue number
- agent
- current dispatch decision
- last wake status
- target session label
- target session id
- PR URL if any
- last updated time

## Deliverable
A one-way sync daemon or webhook-side integration:
- no write-back yet
- Wekan is strictly a visualization layer

---

# Phase 2 — Operational observability board
**Goal:** use Wekan to make orchestration legible.

## Additions
- cards move automatically when issue state changes
- stale cards highlighted
- “failed wake” issues visible
- repeated reroute loops visible
- maybe one swimlane per agent:
  - Aether
  - Sarah
  - Ember
  - Sentinel
  - Human / blocked

## Why
This is where Wekan adds immediate value:
- ops visibility
- multi-repo oversight
- queue management

## Deliverable
Board becomes a live control-room view, even before any write-back exists.

---

# Phase 3 — Planning / triage use
**Goal:** allow Wekan to help before execution starts, but without creating source-of-truth ambiguity.

## Safe pattern
Use Wekan for:
- rough backlog
- prioritization
- grouping
- triage

But once work becomes executable:
- GitHub issue must exist
- GitHub becomes canonical

## Recommended rule
- pre-execution ideas may start as Wekan-only cards
- executable work must map to a GitHub issue
- once GitHub issue exists, Wekan card becomes derivative

## Deliverable
A “promote card to GitHub issue” workflow, if wanted later.

---

# Phase 4 — Limited write-back actions
**Goal:** allow a few carefully controlled Wekan actions to modify GitHub state.

## Safe write-backs only
Examples:
- moving card to **Ready for Agent** -> add `dispatch:ready`
- moving to **Needs Rework** -> create structured GitHub comment + restore `dispatch:ready`
- moving to **Done** -> maybe close issue if checks pass

## Hard rule
No freeform bidirectional sync at first.

Every write-back must be:
- explicit
- narrow
- auditable
- conflict-checked against GitHub state

## Deliverable
A tiny set of high-confidence board actions.

---

# Phase 5 — Review coordination
**Goal:** combine Wekan board clarity with our GitHub-native review loop.

## Possible additions
- attach latest review summary to card
- attach latest Aether decision
- show latest PR / diff / review packet
- mark cards as:
  - awaiting human review
  - awaiting agent rerun
  - blocked on missing context

## Why
This is where Wekan starts helping not just planning, but review management.

---

# Data and sync rules

## Canonical truth
Always:
- GitHub issue/labels/comments = workflow truth
- run ledger/session registry = execution truth
- Wekan = materialized board view

## Conflict policy
If GitHub and Wekan disagree:
- GitHub wins

## Stable sync key
- `repo + issue_number`

## Required metadata on Wekan cards
- GitHub repo
- GitHub issue number
- GitHub issue URL
- assigned agent
- last wake status
- execution status

---

# Risks to avoid

## 1. Dual source of truth
Biggest risk.
Avoid by making Wekan derivative first.

## 2. Unbounded write-back actions
Don’t let arbitrary board moves mutate GitHub until mapping is explicit.

## 3. Missing reconciliation
If sync loses identity, duplicate cards or drift will happen.

## 4. Overbuilding UI too early
First prove value with:
- one board
- one-way sync
- useful status mapping

---

# Priority order I’d recommend

## First
1. one-way GitHub -> Wekan sync
2. Wekan board/list mapping
3. custom fields for agent/session/wake status

## Second
4. stale/failed visibility
5. multi-repo ops board
6. swimlanes by agent/team

## Third
7. controlled write-back actions
8. card-to-GitHub promotion flow
9. richer review metadata on cards

---

# The best first concrete project
If we do just one thing first, it should be:

## “Create one-way GitHub issue -> Wekan board sync for orchestration visibility”

Because it gives:
- immediate usefulness
- almost no workflow risk
- no source-of-truth confusion
- a real test of whether Wekan helps us
