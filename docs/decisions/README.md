# Architecture decision records

Short records of the decisions that shaped the system: the context, the decision and its consequences.
Each one was made after a real failure or a real trade-off (see [lessons](../lessons.md)).

| # | Decision |
|---|---|
| [0001](0001-human-approval-before-send.md) | Human approval of the full text before a document can be sent |
| [0002](0002-gates-block.md) | Gates block; exceptions are explicit and recorded |
| [0003](0003-triage-separate-from-pipeline.md) | Triage (analyses) separate from the pipeline (decisions) |
| [0004](0004-dated-owner-rules.md) | Owner rules are dated data, and changes trigger a review of live discards |
| [0005](0005-closed-vocabularies.md) | Closed vocabularies for states, closures, modality and channel |
| [0006](0006-sent-documents-are-immutable.md) | Sent documents are immutable records |
| [0007](0007-every-role-is-named.md) | Every past role is always named; text is shortened, roles are never omitted |
| [0008](0008-capture-modes-by-source.md) | Capture modes chosen by what each source requires |
| [0009](0009-board-published-as-synthetic-screenshots.md) | The board is published only as screenshots of invented data, each covered by a checked manifest |
