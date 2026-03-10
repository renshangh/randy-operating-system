# SOP: Service Restarts

**Owner:** Aether  
**Status:** Draft  
**Review Cadence:** After every restart-related incident or monthly

## Objective
Treat service restarts as disruptive operations and define safe timing, communication, and verification.

## Risk classification
Gateway or core service restarts are disruptive because they may:
- interrupt live sessions
- break ongoing automation
- temporarily invalidate runtime assumptions

## Pre-restart communication
1. Warn before restarting if user-facing impact is possible.
2. In an active direct chat, obtain approval unless the situation is urgent and harmful to delay.
3. State expected impact, timing, and verification plan.

## Safe timing rules
Do not restart during:
- active direct chats unless necessary and communicated
- critical automation windows
- unresolved incidents where restart is only a guess

Prefer restart during controlled maintenance windows or after live work completes.

## Post-restart verification
After restart:
1. verify service health
2. verify session continuity expectations
3. verify intended config/model routing is active
4. verify the previously impacted workflow works again

## Incident capture
If a restart caused disruption, record:
- trigger
- impact
- resolution
- lesson learned

## Cross-links
- `SOP_CONFIG_CHANGES.md`
- `SOP_MODEL_ROUTING.md`
