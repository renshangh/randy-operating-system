# Memory Disruption Operator SOP

## Purpose
Provide a clear, repeatable procedure for running the completed Memory Disruption workflow end to end.

## Scope
This SOP uses the implementation and documentation delivered under the Memory Disruption workstream:
- `scripts/automation/mem_safety_gate.sh`
- `scripts/automation/mem_snapshot.sh`
- `scripts/automation/mem_prune.sh`
- `scripts/automation/mem_disrupt.sh`
- `docs/memory_disruption_quickstart.md`
- `docs/memory_disruption_daily_runbook.md`

## Primary Operator Rule
Always run a dry run before any live run.

## Recommended Run Sequence
1. Start in the repository root.
2. Review the operator docs first:
   - `docs/memory_disruption_quickstart.md`
   - `docs/memory_disruption_daily_runbook.md`
3. Execute a dry run before any live run:
   - `scripts/automation/mem_disrupt.sh --dry-run --verbose`
4. Review the console output and logs. Confirm the safety gate passes and intended file targets/log paths look correct.
5. If the dry run looks correct, execute the live run:
   - `scripts/automation/mem_disrupt.sh --verbose`
6. Verify expected outputs after the live run:
   - current memory file is handled as designed
   - archive copy exists under `memory/archive/`
   - retention/prune behavior is correct
   - logs exist under `logs/memory-disruption/`
7. If anything looks unsafe or incorrect, stop and use the rollback/safety guidance from the safety workstream and the operator docs before another run.

## Minimum Operator Checklist
- Confirm today's target memory file exists
- Run dry run first
- Confirm safety gate result
- Confirm archive target path
- Confirm prune behavior
- Confirm logs were written
- Only then treat the run as successful

## Expected Log Locations
- `logs/memory-disruption/mem-safety-gate.log`
- `logs/memory-disruption/mem-snapshot.log`
- `logs/memory-disruption/mem-prune.log`
- `logs/memory-disruption/mem-disrupt.log`

## Operational Notes
- This is the parent-level run reference for operators.
- Detailed command examples and troubleshooting remain in:
  - `docs/memory_disruption_quickstart.md`
  - `docs/memory_disruption_daily_runbook.md`
- If QA/process signaling is noisy or incomplete, verify actual artifacts and log outputs before declaring success.

## Success Condition
A run is only considered successful when:
1. the dry run passes,
2. the live run completes without safety exceptions,
3. archive/log outputs exist where expected,
4. and the resulting state matches the documented workflow.
