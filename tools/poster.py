#!/usr/bin/env python3
"""Architecture poster and social card: render each page, gate its text, write PNG + manifest.

    python3 tools/poster.py        # needs Chrome and Node (npm ci)

The poster is the one-page view of the system used outside the code host (the project image on the
professional network); the social card is the picture shown when the repository link is shared (it is
uploaded by hand in the repository settings). Both hold only aggregate numbers, which must match
docs/numbers.yaml (scripts/check_numbers.py). Like every image in the repository, their visible text is gated
before the PNG is written (docs/img/README.md).
"""
from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import imaging  # noqa: E402

# image name → (source page, CSS width, CSS height, device scale, what it is)
PAGES = {
    "poster-architecture": ("poster.html", 1240, 1754, 2, "A4 architecture poster"),
    "social-card": ("social-card.html", 1280, 640, 1, "social preview card"),
}


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="poster-") as tmp:
        out = pathlib.Path(tmp)
        for name, (source, width, height, scale, _) in PAGES.items():
            subprocess.run(["node", str(ROOT / "tools" / "poster.mjs"), str(ROOT / "tools" / source), str(out),
                            name, str(width), str(height), str(scale)], check=True, cwd=ROOT)
        texts = {name: (out / f"{name}.txt").read_text(encoding="utf-8") for name in PAGES}
        imaging.gate(texts)
        for name, (source, *_, what) in PAGES.items():
            imaging.write(name, {f"{name}.png": (out / f"{name}.png").read_bytes()},
                          f"tools/{source}, rendered by tools/poster.py ({what}; aggregate numbers only)",
                          texts[name])
            print(f"✓ {name}.png + manifest")
    return 0


if __name__ == "__main__":
    sys.exit(main())
