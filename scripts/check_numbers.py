#!/usr/bin/env python3
"""Every aggregate number published in the repository must match docs/numbers.yaml.

    python3 scripts/check_numbers.py

The same figures are written in the README (twice, once in Spanish), in docs/metrics.md and on the poster,
and nothing kept them together: a refresh that missed one place would publish two different numbers.
Each check below is a pattern with named groups; a group named after a key of numbers.yaml must hold that
value. A pattern that no longer matches also fails — the sentence changed, so the check must be reviewed
with it. Spaces in a pattern match any run of whitespace. `<key>__es` writes the number in Spanish format (14.800), `<key>__en` in English (14,800) and `<key>__raw` without
separators (an HTML attribute).

The number of decision records is not stored: it is counted in docs/decisions/.
"""
from __future__ import annotations

import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent

# (file, pattern). Patterns are searched in the whole file; every match is checked.
CHECKS = [
    # README
    ("README.md", r"unos (?P<seen__es>[\d.]+) avisos vistos, (?P<triage>\d+) analizados por escrito y "
                  r"(?P<sent>\d+) postulaciones enviadas"),
    ("README.md", r"\*\*Measured on (?P<as_of>[\d-]+)"),
    ("README.md", r"\| Commits \(small, reviewed\) \| (?P<commits>\d+) \|"),
    ("README.md", r"\| Agent skills \(written procedures\) \| (?P<skills>\d+) \|"),
    ("README.md", r"\| Scripts \| (?P<scripts>\d+) \|"),
    ("README.md", r"\| Repository QA blocks \(`check.sh`\) \| (?P<qa_blocks>\d+) \|"),
    ("README.md", r"\| Per-application quality checks \| (?P<gate_checks>\d+) \|"),
    ("README.md", r"\| Unique postings seen from public sources \| ~(?P<seen__en>[\d,]+) \|"),
    ("README.md", r"\| Postings analyzed in writing \(triage\) \| (?P<triage>\d+) \|"),
    ("README.md", r"\| Opportunities recorded in the pipeline \| (?P<pipeline>\d+) \|"),
    ("README.md", r"\| Documents actually sent \| (?P<sent>\d+) \|"),
    ("README.md", r"\| (?P<recommended>\d+) / (?P<recommended_dropped>\d+) \|"),
    ("README.md", r"\| Agent discards the owner reopened \| (?P<discards_reopened>\d+) of (?P<triage_discarded>\d+) \|"),
    ("README.md", r"authorized all (?P<recommended>\d+) of its recommendations; (?P<recommended_sent>\d+) were sent "
                  r"and (?P<recommended_dropped>\d+) were dropped"),
    ("README.md", r"the owner\s+reopened (?P<discards_reopened>\d+) of (?P<triage_discarded>\d+)\."),
    # docs/metrics.md
    ("docs/metrics.md", r"Measured from the private repository on (?P<as_of>[\d-]+)"),
    ("docs/metrics.md", r"\(read only, (?P<as_of>[\d-]+)\)"),
    ("docs/metrics.md", r"\| Commits since the system started \(Aug 2026\) \| (?P<commits>\d+) \|"),
    ("docs/metrics.md", r"\| Agent skills \| (?P<skills>\d+) \|"),
    ("docs/metrics.md", r"\| Scripts \| (?P<scripts>\d+) \|"),
    ("docs/metrics.md", r"\| Repository QA blocks \| (?P<qa_blocks>\d+) \|"),
    ("docs/metrics.md", r"\| Per-application gate checks \| (?P<gate_checks>\d+) \|"),
    ("docs/metrics.md", r"\| LaTeX fragments \| (?P<fragments>\d+) \|"),
    ("docs/metrics.md", r"\| Radar reports \| (?P<radar_reports>\d+) \|"),
    ("docs/metrics.md", r"\| Unique postings seen from public sources \| ~(?P<seen__en>[\d,]+) \|"),
    ("docs/metrics.md", r"\| Postings analyzed in writing \(triage\) \| (?P<triage>\d+) \|"),
    ("docs/metrics.md", r"\| Opportunities in the pipeline \| (?P<pipeline>\d+) \| entries in the pipeline: "
                        r"(?P<pipeline_discarded>\d+) discarded, (?P<pipeline_sent>\d+) sent \(open or closed\), "
                        r"(?P<pipeline_prospects>\d+) prospect"),
    ("docs/metrics.md", r"\| (?P<pipeline_discarded>\d+) \(pipeline\) \+ (?P<triage_discarded>\d+) \(triage\) \|"),
    ("docs/metrics.md", r"\| Documents sent \| (?P<sent>\d+) \| entries with a `sent` date — includes "
                        r"(?P<sent_withdrawn>\d+) later withdrawn"),
    ("docs/metrics.md", r"\| Tailored CV compositions \| (?P<compositions>\d+) \|"),
    ("docs/metrics.md", r"against (?P<sent>\d+) documents sent"),
    ("docs/metrics.md", r"(?P<recommended>\d+) postings recommended .*? the owner authorized all (?P=recommended)"),
    ("docs/metrics.md", r"(?P<recommended_sent>\d+) of the (?P<recommended>\d+) were sent; "
                        r"(?P<recommended_dropped>\d+) were dropped .*?, (?P<recommended_pending>\d+) is pending"),
    ("docs/metrics.md", r"(?P<triage_discarded>\d+) discards with a written reason; the owner reopened "
                        r"(?P<discards_reopened>\d+) \((?P<reopened_pct>[\d.]+) %\)"),
    ("docs/metrics.md", r"(?P<memory_notes>\d+) memory notes"),
    # the rest of the documentation
    ("docs/agent-operating-model.md", r"There are (?P<skills>\d+)\. A \*\*role family\*\* \((?P<role_families>\d+) of them\)"),
    ("docs/posting-lifecycle.md", r"\((?P<role_families>\d+) families,"),
    ("docs/quality-controls.md", r"`check.sh`, (?P<qa_blocks>\d+) blocks"),
    ("docs/quality-controls.md", r"## Repository QA — (?P<qa_blocks>\d+) blocks"),
    ("docs/quality-controls.md", r"## Per-application gate — (?P<gate_checks>\d+) checks"),
    ("docs/glossary.md", r"The (?P<qa_blocks>\d+) blocks of `check.sh`"),
    ("examples/README.md", r"seven of the (?P<skills>\d+) agent skills"),
    ("examples/skills/README.md", r"Seven of the system's (?P<skills>\d+) skills"),
    # the poster
    ("tools/poster.html", r'<div class="num">~(?P<seen__en>[\d,]+)</div>'),
    ("tools/poster.html", r'<div class="num">(?P<triage>\d+)</div><div class="bar" style="height:84px">'),
    ("tools/poster.html", r'<div class="num">(?P<pipeline>\d+)</div><div class="bar" style="height:58px">'),
    ("tools/poster.html", r'<div class="num">(?P<sent>\d+)</div><div class="bar" style="height:24px">'),
    ("tools/poster.html", r"Works through (?P<skills>\d+) written skills"),
    ("tools/poster.html", r"(?P<adrs>\d+) ADRs in the repository"),
    ("tools/poster.html", r'<div class="big">(?P<recommended>\d+) <small>approved by the owner</small></div>'
                          r'<div class="d"[^>]*>(?P<recommended_dropped>\d+) of them'),
    ("tools/poster.html", r'<div class="big">(?P<discards_reopened>\d+) <small>of (?P<triage_discarded>\d+) reopened'),
    # the overview poster
    ("tools/poster-overview.html", r"Claude Code \+ (?P<skills>\d+) skills"),
    ("tools/poster-overview.html", r"(?P<gate_checks>\d+) blocking checks"),
    ("tools/poster-overview.html", r'<span>Postings analyzed</span><b>(?P<triage>\d+)</b>'),
    ("tools/poster-overview.html", r'<span>Documents sent</span><b>(?P<sent>\d+)</b>'),
    ("tools/poster-overview.html", r'<b>(?P<recommended>\d+)<small>/(?P=recommended)</small></b>'),
    ("tools/poster-overview.html", r'Discards reopened</span><b>(?P<discards_reopened>\d+)<small>/(?P<triage_discarded>\d+)</small></b>'),
    ("tools/poster-overview.html", r'<span>Seen</span><div><i data-v="(?P<seen__raw>\d+)">'),
    ("tools/poster-overview.html", r'<span>Analyzed</span><div><i data-v="(?P<triage>\d+)">'),
    ("tools/poster-overview.html", r'<span>Pipeline</span><div><i data-v="(?P<pipeline>\d+)">'),
    ("tools/poster-overview.html", r'<span>Sent</span><div><i data-v="(?P<sent>\d+)">'),
    ("tools/poster-overview.html", r'data-v="(?P<recommended_sent>\d+)"></div><div style="--c:#E8833A" data-v="(?P<recommended_dropped>\d+)"></div>'
                                   r'<div style="--c:#9AA8BA" data-v="(?P<recommended_pending>\d+)">'),
    ("tools/poster-overview.html", r"all (?P<recommended>\d+) were authorized"),
    ("tools/poster-overview.html", r'data-total="(?P<triage_discarded>\d+)" data-part="(?P<discards_reopened>\d+)"'),
    ("tools/poster-overview.html", r"against <b>(?P<sent>\d+) documents sent"),
    # the social card
    ("tools/social-card.html", r'<div class="n">~(?P<seen__en>[\d,]+)</div><div class="l">postings seen'),
    ("tools/social-card.html", r'<div class="n">(?P<triage>\d+)</div><div class="l">analyzed in writing'),
    ("tools/social-card.html", r'<div class="n">(?P<sent>\d+)</div><div class="l">sent, by the human'),
]


