# CLAUDE.md — job-search-agent-system (public documentation repository)

## What this repository is

A **public** repository that describes an agentic decision-support system for managing a job-search
pipeline: how it is designed, which controls it has, which decisions shaped it and what was learned. It
contains **no code copied from the private system and no personal data**. Besides the documentation it
holds:

- `examples/` — invented data, the pipeline JSON Schema, translated skills and prompts, a CLAUDE.md template;
- `reference/` — small implementations of key mechanisms, **written from scratch** here, with tests in `tests/`;
- `docs/img/` — board screenshots and CV previews generated from invented data, and the architecture poster,
  all by `tools/`;
- `scripts/` — the sanitization gate, the link checker and the hook installer.

The private system lives in a sibling folder and is the **read-only source** for this repository.

## The private source — READ ONLY

- Path: `/home/mparraf/myprojects/resume_latex/`
- Allowed: **read** files there to understand the design and to recompute aggregate numbers.
- **Never**: write, edit, commit, regenerate, or run any script that writes in that folder (board
  generator, radar, pipeline, build, `check.sh` with side effects). If a number needs a script there,
  use a read-only invocation or recompute it here from read-only reads.
- Nothing is copied verbatim from there. Everything is **rewritten** here and passes the sanitization
  list below before it is written. This applies to code too: private scripts explain their rules with the
  real cases that produced them, so a mechanism is reimplemented in `reference/`, never copied.
- The one exception is `tools/board_screenshots.py`: it **copies** the board generator into a temporary
  sandbox outside both repositories and runs the copy there (ADR 0009). It never runs anything inside the
  private folder, and neither the copied code nor its HTML ever enters this repository.

## Sanitization — mandatory for every file

**Never** in this repository:
- names of people (recruiters, contacts, colleagues, managers);
- names of real companies or institutions tied to applications, rejections or conversations;
- salaries, rate expectations, market anchors with an identifiable source, any amount with a currency;
- content of real job postings, posting URLs, portal IDs, names of specific job boards;
- personal data of the owner beyond what the public CV already shows (no phone, address, national ID);
- conversations, emails, screenshots, messages;
- content from the private `perfil/`, `postulaciones/`, `credenciales/` or `contenido/` folders.

**Allowed:** folder structure; names of scripts and agent skills and what they do; data schemas with
**invented examples clearly marked as such**; diagrams; decisions and lessons written generically;
aggregate numbers (see `docs/metrics.md`). Invented employers use the fictional companies common in
software documentation (Contoso, Fabrikam, Northwind…), never a real company. The owner's full name appears
only in the license files and the README's Author section.

**Platforms.** The owner's own profile platforms are not named: say *professional network* and
*credentials platform*. The code host and the portfolio may be named. Never describe the agent as
operating the owner's accounts: browser work happens only in a session the owner opened and supervises.

**Images.** A raster image cannot be searched: each one needs a manifest (`docs/img/README.md`) with its
SHA-256 and its visible text. Board screenshots and CV previews are only regenerated with
`tools/board_screenshots.py` and `tools/latex_previews.py`, and the poster only with `tools/poster.py` from
`tools/poster.html` (its numbers must match the README's "Numbers" table); never edited or replaced by hand.
Diagrams stay in Mermaid inside the Markdown, so they can be diffed and searched. The presence
view must keep running on generated series (`tools/presence_fixture.py`), never on the owner's metrics. The owner reviews every image before publishing.

**The local denylist.** `.sanitize-local.yaml` (gitignored; template in `.sanitize-local.example.yaml`)
holds the private-source path, job-board names, the owner's name and the stopwords. It is never committed
and its content is never written into a tracked file: the list would leak what it protects. Without it,
the gate only runs its static patterns — the full gate is the one on the owner's machine.

**Before every commit:** run `scripts/sanitize_check.sh` (it must print `OK`), `python3 scripts/check_links.py`
and `python3 -m unittest discover -s tests -t .`. If the gate finds a hit, fix the text — never weaken the
pattern list to make it pass. `scripts/install_hooks.sh` installs the gate as a pre-commit hook.

## Framing rules (do not drift from these)

1. **Who did what, precisely.** The agent is Claude Code. The owner designed the process, the rules,
   the controls and the data architecture, and operates the system daily. Much of the code was written
   by the agent under the owner's direction and review. Say it this way; never imply hand-written code.
2. **It is not a mass-application bot, and the numbers show it.** It discards far more than it sends,
   no document leaves without human approval, and the human always performs the final submission.
3. **The domain is named, the data is not.** "Job search" is fine. Employers, people, amounts and
   outcomes of specific applications are not.

## Language

English throughout. The README opens with badges, quick links and a **«Para el lector no técnico»** block in Spanish, followed by the English summary, a status line and a table of contents.

## Publishing

Creating the GitHub repository and making it public is the **owner's action** (or explicitly authorized
by the owner). The owner reads the whole repository before publishing.
