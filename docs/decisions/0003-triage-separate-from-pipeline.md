# 0003 · Triage (analyses) separate from the pipeline (decisions)

**Status:** accepted

## Context
The radar marks a posting as "seen" once reported. When the agent analyzed postings and asked the owner
which to authorize, an unanswered question meant the analysis existed nowhere: the postings would not be
shown again, and the work was lost. Meanwhile the pipeline was filling with hundreds of "discarded"
entries for postings that had only been read.

## Decision
Two files with different jobs:
- **Triage** stores the **analysis** of every posting read in depth — verdict (recommended / investigate /
  discarded), reason, and the data that took effort to read (years asked, hard requirements, applicants,
  modality, pay) — and it is written **before** asking.
- **Pipeline** stores **decisions** on opportunities that were worked.

Rule for discards: if a posting was only *read*, its discard lives in triage; if there was an *action*
(an invitation answered, a message written, a prospect registered, a form opened), it goes to the pipeline.

## Consequences
- Pending analyses reappear at the top of the next report without re-reading them.
- Employer-history checks read both files.
- The pipeline stays a record of real work, which keeps the funnel metrics meaningful.
