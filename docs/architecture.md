# Architecture

The system started as "a CV in LaTeX" and grew into four layers with a single rule: **dependencies flow
one way**. Facts feed fragments, fragments feed compositions, and operations read from all three but
never write back into the facts.

```
facts/            LAYER 1 — the only source of truth about the career
fragments/        LAYER 2 — LaTeX blocks; a fact lives in exactly ONE file
compositions/     LAYER 3 — showcase CVs and per-application CVs: only \input, order and headings
operations/       LAYER 4 — pipeline (decisions), triage (analyses), board (generated), radar reports
scripts/          capture, scoring, gates, generators, QA
.claude/skills/   the agent's written procedures (one per recurring task)
```

*(Folder names are translated and simplified; the private repository uses Spanish names.)*

## Layer 1 — Facts

- **Master profile.** Every role, date, metric, tool and credential, each with its evidence and the date
  it was confirmed by the owner. Corrections are written with the date and the reason ("this said X
  until date D; the owner corrected it because…"), so the history of a fact is never lost.
- **Owner rules, dated.** Decision rules (which roles to discard, minimum conditions, relocation limits,
  minimum contract length…) are stored as data with a **`since` date**. When a rule changes,
  a script finds the *live* discards that were justified by the old version (see
  [ADR 0004](decisions/0004-dated-owner-rules.md)).
- **Employer registry.** One record per employer with a closed taxonomy (relationship to physical
  operations, size, scope, stability). It is filled when an opportunity is analyzed and validated by a
  script.

**Rule zero: no invention.** If a posting asks for something that is not in the facts, it is reported
as a gap. It is never written into a document. A CV with an invented number fails in the technical
interview, and the system is designed so that inventing one takes deliberate effort.

## Layer 2 — Fragments

A fragment is a small LaTeX file: one role, one project, one skills block, one summary. Variants of the
same role exist when the *emphasis* changes, not the facts:

| Suffix | Meaning |
|---|---|
| `.dev` | the role told from the software / AI side |
| `.ops` | the same role told from the operations side |
| `.full` | expanded to bullets |
| `.compressed` | several older roles collapsed into one block |

Two rules keep the library honest:

1. **A fragment is justified when two compositions use it.** A one-off sentence lives in the
   composition until it repeats, then it is promoted.
2. **Language parity.** Every fragment that can appear in English has a mirror, and a QA block fails if
   one side changes without the other.

## Layer 3 — Compositions

A composition is ~40 lines: preamble, `\input` of fragments, section headings. It **cannot** contain a fact. A
compiling, invented example of both layers: [`examples/latex/`](../examples/latex/). The same fragment set
produces five showcase CVs (three tracks in Spanish, two of them also in English) and one tailored CV per
application.

Each application folder holds: the posting text, a written analysis (family of role, gaps, risks), the
composition, a follow-up log and — only after human approval — the frozen PDF that was sent.

Build rules enforced by the build helper:
- maximum two pages;
- no missing glyphs (a glyph an ATS cannot extract is a silent failure);
- fonts embedded with a Unicode map, so text extraction works for every parser;
- the PDF reaches the "sent" folder **only** if the owner approved the current text
  ([ADR 0001](decisions/0001-human-approval-before-send.md)).

## Layer 4 — Operations

| Artifact | Holds | Written by |
|---|---|---|
| Pipeline (YAML) | **decisions**: one entry per opportunity that was worked, with state, channel, dates, reason for closure | the agent, after the owner decides |
| Triage (YAML) | **analyses**: verdict and reason for every posting read in depth, even if nobody decides | the agent, before asking the owner |
| Radar reports | what was captured on a given day, scored and deduplicated | capture scripts |
| Board (HTML + CSV) | a generated view: today, pipeline, live, funnel, presence | a generator; **never edited by hand** |

The split between pipeline and triage is deliberate
([ADR 0003](decisions/0003-triage-separate-from-pipeline.md)): an analysis must survive even when the
authorization question goes unanswered.

## Why one-way dependencies

The alternative — editing the CV directly for each application — was the starting point, and it
produced the problems this design removes:

- the same fact written in five places, four of them stale;
- a claim retired from one CV reappearing in the next one;
- no way to answer "what exactly did we tell employer X?".

With one-way dependencies a fact is corrected once, a retired claim is caught by a text search over the
generated PDFs, and the sent PDF is an immutable record that git can verify
([ADR 0006](decisions/0006-sent-documents-are-immutable.md)).
