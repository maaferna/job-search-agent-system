---
name: refresh-numbers
description: Recompute the aggregate numbers this repository publishes, from the private repository in read-only mode, and propagate them — docs/numbers.yaml first, then the README in English and Spanish, docs/metrics.md, the pages the numbers check points to, and the posters and social card, which are regenerated. Shows the owner a before/after table and changes nothing until it is approved. Use it monthly, before announcing the project or a new version, or when the owner asks to "update the numbers", "refresh the metrics" or whether the figures are still current.
---

# Refresh numbers — one source, every place it is published

Stage: **measure (read only), propose, apply after approval**.

## Hard rules

- The private repository (its path is in `CLAUDE.md`) is **read only**. Only commands that read: `git
  rev-list`, `ls`, `wc`, `grep`, `python3 -c` over YAML with `yaml.safe_load`. **Never** run a script of
  the private repository (board generator, radar, `check.sh`, builds): they write.
- Only **aggregates** leave the private repository. No name, employer, posting, date of a single case or
  amount — the same rules as every file here (CLAUDE.md, "Sanitization").
- A number that cannot be recomputed with a read-only command is not updated; report it as stale.

## Procedure

1. **Read the definitions.** `docs/metrics.md` ("Repository numbers" and "Evaluating the agent") says how
   each number is recomputed. `docs/numbers.yaml` lists every key. Each key is measured exactly as defined
   there — if a definition must change, that is a change to `docs/metrics.md`, proposed separately.
2. **Measure**, one read-only command per key, and keep the command next to its result.
3. **Show the owner a table** before writing anything:

   | Key | Published | Measured | Command |
   |---|---|---|---|

   Point out any change that alters a sentence's meaning (for example, a ratio that is no longer "more
   than ten discards per document sent", or a "0.6 %" that becomes "1.1 %").
4. **After approval, apply in this order:**
   1. `docs/numbers.yaml` (and `as_of`);
   2. `python3 scripts/check_numbers.py` — every line it prints is a place to update, in the README (both
      languages: `14.800` in Spanish, `14,800` in English), `docs/metrics.md`, the other pages and the
      poster sources in `tools/`;
   3. sentences whose meaning changed (step 3), with the owner;
   4. `python3 tools/poster.py` — regenerates both posters and the social card; open each PNG and look at it;
   5. `make check`;
   6. an entry in `CHANGELOG.md` (a patch version: "numbers refreshed as of …").
5. **Remind the owner** of what only they can do: upload the new social card (*Settings → Social preview*),
   and update the numbers written on the professional network (project description, posts), which no
   check can see.

## Output

The before/after table, the list of files changed, the result of `make check`, and the reminder of step 5.
