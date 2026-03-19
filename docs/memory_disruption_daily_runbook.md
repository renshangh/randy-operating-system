# Memory Disruption Daily Runbook

## Daily operator flow (<10 minutes)

### 1. Pre-flight checks
Run from repo root:
```bash
cd /Users/danielshan/repo/randy-operating-system
```

Confirm today's memory file exists:
```bash
test -f "memory/$(date +%F).md" || touch "memory/$(date +%F).md"
```

### 2. Safe-mode validation
```bash
scripts/automation/mem_disrupt.sh --dry-run --verbose
```
Checks:
- safety gate reports `PASS`
- snapshot path points to today's memory file
- prune step does not target unexpected files

### 3. Live run
```bash
scripts/automation/mem_disrupt.sh --verbose
```
Expected output:
- `OK: memory disruption workflow completed`

### 4. Verify artifacts
- Archive copy exists:
  ```bash
  ls -l "memory/archive/$(date +%F).md"
  ```
- Disruption log updated:
  ```bash
  tail -n 5 memory/DISRUPTION_LOG.md
  ```
- Logs written:
  ```bash
  ls -1 logs/memory-disruption/
  ```

## Troubleshooting

### Safety gate blocked the run
Cause:
- likely secret/token-like text in today's memory file

Fix:
```bash
scripts/automation/mem_safety_gate.sh --file "memory/$(date +%F).md" --verbose
```
Redact flagged content, then rerun.

### Snapshot failed because file is missing
Fix:
```bash
touch "memory/$(date +%F).md"
```
Then rerun `scripts/automation/mem_disrupt.sh`.

### Prune removed too much in dry-run
Fix:
- rerun with a larger retention window:
  ```bash
  scripts/automation/mem_prune.sh --retain-days 180 --dry-run
  ```

### Need reversible/safe behavior
Use:
```bash
scripts/automation/mem_disrupt.sh --dry-run
```
No files are changed in dry-run mode.

## Outputs and logs
- Archive snapshots: `memory/archive/`
- Disruption ledger: `memory/DISRUPTION_LOG.md`
- Script logs: `logs/memory-disruption/`
  - `mem-safety-gate.log`
  - `mem-snapshot.log`
  - `mem-prune.log`
  - `mem-disrupt.log`

## Script summary
- `scripts/automation/mem_safety_gate.sh` — blocks unsafe runs
- `scripts/automation/mem_snapshot.sh` — archives the daily memory file
- `scripts/automation/mem_prune.sh` — deletes old archive files after retention threshold
- `scripts/automation/mem_disrupt.sh` — wrapper for the daily workflow
