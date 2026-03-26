#!/bin/zsh
set -euo pipefail
export DISCORD_REVIEW_WEBHOOK_URL="https://discord.com/api/webhooks/1485344492226740514/4Byr-rXBg1gxHPXnvakgKo4KE7YbmHGxCTuR_ti_0olrmbQP0P6MsW4JtWujU5PdM6Km"
cd "$HOME/repo/randy-operating-system"
echo '{"job":"amy"}'
python3 -m orchestration.mirror_amy_to_discord
echo '{"job":"sarah"}'
python3 -m orchestration.mirror_sarah_telegram_to_discord
