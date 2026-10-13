# CLAUDE.md — template

*The skeleton of the private repository's project instructions (about 35 KB, in Spanish), with the
content replaced by what each section is for. `CLAUDE.md` is what the agent reads at the start of every
session: it is the constitution of the system, and a new session obeys it literally — which is why
[`document-audit`](skills/document-audit/SKILL.md) audits it like a source of facts.*

---

## What this repository is

One paragraph. Not a software project: a decision-support system for a job search. What it holds and
what it produces.

## Your role in this repository

The role the agent plays (for example, a senior recruitment consultant for hybrid profiles), the markets
it must know, and **the candidate's differentiator in one sentence** — the thing every document must make
evident in six seconds of reading.

### Non-negotiable rules

- **Zero invention.** Every achievement, metric, date, technology or responsibility must exist in
  `facts/master-profile.md` or in the fragments. If something is missing, it is **asked**, never filled in.
- **Rephrasing is not fabricating.** Reordering, prioritizing, translating into the sector's language and
  changing emphasis: correct and expected. Adding a number nobody measured: never.
- **A metric beats an adjective.**
- **Speak plainly about weaknesses.** Point at the real risks of the profile (gaps, ambiguous seniority,
  broken links, inconsistent dates); never dress them up.
- **Read the sources, never the PDFs, for content.** Compiled artifacts cost tokens and add nothing.
- **Boundaries.** What the agent never does: submit, send a message, enter a password, solve a CAPTCHA,
  change a state on its own, publish ([agent operating model](../docs/agent-operating-model.md)).
- **Language** of the conversation and of each document.

## Repository structure

The annotated tree: each folder and each script with one line saying what it is and who writes it.
In the private file this is the longest section, because every script and data file has its entry, and
the QA checks that the paths cited here exist.

```
facts/            # layer 1 — the only source of truth
fragments/        # layer 2 — one fact, one file
compositions/     # layer 3 — only \input, order and headings
operations/       # layer 4 — pipeline (decisions), triage (analyses), board (generated)
scripts/          # capture, scoring, gates, generators, QA — one line each
.claude/skills/   # one procedure per recurring task
```

## Build

How to build each composition, where each PDF lands, and the rule that a PDF reaches the "sent" folder
only after the owner approved its current text. The verified-build checks (pages, glyphs, fonts).

## How to change a fact

The fixed order: master profile → fragment → both languages → build → QA. Never the other way around.

## Available skills

A table: skill, what it does, when to use it, what it is **not** for. Kept in sync with the skills folder
by the QA.

## State of the material

Dated. What exists, what is pending, which blockers are open. The section most likely to go stale — so it
carries a date and is reviewed by the document audit.
