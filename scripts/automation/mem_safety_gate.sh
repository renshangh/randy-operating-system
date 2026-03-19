#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LOG_DIR="$ROOT_DIR/logs/memory-disruption"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/mem-safety-gate.log"
TODAY="$(date +%F)"
TARGET_FILE="$ROOT_DIR/memory/$TODAY.md"
SKIP_GATE=false
DRY_RUN=false
VERBOSE=false

log() {
  local msg="$1"
  printf '%s [mem_safety_gate] %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$msg" | tee -a "$LOG_FILE" >/dev/null
  if [[ "$VERBOSE" == true ]]; then
    printf '%s\n' "$msg"
  fi
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --file)
      TARGET_FILE="$2"; shift 2 ;;
    --skip-gate)
      SKIP_GATE=true; shift ;;
    --dry-run)
      DRY_RUN=true; shift ;;
    --verbose)
      VERBOSE=true; shift ;;
    *)
      echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

log "start target=$TARGET_FILE dry_run=$DRY_RUN skip_gate=$SKIP_GATE"

if [[ ! -f "$TARGET_FILE" ]]; then
  log "missing target file: $TARGET_FILE"
  echo "FAIL: missing target file: $TARGET_FILE" >&2
  exit 1
fi

if [[ "$SKIP_GATE" == true ]]; then
  log "gate skipped by operator"
  echo "PASS (gate skipped): $TARGET_FILE"
  exit 0
fi

PATTERN='(AKIA[0-9A-Z]{16}|-----BEGIN[[:space:]]+PRIVATE[[:space:]]+KEY-----|gh[pousr]_[A-Za-z0-9_]{20,}|token[[:space:]]*[:=][[:space:]]*[^[:space:]]+|api[_-]?key[[:space:]]*[:=][[:space:]]*[^[:space:]]+)'
MATCHES="$(grep -nE "$PATTERN" "$TARGET_FILE" || true)"

if [[ -n "$MATCHES" ]]; then
  log "gate failed; potential sensitive content detected"
  printf '%s\n' "$MATCHES" | tee -a "$LOG_FILE" >&2
  echo "FAIL: safety gate blocked; redact sensitive content first" >&2
  exit 3
fi

log "gate passed"
echo "PASS: $TARGET_FILE"
