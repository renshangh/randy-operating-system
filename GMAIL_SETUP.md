# Gmail Triage Setup Guide

This guide explains how to set up your action-oriented labels and filters in Gmail to stay synced with your Live Control Board.

## 1. Create the Labels
Run these steps in the Gmail web interface or mobile app:
1. Go to **Settings** (gear icon) -> **See all settings** -> **Labels**.
2. Scroll down to the **Labels** section and click **Create new label**.
3. Create the following hierarchy:
   - `Action/Today`
   - `Action/ThisWeek`
   - `Waiting/External`
   - `GitHub/PR`
   - `GitHub/Issue`
   - `Calendar/Prep`

## 2. Set Up the Filters (Automation)
Go to **Settings** -> **Filters and Blocked Addresses** -> **Create a new filter**.

### Filter A: GitHub PR Reviews
- **From:** `notifications@github.com`
- **Has the words:** `review requested`
- **Action:** Apply label `Action/Today` AND `GitHub/PR`.

### Filter B: GitHub Assignments/Mentions
- **From:** `notifications@github.com`
- **Has the words:** `assigned you` OR `mentioned you`
- **Action:** Apply label `Action/Today` AND `GitHub/Issue`.

### Filter C: Calendar Invites
- **From:** `google.com` (or your calendar provider)
- **Subject:** `Invitation:` OR `Updated invitation:`
- **Action:** Apply label `Calendar/Prep`.

## 3. Daily Operating Triage (The 08:30 Block)
The goal is to keep `Action/Today` empty by the end of the day.
1. Open the `Action/Today` label.
2. For each email:
   - **Do it now:** If it takes <2 min.
   - **Move to Board:** If it's a task, add it to the **Live Control Board** and archive the email.
   - **Defer:** Move to `Action/ThisWeek` if not urgent.
   - **Wait:** Move to `Waiting/External` if you are waiting for a reply.
