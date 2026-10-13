---
name: status
description: Opening ritual of a job-search session. Runs the status script and presents the current state without rebuilding it by hand — pipeline by state, opportunities in progress, follow-ups due today, the latest radar report, goals in red and open blockers — and proposes the first action of the session. Read only. Use it when work on the search starts, or when the owner asks "where were we", "what is pending" or "what is next".
---

# Status — opening ritual

Stage: **read and orient**. Shows where the search stands so the session starts without reconstructing
it. Changes nothing.

## Procedure

1. **Run the script:**
   ```bash
   python3 scripts/status.py
   ```
   It prints: pipeline count by state, opportunities **in progress** with their next action,
   **follow-ups due** (`action_date <= today`), the header of the **latest radar report**, the
   **contrast with the goals** in `facts/goals.yaml` (submissions this week, direct contacts, interviews,
   latency), sent applications past their response window, and the **open blockers** of the profile.

2. **Interpret it for the owner in a few lines** — never repeat the raw dump:
   - what is **urgent**: overdue follow-ups, invitations or prepared applications without a decision;
   - what is **waiting** for a reply, with its follow-up date;
   - whether there is a **new radar report** nobody has reviewed (offer to run `radar-daily`);
   - whether a **blocker** affects something about to be sent (a dead link in the CV, for example);
   - **goals in red, each with the action that fixes it**: few submissions → radar; zero direct
     contacts → `direct-contact`; high latency → apply the day the posting appears;
   - sent applications past their window: **offer** them for an own closure. Applying the closure
     modifies the pipeline, so it needs the owner's authorization.

3. **Propose one concrete first action** — the one with the highest return: resolve an overdue
   follow-up, send a prepared application, decline an off-focus invitation, or review the radar.
   Ask whether to start there.

## Rules

- **Read only.** It neither touches `operations/pipeline.yaml` nor creates folders; that belongs to `apply`.
- **No invented state.** What the script does not show is not stated.
- If the script fails (invalid YAML, missing dependency), say so with the error; never guess the state.

## Where it sits

It is step 1 of the full daily procedure, the `day` skill. After it come `radar-daily` (new postings),
`audit-posting` (the gate) and `apply`.
