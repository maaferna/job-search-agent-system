#!/usr/bin/env python3
"""Every relative link and image in the Markdown files points to a file that exists, and every `#anchor`
points to a heading (or an `id`) of its target. Exit 1 otherwise.

External links (http, mailto) are not fetched: CI must not fail because a third-party site is down.
Anchors are computed the way GitHub does: lower case, punctuation dropped, spaces turned into hyphens,
`-1`, `-2`… for repeated headings. Without this, renaming a heading broke links silently.
"""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)|<(?:img|source|a)\b[^>]+(?:src|srcset|href)=\"([^\"]+)\"")
CODE = re.compile(r"```.*?```", re.S)


def slug(heading: str) -> str:
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", heading)          # a link keeps its text
    text = re.sub(r"<[^>]+>", "", text).strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)                              # drops `*`, backticks, punctuation, emoji
    return text.replace(" ", "-")


def anchors(md: pathlib.Path, cache: dict) -> set[str]:
    if md not in cache:
        text = CODE.sub("", md.read_text(encoding="utf-8"))
        seen, found = {}, set()
        for heading in re.findall(r"^#{1,6}\s+(.+?)\s*#*$", text, re.M):
            base = slug(heading)
            n = seen.get(base, 0)
            found.add(base if n == 0 else f"{base}-{n}")
            seen[base] = n + 1
        found |= set(re.findall(r"\b(?:id|name)=\"([^\"]+)\"", text))
        cache[md] = found
    return cache[md]


def main():
    broken, cache = [], {}
    files = [p for p in ROOT.rglob("*.md") if not {".git", "node_modules"} & set(p.parts)]
    for md in files:
        text = CODE.sub("", md.read_text(encoding="utf-8"))   # code blocks are not links
        for m in LINK.finditer(text):
            link = m.group(1) or m.group(2)
            if re.match(r"[a-z]+:", link):
                continue
            path, _, fragment = link.partition("#")
            target = (md.parent / path) if path else md
            if not target.exists():
                broken.append(f"{md.relative_to(ROOT)}: {path}")
            elif fragment and target.suffix == ".md" and fragment not in anchors(target.resolve(), cache):
                broken.append(f"{md.relative_to(ROOT)}: {link} — no such heading")
    print("\n".join(broken) if broken else f"OK — links and anchors in {len(files)} Markdown files resolve")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
