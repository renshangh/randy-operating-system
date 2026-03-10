# SOP: Config Changes

**Owner:** Aether  
**Status:** Draft  
**Review Cadence:** After every material config incident or monthly

## Objective
Provide a safe change procedure for configuration updates affecting routing, automation, or user-facing behavior.

## Pre-change inspection
Before editing config:
1. capture the current value
2. define the exact scope of change
3. identify impacted services or workflows
4. identify whether a restart may be required
5. define rollback in advance

## Minimal change principle
1. Make one logical change at a time.
2. Do not bundle unrelated edits.
3. Prefer the smallest possible diff that proves the intended behavior.

## Verification first
After editing config, verify non-disruptively before restarting anything:
1. inspect the saved config
2. run safe read-only checks where possible
3. verify that the target value is present
4. confirm whether live behavior can be validated without restart

## Restart decision gate
Ask these in order:
1. Is a restart actually required?
2. Can the change be verified without disruption first?
3. Is there an active direct chat or critical workflow in flight?
4. Has the operator warned the user if disruption is possible?

If any answer makes restart unsafe, delay and schedule it.

## Rollback procedure
If the change degrades service:
1. restore the prior known-good value
2. verify health
3. confirm the impacted workflow is stable again
4. document what happened and what was learned

## Cross-links
- `SOP_SERVICE_RESTARTS.md`
- `SOP_MODEL_ROUTING.md`
- `SOP_HEARTBEAT.md`
