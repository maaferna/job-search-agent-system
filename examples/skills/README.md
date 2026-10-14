# Example skills

Eight of the system's 25 skills, **rewritten in English from the private originals**. A skill is a written
procedure for a recurring task: what to read first, which script to run, what to check, what to write and
— just as important — what *not* to do ([agent operating model](../../docs/agent-operating-model.md)).

| Skill | Private original | Why it was chosen |
|---|---|---|
| [`status`](status/SKILL.md) | `estado` | The opening ritual: read only, one proposed first action |
| [`day`](day/SKILL.md) | `dia` | Orchestration: chains the others and decides nothing on its own |
| [`audit-posting`](audit-posting/SKILL.md) | `auditar-aviso` | The GO / NO-GO gate between recommending and composing |
| [`compose-cv`](compose-cv/SKILL.md) | `adaptar-cv` | The tailoring itself: what the agent proposes for one posting, and what it reports back ([example report](../latex/compositions/applications/2026-10-12-contoso-data-engineer/composition-report.md)) |
| [`ats-review`](ats-review/SKILL.md) | `revision-ats` | The ATS audit: four verdicts per requirement and the six-second screen ([audits](../../docs/audits.md)) |
| [`review-application`](review-application/SKILL.md) | `revisar-postulacion` | The last moment a document can still be fixed |
| [`audit-metrics`](audit-metrics/SKILL.md) | `auditar-metricas` | Audits whether a metric *means* one thing, not whether data follows the rules |
| [`document-audit`](document-audit/SKILL.md) | `auditoria-documental` | Keeps what a new session reads as truth actually true |

## What changed in the rewrite

- **No real case.** The originals explain each rule with the incident that produced it, naming the
  employer and the posting. Here the incidents are told generically; the lessons behind them are in
  [`docs/lessons.md`](../../docs/lessons.md).
- **Translated paths and script names.** The private repository uses Spanish names. These examples use the
  folder names of [`docs/architecture.md`](../../docs/architecture.md): `facts/`, `fragments/`,
  `compositions/`, `operations/`. Where a mechanism has a public reference implementation, the skill
  points to it under [`reference/`](../../reference/).
- **Same structure.** Frontmatter with a description that says *when* to use the skill, a stage
  ("read and verdict", "read only"), a numbered procedure, hard rules, and what the skill is **not** for.

They are examples to read, not a working installation: they refer to files and scripts that only exist
in the private repository.
