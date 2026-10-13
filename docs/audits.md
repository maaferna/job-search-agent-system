# Audits — what is checked, by whom, and what is not

[Quality controls](quality-controls.md) lists the checks as they run (repository QA, per-application
gate). This page groups the **audits by what they protect**, in three layers: what a machine can verify
alone, what a machine can find but a person has to judge, and what only reading decides. Each one can be traced
to a failure in [lessons](lessons.md).

| Layer | Who | Blocks? |
|---|---|---|
| **1 · ATS mechanics** — can a machine read the document? | scripts | yes |
| **2 · Truth and coherence** — does every line trace to a fact, and do documents agree? | scripts find, a person decides | yes, for unsent documents |
| **3 · Judgment** — will it win the role, and does the language hold? | the agent proposes, the owner reads and approves | the owner's approval is gate G12 |

## Layer 1 · ATS mechanics

An applicant tracking system reads **extracted text**, not the page. A CV that looks perfect can be
unreadable to it, and nobody notices because nobody reads the extracted text.

| Check | What fails | Where |
|---|---|---|
| Pages | more than two | build helper, QA block 8, gate G2 |
| Missing glyphs | a character the font cannot draw is also a character no parser can extract | build helper, QA 8 |
| Unicode map (ToUnicode) | every font must carry one, or the text extracts as garbage | QA 8, G2 |
| Replacement characters | U+FFFD in the extracted text | G2 |
| Contact data extractable | email and links must come out as text, not only as link targets | G2 |
| **Parser extraction** | an external parser must read full date ranges, role · employer, and no "prepared on" date | QA 10 |
| Metadata | PDF title and keywords are read by some ATS — and searched for retired claims too | G4 |
| Freshness | a deliverable older than the sources it uses | QA 9 |

The parser-extraction check came from documents that passed **every** mechanical check — two pages, no
missing glyphs, extractable email — and still could not give a parser the data that matters most in a
filter. When a heading line overflowed, TeX broke it **inside the date**: the parser got "Jan" on one
line and "2020 – Jun 2021" on the next, and could not compute years of experience, the most frequent gap
in the market. Role and employer came out glued together. And a footer with the date the PDF was built put
an expiry date in front of every reader of a CV that circulates for weeks. Three fixes in the template
(an unbreakable box around the date, a separator between role and employer, no build date), and a check
so they never come back.

### Coverage of the posting

A number, not a judgment: the share of the posting's relevant terms that appear in the CV, weighted by
how often the posting repeats them.

- **Relevant terms** = known technical vocabulary + proper nouns and acronyms + words the posting repeats,
  minus filler and **minus the employer's own name** (not repeating the employer's brand is not a gap).
- Only the **literal text of the posting** counts, not the notes written under it.
- Measured on the **sent PDF** when there is one — what the ATS actually received.
- **A floor, not a target.** Below the floor the tailored CV adds nothing over the generic showcase CV,
  which was the only reason to compose it. Above it, more is not better.
- **A missing term is never added unless it is true.** It is a gap: declared, and the interview answer
  prepared. Filling in the word is the one thing that does close doors.

Working version: [`reference/ats_coverage.py`](../reference/ats_coverage.py). On the
[LaTeX example](../examples/latex/) it shows the point of composing: for the same invented posting, the
tailored CV covers 81 %, the AI showcase 65 % and the operations showcase 74 % — and all three miss the
orchestrator the posting asks for, because the candidate does not have it.

## Layer 2 · Truth and coherence

The expensive failure is not a CV a machine cannot read; it is a CV whose line does not hold in the
interview.

| Audit | What it looks for | How |
|---|---|---|
| **Retired claims** | a claim removed on purpose (a figure later re-measured more conservatively, a detail, a name) coming back by copying an old paragraph | a list of retired claims searched in PDF text, sources, `.docx` backups **and** PDF metadata — red before sending, amber after |
| **Date traceability** (G7) | a date range that does not exist in the master profile | script |
| **Fact traceability** | every employer, role, technology, figure and link of a document exists in the master profile | dates by script; the rest read, document by document |
| **Headline vs. family** (G6) | the CV says something other than what the analysis of the posting chose | script |
| **Language parity** | a fragment changed in one language and not in its mirror | QA block 3 |
| **Letter vs. its CV** (G10) | a cover letter claiming what its CV does not support | script for figures and retired claims; read for the rest |
| **Coherence across sent CVs** | every sent CV must be consistent with every other: the same figure is always written the same way, and different emphases never contradict each other | script finds candidates, a person decides |
| **Gaps are real** | a recorded gap that is not actually a requirement of *its* posting | QA block 17 |

### The audit of what was already sent

A sent PDF is a **record**, not a deliverable: it is what a person read. It is never rebuilt or "fixed".
The audit of sent documents therefore does not correct anything; it **prepares**:

1. **Integrity** — the file in the record must be the one that was sent. The first run found several
   application folders where the PDF had been rebuilt after sending, so nobody could say what the
   recruiter had read. Divergences are adjudicated only with citable evidence (the follow-up log, the
   commit), and what cannot be reconstructed is declared as such — never replaced with a plausible file.
2. **What traveled** — for each retired claim found in a sent document: where it is (visible text or
   metadata, which changes the exposure) and the one-sentence answer if it comes up in the interview.

### The audit of what each job board holds

The most expensive errors of the whole search were not in any CV. They were in the **structured data**
each job board keeps about the candidate — degree status, dates, roles, salary field, seniority — which
the board's filters read *before* anyone opens the CV. On one job board a structured field held a wrong
value for one credential, and sixteen applications went out that way; on another, a single profile-wide
field sent the same outdated value with four applications. A checklist
script prints the canonical values; the owner opens each board (the agent never logs in), and each
difference is classified first: **an error in the data** is fixed, **a quirk of how the board displays
it** is left alone.

## Layer 3 · Judgment

| Audit | Question | Who |
|---|---|---|
| **ATS review** ([skill](../examples/skills/ats-review/SKILL.md)) | match table with four verdicts — *solid*, *exists but invisible* (the most profitable fix), *adjacent*, *absent* (never filled in); fit over hard requirements; literal-keyword and parsing risks | the agent, before composing or when a CV gets no replies |
| **Six-second screen** | reading only name, headline, first line, latest role, employers and education: what does a recruiter conclude? | the agent proposes; part of the ATS review and of the pre-send review |
| **Verb intensity** | "led", "designed the architecture", "in production": does the master profile support that **same** intensity? Inflation is not a lie, it is one degree too many | read at the pre-send review |
| **What the cut left out** | a two-page CV always cuts something; is it what the posting asks for? | read at the pre-send review |
| **Owner's approval** (G12) | the owner read the full text and approved it; the fingerprint of the approved text must match the current one | the owner — the only control that is a person by design |

## What is not audited

**Spelling, grammar and style have no automatic check.** No script runs a spell checker or a grammar
checker over the CVs or letters. They depend on three things: the agent writing them, the language parity
of the fragment library (a fragment is written once and reused, so an error is fixed once), and the
owner's reading of the full text before approving it (G12). This is a known gap, written here so the
documentation does not suggest a control that does not exist. The mechanical step that would close it —
running a spell and grammar checker over the **extracted text** of every deliverable, in both languages,
inside the repository QA — has not been built.
