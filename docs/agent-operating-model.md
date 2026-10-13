# How the agent works

The agent is **Claude Code**, running in the repository with the owner present. It does not run
unattended: a session starts when the owner opens it, and every action with consequences outside the
repository waits for the owner.

## Skills are procedures, role families are data

A **skill** is a written procedure for a recurring task: what to read first, which script to run, which
checks to apply, what to write and what *not* to do. There are 25. A **role family** (13 of them) is data:
the recipe to compose a CV for that kind of role, its ATS keywords and its known gaps.

The rule that keeps the number of skills small: *a new kind of job is a new family, not a new skill.*

Seven of them, translated and without real cases, are in [`examples/skills/`](../examples/skills/), next to a
template of the project instructions the agent reads every session
([`examples/CLAUDE.template.md`](../examples/CLAUDE.template.md)).

| Group | Skills (translated names) |
|---|---|
| Daily operation | `day` (the whole daily procedure in one command), `status` (opening ritual, read only), `radar-full`, `radar-daily` |
| From posting to submission | `apply`, `audit-posting` (the GO / NO-GO gate), `analyze-role`, `compose-cv`, `review-application` (the gate), `ats-review`, `cover-letter`, `estimate-salary`, `portal-content` |
| Channels | `direct-contact` (draft a message to the person who decides; the owner sends it) |
| Follow-up | `review-portals`, `audit-portal-data`, `audit-sent-pdfs`, `interview-prep` |
| Presence | `review-presence`, `review-professional-network`, `review-credentials` (the owner's own profiles) |
| System health | `audit-metrics`, `document-audit`, `profile-audit`, `career-positioning` |

The `day` skill only orchestrates: it calls the others in order and decides nothing on its own. It was
created when the owner noticed they were describing the same steps by hand every morning.

## Rules with a date

The owner's decision rules ("a category of roles accepted only in the home city", "contracts shorter
than six months: no", "rotating shifts outside the home region: always no") live in
a YAML file, each with the **date it became valid** and the reason. Two consequences:

- the agent applies the rule that was valid when a decision was made, and can say so;
- when a rule changes, a script lists the discards that are still "live" and relied on the previous
  version, so they are reviewed instead of silently staying discarded
  ([ADR 0004](decisions/0004-dated-owner-rules.md)).

## Memory

Corrections and preferences the owner gives during a session ("never ask me to open the form to see the
questions before the CV is loaded", "a distant city is not worth it for a long shot") are stored as short
memory notes with the reason and how to apply them. The repository records *what* is true; the memory
records *how the owner wants the work done*. Facts never live in memory: they live in the master profile.

## Hooks

Hooks are commands the Claude Code harness runs on events ([example configuration](../examples/claude/)). At
session start a hook synchronizes the repository, launches the automatic capture in the background if there is
no report for today, captures technical-presence metrics once a day, and prints a short status: pipeline
counts, overdue follow-ups, latest radar, days since the last portal review.

## Boundaries — what the agent never does

| Never | Instead |
|---|---|
| Submit an application | prepares everything; the owner always clicks *send* |
| Send a message on the owner's behalf | drafts it; the owner sends it |
| Enter passwords or solve CAPTCHAs | the owner logs in or solves them; the agent waits |
| Invent a fact, a metric or a date | reports a gap, or asks |
| Write a fact inside a composition | edits the fragment, or proposes a new one |
| Change the state of an opportunity on its own | proposes the change; the owner confirms |
| Publish a page or change a public profile without authorization | prepares the content and asks |

Browser work happens only in a session the owner opened and supervises, and it is **read only** by
default: reading application statuses, reading postings, reading the owner's own profile metrics. Each
write action (filling a form field, editing a profile) is authorized separately — and the final
submission is never one of them.

## Without credits

The mechanical half of the system — capture, scoring, gates, board, QA — is plain Python and shell and
runs without the agent. A small local model (run with Ollama) covers some reading tasks with tested
prompts. The agent is needed for judgment: reading a posting against the profile, composing, reviewing. The
prompts and their measured reliability: [`examples/prompts/`](../examples/prompts/).
