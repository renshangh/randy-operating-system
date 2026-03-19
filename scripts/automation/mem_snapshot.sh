#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LOG_DIR="$ROOT_DIR/logs/memory-disruption"
ARCHIVE_DIR="$ROOT_DIR/memory/archive"
mkdir -p "$LOG_DIR" "$ARCHIVE_DIR"
LOG_FILE="$LOG_DIR/mem-snapshot.log"
DATE_VALUE="$(date +%F)"
DRY_RUN=false
VERBOSE=false

log() {
  local msg="$1"
  printf '%s [mem_snapshot] %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$msg" | tee -a "$LOG_FILE" >/dev/null
  if [[ "$VERBOSE" == true ]]; then printf '%s\n' "$msg"; fi
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --date) DATE_VALUE="$2"; shift 2 ;;
    --dry-run) DRY_RUN=true; shift ;;
    --verbose) VERBOSE=true; shift ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

SRC="$ROOT_DIR/memory/$DATE_VALUE.md"
DEST="$ARCHIVE_DIR/$DATE_VALUE.md"
log "start src=$SRC dest=$DEST dry_run=$DRY_RUN"

if [[ ! -f "$SRC" ]]; then
  log "missing source file: $SRC"
  echo "FAIL: missing source file: $SRC" >&2
  exit 1
fi

if [[ "$DRY_RUN" == true ]]; then
  log "would copy $SRC -> $DEST"
  echo "DRY-RUN: would copy $SRC -> $DEST"
  exit 0
fi

cp "$SRC" "$DEST"
log "copied $SRC -> $DEST"
echo "OK: archived $SRC -> $DEST"
