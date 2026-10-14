# Quality controls

Checks run in three places. Some exist because something went wrong without them, others were designed
before any failure; [the lessons map](lessons.md#which-failure-produced-which-control) shows which is
which. The same checks grouped by what they protect — ATS mechanics, truth, judgment — and what is *not*
checked: [audits](audits.md).

| Layer | Runs | Blocks |
|---|---|---|
| **Repository QA** (`check.sh`, 25 blocks) | before every batch of applications and after any change to the fragments | the whole repository: exit code 1 on any failure |
| **Per-application gate** (12 checks) | before a document is sent | that application |
| **Rendered-board test** | inside the repository QA | publishing the board page |

## Repository QA — 25 blocks

Grouped by what they protect:

**Document integrity**
1. Every `\input` points to a file that exists.
2. Orphan fragments — written and used by no composition.
3. Language parity — a fragment changed in one language must change in the other.
4. Retired claims must not reappear — searched in the **text extracted from the PDFs**, not the source.
   A claim removed on purpose (a figure later re-measured more conservatively, a hardware detail, a project
   name) is easy to bring back by copying an old paragraph; the script does not forget what a person
   forgets.
5. Retired claims in the **sources** too (a clean PDF built from a dirty `.tex` is a time bomb), and in
   the `.docx` backups that are also sent.
6. Placeholders — a letter with `[[ ]]` is not sent.
7. Contact data lives in one file only.
8. Deliverables: page count, missing glyphs, Unicode map present for every font (ATS extractability).
9. Deliverables are newer than the sources they use.
10. Parser extraction: an external parser must read full date ranges and role · employer from every
    showcase PDF, and find no build date in the footer ([why](audits.md#layer-1--ats-mechanics)).

**Operations data**
11. Pipeline: every application folder has an entry and vice versa; states, dates and vocabularies valid.
12. Rendered board: a headless browser opens the generated page on desktop and mobile and compares what
    it **shows** with what the pipeline says (KPIs, rates, "today" list without duplicates, modality,
    channel). **The page is not republished with this check in red.**
13. Triage: every analyzed posting is saved until a decision exists.
14. Fit score and call probability are two separate metrics with their own scales ([metrics](metrics.md)).
15. Radar scoring regression cases (location, gendered titles, the remote-role exception).
16. Owner rules: are there live discards that relied on a rule that has since changed?
17. Gaps: is each recorded gap really a requirement of *its* posting?
18. Employer registry: valid taxonomy and a record for every active process.
19. Sent PDFs: integrity of the record, ATS mechanics and coverage of the posting.
20. Prepared applications: the per-application gate passes before sending.

**Presence and documents**
21–23. Profile-metrics files of three external platforms are valid and recent.
24. Technical presence capture (repository traffic, portfolio visits) is valid and recent.
25. Document validity: reports without a validity mark, superseded statements still written, counts that
    no longer match, broken paths in the documentation and the agent's procedures.

## Per-application gate — 12 checks

| | Check | Why it exists |
|---|---|---|
| G1 | Structure and unresolved markers | a composition with a placeholder or an analysis with "ASK" left unresolved |
| G2 | Mechanics and ATS reading | pages, Unicode map, extractable contact data, replacement characters, density |
| G3 | Immutability | if the application was already sent, its PDF is a record and is never regenerated ([ADR 0006](decisions/0006-sent-documents-are-immutable.md)) |
| G4 | Retired claims, in text **and** metadata | red, because it can still be fixed before sending ([lesson](lessons.md#a-retired-claim-traveled-again)) |
| G5 | Coverage of the posting | threshold, and which technical term of the posting is missing |
| G6 | Headline vs. role family | the composed CV must say what the analysis chose |
| G7 | Date traceability | every date range in the PDF must exist in the master profile |
| G8 | Links | every URL in the PDF answers |
| G9 | Pipeline entry complete | family, profile, channel, URL, call probability, gaps, salary expectation |
| G10 | Cover letter vs. its CV | pages, retired claims, numbers the CV does not support |
| G11 | Salary expectation | declared, and contrasted with the dated market anchors |
| G12 | Human review | the owner read the full text and approved it; the approval fingerprint matches the current text ([ADR 0001](decisions/0001-human-approval-before-send.md)) |

The gate is written for the common case (an application to a published posting). For atypical cases — a
direct request from a contact, for example — some checks do not apply. Those exceptions are written down
in the application's analysis; the gate is never edited to turn green
([ADR 0002](decisions/0002-gates-block.md)).

## No check decides whether a line holds in an interview

No script decides whether a sentence will hold in an interview. The procedure for reviewing an
application ends with a manual reading of exactly that question: *can the candidate defend every line?*
The checks remove the mechanical failures so that the human attention goes there.

## Run a minimal gate

[`reference/gate.py`](../reference/gate.py) implements G1, G2, G4, G7 and G12 over two invented
applications — one ready, one that is blocked six times across four checks — and
[`reference/render_test.mjs`](../reference/render_test.mjs)
is a small working version of the rendered-board test. What the real board looks like:
[the board](board.md).