def expected_values(numbers: dict) -> dict[str, str]:
    flat = {"as_of": str(numbers["as_of"])}
    for section in ("repository", "funnel", "agent_evaluation"):
        flat.update({k: str(v) for k, v in numbers[section].items()})
    flat["adrs"] = str(len(list((ROOT / "docs" / "decisions").glob("[0-9][0-9][0-9][0-9]-*.md"))))
    ev = numbers["agent_evaluation"]
    flat["reopened_pct"] = f"{100 * ev['discards_reopened'] / numbers['funnel']['triage_discarded']:.1f}"
    return flat


def formatted(value: str, style: str) -> str:
    if not value.isdigit() or style == "raw":
        return value
    en = f"{int(value):,}"
    return en.replace(",", ".") if style == "es" else en


def check(numbers: dict) -> list[str]:
    values = expected_values(numbers)
    problems = []
    for rel, pattern in CHECKS:
        text = (ROOT / rel).read_text(encoding="utf-8")
        # a space in a pattern also matches a line break (and a blockquote's ">"): rewrapping is not a change
        matches = list(re.finditer(pattern.replace(" ", r"(?:\s|>)+"), text, re.S))
        if not matches:
            problems.append(f"{rel}: the sentence this check reads is gone — review it and the check together\n"
                            f"    pattern: {pattern[:110]}")
            continue
        for m in matches:
            line = text.count("\n", 0, m.start()) + 1
            for group, shown in m.groupdict().items():
                key, _, style = group.partition("__")
                want = formatted(values[key], style)
                if shown != want:
                    problems.append(f"{rel}:{line}: {key} says {shown}, docs/numbers.yaml says {want}")
    return problems


def main() -> int:
    numbers = yaml.safe_load((ROOT / "docs" / "numbers.yaml").read_text(encoding="utf-8"))
    problems = check(numbers)
    if problems:
        print("\n".join("✗ " + p for p in problems))
        return 1
    print(f"OK — {len(CHECKS)} published sentences agree with docs/numbers.yaml (as of {numbers['as_of']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
