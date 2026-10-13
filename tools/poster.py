#!/usr/bin/env python3
"""Architecture poster: render tools/poster.html, gate its text, write PNG + manifest.

    python3 tools/poster.py        # needs Chrome and Node (npm ci)

The poster is the one-page view of the system used outside the code host (it is the project image on the
professional network). It holds only aggregate numbers, which must match the README's "Numbers" table.
Like every image in the repository, its visible text is gated before the PNG is written
(docs/img/README.md).
"""
from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import imaging  # noqa: E402

SOURCE = ROOT / "tools" / "poster.html"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="poster-") as tmp:
        out = pathlib.Path(tmp)
        subprocess.run(["node", str(ROOT / "tools" / "poster.mjs"), str(SOURCE), str(out)], check=True, cwd=ROOT)
        text = (out / "poster.txt").read_text(encoding="utf-8")
        imaging.gate({"poster-architecture": text})
        imaging.write("poster-architecture", {"poster-architecture.png": (out / "poster.png").read_bytes()},
                      "tools/poster.html, rendered by tools/poster.py (aggregate numbers only)", text)
    print("✓ poster-architecture.png + manifest")
    return 0


if __name__ == "__main__":
    sys.exit(main())
