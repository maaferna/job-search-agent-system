# 0008 · Capture modes chosen by what each source requires

**Status:** accepted

## Context
Sources differ: some expose public APIs, some render only with JavaScript, some require a login or show a
CAPTCHA, and some rate-limit. A single scraper either missed sources or would have needed to evade
protections — which is not acceptable.

## Decision
Three modes, run together and sifted into **one** report with cross-source deduplication:
- **Automatic** — public APIs and unauthenticated pages over HTTP; launched in the background at session
  start.
- **Headless browser** — career sites that need JavaScript; weekly cadence.
- **Assisted** — sources behind a login or a CAPTCHA; a visible browser window is opened and the **human**
  logs in or solves the CAPTCHA; the script waits (with a time limit per page) and skips what is not
  resolved.

Rate limits are respected: pauses with jitter, honoring `Retry-After`, a circuit breaker and a time budget
per source.

## Consequences
- No protection is bypassed; the human stays in the loop exactly where a source asks for a human.
- Coverage is not exhaustive by design; the owner's own finds are added and verified the same way.
