#!/usr/bin/env bash
# SessionStart hook — runs when a Claude Code session opens or resumes in the repository.
# Rewritten from the private version. Budget: ≤ 10 s, always `exit 0`, ≤ 40 lines of output (whatever it
# prints enters the agent's context, so it is a status, not a log).
#
# It does four things, and only four:
#   1. fast-forwards from the remote (if the branches diverged it says so and touches nothing);
#   2. if there is no capture report for today, launches the capture IN THE BACKGROUND and moves on;
#   3. once a day, captures the presence metrics in the background (some platforms keep them for days only);
#   4. prints a short status and the opening question.
# It does NOT: call an LLM, write to the pipeline, open a browser, publish anything.
set -u
cd "$(dirname "$0")/.." || exit 0
mkdir -p .build
TODAY="$(date +%F)"

if timeout 8 git fetch --quiet origin main 2>/dev/null; then
  if git merge-base --is-ancestor HEAD origin/main 2>/dev/null; then
    git merge --ff-only --quiet origin/main 2>/dev/null && echo "git: up to date with origin/main"
  elif ! git merge-base --is-ancestor origin/main HEAD 2>/dev/null; then
    echo "git: branches diverged — resolve by hand (git pull --rebase)"
  fi
else
  echo "git: no network; not synchronized"
fi

if ls "operations/radar/reports/$TODAY"*.json >/dev/null 2>&1; then
  echo "Radar: today's report already captured"
else
  setsid nohup python3 scripts/daily_capture.py > .build/capture.log 2>&1 < /dev/null &
  echo "Radar: today's capture launched in the background (pid $!). When it ends: /radar-daily"
fi

if [ ! -f ".build/presence-$TODAY.ok" ]; then
  setsid nohup sh -c "python3 scripts/presence.py --capture > .build/presence.log 2>&1 && touch .build/presence-$TODAY.ok" \
    < /dev/null > /dev/null 2>&1 &
fi

python3 scripts/status.py --short 2>/dev/null || echo "status.py --short failed"
echo "Opening question: who did you write to yesterday, and what did they answer?"
exit 0
