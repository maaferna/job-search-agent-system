# Examples

Material rewritten from the private system so the design can be read in concrete form. **All data here is
invented**; every data file says so in its first line.

| Folder / file | What it is |
|---|---|
| [`data/pipeline.example.yaml`](data/pipeline.example.yaml) | 37 invented opportunities in the public schema. Employer names are the fictional companies commonly used in software documentation. It feeds the [board screenshots](../docs/board.md) and the [reference code](../reference/) tests |
| [`data/triage.example.yaml`](data/triage.example.yaml) | the triage file: analyses saved before asking ([ADR 0003](../docs/decisions/0003-triage-separate-from-pipeline.md)) |
| [`data/owner-rules.example.yaml`](data/owner-rules.example.yaml) | the owner's rules as dated, versioned data ([ADR 0004](../docs/decisions/0004-dated-owner-rules.md)) |
| [`data/goals.example.yaml`](data/goals.example.yaml) | weekly goals read by the funnel metrics |
| [`schemas/pipeline-entry.schema.json`](schemas/pipeline-entry.schema.json) | JSON Schema of a pipeline entry: closed vocabularies as enums, and the rules between fields ([ADR 0005](../docs/decisions/0005-closed-vocabularies.md)) |
| [`skills/`](skills/) | seven of the 25 agent skills, translated and without real cases |
| [`prompts/`](prompts/) | prompts for a small local model, with their measured reliability |
| [`latex/`](latex/) | a working fragment library and three compositions: how one set of facts becomes several CVs |
| [`claude/`](claude/) | the Claude Code settings: permissions, the session-start hook, and a proposed guard that makes two boundaries impossible instead of forbidden |
| [`CLAUDE.template.md`](CLAUDE.template.md) | the skeleton of the project instructions the agent reads every session |

The schema and the example data are checked against each other by
[`reference/pipeline_check.py`](../reference/pipeline_check.py), which runs in CI.
