# Agent Follow-Up Message Templates

Use these templates for Discord follow-ups when a delegated issue is still active, stale, or needs to be handed back.

## Rules
- Always explicitly @mention the agent.
- Always include the agent name in the message body.
- Always include the repo, issue number, and issue URL.
- Always direct the agent back to GitHub for the durable update.
- Use the closed-loop return path: remove `dispatch:ready`, add `status:done`, then leave the substantive GitHub comment.

## 1) Checkpoint / overtime follow-up
Use when the issue is still active but has gone quiet and you want either a real progress update or a clean return.

```text
<@AGENT_ID> AgentName — quick check on RepoName issue #ISSUE_NUMBER.

If you’re still actively working, post a substantive GitHub progress update now with current status, blocker if any, and next step.

If not, release it back now through the normal return path:
- remove `dispatch:ready`
- add `status:done`
- post a concise `Author: AgentName` GitHub comment with what you attempted, the exact blocker, and the next step

Issue: ISSUE_URL
```

## 2) Final takeover / do-it-now hand-back
Use when the issue is stale enough that Aether is taking the work back and needs the agent to stop active work now.

```text
<@AGENT_ID> AgentName — stop active work on RepoName issue #ISSUE_NUMBER and hand it back now.

Use the normal return path:
- remove `dispatch:ready`
- add `status:done`
- post a substantive `Author: AgentName` GitHub comment with what you completed, the exact blocker/error, and the next debugging step

Issue: ISSUE_URL
```

## Fill-in examples
- Sarah: `<@1483277864655651028> Sarah — ...`
- Mark: `<@1484326408204324934> Mark — ...`
