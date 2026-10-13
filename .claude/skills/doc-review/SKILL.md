---
name: doc-review
description: Editorial review of this repository's documentation before it is published — a Markdown file, a set of files or the current diff. Checks the framing rules of CLAUDE.md (who did what, not a mass-application bot, platforms not named, invented data), that every number and claim is backed by docs/numbers.yaml or docs/metrics.md, the terms of docs/glossary.md, structure and design of the page (one question per section, headings that say something, tables vs. prose, images with alt text), sentence-level clarity, and the Spanish block of the README. Writes a findings table and applies edits only after the owner approves them. Use it before committing any change to text, when the owner asks whether a page reads well, is clear, is ready to publish, or to "improve the writing" or "the design of the README".
---

# Doc review — does the page say the right thing, clearly?

Stage: **read, judge, propose**. The mechanical checks (`make check`) say whether the page is *valid*;
this review says whether it is *good* and *true*. Nothing is edited without the owner's OK.

## What to review

The scope the owner gives; otherwise the changed Markdown in the working tree:

```bash
git diff --name-only HEAD -- '*.md'; git ls-files --others --exclude-standard -- '*.md'
```

Read each file **whole**, not only the diff: a correct sentence can still contradict the paragraph above it.
Also read `CLAUDE.md` (framing and sanitization rules), `docs/glossary.md` and `docs/numbers.yaml` first.

## The checklist, in order of cost if missed

1. **Truth.**
   - Every number comes from `docs/numbers.yaml` or is defined in `docs/metrics.md`. A number that exists in
     neither is a finding, even if it is plausible.
   - Every claim about the private system is something the documentation already supports. "In production",
     "led", "always", "never" are claims: check them like numbers.
   - What is *not* done is not implied (see "What is not audited" in `docs/audits.md`).
2. **Framing** (CLAUDE.md, "Framing rules").
   - Who did what: the owner designed and operates; much of the code was written by the agent under the
     owner's direction and review. Never imply hand-written code, never imply the agent decides.
   - Not a mass-application bot: discards outnumber submissions; the human approves and submits.
   - The owner's own platforms are *professional network* and *credentials platform*; the agent never
     operates the owner's accounts.
   - People: "the owner", "the candidate", they/them — never a guessed pronoun.
3. **Terms.** Each term means what `docs/glossary.md` says. A new term is either added to the glossary (in
   the same change) or replaced with an existing one. Spanish words from the screenshots are translated on
   first use in a page.
4. **Structure and design of the page.**
   - The first paragraph says what the page answers and for whom.
   - One question per section; a heading says something ("Gates block, never warn"), not a category
     ("Notes").
   - Tables for comparisons and lookups, prose for reasons, lists for steps. A table cell that needs two
     sentences belongs in prose.
   - Every image has alt text that describes what it shows, and a caption when it needs a legend.
   - Every page links to where its claims are explained (lessons, ADRs, metrics), and nothing important is
     only in an image.
   - Prose wrapped at about 110 characters; no trailing whitespace; one blank line between blocks.
5. **Clarity, sentence by sentence.**
   - Short sentences; the subject first; one idea per sentence.
   - Concrete over abstract: "a red check stops the document" over "ensures quality".
   - No filler ("very", "really", "in order to", "it is important to note").
   - No marketing words ("revolutionary", "seamless", "cutting-edge"); the numbers do that work.
   - The same thing always has the same name.
6. **The Spanish block** of the README (*Para el lector no técnico*): plain words for a non-technical
   reader, the same numbers as `docs/numbers.yaml` in Spanish format (14.800), and correct accents.

## Output

A table, most serious first:

| # | File:line | Finding | Proposed text |
|---|---|---|---|

Then: what is good and must not be touched (one or two lines), and the question *"Apply all, some (which),
or none?"*. After applying: `make check`, and say which findings were left out and why.

## Rules

- **Never invent to improve a sentence.** If a stronger sentence needs a fact the repository does not hold,
  propose the weaker true one, or ask.
- **Never weaken a check to make text pass** (CLAUDE.md). If `check_numbers.py` fails, the text or
  `docs/numbers.yaml` is wrong, not the check.
- Keep the page's voice: precise, plain, honest about limits. Do not add enthusiasm.
- A finding without a proposed text is not finished.
