# 0005 · Closed vocabularies for states, closures, modality and channel

**Status:** accepted

## Context
Free-text fields read by generators produced wrong views: the board guessed "remote" from prose for a
job that one source described as remote and another as onsite; closures mixed "the job board finished
the process" with "nobody answered".

## Decision
Fields that drive views or metrics take values from closed lists, validated by the board generator and
the repository QA: state, `closed_by`, `closure_reason`, modality (`onsite | hybrid | remote | unresolved
| not_stated`), channel, channel type, portal-signal texts with a strength level. Anything that needs
explaining goes to a separate free-text `*_detail` field. When two sources contradict each other, the
value is `unresolved` and the owner is asked — a hypothesis is never stored as data.

## Consequences
- Metrics can be computed without interpreting prose.
- Adding a new value is a deliberate change to the list, with a comment on why.
