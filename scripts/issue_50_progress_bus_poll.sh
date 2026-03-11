#!/bin/zsh
set -euo pipefail

REPO="renshangh/randy-operating-system"
ISSUE_NUMBER="120"
STATE_DIR="$HOME/.openclaw/workspace/randy-operating-system/.state"
LOG_DIR="$HOME/.openclaw/workspace/randy-operating-system/logs"
STATE_FILE="$STATE_DIR/issue_120_last_comment_id"
LOG_FILE="$LOG_DIR/issue_120_reporter_bus.log"

mkdir -p "$STATE_DIR" "$LOG_DIR"

last_id="0"
if [[ -f "$STATE_FILE" ]]; then
  last_id="$(cat "$STATE_FILE")"
fi

comments_json="$(gh api "repos/${REPO}/issues/${ISSUE_NUMBER}/comments?per_page=100")"

new_lines="$(printf '%s' "$comments_json" | jq -r --argjson last_id "$last_id" '
  map(select(.id > $last_id))
  | sort_by(.id)
  | .[]
  | [
      (.id | tostring),
      .created_at,
      .user.login,
      ((.body // "") | gsub("\r"; "") | gsub("\n"; " ") | .[0:500])
    ]
  | @tsv
')"

if [[ -z "$new_lines" ]]; then
  exit 0
fi

max_id="$last_id"
while IFS=$'\t' read -r cid created_at user body; do
  [[ -z "$cid" ]] && continue
  if (( cid > max_id )); then
    max_id="$cid"
  fi

  needs_action="info"
  body_lc="$(printf '%s' "$body" | tr '[:upper:]' '[:lower:]')"
  if [[ "$body_lc" == *"**needs aether:** review"* ]]; then
    needs_action="review"
  elif [[ "$body_lc" == *"**needs aether:** merge"* ]]; then
    needs_action="merge"
  elif [[ "$body_lc" == *"**needs aether:** decision"* ]]; then
    needs_action="decision"
  elif [[ "$body_lc" == *"**needs aether:** cleanup"* ]]; then
    needs_action="cleanup"
  elif [[ "$body_lc" == *"**status:** blocked"* ]]; then
    needs_action="blocked"
  fi

  printf '%s | issue=%s | comment_id=%s | action=%s | user=%s | %s\n' \
    "$(date '+%Y-%m-%d %H:%M:%S %Z')" "$ISSUE_NUMBER" "$cid" "$needs_action" "$user" "$body" >> "$LOG_FILE"
done <<< "$new_lines"

printf '%s' "$max_id" > "$STATE_FILE"
