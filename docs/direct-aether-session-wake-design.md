# Direct Aether Session Wake Design

## Status
Draft design for replacing Discord-only heartbeat wake semantics with a direct OpenClaw session activation path.

## Problem Statement
The current GitHub webhook flow can successfully:
- receive GitHub issue and issue_comment events on the Mac Mini
- normalize and validate those events
- classify completion comments such as `Status: done|blocked|failed`
- post a human-visible heartbeat notice into Discord

However, the Discord heartbeat message is only a notification layer. It does **not** guarantee that Aether receives a live runtime turn. That creates an architecture gap:

```text
GitHub -> Mac Mini listener -> Discord #heartbeat -> human sees it
```

This proves notification delivery, but not agent activation.

## Goal
Change the orchestration model so that actionable GitHub webhook events can directly wake Aether through OpenClaw session ingress, while preserving Discord as a human-facing visibility channel.

## Design Principles
1. **Machine trigger first**: direct session ingress is the wake mechanism.
2. **Discord is optional visibility**: useful for humans, not required for activation.
3. **Structured payloads**: send normalized event packets, not vague pings.
4. **Deterministic routing**: one clear mapping from event class -> target session.
5. **Auditability**: every webhook delivery records routing, send result, and acknowledgment outcome.
6. **Low-noise operation**: only actionable events wake Aether.
7. **Safe command surface**: comments are parsed into constrained event types, not arbitrary execution instructions.

---

# 1. Current vs Target Architecture

## Current architecture
```text
GitHub webhook
  -> Tailscale Funnel endpoint on Mac Mini
  -> local webhook listener (127.0.0.1:8787)
  -> router classification
  -> optional GitHub reporting / optional Discord heartbeat
```

### Current strengths
- GitHub webhook ingress works.
- Signature verification works.
- Actionability filtering works.
- Completion comment parsing works.
- Discord heartbeat posting now works.

### Current weakness
- Aether does not receive a guaranteed runtime turn from Discord alone.
- Discord mention delivery and agent wake-up are separate concerns.

## Target architecture
```text
GitHub webhook
  -> Tailscale Funnel endpoint on Mac Mini
  -> local webhook listener
  -> router classification
  -> direct OpenClaw session ingress for Aether
  -> acknowledgment / follow-up actions
  -> optional Discord heartbeat mirror for humans
```

### Target outcome
Aether is activated by a direct machine-to-runtime event handoff, not by human-visible chat notifications.

---

# 2. Event Classes

## Events that should wake Aether directly
### Completion notices
Parsed from issue comments such as:
- `Status: done`
- `Status: blocked`
- `Status: failed`

### Operator commands
Parsed from issue comments such as:
- `/retry`
- `/status`
- `/hold`

### High-value dispatch transitions
Examples:
- issue labeled `dispatch:ready`
- issue has exactly one `agent:*` label

### Critical listener/runtime failures
Examples:
- repeated webhook processing failures
- GitHub API write failures
- session send failures
- repeated Discord fallback failures

## Events that should not wake Aether
- unsupported GitHub events
- non-actionable issue edits
- comments without command or completion syntax
- label churn that does not affect dispatch state

---

# 3. Routing Model

## Recommended MVP routing model
Use a **persistent Aether operations inbox session**.

### Session label
Recommended label:
- `aether-ops-inbox`

### Why this is the right MVP
- simplest implementation path
- clean proof of direct wake semantics
- avoids session explosion during early rollout
- keeps all activation logic centralized during validation

## Recommended later-state routing model
Use **repo-specific persistent Aether sessions**.

Examples:
- `aether-randy-operating-system`
- `aether-randy-job-hunt`
- `aether-real-estate-assistant`

### Why later, not first
Repo-specific routing is better long term, but a single inbox session is the fastest safe step to prove the architecture.

---

# 4. Event Packet Contract

The listener should send a structured packet into OpenClaw, not just a prose notification.

## Minimum packet shape
```json
{
  "kind": "github_webhook_event",
  "delivery_id": "<github-delivery-id>",
  "event_type": "issue_comment",
  "action": "created",
  "repository_full_name": "renshangh/randy-operating-system",
  "issue_number": 183,
  "issue_title": "...",
  "issue_url": "https://github.com/...",
  "issue_state": "open",
  "sender_login": "closedclaw",
  "labels": ["agent:sarah", "dispatch:ready"],
  "classification": "completion:done",
  "agent": "aether",
  "summary": "Test completion notice",
  "comment_body": "Status: done\nAgent: aether\n..."
}
```

## Delivery wrapper
The packet should be accompanied by a short instruction for Aether, for example:

```text
Process this GitHub webhook event.
- Acknowledge receipt.
- Decide whether follow-up action is required.
- If no action is needed, record that outcome concisely.
- If this event implies board, issue, or routing cleanup, propose or perform the next step.
```

## Why structured packets matter
- easier debugging
- replayable events
- cleaner session history
- future automation can branch on `kind` or `classification`
- easier dedupe via `delivery_id`

---

# 5. Session Activation Flow

