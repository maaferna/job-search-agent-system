#!/usr/bin/env python3
"""Previews of the example CVs: build each composition, render page 1, write PNG + manifest.

    python3 tools/latex_previews.py        # needs lualatex, pdftoppm and pdftotext (poppler)

The compositions in examples/latex/ are invented; the previews show what they produce, so a reader can
compare two showcase variants and a per-application CV built from the same fragments. The PDF text is
gated before any image is written, like every image in the repository (docs/img/README.md).
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import imaging  # noqa: E402

LATEX = ROOT / "examples" / "latex"
# composition → preview name
PREVIEWS = {"compositions/showcase-ai-en.tex": "cv-showcase-ai",
            "compositions/showcase-ops-en.tex": "cv-showcase-ops",
            "compositions/applications/2026-10-12-contoso-data-engineer/cv.tex": "cv-application"}


def pdf_name(tex: str) -> str:
    path = pathlib.Path(tex)
    return (path.parent.name if path.stem == "cv" else path.stem) + ".pdf"


def main() -> int:
    subprocess.run([str(LATEX / "build.sh"), "all"], check=True)
    rendered = {}
    for tex, name in PREVIEWS.items():
        pdf = LATEX / "out" / pdf_name(tex)
        text = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], check=True, capture_output=True,
                              text=True).stdout
        prefix = LATEX / "out" / name
        subprocess.run(["pdftoppm", "-r", "110", "-png", "-f", "1", "-l", "1", "-singlefile", str(pdf),
                        str(prefix)], check=True)
        rendered[name] = (prefix.with_suffix(".png").read_bytes(), text, tex)
    imaging.gate({name: text for name, (_, text, _) in rendered.items()})
    for name, (png, text, tex) in rendered.items():
        imaging.write(name, {f"{name}.png": png}, f"examples/latex/{tex}, built by examples/latex/build.sh "
                      "and rendered by tools/latex_previews.py (invented data)", text)
        print(f"✓ {name}.png + manifest")
    return 0


if __name__ == "__main__":
    sys.exit(main())
