---
name: review-application
description: Quality gate of one application BEFORE it is sent. Runs the per-application gate on its folder — unresolved markers, pages and ATS readability, retired claims in text and metadata, coverage of the posting against its floor, headline vs. the chosen role family, date traceability, live links, pipeline completeness, the cover letter against its CV, and the owner's approval fingerprint — and then reviews by hand what no machine decides: whether every sentence holds in an interview, whether the CV answers the posting's hard requirement, and whether the cut left out what weighed most. Use it before sending any application, when the owner asks whether a CV is ready, and after fixing a fragment that was already used.
---

# Review an application before sending it

This is the only moment the document can still be fixed. After submission the PDF is an immutable record
([ADR 0006](../../../docs/decisions/0006-sent-documents-are-immutable.md)) and all that is left is
preparing the interview.

## 1. The mechanical gate

```bash
python3 scripts/gate.py operations/applications/<folder>
python3 scripts/gate.py operations/applications/<folder> --links     # if the CV cites repositories or credentials
python3 scripts/gate.py --all                                        # every prepared application
```

It exits non-zero if anything blocks. **Nothing is sent with an open block.** The checks and the reason
each exists are in [quality controls](../../../docs/quality-controls.md); a minimal version is in
[`reference/gate.py`](../../../reference/gate.py).

Two nuances before arguing with the result:

- **Amber is not a permission.** "Technical terms of the posting missing" is the last chance to improve
  the CV. But if the term is not true of the profile **it is not added**: it is a gap, it is declared, and
  the answer is prepared. Filling in the word is the one thing that does close doors.
- **ATS coverage has a floor, not a target.** Below the floor, the tailored CV adds nothing over the
  generic showcase CV, which was the only reason to compose it.

## 2. What requires reading

With `posting.md`, `analysis.md` and the PDF open:

- **The hard requirement.** `analysis.md` lists the gaps. Check that the CV **answers the requirement
  marked as required** when the profile meets it, and does not simulate it when it does not. If it is not
  met, the application can still go — the owner decides — but the honest assessment comes first.
- **The six-second screen.** Read only the headline, the first line of the summary and the first role.
  Does a recruiter of *this* posting understand in six seconds why this candidate? If the answer is in the
  second block, the order is wrong and can still be changed.
- **What the cut left out.** A two-page CV always cuts something. Check against `analysis.md` that what was
  cut is not exactly what the posting asks for. It is the most expensive error and the least visible.
- **The cover letter, if any**, against its own CV and the master profile. A letter cannot claim what its
  CV does not support, nor attribute to the candidate a decision nobody made. The two measured traps:
  turning "worked alongside" into "replaced", and presenting as one's own merit something never decided.
- **The verbs.** "Led", "directed", "designed the architecture", "in production". Each must hold in
  `facts/master-profile.md` with that same intensity. This is where inflation slips in, because it is not
  a lie: it is one degree too many.

## 3. If something does not trace

Two paths, and only two:

1. **It is true and not recorded** → it is added to `facts/master-profile.md` with its source and the date
   the owner confirmed it. Nothing is recorded without asking the owner.
2. **It cannot be supported** → it is fixed in `fragments/`, rebuilt, and the gate runs again.

Not a path: letting it through because it sounds reasonable.

## Hard rules

1. **Nothing leaves with the gate red.**
2. **Fixes go to `fragments/`, never to the application's composition.** A composition only selects and
   orders; a fact written there is lost for every other application.
3. **A missing term of the posting is never invented.** It is declared as a gap.
4. **If the application was already sent, the gate blocks on purpose.** That PDF is not touched: a
   correction is a new version, noted in the follow-up log.
