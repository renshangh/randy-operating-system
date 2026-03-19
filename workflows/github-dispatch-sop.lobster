name: github-dispatch-sop
description: General GitHub-first dispatch workflow for specialist tasking, QA, and reroute
args:
  parent_issue:
    default: "PARENT_ISSUE"
  work_issue:
    default: "WORK_ISSUE"
  specialist:
    default: "agent:sarah"
  qa_specialist:
    default: "agent:sentinel"
steps:
  - id: define_issue
    command: echo "1) Define the issue clearly on GitHub: Goal, Context/Inputs, Required Output, Acceptance Criteria. GitHub is the durable source of truth."

  - id: label_for_dispatch
    command: echo "2) Add the routing labels on GitHub: agent label (for example: agent:sarah / agent:ember / agent:sentinel) plus dispatch:ready. Without dispatch:ready the specialist may not see it."

  - id: github_task_packet
    command: echo "3) Post the task packet on the issue itself with explicit fields: Goal/Objectives, Context/Inputs, Required Deliverables/Outputs, and Acceptance Criteria. State exactly what the specialist must do, what they must produce, and how the work will be judged."

  - id: discord_short_notice
    command: echo "4) Send a short Discord notice in the specialist lane. Discord is only the live heads-up, not the durable record."

  - id: wait_for_specialist_output
    command: echo "5) Wait for the specialist to post the actual work back on GitHub."

  - id: reroute_for_qa
    command: echo "6) If QA is needed, reroute on GitHub first: replace worker label with QA label, keep/add dispatch:ready, and post a QA task packet with PASS/FAIL expectations."

  - id: qa_short_notice
    command: echo "7) Send a short Discord notice to the QA lane pointing back to the GitHub issue."

  - id: review_gate
    command: echo "8) Review only after the QA verdict is posted on GitHub. Decide: accept, revise, expand, or move to next step."

  - id: close_or_advance
    command: echo "9) Record the decision on GitHub, then close the issue or dispatch the next issue in sequence."
