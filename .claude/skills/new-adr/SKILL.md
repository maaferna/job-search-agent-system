---
name: new-adr
description: Write a new architecture decision record for this repository, in the format of docs/decisions/ — context, decision, consequences — numbered after the last one, added to the decisions index, linked to the lesson that caused it and the control or document that implements it, and reflected where the decision is described (and in the poster count, which the numbers check reads). Use it when the owner makes or changes a design decision, when a lesson produces a new rule, or when the owner asks to "record this decision" or "write an ADR".
---

# New ADR — a decision, its reason and its price

Stage: **draft, owner approves, then apply**.

## When a decision deserves an ADR

When it constrains future work and somebody could reasonably decide the opposite: a boundary of the agent,
a rule about data, a trade-off in what is published. Not for a bug fix or a wording change. If unsure, ask.

## Procedure

1. **Read** `docs/decisions/README.md` and two existing records, to keep length and tone (half a page; plain
   sentences; no real case named).
2. **Number:** the next four-digit number after the last file in `docs/decisions/`. The file name is the
   number and a short slug of the decision: `0010-<what-was-decided>.md`.
3. **Draft** with exactly this structure:

   ```markdown
   # 0010 · <The decision, as a sentence>

   **Status:** proposed

   ## Context
   What forced a decision: the failure or the trade-off, described generically.

   ## Decision
   What is now done, stated so that a reader can check whether it is followed.

   ## Consequences
   - What gets better.
   - What it costs, and what it does not protect against.
   ```

   The consequences must include at least one cost. A decision without a cost is usually not a decision.
4. **Show the draft** to the owner. On approval, set **Status: accepted**.
5. **Link it everywhere it belongs**, in the same change:
   - a row in `docs/decisions/README.md`;
   - the lesson in `docs/lessons.md` that caused it (or a new lesson, if the failure is not there);
   - the page that describes the mechanism (architecture, quality controls, state machine…);
   - a superseded record gets **Status: superseded by 00NN**, and is never deleted or rewritten.
6. **Check:** `python3 scripts/check_numbers.py` (the posters state the number of records — update them and
   run `python3 tools/poster.py`), then `make check`, then the `doc-review` skill on the new file.
7. **Changelog:** a minor-version entry in `CHANGELOG.md`.

## Rules

- Generic, like every document here: no employer, person, posting or amount (CLAUDE.md, "Sanitization").
- The ADR records a decision the owner made. The agent may propose one, never accept it.
