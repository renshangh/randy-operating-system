# HEARTBEAT.md

# Keep this file empty (or with only comments) to skip heartbeat API calls.
# Add tasks below when you want the agent to check something periodically.

# 1. Monitor all open PRs in renshangh/real-estate-assistant every 5 minutes
- every 5m: gh pr list --repo renshangh/real-estate-assistant --json number,title,state,updatedAt --limit 10

# QA Heartbeat
- every 30m: ./qa-loop-skill/scripts/qa-heartbeat.sh

# 2. Sync with Randy's Live Control Board every 30 minutes
# This ensures Sarah stays "caught up" with new board items.
- every 30m: gh project item-list 2 --owner renshangh --format json

# Note: Detailed status check for specific PRs or Board items can be triggered by the bot 
# based on updates found in the list above.
