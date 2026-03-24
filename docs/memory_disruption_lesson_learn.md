# Memory Disruption #176 – Historical Lesson Learn 2026-03-19

**Status:** historical reference only. This document describes a deprecated relay experiment and should not be treated as the active production model.

## What remains useful from this doc
The durable lessons are operational, not architectural:
- background jobs need explicit PATH and dependency checks
- LaunchAgent drift can silently break runtime behavior
- "webhook accepted" is not enough proof by itself
- end-to-end validation must be evidenced in logs/ledger plus visible operator receipt

## What is no longer canonical
The old **Mac Mini relay -> MacBook ingress -> direct Aether session injection** path is no longer the preferred production return model.

Do not use this document as the primary SOP for wake-up architecture.

## Current canonical production model
- **GitHub** = authoritative issue state and work record
- **Discord `#general`** = wake path
- **Aether** = validator/reviewer

## Operator note
Keep this file only as a historical lesson-learn artifact. If future cleanup removes the remaining deprecated relay code entirely, this file can be deleted in a later pass.
