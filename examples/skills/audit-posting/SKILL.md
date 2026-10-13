---
name: audit-posting
description: The decision gate that runs BETWEEN recommending a posting (radar-daily) and composing a CV for it (apply). Reads the full posting and returns a structured verdict — content fit, seniority asked vs. the real profile, hard requirements present or missing, channel and its measured call rate — and ends with GO / NO-GO / DIRECT-CONTACT and a one-line reason, plus the fit score and the call probability. Exists to avoid composing a tailored CV for a role out of reach. Almost read only. Use it before applying to a specific posting, when the owner asks whether a role fits the profile, or to validate a radar recommendation before investing in it.
---

# Audit posting — the gate before composing

Stage: **read and verdict**. A posting is cheap to read; composing for nothing is expensive. The only
thing this skill writes is the form's screening questions (step 4), and only after the right CV is loaded.

**Not this skill:** if the decision to apply is already made and the folder and CV are next, that is
`apply`. This gate answers the question before: *is it worth applying?*

## Required context

- `facts/master-profile.md` — what is true of the profile: real years, stack, evidence.
- `facts/owner-rules.yaml` — the owner's dated decision rules (thresholds, locations, role types).
- `facts/career-focus.md` — the current career focus.
- `operations/pipeline.yaml` and `operations/triage.yaml` — whether it is already in progress, sent or discarded.

## Procedure

1. **Read the full posting** from its URL or folder. Pages rendered by JavaScript are read in the owner's
   browser, not with `curl`. Separate what **the posting says** from your inference. If the posting is
   gone, say so; never deduce requirements.

2. **Evaluate six dimensions.** Zero invention: what the posting does not say is "not stated".
   - **Content fit** (high / medium / low, one reason): is the real day-to-day work what the profile can
     do? Count **responsibilities** (strength / partial / empty) before scoring: a role recommended from its
     requirements alone once turned out to be ERP coordination with no data, automation or model.
   - **Seniority**: years and leadership **asked** vs. **real** years in that kind of work — not the CV's
     headline. Apply the current version of the years rule in `facts/owner-rules.yaml`.
   - **Hard requirements**, present or missing, each marked as *required* or *desirable*. Before declaring
     a tool "zero", search the training inventory: a course neither removes the gap nor puts the tool in
     the CV, but it changes a form answer from "no" to "basic training (course X)".
   - **Channel and expected rate**: use the **measured** rate per channel from the funnel script, never a
     remembered one. Is it a mass one-click form with hundreds of applicants, or is there a person?
   - **Freshness**: publication date and whether it still accepts applications.
   - **Stability and modality**: contract type, and whether the location requires relocating.

3. **The two questions that used to be forgotten.**
   - **Has this employer already screened the candidate out?** Run it, do not remember it:
     ```bash
     python3 scripts/employer_history.py "<employer>"     # exits 1 with flags
     ```
     With **two or more closures without anybody calling**, the job board does not convert with that
     employer: the recommendation is DIRECT-CONTACT or nothing. Re-applying to the **same role** after a
     silent closure changes nothing unless something changed (the CV, the channel, a person to write to).
   - **Does the posting ask for MUCH LESS than the profile has?** If it asks for less than half of the
     candidate's experience, or is a technician-level role, overqualification **lowers** the score and
     goes to `risks` with that word — not to `gaps`, which only holds requirements of the posting. A
     recruiter reads overqualification as "will leave as soon as something better appears".

4. **Screening questions of a one-click form — ONLY AFTER the right CV is loaded.** The owner's rule:
   never open the form "just to see the questions" before composing. A form with no extra questions goes
   straight from the CV step to submission, and a document composed for another employer once left that
   way. The order is fixed:
   1. provisional verdict with the posting's text (steps 2–3). NO-GO ends here: the form is never opened;
   2. GO: `apply` composes the CV and the owner approves its full text;
   3. the owner opens the form and loads **that** CV;
   4. only then the questions are read, copied literally to `posting.md`, and counted: how many are
      honestly answered "0" or "no"? **Two or more → NO-GO**, or a low-cost bet declared as such with a
      call probability of 5 % or less. Each one goes to `gaps` with the question's text.

   Forbidden: a "provisional" CV, a generic showcase CV or another application's sent PDF in the form.

5. **Verdict**, short:
   - **GO** — in focus, reachable seniority, no missing hard requirement. Next: `apply`.
   - **NO-GO (one-line reason)** — missing hard requirement, seniority out of range, out of focus, or
     already applied without reply. Recorded with its reason so the radar does not propose it again.
   - **DIRECT-CONTACT (why not the board)** — the content fits but the channel is bad for a profile that
     stretches: better to write to a person. Chains to `direct-contact`.

6. **Two numbers that are never mixed** ([metrics](../../../docs/metrics.md)):
   - **Fit (0–100), the employer's view**: `fit_detail: "F/S/R/D"` and its sum in `fit`. Bands
     A ≥ 75 · B 55–74 · C < 55. It does **not** include channel, pay, city or stability.
   - **`channel_type`**: `board` · `ats` · `public_sector` · `direct`. Direct requires having written to a
     *person*; a generic mailbox is a board.
   - **`call_probability`** = base(channel) × m(fit band) × m(competition). Never estimated by eye: the
     probability script computes it ([reference implementation](../../../reference/probability.py)).
     Written **before** the outcome and never edited: it is what gets calibrated.

7. **Gaps as a list, not only prose.** Each requirement the profile lacks goes to `gaps`, in the posting's
   words. The funnel normalizes and counts them: that decides what to study, by real demand.

## Delivery

One block per posting: the six dimensions, the verdict, fit with band and detail, channel type and call
probability, gaps as a list, and the **next concrete action**. A NO-GO on a posting that was only read goes
to the triage file; on an entry already in the pipeline, to the pipeline as `discarded` with its reason —
**written only after the owner authorizes it**.

## Hard rules

1. **Zero invention.** Not a requirement, a salary or a seniority the posting does not state.
2. **A missing hard requirement is named, never dressed up.** Applying anyway is the owner's decision;
   the honest evaluation comes first.
3. **The radar's score does not rule here.** This gate exists because a score based on the title oversells.
