#!/usr/bin/env python3
"""Every relative link and image in the Markdown files points to a file that exists. Exit 1 otherwise.

External links (http, mailto) are not fetched: CI must not fail because a third-party site is down.
"""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)|<(?:img|source)[^>]+(?:src|srcset)=\"([^\"]+)\"")


def main():
    broken = []
    files = [p for p in ROOT.rglob("*.md") if not {".git", "node_modules"} & set(p.parts)]
    for md in files:
        text = re.sub(r"```.*?```", "", md.read_text(encoding="utf-8"), flags=re.S)   # code blocks are not links
        for m in LINK.finditer(text):
            target = (m.group(1) or m.group(2)).split("#")[0]
            if not target or re.match(r"[a-z]+:", target):
                continue
            if not (md.parent / target).exists():
                broken.append(f"{md.relative_to(ROOT)}: {target}")
    print("\n".join(broken) if broken else f"OK — links in {len(files)} Markdown files resolve")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
