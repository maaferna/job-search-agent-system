# Reference implementations

Small, working versions of six mechanisms of the private system, **written from scratch for this
repository**. The private code cannot be published even with its data removed: every rule in it is
explained by a comment that names the real case behind it. These keep the mechanism and drop the case.

The Python scripts use the standard library and PyYAML only; `render_test.mjs` needs Node and Chrome. Each
runs on the [invented example data](../examples/data/).

| Script | Mechanism | Documented in |
|---|---|---|
| [`pipeline_check.py`](pipeline_check.py) | closed vocabularies and rules between fields, read from the [JSON Schema](../examples/schemas/pipeline-entry.schema.json) — the vocabularies are written once | [ADR 0005](../docs/decisions/0005-closed-vocabularies.md) |
| [`dated_rules.py`](dated_rules.py) | live discards that relied on an owner rule that has since changed | [ADR 0004](../docs/decisions/0004-dated-owner-rules.md) |
| [`probability.py`](probability.py) | fit (F/S/R/D, bands), call probability at submission and today, Brier score | [metrics](../docs/metrics.md) |
| [`gate.py`](gate.py) | per-application gate: markers, extractable text, retired claims in text **and** metadata, date traceability, and the human-approval fingerprint | [quality controls](../docs/quality-controls.md), [ADR 0001](../docs/decisions/0001-human-approval-before-send.md) |
| [`ats_coverage.py`](ats_coverage.py) | coverage of a posting's terms by a CV, computed from the LaTeX sources or the PDF — tailored vs. showcase on the [LaTeX example](../examples/latex/) | [audits](../docs/audits.md) |
| [`mini_board.py`](mini_board.py) + [`render_test.mjs`](render_test.mjs) | the rendered-page test: what the page *shows* vs. what a second implementation says it must show | [the board](../docs/board.md) |

```bash
pip install pyyaml
python3 reference/pipeline_check.py                              # ✓ example data valid
python3 reference/dated_rules.py                                 # ! one live discard under a superseded rule
python3 reference/probability.py                                 # live applications: fit, band, probability today
python3 reference/gate.py reference/fixtures/applications/ready      # ✓ passes
python3 reference/gate.py reference/fixtures/applications/blocked    # ✗ six blocks, exit 1
(cd examples/latex && python3 ../../reference/ats_coverage.py \
   compositions/applications/2026-10-12-contoso-data-engineer/posting.md \
   compositions/applications/2026-10-12-contoso-data-engineer/cv.tex compositions/showcase-*.tex)
npm ci && node reference/render_test.mjs                         # needs Chrome
python3 -m unittest discover -s tests -t .                       # all tests
```

## What they leave out

They are the mechanism, not the system. The private versions read PDFs (`pdftotext`, `pdffonts`) instead
of a text file, run all twelve gate checks instead of five, compute the probability bases from the measured
funnel instead of constants, and run over five board views. The probability multipliers here are
illustrative — in the private system they are also judgment, and labeled as such.

Code under the MIT License ([`LICENSE-CODE`](../LICENSE-CODE)); written by the agent under the owner's
direction and review, like the rest of the system.
