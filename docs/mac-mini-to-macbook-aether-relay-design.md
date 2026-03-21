# Mac Mini → MacBook Aether Relay Design

> Deprecated / historical design note: this relay approach is no longer the active direction. Keep for reference only while we move toward a GitHub-webhook-driven wake-up path plus Discord as the execution/clarification layer.

## Status
Historical draft for the corrected production architecture where the Mac Mini receives GitHub webhooks and relays actionable events to the real Aether runtime on the MacBook Pro.

## Correction from prior direct-wake prototype
Aether is **MacBook-resident**. The Mac Mini is **not** the production home of Aether and must not host or impersonate Aether’s canonical runtime.

That means the correct production path is:

```text
GitHub -> Mac Mini listener -> relay to MacBook Aether -> Aether acts
```

and **not**:

```text
GitHub -> Mac Mini listener -> Mac Mini local main session
```

The Mac Mini-local direct session wake proved transport mechanics only. It is not the final architecture.

---

# 1. Problem Statement

The Mac Mini is the right place to host:
- GitHub webhook ingress
- public Tailscale Funnel endpoint
- specialist execution runtimes
- local event normalization and filtering
- durable relay ledgering

But the Mac Mini is **not** the right place to host Aether’s orchestrator brain.

Aether lives on the MacBook Pro, where the canonical:
- memory
- user-facing operating context
- orchestration logic
- primary assistant identity

already reside.

The production architecture therefore needs a relay model where the Mac Mini acts as an event ingress and forwarding node, and the MacBook runs the actual Aether runtime.

---

# 2. Role Separation

## Mac Mini
The Mac Mini should own:
- webhook ingress from GitHub
- signature verification
- allowlist filtering
- event normalization
- event classification
- relay-attempt logging
- fallback Discord heartbeat visibility
- specialist execution for Sarah / Ember / Sentinel when appropriate

## MacBook Pro
The MacBook Pro should own:
- real Aether runtime
- Aether session state and canonical context
- orchestration decisions
- follow-up actions that belong to Aether
- consumption acknowledgments

## GitHub
GitHub remains:
- durable source of truth for task state
- issue/comment surface for workflow events

## Discord #heartbeat
Discord remains:
- human-facing visibility mirror
- failure notification surface
- not the primary machine-trigger path

---

# 3. Design Goal

When the Mac Mini receives an actionable GitHub webhook event, it should reliably relay a structured event packet to the MacBook-hosted Aether runtime.

The design must satisfy:
1. **Correct assistant identity** — only MacBook-hosted Aether acts as Aether.
2. **Deterministic delivery** — relay attempts are recorded and observable.
3. **Restart safety** — relay can be retried or replayed.
4. **Separation of concerns** — ingress stays on Mac Mini; orchestration stays on MacBook.
5. **No split brain** — never create a pseudo-Aether on the Mac Mini.

---

# 4. Recommended Architecture

## Recommended pattern
Use a **relay client** on the Mac Mini and an **Aether ingress endpoint** on the MacBook.

```text
GitHub webhook
  -> Mac Mini listener
  -> Router classifies actionable event
  -> Relay client sends structured event to MacBook Aether ingress
  -> MacBook Aether runtime receives event and processes it
  -> Ack / response path updates relay ledger
  -> Discord mirror posts success/failure visibility
```

## Why this is correct
- preserves a single canonical Aether
- keeps the public ingress surface off the MacBook if desired
- makes the Mac Mini an event edge node, not an assistant identity node
- fits the current operational model cleanly

---

# 5. Candidate Transport Options

## Option A — MacBook OpenClaw relay endpoint (recommended)
Expose a controlled inbound path on the MacBook that accepts relay packets and delivers them to the real Aether session/runtime.

### Concept
The Mac Mini sends a structured event packet to a MacBook-side ingress service, which then posts into the actual Aether session.

### Advantages
- clean separation between ingress and assistant runtime
- explicit cross-host transport
- easiest to reason about operationally
- no fake Aether session on the Mac Mini

