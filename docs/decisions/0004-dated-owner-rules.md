# 0004 · Owner rules are dated data, and changes trigger a review of live discards

**Status:** accepted

## Context
The owner's criteria change as the search evolves: a category of roles reopened for the home city, a
relocation limit, a minimum contract length. Decisions made under an old rule silently
kept their old outcome — including discards of postings that were still open.

## Decision
Each rule lives in a YAML file with an id, the text, the **date it became valid**, the previous version
and the date it replaced. Discard reasons cite the rule and date they relied on. A script cross-checks the
pipeline: a **live** discard (its posting still open) that cites a superseded rule is flagged for review.

## Consequences
- "Why was this discarded?" has an answer that survives rule changes.
- A rule change has a cost — reviewing the flagged discards — which is exactly the point.
- The agent's memory notes point to these rules but never replace them.

**Implemented by:** repository QA block 16
([quality controls](../quality-controls.md#repository-qa--25-blocks)); a minimal version in [`reference/dated_rules.py`](../../reference/dated_rules.py).
