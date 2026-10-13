# The life of a posting

From the moment a posting is captured to the follow-up after sending. Every step that leads to a
submission passes through a human decision.

```mermaid
flowchart TD
    A[1 · Capture<br/>three capture modes] --> B[2 · Score & dedupe<br/>written criteria]
    B --> C[3 · Triage<br/>agent reads, analysis saved]
    C --> D{4 · Owner<br/>authorizes?}
    D -- no / no answer --> T[(triage keeps<br/>the analysis)]
    D -- yes --> E[5 · Posting audit<br/>GO / NO-GO / DIRECT-CONTACT]
    E -- NO-GO --> X[discarded with reason]
    E -- DIRECT-CONTACT --> K[message drafted;<br/>owner sends it]
    E -- GO --> F[6 · Compose CV<br/>from fragments]
    F --> G[7 · Owner reads the full<br/>text and approves]
    G --> H[8 · Quality gate<br/>G1–G12]
    H -- red --> F
    H -- green --> I[9 · Owner submits]
    I --> J[10 · Follow-up<br/>portal signals, closure rules]
```

## 1 · Capture

Three capture modes, chosen by what each source demands
([ADR 0008](decisions/0008-capture-modes-by-source.md)):

| Mode | Sources | Runs |
|---|---|---|
| **Automatic** | public APIs and unauthenticated search pages; corporate career sites over HTTP | at session start, in the background (a hook) |
| **Headless browser** | corporate career sites that only render with JavaScript | weekly |
| **Assisted** | job boards that require a login or show a CAPTCHA | on demand; a visible browser window waits while the **human** solves the CAPTCHA |

The assisted mode never solves CAPTCHAs: it watches the window and continues when the person has solved
it, with a time limit per page. Rate limits are handled the same way — with pauses, a circuit breaker
and a time budget, never by evading them (see [lessons](lessons.md#rate-limits-are-a-design-input)).

## 2 · Score and deduplicate

Each posting gets a score against a written criteria file: target profiles with weighted terms,
locations, penalties (e.g. shifts outside the home region) and a title-noise pattern. A regression test
protects the scorer: a set of known postings must keep their expected scores after every change.

The score is **triage, not a decision**. A low score does not discard a posting that matches the focus,
and a high score does not justify applying. Postings seen before — in the pipeline or in a previous
report — are not shown again.

## 3 · Triage — the analysis is saved before asking

The agent reads the reported postings, validates each recommended one (is it still open? which
seniority does it really ask for? which hard requirements does the candidate not meet?) and writes an
entry in the triage file **before** asking the owner anything:

```yaml
# Invented example
- key: board:12345
  date: 2026-09-15
  title: Data Engineer
  verdict: discarded          # recommended | investigate | discarded
  reason: "core stack is a cloud warehouse the candidate has never operated; 5 years required"
  data: {years: "5", hard_requirements: "warehouse X", applicants: "", mode: "hybrid", pay: ""}
  promoted_to: ""             # pipeline id, once the owner authorizes
```

Pending analyses reappear at the top of the next report without being re-analyzed
([ADR 0003](decisions/0003-triage-separate-from-pipeline.md)).

## 4 · The owner authorizes, by name

Only the postings the owner authorizes by name enter the pipeline. Nothing enters by default.

## 5 · Posting audit — the gate before composing

Reading a posting is cheap; composing a tailored CV is not. The audit produces a verdict and two
numbers that are never mixed ([metrics](metrics.md)):

- **GO** — in focus, reachable seniority, no missing hard requirement.
- **NO-GO** — with a one-line reason, so the radar never proposes it again.
- **DIRECT-CONTACT** — the content fits but the channel is poor (a mass-apply form, seniority at the
  edge): writing to a person beats the form.

It also asks two questions that were added after real misses:
- *Has this employer already screened the candidate out?* (an employer-history script flags repeated closures
  without a call).
- *Does the posting ask for much less than the candidate has?* Overqualification is a **risk**, not an
  advantage: recruiters assume the candidate will leave.

## 6 · Composition

A per-application composition selects fragments and their order according to a **recipe** for the role
family (13 families, each with its fragments, ATS keywords and known gaps). The composition contains no
facts ([architecture](architecture.md)).

## 7 · Human review of the full text

A preview script prints the CV section by section, marking the origin of each block (library fragment or
text written for this application) and flagging every number. The owner reads it and, only with an
explicit OK, the approval is recorded together with a **fingerprint of the approved text**. If the text
changes afterwards, the approval no longer matches
([ADR 0001](decisions/0001-human-approval-before-send.md)).

## 8 · Quality gate

Twelve checks per application, from unresolved placeholders to the owner's approval fingerprint; a red check
blocks the document ([quality controls](quality-controls.md)).

## 9 · Submission — always by the person

The agent prepares everything; the final click on *send* is always the owner's. Browser work happens
only in a session the owner opened and supervises. Two lessons shaped this step: verify which file the
form will actually attach, and never open an application form "just to read the questions" before the
right CV is loaded ([lessons](lessons.md)).

## 10 · Follow-up

- A weekly read-only review of each job board's "my applications" page records **portal signals** with
  their literal text and a strength level (read < downloaded < advanced; closure = 0). A signal is not a
  state change: the state moves to *contact* only when a person writes or calls.
- Closures are classified by **who** closed the process (job board, employer, or the owner after a
  silence) and **why**, in a closed vocabulary ([state machine](state-machine.md)).
- A process is never closed for silence while its posting is still receiving applications.
