"""Shared by the image tools: strip PNG metadata, gate visible text, write images with their manifest.

Every published image follows the same rule (ADR 0009): its visible text goes through the sanitization
patterns BEFORE anything is written, and it is written next to a manifest holding its SHA-256 and that
text, which scripts/sanitize_check.py verifies on every run.
"""
from __future__ import annotations

import hashlib
import pathlib
import struct
import sys
import zlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import sanitize_check  # noqa: E402

OUT = ROOT / "docs" / "img"


def strip_png(data: bytes) -> bytes:
    """The same PNG without text, EXIF or timestamp chunks."""
    out, pos = [data[:8]], 8
    while pos + 8 <= len(data):
        length, kind = struct.unpack(">I4s", data[pos:pos + 8])
        if kind not in (b"tEXt", b"iTXt", b"zTXt", b"eXIf", b"tIME"):
            out.append(data[pos:pos + 12 + length])
        pos += 12 + length
    result = b"".join(out)
    assert result.endswith(struct.pack(">I", 0) + b"IEND" + struct.pack(">I", zlib.crc32(b"IEND")))
    return result


def gate(texts: dict[str, str]) -> None:
    """Exit without writing anything if any visible text has a hit. `texts`: label → text."""
    patterns, deny_re, _ = sanitize_check.build_patterns()
    hits = []
    for label, text in texts.items():
        hits += sanitize_check.scan_lines(text.splitlines(), patterns, deny_re, f"visible text of '{label}'")
    if hits:
        print("\n".join(hits))
        sys.exit("✗ an image would show something that cannot be published; nothing was written")


def write(manifest: str, images: dict[str, bytes], source: str, text: str, note: str = "") -> None:
    """Write PNGs (metadata stripped) and docs/img/<manifest>.txt covering them."""
    OUT.mkdir(parents=True, exist_ok=True)
    items = []
    for name, data in sorted(images.items()):
        data = strip_png(data)
        (OUT / name).write_bytes(data)
        items.append(f"# image: {name} sha256={hashlib.sha256(data).hexdigest()}")
    body = "\n".join(line.rstrip() for line in text.strip().splitlines() if line.strip())
    (OUT / f"{manifest}.txt").write_text(
        f"{sanitize_check.MANIFEST_HEAD}\n" + "\n".join(items) + f"\n# source: {source}\n"
        + (f"# {note}\n" if note else "") + "# visible text below\n\n" + body + "\n", encoding="utf-8")
