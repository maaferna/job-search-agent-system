#!/usr/bin/env bash
# PreToolUse hook for Bash — blocks the commands the agent must never run, whatever its instructions say.
# Claude Code passes the tool call as JSON on stdin; exit code 2 blocks it and stderr is shown to the agent.
#
# Proposed hardening (see README): the private system relies on the agent's instructions and on the owner's
# explicit OK for these; this hook makes two of them impossible instead of forbidden.
command=$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("tool_input",{}).get("command",""))')

case "$command" in
  *--approve*)
    echo "Blocked: approving a document is the owner's act, at their own terminal (ADR 0001)." >&2; exit 2 ;;
  *"/sent/"*)
    case "$command" in
      *" cat "*|cat\ *|*pdftotext*|*pdfinfo*|ls\ *) exit 0 ;;          # reading a sent record is fine
    esac
    echo "Blocked: a sent document is an immutable record (ADR 0006)." >&2; exit 2 ;;
esac
exit 0
