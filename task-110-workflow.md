# Generic Runbook – From a Parent Issue → Sub‑issues → Live Control Board → Automated Execution

# Quick environment‑setup one‑liner (paste before running any script)
export PARENT=150 REPO=renshangh/randy-job-hunt-pipeline BOARD_ID=$(gh project view "$REPO" --owner renshangh --json id -q .id) COUNT=35

This runbook provides a single, reusable process for handling any number of sub‑issues (e.g., Issue 150 with 10 sub‑issues, or an Epic with 50 items). It ties every step to the **Live Control Board** for real‑time visibility and enforces a consistent safety pattern (dry‑run → execution → verification → logging) for each sub‑issue.

---

## 1️⃣ Prerequisites (once per repo)

| Item | Command / Action | Description |
|------|------------------|-------------|
| **GitHub CLI** | `brew install gh` | Required for board automation. |
| **Project board** | `gh project view <board> --owner <org>` | Identify the board that will host the cards. |
| **Automation script template** | `scripts/run_step.py` | Generic runner accepting `--dry-run`, `--confirm`, etc. |
| **Log directory** | `mkdir -p logs && touch logs/runbook.log` | Centralized log file for the entire run. |
| **Backup policy** | `cp jobs.db jobs.db.bak` | Ensure a restore point before destructive steps. |

---

## 2️⃣ Parent Issue Setup (one‑time per project)

1. **Create the parent issue** (e.g., `#150 – New Feature X`).
2. Add a **metadata block** to the issue body:

   ```yaml
   workflow: generic-sub-issue-pipeline
   board: renshangh/randy-job-hunt-pipeline
   steps:
     - dry-run
     - execute
     - verify
     - log
   ```

3. **Add a label** (e.g., `pipeline`) that the automation watches for.

---

## 3️⃣ Sub‑issue Generation (automated)

A helper script creates the numbered sub‑issues and links them to the board. Adjust `COUNT` to the exact number you need (e.g., 35, 49, 50).

```bash
COUNT=50   # <-- change to the required number of sub‑issues
for i in $(seq 1 ${COUNT}); do
  TITLE="150-${i} – Step ${i}"
  BODY="**Parent:** #150\n**Step:** ${i}\n\n---\n*Workflow:* dry‑run → execute → verify → log"
  ISSUE=$(gh issue create \
          --repo renshangh/randy-job-hunt-pipeline \
          --title "$TITLE" \
          --body "$BODY" \
          --label pipeline \
          --json number -q .number)

  # Add the card to the board (To‑Do column)
  BOARD_ID=$(gh project view renshangh/randy-job-hunt-pipeline --json id -q .id)
  gh project item-add "$BOARD_ID" --owner renshangh --issue "$ISSUE"
done
```

---

## 4️⃣ Execution Engine (single reusable script)

`scripts/run_step.py` is used for every sub‑issue. Only the arguments change to encode specific logic.

```python
#!/usr/bin/env python3
import argparse, subprocess, logging, sys
from pathlib import Path

log_file = Path("logs/runbook.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)],
)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--issue", type=int, required=True)
    p.add_argument("--step", choices=["dry-run","execute","verify","log"], required=True)
    p.add_argument("--confirm", action="store_true")
    args = p.parse_args()

    # Step logic goes here...
    logging.info(f"[{args.step.upper()}] Issue {args.issue}")

if __name__ == "__main__":
    main()
```

---

## 5️⃣ Orchestrator – Runbook Engine

A driver loops through sub‑issues, moving cards on the board.

```bash
#!/usr/bin/env bash
PARENT=150
BOARD_ID=$(gh project view renshangh/randy-job-hunt-pipeline --json id -q .id)

move_card() {
  gh project item-edit "$1" --status "$2"
}

# Pull the list of sub‑issues (ordered by title number)
SUB_ISSUES=$(gh issue list \
               --repo renshangh/randy-job-hunt-pipeline \
               --label pipeline \
               --json number -q '.[].number')

for ISS in $SUB_ISSUES; do
  ITEM_ID=$(gh project item-list "$BOARD_ID" --owner renshangh \
            --json id,content --jq ".[] | select(.content | contains(\"#${ISS}\")) | .id")

  # 1. Dry‑run & Move to In‑Progress
  python scripts/run_step.py --issue "$ISS" --step dry-run
  move_card "$ITEM_ID" "InProgress"

  # 2. Execute (add --confirm for manual gating)
  python scripts/run_step.py --issue "$ISS" --step execute --confirm

  # 3. Verify & Log & Move to Done
  python scripts/run_step.py --issue "$ISS" --step verify
  python scripts/run_step.py --issue "$ISS" --step log
  gh issue close "$ISS"
  move_card "$ITEM_ID" "Done"
done

# Final PR creation
gh pr create --title "Feature X Complete" \
            --body "All steps finished. See logs in logs/runbook.log."
```

---

## 6️⃣ Usage Summary
1. Create parent issue with metadata.
2. Generate sub‑issues (e.g., `./generate_subissues.sh --count 35`).
3. Run orchestrator (e.g., `./orchestrate.sh`).
4. Watch the Live Control Board for real‑time card movement.
5. Review final PR and logs.

---

## 7️⃣ Turning This Into a Skill
- Store this file (or a trimmed version) under `skills/generic-workflow/`.
- Add a `SKILL.md` (see `skills/generic-workflow/SKILL.md`) that describes the parameters (`COUNT`, board ID, repo, etc.).
- Future projects can invoke the skill by referencing its name; you only need to supply the parent issue number and desired sub‑issue count.

---

**TL;DR**: Adjust `COUNT` to whatever number of sub‑issues you need, run the generator script, then run the orchestrator. The Live Control Board will show each card move from *To‑Do → In‑Progress → Done* and the safety steps will be applied automatically.
