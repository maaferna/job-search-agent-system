#!/usr/bin/env python3
"""Per-application quality gate — a minimal version of five of the twelve checks.

    python3 reference/gate.py reference/fixtures/applications/ready      # exit 0
    python3 reference/gate.py reference/fixtures/applications/blocked    # exit 1, one line per block
    python3 reference/gate.py <folder> --approve                         # the human step of G12

Reference implementation of docs/quality-controls.md. It runs at the only moment a document can still be
fixed: between building it and sending it. An application folder holds:

    cv.txt          text extracted from the built PDF (the private gate extracts it itself with pdftotext)
    metadata.json   the PDF's document properties (title, subject, keywords…)
    analysis.md     the written analysis of the posting
    approval.json   {"sha256": …, "approved_on": …} — written only by --approve

and the facts folder holds `retired-claims.yaml` and `date-ranges.yaml`.

  G1   unresolved markers    a `[[placeholder]]` in the CV, or an `ASK:` left open in the analysis
  G2   extractable text      an ATS reads text, not glyphs: U+FFFD means a character it cannot read
  G4   retired claims        searched in the text AND in the metadata, where nobody looks
  G7   date traceability     every date range in the CV exists in the master profile
  G12  human review          the owner read the full text and approved it; the fingerprint of the
                             approved text must match the CURRENT text, so any later edit voids it
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import re
import sys
import unicodedata

import yaml

ROOT = pathlib.Path(__file__).resolve().parent
FACTS = ROOT / "fixtures" / "facts"
MONTH = r"(?:[A-Za-z]{3,9}\.?\s+)?"                 # "Mar 2019", "March 2019" or just "2019"
RANGE = re.compile(rf"\b{MONTH}((?:19|20)\d\d)\s*[–—-]\s*{MONTH}((?:19|20)\d\d|present|now|current)\b", re.I)
OPEN = {"present", "now", "current"}


def fold(text: str) -> str:
    """Lowercase, no accents, single spaces: 'Lideré  equipos' and 'lidere equipos' are the same claim."""
    text = unicodedata.normalize("NFKD", text.lower())
    return " ".join("".join(c for c in text if not unicodedata.combining(c)).split())


def fingerprint(text: str) -> str:
    return hashlib.sha256(" ".join(text.split()).encode("utf-8")).hexdigest()


def run(folder: pathlib.Path, facts: pathlib.Path) -> list[tuple[str, str]]:
    """[(check, problem)] — empty means the application may be sent."""
    cv = (folder / "cv.txt").read_text(encoding="utf-8")
    analysis = (folder / "analysis.md").read_text(encoding="utf-8") if (folder / "analysis.md").exists() else ""
    meta_file = folder / "metadata.json"
    metadata = json.loads(meta_file.read_text(encoding="utf-8")) if meta_file.exists() else {}
    retired = yaml.safe_load((facts / "retired-claims.yaml").read_text(encoding="utf-8"))
    ranges = yaml.safe_load((facts / "date-ranges.yaml").read_text(encoding="utf-8"))
    blocks = []

    for m in re.finditer(r"\[\[[^\]]*\]\]", cv):
        blocks.append(("G1", f"placeholder left in the CV: {m.group(0)}"))
    for line in analysis.splitlines():
        if line.strip().startswith("ASK:"):
            blocks.append(("G1", f"open question in the analysis: {line.strip()}"))

    if "\ufffd" in cv:
        blocks.append(("G2", f"{cv.count(chr(0xFFFD))} unreadable character(s) (U+FFFD) in the extracted text"))
    if len(cv.split()) < 50:
        blocks.append(("G2", "almost no extractable text: the PDF may be an image"))

    places = {"text": fold(cv), **{f"metadata '{k}'": fold(str(v)) for k, v in metadata.items()}}
    for claim in retired:
        pattern = re.compile(rf"(?<!\w){re.escape(fold(claim['claim']))}(?!\w)")
        for where, text in places.items():
            if pattern.search(text):
                blocks.append(("G4", f"retired claim in {where}: \"{claim['claim']}\" "
                                     f"(retired {claim['retired_on']}: {claim['why']})"))

    def norm(end: str) -> str:
        return "present" if end.lower() in OPEN else end.lower()

    known = {(str(r["from"]), norm(str(r["to"]))) for r in ranges}
    for start, end in RANGE.findall(cv):
        if (start, norm(end)) not in known:
            blocks.append(("G7", f"date range {start}–{end} does not exist in the master profile"))

    approval_file = folder / "approval.json"
    if not approval_file.exists():
        blocks.append(("G12", "the owner has not approved this text (run with --approve)"))
    elif json.loads(approval_file.read_text(encoding="utf-8"))["sha256"] != fingerprint(cv):
        blocks.append(("G12", "the text changed after the owner approved it: the approval is void"))
    return blocks


def approve(folder: pathlib.Path) -> int:
    """Show the WHOLE text and record its fingerprint only if the human types APPROVE."""
    if not sys.stdin.isatty():
        # A pipe or a script cannot approve: the owner types it, at a terminal, after reading.
        print("✗ approval needs an interactive terminal; it cannot be piped or scripted")
        return 1
    cv = (folder / "cv.txt").read_text(encoding="utf-8")
    print(cv)
    print("─" * 72)
    if input("Read every line above? Type APPROVE to record the fingerprint: ").strip() != "APPROVE":
        print("not approved")
        return 1
    (folder / "approval.json").write_text(json.dumps(
        {"sha256": fingerprint(cv), "approved_on": dt.date.today().isoformat()}, indent=2) + "\n")
    print("✓ approval recorded; any later edit of the text voids it")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder", type=pathlib.Path)
    ap.add_argument("--facts", type=pathlib.Path, default=FACTS)
    ap.add_argument("--approve", action="store_true", help="show the full text and record the owner's approval")
    args = ap.parse_args(argv)
    if args.approve:
        return approve(args.folder)
    blocks = run(args.folder, args.facts)
    for check, problem in blocks:
        print(f"✗ {check}  {problem}")
    if blocks:
        print(f"BLOCKED — {len(blocks)} problem(s). Nothing is sent with the gate red.")
        return 1
    print(f"✓ {args.folder.name}: G1 G2 G4 G7 G12 pass")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
