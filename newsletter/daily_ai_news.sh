#!/usr/bin/env bash
set -euo pipefail

# Query the web for the latest AI news (5 results)
RAW=$(openclaw tool web_search -- \
  --query "latest AI news 2026" \
  --count 5 \
  --country US \
  --language en \
  --freshness day \
  --json)

# Build the message
MSG="🗞️ **Top‑5 AI news for $(date '+%Y-%m-%d')**\n\n"

i=1
while IFS= read -r line; do
  title=$(echo "$line" | jq -r .title)
  url=$(echo "$line" | jq -r .url)
  MSG+="${i}. [$title]($url)\n"
  ((i++))
 done <<< "$(echo "$RAW" | jq -c '.[]')"

# Send the message via Ember account
openclaw message send --channel discord --target channel:1483095196018278423 --message "$MSG" --account ember
