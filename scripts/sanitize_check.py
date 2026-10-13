#!/usr/bin/env python3
"""Sanitization gate for the public repository. Prints OK or the offending lines; exit 1 on any hit.

Three layers:
  1. Static patterns (in this file): currency amounts, emails, national IDs, phone numbers, private paths.
  2. Local denylist (`.sanitize-local.yaml`, never committed): extra patterns such as job-board names,
     plus employer and contact names read READ ONLY from the private source repository. The list lives
     outside git because the list itself would leak what it protects. Without that file (in CI, for
     example) only layer 1 runs, with a warning: the full gate is the one that runs on the owner's machine.
  3. Images: a raster image cannot be searched, so every one must be covered by a text manifest that
     holds the image's SHA-256 and its visible text. The manifest is searched like any other file, the
     hash proves it describes the current image, and PNG / JPEG metadata blocks are rejected.

Never weaken a pattern to make the check pass: fix the text instead.
"""
import hashlib, os, pathlib, re, struct, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOCAL = ROOT / ".sanitize-local.yaml"
SKIP_FILES = {".sanitize-local.yaml"}
TEXT_EXT = {".md", ".txt", ".mmd", ".svg", ".yaml", ".yml", ".json", ".sh", ".py", ".mjs", ".js", ".html", ".css",
            ".tex", ".cls", ".sty", ".log", ".aux", ".fls", ".fdb_latexmk", ".toml", ".cfg", ".ini", ".csv", ".cff"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
SKIP_DIRS = {".git", "node_modules", "__pycache__"}

STATIC = {
    "currency amount": r"(\$\s?\d[\d.,]*\d|\bUSD\s?\d|\bCLP\b|\bUF\s?\d|\d[\d.,]*\s?(?:millones|lucas)\b)",
    "email": r"[\w.+-]+@[\w-]+\.[a-z]{2,}\b",
    "national ID": r"\b\d{1,2}\.?\d{3}\.?\d{3}-[\dkK]\b",
    "phone": r"(?<![\w])\+?56\s?9?\s?\d{4}\s?\d{4}(?![\w])",
    "private path": r"resume_latex/(perfil|postulaciones|credenciales|contenido)/",
}
# Allowed on purpose: the noreply address GitHub uses in commits and examples on reserved domains.
EMAIL_OK = re.compile(r"@(users\.noreply\.github\.com|example\.(com|org|net))\b", re.I)
# Words that also appear inside employer strings ("Confidential company", "Consulting firm"…).
GENERIC = re.compile(r"confidencial|no identificad|reservad|empresa |^empresa$|consultora|estado|"
                     r"oferente|cliente", re.I)
# The only places a local-denylist label is allowed on purpose: (label, file). Narrow by design.
# The owner's name is authorship: the license files, the README's Author section and the citation file.
ALLOWED = {("owner name", "LICENSE"), ("owner name", "LICENSE-CODE"), ("owner name", "README.md"),
           ("owner name", "CITATION.cff")}
MANIFEST_HEAD = "# image-manifest"
MANIFEST_ITEM = re.compile(r"^# image: (\S+) sha256=([0-9a-f]{64})$")


def load_local():
    if not LOCAL.exists():
        return None
    try:
        import yaml
    except ImportError:
        print("! pyyaml missing: local denylist skipped", file=sys.stderr)
        return None
    return yaml.safe_load(LOCAL.read_text(encoding="utf-8")) or {}


def private_names(source, stopwords):
    """Employer and contact names from the private pipeline (read only)."""
    import yaml
    pipe = pathlib.Path(source) / "postulaciones" / "pipeline.yaml"
    if not pipe.exists():
        print(f"! private pipeline not found under {source}: name denylist skipped", file=sys.stderr)
        return []
    stop = {s.lower() for s in stopwords}
    names = set()
    for e in yaml.safe_load(pipe.read_text(encoding="utf-8")) or []:
        for key in ("empresa", "empresa_ref", "persona_contactada"):
            raw = str(e.get(key) or "").split("(")[0]          # what follows "(" is a description
            for part in re.split(r"[—·/,;:]| - | via | vía ", raw):
                part = part.strip(" \"'.)")
                if (len(part) >= 3 and (part[0].isupper() or part[0].isdigit())
                        and not GENERIC.search(part) and part.lower() not in stop):
                    names.add(part)
    return sorted(names, key=len, reverse=True)


def png_metadata(data):
    """Names of PNG chunks that carry text or EXIF (tEXt, iTXt, zTXt, eXIf)."""
    found, pos = [], 8
    while pos + 8 <= len(data):
        length, kind = struct.unpack(">I4s", data[pos:pos + 8])
        if kind in (b"tEXt", b"iTXt", b"zTXt", b"eXIf"):
            found.append(kind.decode())
        pos += 12 + length
    return found


def check_images(files, rel):
    hits, covered = [], {}
    for p in files:
        if p.suffix != ".txt":
            continue
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        if not lines or lines[0].strip() != MANIFEST_HEAD:
            continue
        for line in lines:
            if m := MANIFEST_ITEM.match(line.strip()):
                covered[(p.parent / m.group(1)).resolve()] = (m.group(2), rel(p))
    for p in files:
        if p.suffix.lower() not in IMAGE_EXT:
            continue
        data = p.read_bytes()
        entry = covered.get(p.resolve())
        if not entry:
            hits.append(f"{rel(p)}: [image] no manifest lists it (see docs/img/README.md)")
        elif hashlib.sha256(data).hexdigest() != entry[0]:
            hits.append(f"{rel(p)}: [image] changed since its manifest {entry[1]} was written")
        if p.suffix.lower() == ".png" and (meta := png_metadata(data)):
            hits.append(f"{rel(p)}: [image] metadata chunks {', '.join(meta)}")
        if p.suffix.lower() in (".jpg", ".jpeg") and b"Exif\x00\x00" in data[:65536]:
            hits.append(f"{rel(p)}: [image] EXIF block")
    return hits


def build_patterns(quiet=False):
    """(patterns, deny_re, n_names): static patterns plus the local denylist, if present."""
    patterns = dict(STATIC)
    deny = []
    local = load_local()
    if local is None:
        if not quiet:
            print("! .sanitize-local.yaml not found: only static patterns and images are checked", file=sys.stderr)
    else:
        for label, alts in (local.get("deny_patterns") or {}).items():
            patterns[label] = "(" + "|".join(alts) + ")"
        source = os.environ.get("PRIVATE_SOURCE") or local.get("private_source")
        if source:
            deny = private_names(source, local.get("stopwords") or [])
    deny_re = re.compile(r"\b(" + "|".join(re.escape(n) for n in deny) + r")\b", re.I) if deny else None
    return patterns, deny_re, len(deny)


def scan_lines(lines, patterns, deny_re, where):
    """One hit per offending line and label, as `where:line: [label] text`."""
    hits = []
    for n, line in enumerate(lines, 1):
        for label, pat in patterns.items():
            if (label, where) in ALLOWED:
                continue
            for m in re.finditer(pat, line, re.I):
                if label == "email" and EMAIL_OK.search(m.group(0)):
                    continue
                hits.append(f"{where}:{n}: [{label}] {line.strip()[:120]}")
                break
        if deny_re and (m := deny_re.search(line)):
            hits.append(f"{where}:{n}: [private name: {m.group(0)}] {line.strip()[:120]}")
    return hits


def candidate_files():
    """What can be published: tracked files plus untracked ones git would add (.gitignore respected).
    Outside a git checkout, every file except SKIP_DIRS."""
    try:
        out = subprocess.run(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"], cwd=ROOT,
                             capture_output=True, check=True).stdout.decode()
        return [ROOT / f for f in out.split("\0") if f and (ROOT / f).is_file()]
    except (OSError, subprocess.CalledProcessError):
        return [p for p in ROOT.rglob("*") if p.is_file() and not SKIP_DIRS & set(p.relative_to(ROOT).parts)]


def main():
    def rel(p):
        return str(p.relative_to(ROOT))

    files = [p for p in candidate_files() if rel(p) not in SKIP_FILES]
    patterns, deny_re, n_names = build_patterns()
    hits = []
    # Text files by extension, plus extensionless ones (LICENSE, .gitignore…) unless they look binary.
    texts = [p for p in files if p.suffix in TEXT_EXT or (not p.suffix and b"\0" not in p.read_bytes()[:4096])]
    for p in texts:
        hits += scan_lines(p.read_text(encoding="utf-8", errors="replace").splitlines(), patterns, deny_re, rel(p))
    hits += check_images(files, rel)
    n_img = sum(p.suffix.lower() in IMAGE_EXT for p in files)
    if hits:
        print("\n".join(hits))
        print(f"✗ {len(hits)} hit(s) in {len(texts)} text files and {n_img} images")
        return 1
    print(f"OK — {len(texts)} text files, {n_img} images, {len(patterns)} patterns, "
          f"{n_names} private names checked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
