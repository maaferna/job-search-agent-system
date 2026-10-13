# Claude Code configuration — example

How the agent is wired into the repository: which commands it may run without asking, which it may never
run, and what runs on its own when a session starts. Paths and script names are translated to the public
folder names ([architecture](../../docs/architecture.md)); in a real checkout the two scripts live in
`scripts/` as `session_start.sh` and `guard_bash.sh`, which is what the settings file points to.

| File | What it is | In the private system? |
|---|---|---|
| [`settings.example.json`](settings.example.json) → `permissions.allow` | build, read-only git: the commands the agent runs every day without a prompt | **yes** |
| [`settings.example.json`](settings.example.json) → `hooks.SessionStart` + [`session_start.example.sh`](session_start.example.sh) | sync, today's capture in the background, presence metrics once a day, a short status | **yes** (rewritten) |
| [`settings.example.json`](settings.example.json) → `permissions.deny` | no `git push`, no edits under `sent/`, no reading of credentials | **proposed** |
| [`settings.example.json`](settings.example.json) → `hooks.PreToolUse` + [`guard_bash.example.sh`](guard_bash.example.sh) | blocks approving a document and touching a sent record from the shell | **proposed** |

## Why the "proposed" rows exist

The private system keeps its boundaries
([what the agent never does](../../docs/agent-operating-model.md#boundaries--what-the-agent-never-does))
through **instructions** — the project's `CLAUDE.md` and each skill's hard rules — and through the owner's
explicit OK in the conversation. That has held in daily use, but it is a policy, not a mechanism. A review of
this repository pointed out the difference: an agent with a shell could, in principle, type the approval
itself. The two proposed rows turn the most important boundaries into something the harness enforces:

- a **deny rule** is evaluated by Claude Code before any tool call, whatever the agent was told;
- a **PreToolUse hook** sees every shell command first, and exit code 2 blocks it with a message the agent
  reads.

The [reference gate](../../reference/gate.py) also refuses an approval that does not come from an
interactive terminal, so a piped `APPROVE` fails even without the hook.

## How a skill is triggered

Each skill's frontmatter has a `description` that says *when* to use it ("use it before sending any
application, when the owner asks whether a CV is ready…"). Claude Code reads those descriptions and loads
the skill when the request matches; the owner can also invoke one by name (`/day`, `/status`). See the
[example skills](../skills/).
