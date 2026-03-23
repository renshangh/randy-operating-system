# Aether Orchestration Decision Memo: Lobster-first vs LangGraph-first

## Executive Summary

For the current Aether control-plane problem, the recommended path is:

- **Near term:** **Lobster-first**
- **Medium term:** add a **small explicit orchestration state machine**
- **Later, only if needed:** evaluate **LangGraph** as a richer orchestration runtime

### Why
The immediate problem is not model intelligence. It is orchestration reliability:
- unreliable wake paths
- brittle return-path handling
- distributed control state across GitHub, Discord, Mac Mini, and MacBook
- weak observability and auditability
- orchestration policy drift

That means the right first move is to strengthen the control plane with the least operational risk, not to adopt the most feature-rich agent framework.

The recommended architecture remains:
- **GitHub** = source of truth
- **Discord** = wake-up / notification path
- **OpenClaw** = tool/runtime surface
- **Aether** = validator / reviewer / orchestrator

## Problem Framing

Aether is not functioning as a simple assistant. It is acting as:
- dispatcher
- reviewer
- state interpreter
- watchdog
- escalation router
- control-plane coordinator

That requires support for:
1. event ingestion
2. state interpretation
3. policy enforcement
4. dispatch generation
5. return-path validation
6. stale-work intervention
7. wake-up signaling
8. audit trail creation

This is fundamentally an orchestration system problem.

## Existing System Reality

### Durable state
- GitHub issues, labels, and comments

### Live wake / ops signaling
- Discord

### Runtime / tools
- OpenClaw

### Operational topology
- Mac Mini path is relatively stable
- MacBook listener / wake path is less reliable

Any orchestration layer must fit this reality instead of replacing it.

## LangChain / LangGraph Assessment

### LangChain
LangChain is strongest for:
- model abstraction
- prompt and tool composition
- structured outputs
- RAG and tool integrations
- rapid prototyping of LLM workflows

#### Strengths
- easy tool/model composition
- broad ecosystem
- quick prototyping of agent flows

#### Weaknesses for this problem
- does not inherently solve GitHub/Discord control-plane reliability
- does not define authoritative issue state
- does not solve wake-path instability
- does not provide the domain-specific return-path contract

**Conclusion:** LangChain by itself is not the right primary answer to the Aether orchestration problem.

### LangGraph
LangGraph is more relevant because it is designed for:
- stateful workflows
- graph-based orchestration
- conditional branching
- long-running processes
- persistence / resumability
- multi-step agent and tool workflows

#### Strengths
- explicit state passing
- node-edge workflow execution
- richer branching and retry logic
- support for long-running orchestration
- stronger fit for formal workflow engines

#### Attractive use cases for Aether
Aether could eventually model workflows like:
- ingest event
- inspect GitHub state
- validate labels
- decide next action
- send wake-up
- await specialist return
- review return
- hand back stale issue
- close or requeue

#### Constraint
LangGraph does not remove the need to explicitly define:
- canonical state model
- label contract
- wake-up contract
- audit ledger
- repo rules
- review gates

Without those, LangGraph only provides a more powerful place to encode ambiguity.

**Conclusion:** LangGraph is a credible future orchestration runtime, but not the first stabilization move.

## Lobster Assessment

Local evidence from the Lobster engine in the workspace suggests support for:
- fluent workflow building
- stage-based pipelines
- resumable approval points
- persistent state get/set
- pluggable execution stages
- recipe/workflow structure

This makes Lobster a good fit for:
- orchestration playbooks
- workflow scripting
- SOP execution
- lightweight persistent coordination
- operational policy enforcement

### What Lobster appears best suited for
- dispatch protocol workflows
- return-path validation flows
- stale hand-back SOPs
- Discord wake-up fallback logic
- daily orchestration probe workflows
- review gate workflows

### Lobster strengths in this environment
- already present in the workspace
- closer to the current workflow/SOP mindset
- lower adoption cost
- more human-readable than a full graph runtime
- can encode operational policy quickly

