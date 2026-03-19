#!/usr/bin/env bash
set -euo pipefail

# -------------------------------------------------------------------
# daily_openclaw_repos.sh
#  • Uses the GitHub CLI (gh) to find the top 3 repositories that mention
#    "openclaw" in their name/description.
#  • Sorts by star count (most popular first).
#  • Formats a markdown message and sends it to the #eng-updates channel
#    using Ember's Discord account.
# -------------------------------------------------------------------

# Query GitHub for the top 3 repos related to "openclaw"
# The GH CLI must already be authenticated (gh auth status should be OK).
REPOS_JSON=$(gh repo search "openclaw" --limit 3 --sort stars --json nameWithOwner,url,description,stargazersCount)

# Build the message
MSG="🛠️ **Top 3 OpenClaw‑related repos (as of $(date '+%Y-%m-%d'))**\n\n"

INDEX=1
echo "$REPOS_JSON" | jq -c '.[]' | while IFS= read -r repo; do
  NAME=$(echo "$repo" | jq -r .nameWithOwner)
  URL=$(echo "$repo" | jq -r .url)
  DESC=$(echo "$repo" | jq -r .description // "(no description)")
  STARS=$(echo "$repo" | jq -r .stargazersCount)
  MSG+="${INDEX}. [$NAME]($URL) – ⭐ ${STARS}\n> ${DESC}\n\n"
  ((INDEX++))
done

# Send the message via Ember's Discord account
openclaw message send \
  --channel discord \
  --target channel:1483095196018278423 \
  --message "$MSG" \
  --account ember
