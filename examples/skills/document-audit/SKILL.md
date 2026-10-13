---
name: document-audit
description: Global audit of the VALIDITY and CONSISTENCY of the repository's documents (facts, skills, manuals, CLAUDE.md) — which document rules, which dated report has been superseded, which retired statement is still written, which counts disagree and which cited paths no longer exist. Runs the document-validity script for the mechanical part, applies judgment document by document against the master profile and the owner's rules, and writes a dated report with proposals the owner approves before anything is applied. Use it when the owner asks whether the repository is up to date, to find contradictions between documents, or to clean up what is outdated. Monthly.
---

# Document audit — what rules and what was left behind

Stage: **read, contrast, propose**. Nothing is deleted; every change is approved by the owner.

**Not this skill:** the CV and its PDFs (repository QA and the sent-PDF audit); the structured data each
job board holds about the owner (`audit-portal-data`); the profile as a product (`profile-audit`).
This skill audits the **system of documents**: what a new session reads as truth must be true.

## Why it exists

The repository accumulates dated reports — audits, panels, plans — and none of them said whether it was
still valid. One report kept stating two facts about the candidate weeks after the owner had corrected
both; the project instructions described "three variants" of the CV when there were five. Nothing checked
that: the QA only looked at the CV. An agent starting a new session reads all of it literally.

## Document classes (`facts/validity.yaml`)

| Class | What it is | How it is audited |
|---|---|---|
| **source** | current facts (master profile, achievement bank, timeline) | must be current: retired statements, counts, paths |
| **rule** | decision criteria (career focus, goals, radar criteria) | same as a source |
| **instruction** | `CLAUDE.md`, skills, manuals, READMEs | same: a new session obeys them to the letter |
| **record** | series and logs (findings, metrics, owner rules) | keep history on purpose: never corrected, only paths checked |
| **report** | name ending in `-YYYY-MM` or `-YYYY-MM-DD` | **never rewritten: marked.** Only one marked current is audited as a source |

A report's mark goes in its first 25 lines, in one of three forms:

```markdown
> **Validity:** current
> **Validity:** superseded by `facts/<file>` (YYYY-MM-DD) — reason in one line
> **Validity:** historical — reason in one line (done, executed, or kept as a record)
```

## Procedure

1. **Mechanical part.**
   ```bash
   python3 scripts/doc_validity.py               # findings
   python3 scripts/doc_validity.py --inventory   # class and validity of every document
   ```
   The repository QA runs it too, as a warning.

2. **Classify every unmarked report.** Read it whole and decide: **current** (still rules, e.g. a plan in
   progress), **superseded** (a later document replaces it — name it) or **historical** (executed, closed,
   or only records what happened). A report whose conclusions already live in a source is historical even
   if it is still correct. *Current is the exception, not the rule.*

3. **Contrast what rules against the sources of truth**, in this order of authority: master profile →
   owner rules → career focus → the owner's memory notes → the rest. Look for: statements contradicting a
   higher authority; old state presented as current ("pending", "missing" about something already done);
   outdated counts and dates; skill instructions that no longer apply. Each finding: document and line,
   what it says vs. what the source says, and the proposed correction.

4. **Feed the mechanism.** Every retired statement found is added to `facts/validity.yaml › retired` with
   its date and the sentence that replaces it, so the script finds it alone next time. This is the step
   that keeps the problem from piling up again.

5. **Write** `facts/reports/document-audit-YYYY-MM-DD.md`: summary, report classification with the
   proposed mark, contradictions with their correction, counts and paths, and what enters `validity.yaml`.
   The report carries its own validity mark.

6. **Ask the owner** what is applied: everything, by block, or by finding. **Only with approval**: marks are
   set, sources, skills and `CLAUDE.md` are corrected, and the commit message says what was retired.
   At the end the script must report no new findings.

## Hard rules

1. **A report is never rewritten.** It is history and gets a mark. Correcting its content would erase what
   was decided and why.
2. **Zero invention.** If two documents contradict each other and no higher authority settles it, **ask the
   owner**; never pick a version by hypothesis.
3. **Nothing is deleted.** A superseded document stays, with its mark.
4. **Records are not touched**: the history inside them is their function.

## Cadence

Monthly, and every time an owner rule changes: the old wording is added to `validity.yaml › retired`.