### Lobster limitations
Compared with LangGraph, Lobster appears less naturally suited for:
- formal graph transitions
- many-node long-running orchestration runtimes
- richer resumable branching across large stateful workflows
- fully explicit orchestration runtime semantics

**Conclusion:** Lobster is a strong fit for the near-term orchestration policy layer.

## Direct Comparison

### Conceptual fit
- **Lobster-first:** orchestration **policy layer**
- **LangGraph-first:** orchestration **runtime layer**

### Time to value
- **Lobster-first:** faster
- **LangGraph-first:** slower

### Operational risk
- **Lobster-first:** lower risk, easier to adopt incrementally
- **LangGraph-first:** higher risk, easier to overbuild too early

### Fit to actual pain points
Current pain points:
- missed wake-ups
- unstable MacBook listener path
- weak return-path certainty
- lack of durable workflow enforcement
- need for daily probe
- need for visible stale intervention

These can be addressed immediately by Lobster-driven policy and explicit state rules.

### State management
- **Lobster:** lightweight persisted workflow state
- **LangGraph:** stronger formal workflow state / graph execution

### Auditability
- **Lobster:** likely better human legibility sooner
- **LangGraph:** stronger machine-structured workflow semantics if the system grows more complex

## Recommendation

## Decision
**Choose Lobster-first.**

## Rationale
The immediate need is to stabilize orchestration policy and operational flow, not to introduce a full orchestration runtime.

## Recommended rollout

### Phase 1 — Lobster as orchestration policy layer
Use Lobster to codify and standardize:
1. dispatch policy
2. return-path validation
3. Discord wake-up fallback
4. daily orchestration probe
5. stale-dispatch intervention
6. review gating
7. repo-selective operational checks

### Phase 2 — Add an explicit canonical state model
Define and enforce a small state model such as:
- `new`
- `dispatched`
- `returned`
- `under_review`
- `rework_requested`
- `stale`
- `closed`

And explicit rules such as:
- `dispatch:ready` + `agent:*` = dispatched
- `status:done` + no `dispatch:ready` = returned
- both present = invalid
- no substantive comment = incomplete return

### Phase 3 — Reassess if LangGraph is needed
Move to LangGraph only if Aether truly needs:
- richer multi-step graph execution
- formal long-running workflow state
- resumable branching with higher complexity
- a true orchestration runtime beyond Lobster’s policy/workflow role

## What Not To Do
- Do not use LangChain as the primary answer to an operations/control-plane problem.
- Do not replace GitHub, Discord, or OpenClaw with a framework abstraction.
- Do not let the LLM infer authoritative workflow state from prose when labels/comments already exist.
- Do not adopt a graph runtime before the canonical state contract is stable.

## Proposed Target Architecture

### Outer system
- **GitHub** — authoritative task state
- **Discord** — wake and operational signaling
- **OpenClaw** — tools and runtime surface

### Aether orchestration core
- **Lobster workflows** for policy execution
- **explicit state validation layer**
- **event ledger / watchlist**
- **review gate logic**

### Optional future evolution
- augment or replace parts of the inner policy engine with **LangGraph** if workflow complexity truly requires a graph runtime

## Decision Table

| Criterion | Lobster-first | LangGraph-first |
|---|---|---|
| Immediate fit to current stack | Strong | Moderate |
| Time to value | Fast | Slower |
| Incremental adoption | Easy | Harder |
| Policy/SOP encoding | Strong | Moderate |
| Human readability | Strong | Moderate |
| Formal workflow runtime | Moderate | Strong |
| Graph/state branching | Moderate | Strong |
| Long-running resumable orchestration | Moderate | Strong |
| Risk of overbuilding | Lower | Higher |
| Best near-term choice | Yes | No |

## Final Recommendation

Use **Lobster-first** to stabilize Aether orchestration policy now.

Keep the authoritative model:
- GitHub = source of truth
- Discord = wake path
- OpenClaw = runtime/tool surface
- Aether = validator/reviewer/orchestrator

Only move toward **LangGraph-first** if the Aether control plane later proves to need a richer formal graph runtime with more persistent branching and resumability than Lobster can comfortably support.
