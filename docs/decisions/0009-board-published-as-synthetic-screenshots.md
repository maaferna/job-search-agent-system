# 0009 · The board is published only as screenshots of invented data, each covered by a checked manifest

**Status:** accepted

## Context
The board is the most readable view of the system, and the documentation was text only. Publishing it
looked simple: run the generator on invented data and publish the page. A trial did that in a sandbox and
found three problems:

- **The generated HTML leaks even with invented data.** The generator's JavaScript and comments carry
  strings from the private repository — employer names in the comments that explain a rule, job-board
  names in closed vocabularies. None of them is *visible* on the page, but all of them are in the file.
- **The generator is private code** with the same problem in its source: every rule is explained with the
  real case that produced it.
- **An image cannot be searched**, so a screenshot would bypass the sanitization gate. A first capture
  showed the owner's full name in the page header, and the gate did not see it.

## Decision
The board is published **only as PNG screenshots**, produced by `tools/board_screenshots.py`:

1. the generator is copied read only into a temporary sandbox and fed the invented pipeline of
   `examples/data/` (translated to the private schema, dates shifted to today);
2. the owner's name in the header is replaced, and the location map is hidden;
3. the **visible text** of each view goes through the sanitization patterns and the private denylist —
   one hit, and nothing is written;
4. each PNG is written without metadata chunks, next to a **manifest** holding its SHA-256 and its visible
   text; the sanitization gate requires a manifest for every image, checks the hash, and searches the text.

Four views are captured: today, pipeline, funnel and presence. The presence view reads the owner's own
metrics on external platforms, so it is captured only with **generated** series in their place, chosen so
that no alert built from the owner's real history is rendered. Job-board names, the names of the owner's
profile platforms, and a few fixed interface texts that cite real things are replaced on the page by a generic label before capturing; their patterns
live in the local denylist, never in the public code.

## Consequences
- An image is a checked artifact: replacing it without regenerating its manifest fails the gate.
- The screenshots show the interface in Spanish, as it is. Captions explain it.
- Neither the HTML nor a live page (GitHub Pages) is ever published. A public live demo would need a
  generator rewritten from scratch — the same rule as all the code in [`reference/`](../../reference/).
- The owner still reviews every image before publishing: the gate removes the mechanical failures so the
  human attention goes to the picture.
