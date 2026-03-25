#!/bin/sh
set -eu

if [ "$#" -lt 3 ]; then
  echo "Usage: $0 <repo> <issue_number> <agent> [dispatch body...]" >&2
  exit 2
fi

REPO="$1"
ISSUE="$2"
AGENT="$3"
shift 3
BODY="$*"

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)

cd "$REPO_ROOT"
python3 -m orchestration.dispatch_helper \
  --repo "$REPO" \
  --issue "$ISSUE" \
  --agent "$AGENT" \
  --body "$BODY"
