#!/usr/bin/env python3
"""ATS coverage: the share of a posting's relevant terms that appear in a CV, as a reproducible number.

    python3 reference/ats_coverage.py [--root LATEX_ROOT] POSTING.md CV.(tex|pdf|txt) [CV2 …]

    # the example application: its tailored CV against the two showcase CVs
    cd examples/latex && python3 ../../reference/ats_coverage.py \\
        compositions/applications/2026-10-12-contoso-data-engineer/posting.md \\
        compositions/applications/2026-10-12-contoso-data-engineer/cv.tex \\
        compositions/showcase-ai-en.tex compositions/showcase-ops-en.tex

Reference implementation of the coverage check (gate G5, docs/audits.md). A number, not a judgment: it
exists to compare a tailored CV with the generic showcase, and to be crossed with outcomes later.

Relevant terms of the posting = known technical vocabulary
                               + proper nouns and acronyms (capitalized more than once, or all caps)
                               + words repeated two or more times that are not filler,
minus the employer's own name (not repeating the employer's brand is not a gap).

Only the literal text of the posting counts: the section after "## Text…" up to the next "## " heading,
because notes written below it (channel, screening questions) are not requirements.

A .tex CV is read from its sources, with every \\input resolved, so the number can be computed before
building; a .pdf is read with pdftotext, which is what an ATS sees. The private version reads the sent
PDF when there is one.

⚠ A missing term is NOT a word to add. If it is not true of the profile, it is a gap: it is declared,
and the answer is prepared. The floor exists only to tell whether the tailored CV adds anything.
"""
from __future__ import annotations

import collections
import pathlib
import re
import subprocess
import sys
import unicodedata

FLOOR = 40          # below this, the tailored CV adds nothing over the showcase
TECHNICAL = set("""
python sql postgresql postgres mysql docker kubernetes aws azure gcp fastapi django flask api apis git linux
bash ci cd pytorch tensorflow opencv pandas numpy spark airflow kafka redis mongodb llm rag mlops mlflow etl
pipeline pipelines dbt bigquery snowflake tableau excel sap erp typescript javascript react java scala go rust
terraform grafana vision computer nlp ocr automation agile scrum jira lean sigma kpi iot plc scada machine
learning deep ai ml data analytics dashboards backend frontend cloud devops orchestrator english
""".split())
STOP = set("""
a an and are as at be by for from in is it its of on or our the their this to we will with you your
who what which into over under about than then they them can may must should would also more most other
join team looking role responsibilities requirements desirable experience years year work working build
building design operate need needs one two three similar so trust new
""".split())


def fold(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in text if not unicodedata.combining(c))


def forms(word: str) -> set[str]:
    """The word and its likely singulars, so 'pipelines' meets 'pipeline' and 'processes' meets 'process'."""
    out = {word}
    if len(word) > 4 and word.endswith("s") and not word.endswith("ss"):
        out.add(word[:-1])
        if word.endswith("es"):
            out.add(word[:-2])
        if word.endswith("ies"):
            out.add(word[:-3] + "y")
    return out


def tokens(text: str) -> list[str]:
    return [w.strip(".") for w in re.findall(r"[a-z0-9][a-z0-9+#./-]*[a-z0-9+#]|[a-z0-9]", fold(text))
            if len(w.strip(".")) >= 2]


def posting_body(text: str) -> str:
    m = re.search(r"^## Text[^\n]*\n", text, re.M)
    body = text[m.end():] if m else text
    cut = re.search(r"^## ", body, re.M)
    return body[: cut.start()] if cut else body


def posting_terms(text: str, employer: str = "") -> collections.Counter:
    body = re.sub(r"https?://\S+", " ", posting_body(text))
    freq = collections.Counter(tokens(body))
    proper = set()
    for m in re.finditer(r"\b([A-Z][\w+#./-]+|[A-Z0-9]{2,}[+#]?)\b", body):
        if m.group(1).isupper() or body.count(m.group(1)) > 1:
            proper.add(fold(m.group(1)).strip("."))
    brand = {fold(x) for x in re.split(r"\W+", employer) if len(x) > 3}
    relevant = collections.Counter()
    for word, n in freq.items():
        if word in brand or word in STOP or re.fullmatch(r"[\d.,:/+-]+", word):
            continue
        if word in TECHNICAL or word in proper or n >= 2:
            relevant[word] = n
    return relevant


def latex_text(path: pathlib.Path, root: pathlib.Path) -> str:
    """The text of a LaTeX source with every \\input inlined, comments and command names removed."""
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = re.sub(r"(?<!\\)%.*", "", line)
        m = re.search(r"\\input\{([^}]+)\}", line)
        if m:
            target = root / m.group(1)
            out.append(latex_text(target if target.suffix else target.with_suffix(".tex"), root))
            continue
        out.append(line)
    text = "\n".join(out)
    text = re.sub(r"\\(newcommand|hypersetup|documentclass|usepackage|setmainfont)\b.*", " ", text)
    return re.sub(r"\\[a-zA-Z]+\*?|[{}\[\]&]", " ", text)


def cv_text(path: pathlib.Path, root: pathlib.Path) -> str:
    if path.suffix == ".pdf":
        return subprocess.run(["pdftotext", str(path), "-"], check=True, capture_output=True, text=True).stdout
    if path.suffix == ".tex":
        return latex_text(path, root)
    return path.read_text(encoding="utf-8")


def coverage(terms: collections.Counter, cv: str) -> tuple[int, list[str], list[str]]:
    """(percent, present, missing) — weighted by how often the posting repeats each term."""
    have = set().union(*(forms(w) for w in tokens(cv)))
    present = [w for w in terms if forms(w) & have]
    missing = [w for w in terms if not forms(w) & have]
    total = sum(terms.values())
    pct = round(100 * sum(terms[w] for w in present) / total) if total else 0
    return pct, sorted(present), sorted(missing, key=lambda w: (-terms[w], w))


def employer_of(posting: str) -> str:
    m = re.search(r"\*\*Employer:\*\*\s*([^·\n(]+)", posting)
    return m.group(1).strip() if m else ""


def main(argv: list[str]) -> int:
    root = pathlib.Path.cwd()
    if argv[:1] == ["--root"] and len(argv) > 1:
        root, argv = pathlib.Path(argv[1]), argv[2:]
    if len(argv) < 2:
        print(__doc__)
        return 2
    posting = pathlib.Path(argv[0]).read_text(encoding="utf-8")
    terms = posting_terms(posting, employer_of(posting))
    print(f"{len(terms)} relevant terms in the posting (floor {FLOOR} %)")
    for cv in map(pathlib.Path, argv[1:]):
        try:
            text = cv_text(cv, root)
        except FileNotFoundError as missing_file:
            print(f"✗ {missing_file.filename}: not found — \\input paths resolve from the LaTeX root; "
                  "run from examples/latex or pass --root examples/latex")
            return 1
        pct, _, missing = coverage(terms, text)
        flag = "below the floor" if pct < FLOOR else "ok"
        technical = [w for w in missing if w in TECHNICAL][:6]
        print(f"  {pct:3d} %  {flag:15}  {cv}")
        if technical:
            print(f"         missing technical terms: {', '.join(technical)}  (a gap unless true of the profile)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
