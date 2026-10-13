---
name: ats-review
description: Audits a CV against one specific job posting — keyword match, ATS filter risk and a simulation of a recruiter's six-second screen. A diagnosis, not a rewrite. Use it when the owner pastes a posting and asks whether the CV passes, what it lacks or how well it fits, and to diagnose why a CV gets no replies.
---

# ATS review and recruiter screen

Diagnosis, not rewriting. If the owner wants the CV already adjusted, that is `compose-cv`.

## Required context

Read before giving an opinion:
- `facts/master-profile.md` — what is true of this profile;
- `facts/role-families.md` — the role family, its keywords and its known gaps;
- `facts/findings.md` — problems already found (cite them; do not rediscover them);
- the matching composition and its fragments — **never the PDF** for reading content.

If the owner did not paste the posting, ask for it. Without a posting there is no ATS review, only a
generic opinion, and that is useless.

## Procedure

### 1. Break the posting down

Three lists, separating what the posting **requires** from what it **wishes**:
- **hard requirements** (degree, years, technology, location, language);
- **desirable** items;
- **cultural and context signals** (company size, industry, technical maturity, who the role reports to,
  new role or replacement).

Note also what the posting **does not say** and should: pay band, modality, team size. Silences are
information for the interview.

### 2. Classify the role family

Apply the decision rule of the role families. If the posting mixes industry and technology, say so
explicitly: it is the profile's best-fitting niche.

### 3. Match table

| Posting requirement | In the profile? | Evidence (file / achievement) | Visible in the CV? | Action |
|---|---|---|---|---|

Four verdicts per requirement, and only four:
- **Solid** — exists in the profile and is visible in the CV.
- **Exists but invisible** — it is in the master profile and not in the CV → *the most profitable fix
  of all*: a fragment that says it, chosen by the composition.
- **Adjacent** — something close but not equivalent; say exactly what the difference is.
- **Absent** — it is not there; **it is never filled in**.

### 4. Fit verdict

Percentage of hard requirements met, and one of three recommendations:
- **apply now** (≥ 70 % of hard requirements);
- **apply with a CV adjustment** (50–69 %, or the gaps are "exists but invisible");
- **do not apply / apply only through a person** (< 50 %).

Be direct. Recommending a 30 % fit wastes the owner's weeks.

### 5. ATS risk

On the sources:
- do the posting's keywords appear **literally**? An ATS does not know that a translated term means the
  same thing; if the posting is in English, the CV must be too. The coverage script gives the number
  ([reference implementation](../../../reference/ats_coverage.py));
- does the CV's headline resemble the posting's title?
- parsing risks of **this** template: link text that a parser may drop, a block written as a run-on
  paragraph that fragments badly, two-column layouts that scramble the contact line;
- channels where this CV should **not** go without review: forms that require `.docx`.

### 6. The six-second screen

Simulate the recruiter reading only: name, headline, first line of the summary, most recent role,
employer names, education. Write literally what they would conclude. If that conclusion is not the one
that wins the role, the problem is at the top of the document, not in the details.

## Output

1. **Verdict** — family, % of fit, recommendation (three lines at most).
2. **Match table.**
3. **The three highest-impact fixes**, in order, each with the concrete text to change.
4. **ATS risks.**
5. **What to ask in the interview**, derived from the posting's silences.

No motivational filler. The owner has a long career; speak as a peer.
