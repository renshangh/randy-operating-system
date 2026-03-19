#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LOG_DIR="$ROOT_DIR/logs/memory-disruption"
ARCHIVE_DIR="$ROOT_DIR/memory/archive"
mkdir -p "$LOG_DIR" "$ARCHIVE_DIR"
LOG_FILE="$LOG_DIR/mem-prune.log"
RETAIN_DAYS=90
DRY_RUN=false
VERBOSE=false

log() {
  local msg="$1"
  printf '%s [mem_prune] %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$msg" | tee -a "$LOG_FILE" >/dev/null
  if [[ "$VERBOSE" == true ]]; then printf '%s\n' "$msg"; fi
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --retain-days) RETAIN_DAYS="$2"; shift 2 ;;
    --dry-run) DRY_RUN=true; shift ;;
    --verbose) VERBOSE=true; shift ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

log "start archive_dir=$ARCHIVE_DIR retain_days=$RETAIN_DAYS dry_run=$DRY_RUN"
FILES_RAW="$(find "$ARCHIVE_DIR" -type f -name '*.md' -mtime "+$RETAIN_DAYS" 2>/dev/null | sort || true)"

if [[ -z "$FILES_RAW" ]]; then
  log "nothing to prune"
  echo "OK: nothing to prune"
  exit 0
fi

COUNT="$(printf '%s\n' "$FILES_RAW" | sed '/^$/d' | wc -l | tr -d ' ')"
printf '%s\n' "$FILES_RAW" | tee -a "$LOG_FILE" >/dev/null
if [[ "$DRY_RUN" == true ]]; then
  echo "DRY-RUN: would prune ${COUNT} file(s)"
  exit 0
fi

printf '%s\n' "$FILES_RAW" | while IFS= read -r file; do
  [[ -z "$file" ]] && continue
  rm "$file"
done
log "pruned ${COUNT} file(s)"
echo "OK: pruned ${COUNT} file(s)"
