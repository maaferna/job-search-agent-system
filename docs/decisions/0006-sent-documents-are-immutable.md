# 0006 · Sent documents are immutable records

**Status:** accepted

## Context
Showcase CVs are regenerated whenever a fragment improves. If the CVs sent to employers were regenerated
too, there would be no way to answer "what exactly did this employer receive?" — which is the first thing
to check before an interview.

## Decision
Showcase PDFs are artifacts (regenerated freely; git keeps history). The PDF in an application's "sent"
folder is a **record**: once the application is sent it is never rebuilt, and the gate (G3) and the
repository QA verify it against the git history. A correction after sending is a new, separately recorded
version.

## Consequences
- An audit of sent PDFs can tell, for each one, which retired claim traveled and how to answer it in an
  interview.
- Fixing a fragment does not silently "fix" what an employer already has.
