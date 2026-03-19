#!/usr/bin/env bash
set -euo pipefail

python3 - <<'PY'
import json
import subprocess
import sys
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

CONFIG = Path.home() / '.openclaw' / 'openclaw.json'
CHANNEL_ID = '1483095196018278423'
ACCOUNT_ID = 'ember'

cfg = json.loads(CONFIG.read_text())
api_key = (
    cfg.get('tools', {})
       .get('web', {})
       .get('search', {})
       .get('apiKey')
)
if not api_key:
    raise SystemExit('Brave API key not found in ~/.openclaw/openclaw.json')

today = datetime.now().strftime('%Y-%m-%d')

# --- AI news via Brave Search API ---
query = urllib.parse.quote('latest AI news')
url = f'https://api.search.brave.com/res/v1/web/search?q={query}&count=5&freshness=pd&country=US&search_lang=en'
req = urllib.request.Request(url, headers={
    'Accept': 'application/json',
    'X-Subscription-Token': api_key,
})
with urllib.request.urlopen(req, timeout=30) as resp:
    brave = json.load(resp)
results = brave.get('web', {}).get('results', [])[:5]

lines = [f'🗞️ **Top-5 AI news for {today}**', '']
for i, item in enumerate(results, start=1):
    title = item.get('title', 'Untitled')
    link = item.get('url', '')
    lines.append(f'{i}. [{title}]({link})')

lines += ['', '---', '']

# --- OpenClaw repos via gh CLI ---
gh_raw = subprocess.check_output([
    'gh', 'search', 'repos', 'openclaw',
    '--limit', '3',
    '--sort', 'stars',
    '--json', 'fullName,url,description,stargazersCount'
], text=True)
repos = json.loads(gh_raw)

lines.append(f'🛠️ **Top 3 OpenClaw-related repos (as of {today})**')
lines.append('')
for i, repo in enumerate(repos, start=1):
    name = repo.get('fullName', 'unknown')
    link = repo.get('url', '')
    desc = repo.get('description') or '(no description)'
    stars = repo.get('stargazersCount', 0)
    lines.append(f'{i}. [{name}]({link}) - ⭐ {stars}')
    lines.append(f'> {desc}')
    lines.append('')

message = '\n'.join(lines).strip() + '\n'

subprocess.run([
    'openclaw', 'message', 'send',
    '--channel', 'discord',
    '--target', f'channel:{CHANNEL_ID}',
    '--message', message,
    '--account', ACCOUNT_ID,
], check=True)
PY