### Risks
- MacBook needs a reachable and protected endpoint
- requires auth / allowlist / signature validation between hosts

## Option B — Shared gateway / shared session control plane
Both Mac Mini and MacBook talk to a shared OpenClaw/Gateway control plane, and the Mac Mini targets the MacBook-resident Aether session through that shared control plane.

### Advantages
- elegant if already supported by OpenClaw deployment topology
- no custom relay endpoint needed

### Risks
- depends on session addressing and cross-host session semantics being well-defined
- if not first-class, becomes brittle

## Option C — Durable relay queue consumed by MacBook
Mac Mini writes actionable packets into a queue or relay store; MacBook polls or subscribes and Aether consumes them.

### Advantages
- strong restart safety
- excellent replay semantics
- decoupled producer/consumer

### Risks
- more moving parts
- more operational complexity than needed for MVP

## Recommendation
For the MVP, choose **Option A** if feasible. It best matches the intended operating model:

- Mac Mini = edge ingress / relay
- MacBook = real Aether

## Operational note from live validation (2026-03-19)
The transport path is now validated end-to-end on the MacBook ingress side, but one runtime caveat matters:

- session-label auto-discovery may not be sufficient by itself if `~/.openclaw/agents/main/sessions/sessions.json` is empty or stale
- explicit `AETHER_SESSION_ID` binding in the installed MacBook LaunchAgent is currently the most reliable operational fallback

This does not change the architecture recommendation. It is an implementation/runtime detail that should be cleaned up later by establishing a durable inbox session and a trustworthy discovery source.

---

# 6. Relay Packet Contract

The Mac Mini listener should send a structured packet, not freeform prose.

