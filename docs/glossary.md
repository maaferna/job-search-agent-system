# Glossary

The terms used across this repository, each with one meaning. Spanish words in the board screenshots are
listed at the end.

## People and roles

| Term | Meaning |
|---|---|
| **Owner** | The candidate: the person who designed the system and uses it for their own search. Approves every document and makes every submission. |
| **Agent** | [Claude Code](https://claude.com/claude-code), working in the repository in a session the owner opened. It proposes; it never sends, approves or closes on its own ([boundaries](agent-operating-model.md#boundaries--what-the-agent-never-does)). |
| **Skill** | A written procedure the agent follows for a recurring task: what to read, which script to run, what not to do ([examples](../examples/skills/)). |
| **Role family** | Data, not a procedure: the recipe to compose a CV for one kind of role, with its ATS keywords and known gaps. A new kind of job is a new family, not a new skill. |

## Documents

| Term | Meaning |
|---|---|
| **Master profile** | The only source of facts about the career: every role, date, metric and credential, with its evidence ([architecture](architecture.md#layer-1--facts)). |
| **Fragment** | A small LaTeX file holding one block (a role, a project, a summary). A fact lives in exactly one fragment. |
| **Composition** | A CV that only selects fragments and orders them. It cannot contain a fact. |
| **Showcase CV** | A general composition for one career track, used when no posting justifies a tailored one. |
| **Tailored CV** | The composition made for one application; also called a *per-application CV*. |
| **Variant** | The same role told from another side (`.dev`, `.ops`) or at another length (`.full`, `.compressed`): same employer, dates and figures. Choosing the variant is part of tailoring; changing a fact is not. |
| **Recipe** | The starting composition of a role family: headline, summary, experience fragments in order, projects, skills, credentials. The agent deviates from it only with a written reason. |
| **Composition report** | What the agent hands the owner with a tailored CV: the family, each choice with the line of the posting behind it, deviations from the recipe, coverage and open gaps ([example](../examples/latex/compositions/applications/2026-10-12-contoso-data-engineer/composition-report.md)). |
| **Retired claim** | A statement removed from the CV on purpose. A list of them is searched in every PDF, source, backup and PDF metadata so none comes back. |
| **Sent document** | The PDF a recruiter actually received. It is a record: never rebuilt or corrected ([ADR 0006](decisions/0006-sent-documents-are-immutable.md)). |

## From posting to submission

| Term | Meaning |
|---|---|
| **Capture / radar** | Collecting postings from public sources, scoring them against written criteria and removing the ones already seen. |
| **Triage** | The agent's written analysis of a posting, with a verdict (*recommended*, *investigate*, *discarded*) and a reason — saved before the owner is asked ([ADR 0003](decisions/0003-triage-separate-from-pipeline.md)). |
| **Pipeline** | One entry per opportunity that was actually worked, moving through a fixed set of [states](state-machine.md). |
| **Posting audit** | The check before composing: **GO**, **NO-GO**, or **DIRECT-CONTACT** when writing to a person beats the form. |
| **Fit** | 0–100, the employer's view: would they pick this candidate? Read in bands A ≥ 75, B 55–74, C < 55 ([metrics](metrics.md#a--fit-0100--the-employers-view)). |
| **Call probability** | The channel's view: will anybody read it? Written once at submission and never edited. |
| **Brier score** | How far the predicted call probabilities were from what happened; it measures calibration. |
| **Coverage** | The share of a posting's relevant terms that appear in the CV. A floor, not a target ([audits](audits.md#coverage-of-the-posting)). |
| **Per-application gate** | The twelve checks (G1–G12) a document must pass before it can be sent; a red check blocks it ([quality controls](quality-controls.md#per-application-gate--12-checks)). |
| **Approval fingerprint** | A hash of the text the owner approved. If the text changes afterwards, the approval no longer matches (G12). |
| **Repository QA** | The 25 blocks of `check.sh` that check the whole repository, not one application. |

## After sending

| Term | Meaning |
|---|---|
| **Portal signal** | What a job board shows about an application ("viewed", "CV downloaded"), recorded with its literal text. It is not a state change. |
| **Response window** | The time in which replies historically arrive, counted from the posting's close. |
| **Own closure** | The owner closes an application after its window expired with no signal (`no_response`). It is reopened if a signal arrives later. |
| **Closed vocabulary** | A field that only accepts listed values (states, channels, who closed and why), validated by a script ([ADR 0005](decisions/0005-closed-vocabularies.md)). |
| **Owner rules** | Decision rules stored as data with the date they became valid; a change reopens the discards made under the old version ([ADR 0004](decisions/0004-dated-owner-rules.md)). |
| **Live discard** | A discard whose posting is still open, so a rule change can still reopen it ([ADR 0004](decisions/0004-dated-owner-rules.md)). |

## This repository

| Term | Meaning |
|---|---|
| **Invented data** | Every name, employer and number shown in examples and screenshots is made up. Employers are the fictional companies of software documentation (Contoso, Fabrikam, Northwind…). |
| **Sanitization gate** | The script that searches every published file — and the visible text of every image — for what must never be published ([how it works](../README.md#how-this-repository-is-kept-clean)). |
| **Manifest** | The text file next to an image with its SHA-256 and its visible text, so an image can be searched ([images](img/README.md)). |
| **Professional network / credentials platform** | The owner's own profile platforms, named generically on purpose. |

## Spanish words in the screenshots

| On screen | Meaning |
|---|---|
| *Hoy · Pipeline · Vivas · Embudo · Presencia* | Today · Pipeline · Live · Funnel · Presence (the board's views) |
| *calce A/B/C* | fit band |
| *triage 1–3* | priority given when the entry was created |
| *P1–P3* | search profile |
| *Por decidir · Preparadas · Contacto enviado · Enviadas · Con respuesta* | to decide · prepared · outreach sent · sent · with a reply |
| *Próxima acción · atrasada* | next action · overdue |
