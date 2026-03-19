#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LOG_DIR="$ROOT_DIR/logs/memory-disruption"
mkdir -p "$LOG_DIR" "$ROOT_DIR/memory"
LOG_FILE="$LOG_DIR/mem-disrupt.log"
DISRUPTION_LOG="$ROOT_DIR/memory/DISRUPTION_LOG.md"
DRY_RUN=false
VERBOSE=false
SKIP_GATE=false
RETAIN_DAYS=90
DATE_VALUE="$(date +%F)"

log() {
  local msg="$1"
  printf '%s [mem_disrupt] %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$msg" | tee -a "$LOG_FILE" >/dev/null
  if [[ "$VERBOSE" == true ]]; then printf '%s\n' "$msg"; fi
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --date) DATE_VALUE="$2"; shift 2 ;;
    --retain-days) RETAIN_DAYS="$2"; shift 2 ;;
    --skip-gate) SKIP_GATE=true; shift ;;
    --dry-run) DRY_RUN=true; shift ;;
    --verbose) VERBOSE=true; shift ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

COMMON_ARGS=()
[[ "$DRY_RUN" == true ]] && COMMON_ARGS+=(--dry-run)
[[ "$VERBOSE" == true ]] && COMMON_ARGS+=(--verbose)

log "start date=$DATE_VALUE retain_days=$RETAIN_DAYS dry_run=$DRY_RUN skip_gate=$SKIP_GATE"

if [[ "$SKIP_GATE" == true ]]; then
  "$ROOT_DIR/scripts/automation/mem_safety_gate.sh" --file "$ROOT_DIR/memory/$DATE_VALUE.md" --skip-gate "${COMMON_ARGS[@]}"
else
  "$ROOT_DIR/scripts/automation/mem_safety_gate.sh" --file "$ROOT_DIR/memory/$DATE_VALUE.md" "${COMMON_ARGS[@]}"
fi

"$ROOT_DIR/scripts/automation/mem_snapshot.sh" --date "$DATE_VALUE" "${COMMON_ARGS[@]}"
"$ROOT_DIR/scripts/automation/mem_prune.sh" --retain-days "$RETAIN_DAYS" "${COMMON_ARGS[@]}"

ENTRY="- $(date -u +%Y-%m-%dT%H:%M:%SZ) | date=$DATE_VALUE | snapshot=ok | prune_retain_days=$RETAIN_DAYS | dry_run=$DRY_RUN"
if [[ "$DRY_RUN" == true ]]; then
  log "would append disruption log entry"
  echo "DRY-RUN: $ENTRY"
else
  printf '%s\n' "$ENTRY" >> "$DISRUPTION_LOG"
  log "appended disruption log entry"
fi

log "completed"
echo "OK: memory disruption workflow completed"
