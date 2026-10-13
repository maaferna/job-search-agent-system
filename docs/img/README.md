# Images

Every image here is checked by the sanitization gate ([ADR 0009](../decisions/0009-board-published-as-synthetic-screenshots.md)).
An image cannot be searched, so each one is covered by a **manifest**: a `.txt` file next to it that
starts with `# image-manifest`, lists each image with its SHA-256, and holds the image's visible text.

```
# image-manifest
# image: board-today-desktop-light.png sha256=…
# image: board-today-desktop-dark.png sha256=…
# source: invented data (…), rendered by tools/board_screenshots.py
# visible text below

…the text shown in the picture…
```

`scripts/sanitize_check.py` fails when an image has no manifest, when the image changed after its
manifest was written, or when a PNG carries text or EXIF metadata chunks. The manifest's text is searched
like any other file.

## Board screenshots

Generated, never edited by hand:

```bash
python3 tools/board_screenshots.py      # needs the private source (read only), Chrome and Node
./scripts/sanitize_check.sh
```

| Manifest | Images | View |
|---|---|---|
| `board-today.txt` | desktop light, desktop dark, mobile | *Hoy* — conversations with people, actions due, weekly goals |
| `board-pipeline.txt` | desktop light, desktop dark, mobile | *Pipeline* — live opportunities by state |
| `board-funnel.txt` | desktop light, desktop dark (full page), mobile | *Embudo* — funnel, goals, gaps, per-channel table, weekly activity, response windows |
| `board-presence.txt` | desktop light, desktop dark, mobile | *Presencia* — one card per platform, portal signals, profile and posts (generated series) |

## CV previews

```bash
python3 tools/latex_previews.py         # needs lualatex and poppler
```

| Manifest | Image | What it is |
|---|---|---|
| `cv-showcase-ai.txt` | `cv-showcase-ai.png` | page 1 of the invented AI showcase CV |
| `cv-showcase-ops.txt` | `cv-showcase-ops.png` | the same fragment library, operations choices |
| `cv-application.txt` | `cv-application.png` | a per-application composition for an invented posting |

Any other image added to the repository needs a manifest written by hand, and the same review.
