# Security and privacy

This repository promises one thing above all: **nothing in it identifies a real person, employer, posting
or amount**, and nothing in it is the owner's personal data beyond the public profile. If you find something
that breaks that promise, it is treated as a security issue.

## What to report

- a name of a person, or of a real company tied to an application, a rejection or a conversation;
- the text, URL or ID of a real job posting, or the name of a specific job board;
- a salary, a rate or any amount tied to a real case;
- personal data of the owner (phone, address, national ID) or of anyone else;
- the same things in an **image** — screenshots and previews are generated from invented data, but an image
  is the hardest place to check;
- a vulnerability in the code (`reference/`, `scripts/`, `tools/`), for example a path that runs something it
  should not.

## How to report

Use **[Report a vulnerability](https://github.com/maaferna/job-search-agent-system/security/advisories/new)**
(the *Security* tab of the repository). The report is private: only the owner sees it.

Please do **not** open a public issue or pull request that quotes the data: that would publish it a second
time. Saying *which file and which line* is enough.

## What happens next

1. The data is removed, and if it reached the published history, the history is rewritten so that it no longer
   exists in any commit.
2. The [sanitization gate](scripts/sanitize_check.py) gets a pattern, a test or a rule that would have caught
   it — the same rule the private system follows: every failure becomes a control
   ([lessons](docs/lessons.md)).
3. You get an answer in the report, usually within a few days. This is a personal project maintained by one
   person, so there is no formal service level.

Thank you for looking carefully.
