---
name: audit-metrics
description: DESIGN audit of the metrics and columns of the system (pipeline, board, funnel, triage) — whether each one answers a single question, on a single scale, comparable across rows, does not age while displayed as fixed, and nobody has to recompute by hand. It does not audit whether data follows the rules (that is the repository QA) but whether a metric means what everybody thinks it means. Runs the metrics-audit script for the mechanical part, applies six questions column by column and writes a dated report with proposals the owner approves. Use it monthly, when a field is added or redefined, when a panel or report recomputes a metric by hand, or when the owner says a number "makes no sense".
---

# Audit metrics — one question, one scale

Stage: **read, diagnose, propose**. It changes neither the pipeline nor the scripts without the owner's
approval.

## Why it exists

A single "call probability" column mixed fit with channel, two scales (an assumed base rate and, later, a
measured one more than ten times smaller) and values written after the fact; and it did not age. Two separate
reports had re-estimated it by hand and written it down as a caveat, not as a defect — and the agent defended
the column instead of questioning it. The owner noticed when the best-fitting posting ranked below worse
ones. The repository QA could not see it: it validates that data follows the rules, not that a metric
means one thing. The column was split in two ([metrics](../../../docs/metrics.md)). This skill looks for
the same defect everywhere else.

**Not this skill:**
- data that breaks a rule (vocabulary, range, missing field) → repository QA;
- outdated or contradictory documents → `document-audit`.

## Procedure

1. **The mechanical part.**
   ```bash
   python3 scripts/metrics_audit.py                   # inventory, redefinitions, overlaps
   python3 scripts/metrics_audit.py <field> [<field>…]  # steps per fortnight, mix per channel, manual re-estimates
   ```
   Also read the pipeline header (the declared definition of each field) and the board generator (which
   column is sorted, filtered or averaged).

2. **Six questions per metric used to decide** — first what the board sorts or filters by, then what a
   formula uses, then what a report quotes:
   1. **Does it answer one question?** If it mixes two (fit and channel; being read and being contacted),
      it is split.
   2. **Did its scale or definition change over time?** A step in the median per fortnight, a
      `*_reclassified` / `*_retroactive` field, or a "since …" in the header. If so, old rows are labeled by
      scale and never mixed in averages or calibrations.
   3. **Is it comparable across rows?** Same source, same moment. Medians per channel that differ by more
      than 3×, or values captured at different points of the cycle, are not compared without normalizing.
   4. **Does it age while displayed as fixed?** Anything that depends on time (probability, validity,
      waiting) is computed when displayed, never written by hand in the YAML.
   5. **Does anyone recompute it by hand?** A panel, note or report that "re-estimates" or "corrects" the
      number is the strongest alarm: the defect is in the design. **Propose the fix, not a caveat.**
   6. **Does it decide anything?** If no script reads it and no skill uses it, it is surplus — or its use
      is missing. Two metrics with |ρ| ≥ 0.7 probably measure the same thing.

3. **Report** — `facts/reports/metrics-audit-YYYY-MM-DD.md`, with the validity mark used by
   `document-audit`. Per metric: the six answers with evidence (script output, header line, report that
   re-estimates it), a verdict (**healthy / label / split / normalize / compute instead of write /
   retire**) and the concrete proposal (field, script, board column). At the end, the list of what the
   owner decides.

4. **Apply only what was approved.** Each definition change is documented in the pipeline header with its
   date, validated by the QA if it is mechanical, and the board is republished only with the QA green.

## Rules

- **The past is not rewritten to look better.** A value recorded under the old definition is labeled, not
  recomputed in place.
- **Zero invention.** A multiplier or base rate that was not measured is declared as an estimate, with a
  review date.
- **A repeated caveat is a defect.** If two reports explain the same oddity of a number, next time the
  number is fixed.