## Packet shape
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
  "labels": ["dispatch:ready", "agent:sarah"],
  "classification": "completion:done",
  "target_agent": "aether",
  "summary": "Test completion notice",
  "comment_body": "Status: done\nAgent: aether\n...",
  "notice_only": true,
  "sent_from_host": "mac-mini",
  "sent_at": "2026-03-18T19:00:00Z"
}
```

## Why this contract works
- replayable
- debuggable
- transport-agnostic
- easy to dedupe via `delivery_id`
- future-proof for repo-specific routing

---

# 7. Relay Ledger Model

The Mac Mini should keep the relay ledger locally. It is the event flight recorder for cross-host handoff.

## Ledger must record
- GitHub delivery id
- classification decision
- relay destination
- relay send status
- relay send error if any
- ack status from MacBook Aether
- Discord mirror status

## Important rule
The ledger records the transport lifecycle, but it does **not** replace GitHub as the durable work-state system of record.

## Suggested states
### Relay send status
- `not_attempted`
- `sent`
- `failed`

### Ack status
- `not_expected`
- `pending`
- `acked`
- `timeout`

### Discord status
- `not_attempted`
- `sent`
- `failed`

---

# 8. Acknowledgment Model

## Why ack matters
The Mac Mini must know whether the event merely left the machine or was actually consumed by the real Aether runtime.

## Recommended contract
The MacBook Aether ingress should emit a compact acknowledgment payload such as:

```json
{
  "delivery_id": "<id>",
  "status": "acked",
  "action": "none"
}
```

Or, if Aether produces text-based acknowledgment internally, the ingress can translate it into this compact form before returning to the Mac Mini relay.

## Why translate at the ingress layer
This prevents the Mac Mini relay from depending on raw model output format.

---

# 9. Failure Handling

## Relay send failure
If the Mac Mini cannot reach the MacBook ingress:
- mark relay send failed in ledger
- emit Discord warning/critical heartbeat
- allow replay later using stored packet

## Ack timeout
If relay send succeeded but no ack arrives in time:
- mark ack timeout in ledger
- emit Discord warning
- allow manual or automatic replay depending on policy

## Discord failure
Discord failure should never block relay. It is a visibility-layer problem only.

---

# 10. Security Model

## Between GitHub and Mac Mini
Keep:
- GitHub HMAC secret verification
- repo allowlist
- actionable-event filtering

## Between Mac Mini and MacBook
Add:
- host-to-host shared secret or signed relay token
- source allowlist (only Mac Mini relay is accepted)
- replay/dedupe via `delivery_id`
- no arbitrary shell execution from payloads
- strict schema validation on incoming relay packets

## Important principle
The MacBook ingress should accept only structured event packets, not arbitrary instructions.

---

# 11. Operational Flow

## Happy path
```text
1. GitHub sends webhook to Mac Mini
2. Mac Mini listener verifies signature
3. Router classifies event as actionable
4. Mac Mini relay client sends structured packet to MacBook Aether ingress
5. MacBook ingress delivers event to real Aether runtime/session
6. MacBook returns ack to Mac Mini relay
7. Mac Mini writes ledger state
8. Mac Mini posts Discord heartbeat mirror
```

## Recovery path
```text
1. Relay send fails or ack times out
2. Mac Mini ledger marks failure state
3. Discord heartbeat posts concise failure alert
4. operator can replay the stored event packet
```

---

# 12. Recommended MVP Scope

The first corrected relay MVP should handle only:
- completion comments: `Status: done|blocked|failed`
- operator commands: `/retry`, `/status`, `/hold`

Do not relay every issue event yet.

## Why
- smallest safe scope
- highest signal
- easiest to validate
- avoids flooding MacBook Aether during rollout

---

# 13. Components to Build / Modify

## On the Mac Mini side
### Existing components to keep
- `orchestration/webhook_listener.py`
- `orchestration/router.py`
- `orchestration/run_ledger.py`
- `orchestration/task_packet.py`

### New or refactored component
- `orchestration/relay_client.py`

#### Purpose
- send structured packets to the MacBook Aether ingress
- normalize transport responses
- return `sent|failed` plus ack metadata if available

### Config changes
- remove assumption that `AETHER_SESSION_ID` is local to the Mac Mini
- replace with something like:
  - `AETHER_RELAY_URL`
  - `AETHER_RELAY_SECRET`
  - `AETHER_RELAY_LABEL` (logical target only)

## On the MacBook side
### New ingress component needed
Suggested concept:
- lightweight local service or OpenClaw-facing ingress helper that receives relay packets and injects them into real Aether

Possible name:
- `aether_relay_ingress.py`

#### Responsibilities
- verify Mac Mini relay auth
- validate packet schema
- dedupe by `delivery_id`
- deliver to the real Aether runtime/session
- return structured ack response

---

# 14. What to Preserve from the Current Prototype

The following work remains valuable and should be preserved conceptually:
- structured packet contract
- expanded relay ledger
- Discord mirror behavior
- actionable-event filtering
- narrow event scope for MVP

The part to change is only the **destination transport model**.

---

# 15. What to Avoid

Do **not**:
- use the Mac Mini local `main` session as the production Aether target
- create a pseudo-Aether on the Mac Mini
- let Discord mentions serve as the primary wake mechanism
- blur specialist execution and Aether identity
- allow arbitrary freeform comment execution

---

# 16. Recommended Next Step

## Next implementation slice
Build the **Mac Mini relay client + MacBook ingress pair**.

### Minimal path
1. Mac Mini listener classifies actionable event
2. Mac Mini relay client POSTs packet to MacBook ingress
3. MacBook ingress verifies packet and forwards to real Aether runtime
4. MacBook ingress returns ack
5. Mac Mini writes ledger + emits Discord mirror

## Why this is the right next move
It preserves the correct operating model:
- ingress on the Mac Mini
- orchestration on the MacBook
- no split-brain Aether

---

# Summary

The correct production design is not “direct wake on the Mac Mini.”
It is:

**Mac Mini as trusted ingress + relay, MacBook as the real Aether brain.**

That is the architecture that matches your operating model and avoids identity drift or split-brain orchestration.
