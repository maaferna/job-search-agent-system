---
name: day
description: The whole daily procedure of the job search in one command. Chains the opening status, the radar capture and its review, overdue follow-ups, the weekly portal review when it is due, the metrics refresh, the board, the repository QA, a ranking of the day's actions and the commit. It orchestrates the other skills and decides nothing on its own. Use it when the owner says "let's do the day", "daily routine" or starts a working session without a narrower request.
---

# Day — the daily procedure

Stage: **orchestration**. Each step belongs to another skill or script; this one fixes the order and the
delivery. It was created when the owner noticed they were describing the same steps by hand every
morning.

## 1. Status

Run the `status` skill. Do not repeat its dump; it is interpreted in step 8.

## 2. Radar — capture first, interpretation after

**This skill TRIGGERS the capture; it does not only read whatever exists.** The session-start hook
launches the capture once per *session*, and a long session that spans several days never fires it
again: the radar freezes and nothing says so. The hook covers "I opened the agent", not "it is a new day".

```bash
ls -t operations/radar/reports/*.json | head -1      # date of the latest report
```

- **No report for today** → launch the capture **in the background** (several minutes) and continue with
  the rest while it runs. When it finishes, run `radar-daily` on the new report. The report opens with
  "analyzed, not decided" (the triage file): those are decided first and never re-analyzed.
- **Today's report exists and was not reviewed** → run `radar-daily` directly.
- **The latest report is several days old** → say it and say why (read the capture log before blaming
  the hook).

The automatic capture only reads sources that can be read without a session. Sources that need a
browser, or a human to solve a CAPTCHA, have their own captures with a weekly cadence; the delivery
always states the age of each of them, and any older than seven days goes to "urgent today".

## 3. Overdue follow-ups

Every entry with `action_date <= today` is resolved today: executed, rescheduled with a new date, or
closed. **A due date left to pass turns the pipeline into decoration.** Anything that means writing to
someone or sending something is *proposed*, never done on its own.

## 4. Job-board review, when due

If the last review of the owner's job-board accounts is more than seven days old, run `review-portals`
(it needs the owner's browser session, read only). With the same cadence, a script reads over public HTTP
whether each live posting still accepts applications and records its closing date: the follow-up window
is counted from the posting's close, not from the submission, and a closed posting is **not** a rejection.

## 5. Metrics — always

```bash
python3 scripts/funnel.py --md          # funnel report
python3 scripts/funnel.py --closures    # sent applications past their window, NOT applied
python3 scripts/ats_coverage.py --all
python3 scripts/board.py                # board HTML + CSV
./scripts/check.sh                      # repository QA
```

**The board generator can fail without writing anything, and someone has to look.** On an integrity
error (typically an application folder without a pipeline entry) it exits 1 and regenerates nothing.
**Never run it with its output silenced**: read its last line and check the date of the generated file.
A generator silenced this way once froze the board for three days.

## 6. What to read in the metrics, and what not

Do not dump tables. Report only what changed or is red:

- goals in red, and the action that fixes each one;
- **call-probability calibration**: if the call probabilities of closed applications no longer differ from the
  live ones, the gate does not discriminate — say so;
- `closure_reason`: what is closing and why. `conditions` is **not** a profile rejection and stays out
  of the calibration;
- ATS coverage only when a prepared application is below the median, and only to fix the CV *before*
  sending. A missing term that is not true of the profile is a gap, never a word to add.

## 7. Selection criterion

Before recommending a submission, verify that **no declared hard requirement is missing** from the
profile. The years threshold is an owner rule, dated, in `facts/owner-rules.yaml`; read the current
version, do not remember it. Coverage of the posting's terms does not override it.

## 8. Delivery to the owner

In this order, without filler:

1. **Urgent today** — overdue follow-ups, prepared applications not sent, unanswered invitations, stale
   captures.
2. **What changed since yesterday** — new portal signals, replies, closures.
3. **Goals in red** and the concrete action.
4. **Ranking of the day's actions, five at most**, ordered by real return, not apparent urgency.
5. **What is proposed and needs approval** — closures, submissions, discards.

## 9. Close

- Republish the private board page **only** with `check.sh` and the rendered-board test green: the test
  compares what the page *shows* with what the data says, and a red test means the page would publish a
  false number.
- **Commit** with a message that says which states changed and why, never "daily update".
- If `check.sh` is red because of something new, do not commit without saying so.

## What this skill does NOT do

- It does not apply. That is `apply`, invoked separately and by name.
- It does not write to anyone. That is `direct-contact`, and the owner sends.
- It does not decide. It proposes, with the data next to the proposal, and the owner decides.
