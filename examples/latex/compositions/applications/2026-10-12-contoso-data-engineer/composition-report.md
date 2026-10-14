# Composition report — INVENTED EXAMPLE

**Application:** Contoso Mining (fictional) · Data Engineer · posting of 2026-10-10 ([`posting.md`](posting.md))

**Composition:** [`cv.tex`](cv.tex) · **Written by:** the agent (`compose-cv`) · **Status:** proposal, waiting
for the owner

This is what the agent hands the owner after composing: what it chose, why, what it changed from the
recipe, what the CV now covers and what it cannot cover. The owner accepts, changes or rejects each choice
before the text goes to review. Candidate, employer and posting are invented.

## 1 · Keywords of the posting, in its own words

| Term | Where in the posting | Weight |
|---|---|---|
| data pipelines | responsibilities, requirements | required |
| Python, SQL | requirements | required |
| PostgreSQL, Docker | requirements | required |
| Airflow *or a similar orchestrator* | requirements | required |
| CI (tests and releases) | responsibilities | — |
| sensor and production data, three sites | responsibilities | — |
| site supervisors and planners | responsibilities | — |
| computer vision or image data | requirements | desirable |
| operations or production planning | requirements | desirable |
| English, professional working proficiency | requirements | required |

## 2 · Family and recipe

**Family: data engineering.** The posting asks for pipelines, SQL and data modeling; it mentions neither
models nor inference as the job (decision rule, step 2 of the skill). The AI family was the runner-up because
computer vision is desirable; data engineering wins the tie-break because it closes more gaps with facts
already verified: PostgreSQL and SQL are only in the data fragments.

## 3 · Choices, each with its reason

| Block | Proposed | Instead of | Why — the line of the posting |
|---|---|---|---|
| Headline | `headline/data` — *Data Engineer · Pipelines and Models for Physical Operations* | `headline/ai` | the title of the role, said in the first line a recruiter reads |
| Summary | `summary/ai` | — | see deviation 1 |
| Current role | `example-institute.dev` | `.ops` | "design, build and operate data pipelines"; "package and deploy services with Docker" — the `.dev` variant names the pipeline, Docker and the service |
| Older roles | `example-manufacturing.compressed` | `.full` | keeps both roles named and production planning visible in one block, so the data work leads |
| Skills | `skills/data` first, then `skills/ai` | `skills/ai` alone | PostgreSQL, SQL and CI are required or named in the posting and live only in `skills/data` |
| Projects | `vision-pipeline` only | + `scheduling-optimizer` | "computer vision or image data" is desirable; the optimizer adds nothing this posting asks for |
| PDF metadata | title *Data Engineer*; keywords from section 1 | the showcase's | what an ATS reads before the text |

## 4 · Deviations from the recipe

1. **Summary.** The data-engineering recipe asks for a data summary, and the library has none yet. The
   agent used `summary/ai`, which is true and names Python and Docker, but opens with computer vision.
   **Proposal:** a new fragment `summary/data`, written from the master profile. It is a new fragment, so
   it needs the owner's OK on its text, and it is justified only if a second composition will use it.
2. **One project instead of two,** to keep two pages without shortening a role.

## 5 · Coverage against the showcase CVs

Computed with [`reference/ats_coverage.py`](../../../../../reference/ats_coverage.py) on 16 relevant terms
of the posting:

| CV | Coverage | Missing |
|---|---|---|
| **This composition** | **81 %** | analytics, planners, Airflow, orchestrator |
| AI showcase | 65 % | also PostgreSQL, SQL, CI |
| Operations showcase | 74 % | also computer, vision |

Same facts in all three. The difference is only which fragments were chosen and in what order.

## 6 · Open gaps — declared, not filled

| Term | Required? | Reading | What the owner can honestly say |
|---|---|---|---|
| Airflow / orchestrator | **required** | a real gap: the master profile has a pipeline that feeds three sites, and no orchestrator | "Designed the pipeline that feeds three sites, without a dedicated orchestrator; no experience with Airflow." The word is **not** added to the CV |
| planners | — | the people who use the data. The `.ops` variant says it ("worked with site supervisors… how it is used to plan"); the `.dev` variant does not | see question 2 |
| analytics | — | the name of the team ("Operations Analytics"), not a skill | no action |

## 7 · Questions for the owner

1. Accept data engineering as the family and `headline/data` as the headline?
2. The current role: keep `.dev` (pipeline and Docker in front), or use `.ops`, which names the
   supervisors and planners but loses the service and Docker? The agent proposes `.dev`.
3. Write `summary/data` now (deviation 1), or send with `summary/ai`?
4. Apply with Airflow missing as a required term? The posting audit gave GO with that gap declared; the
   decision is the owner's.
