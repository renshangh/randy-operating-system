# Heartbeat Instruction Extraction Summary (#52)

This document consolidates all current heartbeat-related instructions and rules found within the repository.

## 1. Core Definitions and Logic (AGENTS.md)
- **Line 130**: "When you receive a heartbeat poll (message matches the configured heartbeat prompt), don't just reply `HEARTBEAT_OK` every time. Use heartbeats productively!"
- **Line 139**: Guidance on when to use heartbeats: "Multiple checks can batch together", "need conversational context", "timing can drift slightly", "reduce API calls".
- **Line 163**: "Track your checks in `memory/heartbeat-state.json`".
- **Line 199**: "Periodically (every few days), use a heartbeat to: Read through recent `memory/YYYY-MM-DD.md` files, identify significant events, update `MEMORY.md`".

## 2. Configuration and Execution (HEARTBEAT.md)
- **Line 3**: "# Keep this file empty (or with only comments) to skip heartbeat API calls."
- **Line 10**: Scheduled task: `- every 30m: ./qa-loop-skill/scripts/qa-heartbeat.sh`

## 3. Operational Tasks (RUNBOOK.md)
- **Line 30**: Scheduled task: `- every 30m: ./qa-loop-skill/scripts/qa-heartbeat.sh`
- **Line 39**: "6. Support – Daily health check via heartbeat; weekly check‑in call."

## 4. Metadata and Context (MEMORY.md / README.md)
- **MEMORY.md Line 6**: Mentions creating QA actions for heartbeats.
- **MEMORY.md Line 13**: Mentions implementing `scripts/qa-heartbeat.sh` for heartbeat commands.
- **README.md Line 13**: Defines `RUNBOOK.md` as the operational guide for heartbeats.
- **README.md Line 22**: Instruction to follow `RUNBOOK.md` to set up heartbeats.

## 5. Summary of Rules
- Heartbeats should be batch-oriented and used for awareness/triage.
- Heartbeat timing is flexible (drift is acceptable).
- `HEARTBEAT.md` acts as the primary configuration file for these recurring tasks.
- Success/Failure status should be logged to track frequency.