## Happy path
```text
1. GitHub sends webhook
2. listener verifies signature
3. listener normalizes payload
4. router marks event actionable
5. listener maps event -> target Aether session
6. listener sends packet into OpenClaw session ingress
7. OpenClaw schedules Aether turn
8. Aether processes the event
9. listener records send success and optional acknowledgment
10. optional Discord heartbeat is posted for human visibility
```

## Important separation
There are now two independent outputs:

### Machine output
- direct OpenClaw session message
- required for actual wake-up

### Human output
- Discord heartbeat summary
- optional, not required for activation

---

# 6. Acknowledgment Model

## Why acknowledgments matter
A successful session send does not always prove that Aether completed reasoning on the event. To reduce ambiguity, the design should support an acknowledgment phase.

## MVP acknowledgment
At minimum, record:
- target session label
- send attempted
- send succeeded or failed
- session identifier if available

## Recommended acknowledgment contract
Aether responds with a compact machine-readable line at the top of its first reply, for example:

```text
ACK delivery_id=<id> action=<none|followup|escalate>
```

### Example meanings
- `action=none`: event consumed, no next action needed
- `action=followup`: Aether took or plans next operational action
- `action=escalate`: human attention required

## Why this helps
- proves event was consumed, not merely queued
- enables timeout detection
- improves ledger accuracy

---

# 7. Failure Handling

## Session-send failure
If direct session ingress fails:
1. record failure in the ledger
2. retry with bounded backoff
3. emit Discord fallback alert
4. optionally emit GitHub comment if repeated failures occur

## Aether no-ack timeout
If the event is sent but not acknowledged within a configured window:
1. mark status as `send_succeeded_ack_missing`
2. alert via Discord heartbeat or Telegram
3. allow manual replay using the stored packet

## Discord failure
Discord failure must not block agent activation. It should be logged as a visibility-layer failure only.

---

# 8. Security Model

## Keep existing controls
- `ALLOWED_REPOS` allowlist
- HMAC verification via `GITHUB_WEBHOOK_SECRET`
- actionable-event filtering
- constrained comment parsing for command/completion semantics

## Add for direct session wake
- allowlist of permitted target session labels
- allowlist of permitted packet `kind` values
- store raw event metadata, but never treat freeform comment text as executable instructions
- preserve `delivery_id` for dedupe and audit

---

# 9. Data and State Model

The run ledger should evolve from only webhook delivery tracking to full activation tracking.

## Existing useful fields
- GitHub delivery id
- repo
- issue number
- decision
- note

## New fields to add
- `target_session_label`
- `target_session_key` (if known)
- `session_send_status` (`queued|sent|failed`)
- `session_send_error`
- `ack_status` (`pending|acked|timeout|not_expected`)
- `ack_received_at`
- `ack_action`
- `discord_notice_status`
- `discord_notice_error`

## Why this matters
This makes the ledger the operational source of truth for activation, not only for webhook acceptance.

---

# 10. Operational Modes

## Mode A: Direct wake + Discord mirror (recommended default)
- wake Aether directly through OpenClaw
- also post Discord summary

## Mode B: Direct wake only
- useful for quiet mode or testing

## Mode C: Discord mirror only (legacy fallback)
- maintain only as emergency fallback, not as normal architecture

---

# 11. Recommended User Experience

## For Randy
A GitHub completion comment should result in:
1. Aether gets a real turn
2. optional Discord heartbeat appears
3. follow-up action happens without guessing whether the mention woke the agent

## For operators
They should be able to answer these questions quickly:
- Did GitHub deliver the event?
- Did the listener accept it?
- Which session did it route to?
- Was the session send successful?
- Did Aether acknowledge it?
- Was a human heartbeat notice also posted?

---

# 12. MVP Decision

## Recommended MVP
Implement direct wake for these event types only:
- completion comments (`Status: done|blocked|failed`)
- operator commands (`/retry`, `/status`, `/hold`)

Do **not** route all issue events into Aether yet.

## Why
- smallest safe scope
- easiest to verify
- aligned with current operational pain
- avoids flooding Aether with non-essential state changes

---

# Implementation Plan

## Phase 1 — Direct Wake MVP

### Objective
Add direct OpenClaw session ingress for accepted completion and command events while keeping Discord heartbeat enabled.

### Exact components to modify

#### 1. `orchestration/config.py`
Add environment-backed configuration for session ingress:
- `aether_session_label` (default suggested: `aether-ops-inbox`)
- `enable_direct_session_wake` (bool)
- `session_ack_timeout_seconds`
- optional `session_route_by_repo` flag for later rollout

#### 2. `orchestration/webhook_listener.py`
Add the direct wake call after router acceptance:
- build event packet from normalized event + router result
- send packet into OpenClaw session ingress
- log send result
- include direct wake result in response body/logging
- keep Discord heartbeat call as a non-blocking mirror

#### 3. `orchestration/router.py`
Expose cleaner event classification fields for downstream delivery:
- `classification`
- `target_agent`
- `notice_only`
- `requires_aether_wake`

