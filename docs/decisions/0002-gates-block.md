# 0002 · Gates block; exceptions are explicit and recorded

**Status:** accepted

## Context
Warnings that do not block get ignored: a check that only prints a message competes with everything else
in a busy session, and the cost of ignoring it lands later, on a document an employer already has.

## Decision
The repository QA exits with code 1 on any failure, the per-application gate marks red checks as
blocking, and the board page is not republished with its render test in red. When a check does not apply
to an atypical case, the exception is written in that case's analysis — **the check is never edited to
pass**.

## Consequences
- Fewer silent failures; occasionally a blocked step for a case the gate was not designed for, which is
  resolved by writing down why it does not apply.
- Warnings still exist for things that need judgment (e.g. a gap that may not be a requirement), but
  they are labeled as warnings, not failures.
