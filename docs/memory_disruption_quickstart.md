# Memory Disruption Quickstart

## Goal
Get a new operator from zero to a verified first run in under 10 minutes.

## Prerequisites
- Local clone of `randy-operating-system`
- `bash` available
- `gh` installed and authenticated if GitHub context needs checking
- Writable repo checkout
- Daily memory file exists at `memory/YYYY-MM-DD.md`

## First Run
1. Open the repo root:
   ```bash
   cd /Users/danielshan/repo/randy-operating-system
   ```
2. Make the automation scripts executable (first time only):
   ```bash
   chmod +x scripts/automation/*.sh
   ```
3. Create today's memory file if needed:
   ```bash
   touch "memory/$(date +%F).md"
   ```
4. Run the workflow in safe mode first:
   ```bash
   scripts/automation/mem_disrupt.sh --dry-run --verbose
   ```
5. Verify the dry-run output:
   - safety gate passes
   - snapshot target is correct
   - prune count looks reasonable
6. Run the real workflow:
   ```bash
   scripts/automation/mem_disrupt.sh --verbose
   ```
7. Confirm success:
   - `memory/archive/YYYY-MM-DD.md` exists
   - `memory/DISRUPTION_LOG.md` contains a new entry
   - logs exist in `logs/memory-disruption/`

## Key Commands
- Full safe run:
  ```bash
  scripts/automation/mem_disrupt.sh --dry-run
  ```
- Full live run:
  ```bash
  scripts/automation/mem_disrupt.sh
  ```
- Snapshot only:
  ```bash
  scripts/automation/mem_snapshot.sh --date "$(date +%F)"
  ```
- Prune old archives:
  ```bash
  scripts/automation/mem_prune.sh --retain-days 90
  ```
- Check safety gate:
  ```bash
  scripts/automation/mem_safety_gate.sh --file "memory/$(date +%F).md"
  ```
