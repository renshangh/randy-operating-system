# Discord Operating Model / SOP

## Purpose
Define how Aether, Sarah, Ember, and Sentinel operate together in Discord without creating routing confusion, bot-chaos, or unclear ownership.

## Core Roles
- **Aether** — primary orchestrator and command intake
- **Sarah** — planning, architecture, workflow design
- **Ember** — implementation, code, technical execution
- **Sentinel** — QA, validation, bug checking

## Control Rule
- **Aether is the default active assistant**
- **Sarah, Ember, and Sentinel are wake-on-demand specialists**
- **Randy manually switches a specialist's model on when Aether requests it**

## Specialist Activation
Aether will explicitly request:
- **Wake Sarah** → planning / architecture / structured design
- **Wake Ember** → implementation / coding / technical fixes
- **Wake Sentinel** → QA / testing / validation

## Workflow
1. Randy starts with **Aether**
2. Aether decides whether specialist help is needed
3. If needed, Aether tells Randy **which specialist to wake**
4. Randy manually switches that specialist on
5. Specialist handles the bounded task
6. Aether synthesizes results and drives next steps

## Channel Discipline
- **#general** → strategic control / Aether-led discussion
- **#wish-list** → ideas, wishlist, brainstorm backlog
- specialist lanes → specialist-specific execution or updates
- **GitHub** remains the durable system of record for tasks and outcomes

## Operating Principles
- no uncontrolled bot-swarm behavior
- no free-form specialist self-direction
- Aether manages handoff and sequencing
- specialists are activated only when needed
- keep live coordination in Discord, durable records in GitHub

## Default Rule
**Aether orchestrates. Randy controls specialist activation. Specialists engage only on demand.**

## Agent Visibility Requirement
This document should be treated as a shared operating reference.

To make all agents aware of it:
1. keep this SOP in the canonical repo (`randy-operating-system`)
2. link it from the main README or runbook if needed
3. include the SOP or a short reference to it in each agent workspace/context files where appropriate
4. use it as the source document when updating agent instructions or dispatch guidance

## Practical Note
If the operating model changes, update this document first, then align agent-specific instructions second.
