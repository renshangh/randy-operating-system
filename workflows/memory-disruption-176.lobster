name: memory-disruption-176
description: Orchestrate #176 sub-issues in correct order using the GitHub-first dispatch SOP (data → workflow → safety → automation → runbook)
args:
  dry_run:
    default: "true"
  dispatch_sop:
    default: "workflows/github-dispatch-sop.lobster"
steps:
  - id: define_data_structures
    command: echo "Step 1: #181 Define data structures (files, naming, schema) using the GitHub dispatch SOP"
  - id: define_workflow
    command: echo "Step 2: #177 Define daily workflow (prompts, triggers, cadence) using the GitHub dispatch SOP"
  - id: define_safety
    command: echo "Step 3: #178 Safety gates + rollback plan using the GitHub dispatch SOP"
  - id: define_automation
    command: echo "Step 4: #179 Implement scripts/automation (if needed) using the GitHub dispatch SOP"
  - id: define_runbook
    command: echo "Step 5: #180 Quickstart + daily runbook using the GitHub dispatch SOP"
