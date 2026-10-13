#!/usr/bin/env python3
"""Are there LIVE discards that relied on an owner rule that has since changed?

    python3 reference/dated_rules.py                       # example rules + example pipeline
    python3 reference/dated_rules.py RULES PIPELINE [--today YYYY-MM-DD]

Reference implementation of ADR 0004. Owner rules are data with a `since` date per version; a rule is never
edited in place. When a rule changes, the discards made under the old version do not change by themselves —
in the private system one stayed discarded while its posting was still accepting applications.

An entry is flagged when the three conditions hold:
  1. its state is `discarded`;
  2. the posting is still open: `closes` is today or later (a closed posting can no longer be used);
  3. its `reason` cites a date that falls inside the window of a SUPERSEDED version of a rule — of the rule
     it names, if it names one; of any rule otherwise.

Condition 3 is what keeps the noise down: a discard for content (five years asked, a missing degree) also
cites dates, but they do not fall in the window of an old version of the rule it names.

"Today" defaults to the pipeline's `as_of` when it has one (example data), else the real date.
Exit 0 always: this is a warning to review, not a failure.
"""
from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
RULES = ROOT / "examples" / "data" / "owner-rules.example.yaml"
PIPELINE = ROOT / "examples" / "data" / "pipeline.example.yaml"
DATE = re.compile(r"\b20\d\d-\d\d-\d\d\b")


def superseded_windows(rules: list[dict]) -> dict[str, list[tuple[dt.date, dt.date, str]]]:
    """rule id → [(since, until, wording)] for every version that a later version replaced."""
    out = {}
    for rule in rules:
        versions = sorted(rule["versions"], key=lambda v: v["since"])
        out[rule["id"]] = [(v["since"], nxt["since"], " ".join(v["rule"].split()))
                           for v, nxt in zip(versions, versions[1:])]
    return out


def findings(rules: list[dict], entries: list[dict], today: dt.date) -> list[str]:
    windows = superseded_windows(rules)
    found = []
    for e in entries:
        closes = e.get("closes")
        closes = closes if isinstance(closes, dt.date) or not closes else dt.date.fromisoformat(str(closes))
        if e.get("state") != "discarded" or not closes or closes < today:
            continue
        reason = str(e.get("reason", ""))
        named = [rid for rid in windows if re.search(rf"(?<![\w-]){re.escape(rid)}(?![\w-])", reason)]
        for rid in named or list(windows):
            for cited in (dt.date.fromisoformat(d) for d in DATE.findall(reason)):
                for since, until, wording in windows[rid]:
                    if since <= cited < until:
                        found.append(f"{e['id']} ({e.get('role')}, open until {closes}): discarded on "
                                     f"{cited} under rule '{rid}' as worded since {since} — replaced on {until}. "
                                     f"Old wording: \"{wording}\"")
    return found


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rules", nargs="?", default=RULES, type=pathlib.Path)
    ap.add_argument("pipeline", nargs="?", default=PIPELINE, type=pathlib.Path)
    ap.add_argument("--today", type=dt.date.fromisoformat)
    args = ap.parse_args(argv)
    rules = yaml.safe_load(args.rules.read_text(encoding="utf-8"))["rules"]
    data = yaml.safe_load(args.pipeline.read_text(encoding="utf-8"))
    entries = data["entries"] if isinstance(data, dict) else data
    today = args.today or (data.get("as_of") if isinstance(data, dict) else None) or dt.date.today()
    hits = findings(rules, entries, today)
    if not hits:
        print(f"✓ no live discard relies on a superseded rule (today = {today})")
        return 0
    print(f"! {len(hits)} live discard(s) rely on a superseded rule — review them with the owner:")
    for h in hits:
        print("  ·", h)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
