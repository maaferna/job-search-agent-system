# 0001 · Human approval of the full text before a document can be sent

**Status:** accepted

## Context
Tailored CVs are composed by the agent from a fact library. Even with no invented facts, a composition
can emphasize the wrong thing, keep a sentence the candidate cannot defend in an interview, or carry a
number the candidate no longer stands behind. Automated checks catch mechanics, not judgment.

## Decision
A per-application CV reaches the "sent" folder **only** if the owner has read its full text and approved
it. A preview script prints the CV section by section, marking the origin of each block (library fragment
vs. text written for this application) and flagging every number. The approval is stored with a
**fingerprint of the approved text**. The build helper refuses to copy the PDF to the "sent" folder
without a matching approval; the per-application gate (G12) blocks as well.

## Consequences
- An edit after approval invalidates it: the owner reads again.
- The agent can never approve on the owner's behalf; "approve" requires an explicit OK in the conversation.
- **What the fingerprint protects against, and what it does not.** It protects against *stale* approvals:
  any edit after the owner read the text voids the approval. It is not, by itself, a defense against an
  agent that misbehaves. In the private system that boundary is kept by instructions and by the owner's
  explicit OK — a policy, not a mechanism. The [reference gate](../../reference/gate.py) refuses an approval
  that does not come from an interactive terminal, and the [example settings](../../examples/claude/)
  show the proposed hardening: a deny rule and a hook that block the approval command and any write to a
  sent record, whatever the agent was told.
- It adds a few minutes per application. Since more than ten postings are discarded for every application
  sent, those minutes are a small share of the effort.