This avoids overloading `status` strings for routing logic.

#### 4. `orchestration/run_ledger.py`
Extend schema and helper methods to store:
- target session label/key
- direct send status
- ack status
- fallback notice status

#### 5. `orchestration/task_packet.py`
Either extend this module or add a sibling packet builder for Aether session events:
- standardize JSON packet shape
- include delivery id, repo, issue, action, classification, summary
- centralize packet formatting so the listener does not hand-build strings

#### 6. `orchestration/README.md`
Document:
- direct wake architecture
- required env vars
- routing behavior
- distinction between machine trigger and human heartbeat

#### 7. `docs/github-webhook-mac-mini-runbook.md`
Add runbook sections for:
- verifying direct wake configuration
- testing session ingress
- checking ledger rows for send/ack status
- fallback behavior when Discord works but session wake fails

### New components likely needed

#### 8. `orchestration/session_client.py` (new)
Purpose:
- encapsulate OpenClaw session ingress calls
- target a persistent session label
- optionally create session if missing
- return normalized send result

This should be the only module that knows how the listener talks to OpenClaw sessions.

#### 9. `orchestration/session_event.py` or `orchestration/session_packet.py` (new, optional)
Purpose:
- define typed payload contract
- keep event serialization clean and testable

If `task_packet.py` remains clean enough, this can be avoided.

#### 10. `orchestration/tests/test_session_client.py` (new)
Add tests for:
- packet formation
- allowed routing
- send failure handling
- ack parsing helpers

### Verification steps
1. Trigger a safe `Status: done` comment on a test issue.
2. Confirm GitHub delivery was accepted.
3. Confirm ledger row stores target session and send success.
4. Confirm Aether session receives the event.
5. Confirm optional Discord heartbeat still appears.

---

## Phase 2 — Acknowledgment and Retry

### Objective
Prove not only that the session send succeeded, but that Aether consumed the event.

### Exact components to modify

#### 1. `orchestration/run_ledger.py`
Add ack timestamps and status transitions.

#### 2. `orchestration/session_client.py`
Add:
- wait-for-ack mode
- ack parser
- timeout result normalization

#### 3. `orchestration/webhook_listener.py`
After send:
- optionally wait for ack within configured timeout
- log `acked` vs `timeout`
- emit fallback alert if needed

#### 4. `docs/github-webhook-mac-mini-runbook.md`
Add timeout and replay procedures.

### Verification steps
- post test event
- verify `ACK delivery_id=...` recorded
- verify timeout path on forced non-response

---

## Phase 3 — Repo-Specific Routing

### Objective
Split the single inbox into cleaner repo-specific Aether sessions.

### Exact components to modify

#### 1. `orchestration/config.py`
Add repo -> session label mapping support.

#### 2. `orchestration/router.py`
Return target route based on repo and event class.

#### 3. `orchestration/session_client.py`
Resolve session label from map instead of single default.

#### 4. `orchestration/README.md`
Document routing matrix.

### Suggested session mapping
- `renshangh/randy-operating-system` -> `aether-randy-operating-system`
- `renshangh/randy-job-hunt-pipeline` -> `aether-randy-job-hunt`
- `renshangh/real-estate-assistant` -> `aether-real-estate-assistant`

---

## Phase 4 — Specialist-Aware Routing

### Objective
Use direct session wake for specialist routing while preserving Aether as final orchestrator.

### Target behavior
- `dispatch:ready + agent:sarah` -> Sarah session wake
- completion/blocker/failure from specialists -> Aether session wake

### Exact components to modify

#### 1. `orchestration/router.py`
Distinguish:
- specialist dispatch events
- Aether oversight events

#### 2. `orchestration/session_client.py`
Support multiple target labels for Aether, Sarah, Ember, Sentinel.

#### 3. `orchestration/adapters/`
Potentially align adapter contracts with session-based delivery rather than local-only runner assumptions.

#### 4. `docs/github_dispatch_sop.md`
Update SOP so durable GitHub state and live OpenClaw session wake semantics match.

---

# Recommended Build Order

## First implementation slice
Do these first, in order:
1. add config for direct wake
2. add `session_client.py`
3. add event packet builder
4. call direct wake from `webhook_listener.py`
5. extend ledger for send result
6. document runbook + README

## First successful demo
A single `Status: done` comment should produce:
- accepted GitHub delivery
- direct event send to `aether-ops-inbox`
- ledger row showing `sent`
- optional Discord heartbeat
- visible Aether acknowledgment in session history

---

# Non-Goals for MVP
- full auto-routing of all GitHub issue events
- replacing GitHub as durable system of record
- replacing Discord entirely
- auto-executing arbitrary instructions embedded in comments
- broad multi-agent dynamic routing without a stable ack model

---

# Recommendation Summary
Implement **Direct Wake MVP** first:
- keep Discord heartbeat for human visibility
- add direct OpenClaw session ingress for completion and command events
- treat Discord as dashboard, not ignition
- record session send and acknowledgment in the run ledger

This is the shortest path from “notification works” to “Aether actually wakes and acts.”
