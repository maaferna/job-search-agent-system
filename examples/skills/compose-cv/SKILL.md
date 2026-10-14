---
name: compose-cv
description: Composes the CV for one posting — or a new showcase for a career track — from the fragment library, builds it and verifies the PDF. Reads the posting, takes its literal keywords, picks the role family and its recipe, and PROPOSES the headline, the summary, which variant of each role, the order of the experience, the projects, the skills and the credentials; then reports what it changed against the recipe and why, which terms of the posting the CV now covers, and which gaps stay open. The owner decides on that proposal. Use it after a GO at the posting audit, when the owner wants a CV for a specific application, a different emphasis (AI, backend, operations), a reordered experience, the English version of a composition, or a new composition.
---

# Compose a CV — one per posting

Stage: **propose and build**. The output is a compilable `.tex`, a verified PDF and a **composition
report** — not suggestions in prose. Nothing is sent from here: the owner reads the full text next
(`review-application`), and only the owner submits.

**The CV is not written: it is composed.** Facts live in `fragments/`; a composition is a file of about
forty lines that chooses fragments and their order. If you find yourself writing an achievement inside a
composition, stop: that text belongs in `fragments/`, anchored in the master profile.

**Not this skill:** deciding *whether* to apply is `audit-posting`, and it runs first. Checking the result
before sending is `review-application`.

## Required context

- `facts/master-profile.md` — the only allowed source of facts.
- `facts/role-families.md` — the recipe per role family: headline, summary, order of the experience
  fragments, projects, skills, credentials, ATS keywords and known gaps.
- `facts/achievements.md` — achievements already written, and their relative strength.
- `facts/credentials.md` — the publishable credentials and their relevance per track. **The credentials
  block is chosen from here**, never from memory.
- `facts/career-focus.md` — the thesis and keywords of each track.
- `facts/findings.md` — inconsistencies found before, which must **not** be repeated.
- `fragments/` — the fragments available (the sources, never the built PDFs).
- The application folder: `posting.md` (the literal text) and the verdict of `audit-posting`.

## What changes from one posting to another, and what never does

| The agent proposes a change in | Never changes |
|---|---|
| The headline | Dates, employers, job titles |
| The professional summary | Verified metrics |
| Which variant of each role: `.dev` (software side) / `.ops` (operations side) / `.full` / `.compressed` | Degrees and credentials held |
| The order of the experience | Contact details |
| The projects included | That every role is named ([ADR 0007](../../../docs/decisions/0007-every-role-is-named.md)) |
| The skills block and the visible credentials | |
| The PDF title and keywords (metadata an ATS reads) | |

The same fact can be told from two sides — `.dev` and `.ops` are the **same** role, employer, dates and
figures with a different emphasis. Choosing the side is the tailoring; changing the fact is not allowed.

## Procedure

1. **Read the posting and extract its literal keywords** before deciding anything: the terms in its
   responsibilities and requirements, in its own words, each marked *required* or *desirable*. Keep them
   in the posting's words; they are what the coverage check and the gaps list will use.

2. **Pick the role family** with the decision rule in `facts/role-families.md`:
   1. responsibility for people and for a physical process → an operations family;
   2. models, vision, machine learning or inference → an AI family;
   3. APIs, services, architecture, cloud, "developer" → a backend family;
   4. industry and technology mixed (digital transformation of a plant) → the hybrid family, the niche
      with the best fit and the least competition for this profile;
   5. **tie-break:** the family that closes more gaps with what is already verified wins — not the one
      that sounds better.

3. **Take the family's recipe** as the starting point: headline, summary, experience fragments in order,
   projects, skills, credentials. The recipe is a starting point, not a cage. If the posting stresses
   something specific, reorder — and write down the deviation and its reason (step 7).

4. **Create the composition** in `operations/applications/<folder>/cv.tex`, from the template of an
   application folder. A new permanent variant (a showcase) goes to `compositions/` instead. Never delete
   an existing composition; create a new one.

5. **If a fragment is missing,** create it in `fragments/`, anchored in `facts/master-profile.md`, with its
   mirror in the other language when the content can go out in both. If the master profile does not
   support the sentence, **there is no fragment**: it is a gap (step 7).

6. **Build and verify:**
   ```bash
   ./scripts/build_cv.sh operations/applications/<folder>/cv.tex <output-name>
   python3 scripts/ats_coverage.py operations/applications/<folder>/posting.md \
       operations/applications/<folder>/cv.tex compositions/<closest-showcase>.tex
   ```
   The build compiles twice and **fails** above two pages, on a missing glyph or on text that cannot be
   extracted. The coverage script compares the tailored CV with the closest showcase CV
   ([reference implementation](../../../reference/ats_coverage.py)): if the tailored one does not cover
   more of the posting, composing it added nothing.

7. **Report to the owner, in the session,** with the composition report. It is the agent's proposal, in
   five parts. Deviations and open gaps are also written to the application's `analysis.md`, where
   `review-application` reads them. The
   [invented example](../../latex/compositions/applications/2026-10-12-contoso-data-engineer/composition-report.md)
   shows the report as a file:
   - **family and recipe** used, and why that family;
   - **choices** — headline, summary, the variant of each role, order, projects, skills, credentials — each
     with the line of the posting that motivated it;
   - **deviations from the recipe** and their reason;
   - **coverage**: the terms of the posting the CV covers, against the closest showcase;
   - **open gaps**: each missing term in the posting's words, whether it is *required*, and what the
     owner can honestly answer if asked. A gap is never closed by adding the word.

   Then ask. The owner accepts, changes or rejects each choice; the composition is rebuilt with the
   decision, and only then goes to `review-application`.

## Checks when `fragments/` or the preamble change

A change meant to be cosmetic **must** leave the extracted text identical:

```bash
pdftotext -layout <built.pdf> before.txt
# … the change, then rebuild …
pdftotext -layout <built.pdf> after.txt
diff before.txt after.txt     # empty = the refactor did not touch content
```

If the diff is not empty and you expected it to be, do not explain it away: review it. Then run the
repository QA, which finds broken references, orphan fragments, a language changed without the other and
the return of a retired claim.

## Hard rules

1. **Zero invention.** If the posting asks for something the master profile does not have, it is a gap in
   the report; it is not written in the CV.
2. **No facts in a composition.** Only `\input`, order and section headings.
3. **Two pages.** To make room, credentials are cut before achievements, and a role's text is shortened —
   **the role is never removed**. Removing one raises coverage and creates an artificial gap in the
   timeline, which a recruiter reads as a real one.
4. **Language parity.** A fragment changed in one language is changed in the other.
5. **Showcase PDFs are regenerated; sent PDFs never are**
   ([ADR 0006](../../../docs/decisions/0006-sent-documents-are-immutable.md)).
6. **Do not deliver without building.** The verified PDF and the report are the deliverable, not the `.tex`.
7. **The report proposes; the owner decides.** No composition goes to review without the owner having seen
   its choices and its open gaps.
