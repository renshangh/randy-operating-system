#!/usr/bin/env bash
set -euo pipefail

python3 - <<'PY'
import json
import subprocess
import urllib.parse
import urllib.request
from datetime import datetime

CHANNEL_ID = '1483095196018278423'
ACCOUNT_ID = 'ember'

today = datetime.now().strftime('%Y-%m-%d')

# --- AI news via Google News RSS (no Brave dependency) ---
query = urllib.parse.quote('latest AI news')
url = f'https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en'
with urllib.request.urlopen(url, timeout=30) as resp:
    rss = resp.read().decode('utf-8', errors='ignore')

items = rss.split('<item>')[1:6]
results = []
for item in items:
    title = item.split('<title>', 1)[1].split('</title>', 1)[0].strip() if '<title>' in item else 'Untitled'
    link = item.split('<link>', 1)[1].split('</link>', 1)[0].strip() if '<link>' in item else ''
    if title:
        results.append({'title': title, 'url': link})

lines = [f'🗞️ **Top-5 AI news for {today}**', '']
for i, item in enumerate(results, start=1):
    title = item.get('title', 'Untitled')
    link = item.get('url', '')
    lines.append(f'{i}. [{title}]({link})')

lines += ['', '---', '']

# --- OpenClaw repos via gh CLI ---
gh_env = dict(__import__('os').environ)
gh_env.pop('GH_TOKEN', None)
gh_raw = subprocess.check_output([
    'gh', 'search', 'repos', 'openclaw',
    '--limit', '3',
    '--sort', 'stars',
    '--json', 'fullName,url,description,stargazersCount'
], text=True, env=gh_env)
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
