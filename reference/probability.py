#!/usr/bin/env python3
"""Fit and call probability: two metrics that are never mixed.

    python3 reference/probability.py              # table of the example's live applications
    python3 reference/probability.py --brier      # calibration of the probability written at submission

Reference implementation of docs/metrics.md.

  · FIT (0–100), the employer's view: F/S/R/D = functions 0–35, seniority 0–25, requirements 0–25,
    differentiator 0–15. Read in bands: A ≥ 75 · B 55–74 · C < 55. No channel, pay, city or stability.
  · CALL PROBABILITY AT SUBMISSION = base(channel) × m(fit band) × m(competition). Written once, before
    the outcome, and never edited: it is what gets calibrated.
  · CALL PROBABILITY TODAY = at submission × m(clock) × m(signal), capped. Never stored: it depends on the
    day it is computed.

⚠ The bases for `board` and `direct` are the ones measured in the first cycle; the others and every
multiplier are JUDGMENT, not data, and are labeled as such. With a dozen outcomes nobody can calibrate
them: the point of writing the probability at submission is that, one day, somebody can.
"""
from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
PIPELINE = ROOT / "examples" / "data" / "pipeline.example.yaml"

LIMITS = (35, 25, 25, 15)                      # F, S, R, D
BASE = {"board": 0.02, "direct": 0.43,         # measured: 1 call in 64 submissions; 3 in 7
        "ats": 0.04, "public_sector": 0.05}    # estimated
M_BAND = {"A": 1.5, "B": 1.0, "C": 0.5}        # judgment
M_COMPETITION = {"low": 1.3, "normal": 1.0, "high": 0.6}   # judgment
M_SIGNAL = {None: 1.0, "Viewed": 1.2, "CV downloaded": 2.0, "In process": 3.0}   # judgment
CAP_TODAY = 0.60
WINDOW_DAYS = 30                               # replies historically arrive within this window
SENT_STATES = {"sent", "contact", "interview", "offer", "rejected", "no_response"}
CALLED_STATES = {"contact", "interview", "offer"}
CALLED_EVENTS = {"reply", "interview", "offer"}


def was_called(e: dict) -> bool:
    """An interview followed by a rejection was still a call: read the history, not only the state."""
    return e["state"] in CALLED_STATES or bool(CALLED_EVENTS & {h.get("type") for h in e.get("history") or []})


def as_date(value) -> dt.date:
    return value if isinstance(value, dt.date) else dt.date.fromisoformat(str(value))


def fit_score(detail: str) -> int:
    """'F/S/R/D' → total, refusing a component above its limit (a 40 in functions is a typo, not a 35)."""
    parts = [int(x) for x in detail.split("/")]
    if len(parts) != 4:
        raise ValueError(f"fit_detail needs four parts: {detail!r}")
    for value, limit, name in zip(parts, LIMITS, "FSRD"):
        if not 0 <= value <= limit:
            raise ValueError(f"{name}={value} outside 0–{limit} in {detail!r}")
    return sum(parts)


def band(fit: int) -> str:
    return "A" if fit >= 75 else "B" if fit >= 55 else "C"


def at_submission(channel: str, fit: int, competition: str = "normal") -> float:
    return BASE[channel] * M_BAND[band(fit)] * M_COMPETITION[competition]


def clock_factor(days_waiting: int, window: int = WINDOW_DAYS) -> float:
    """1 inside the window; then it decays linearly to 0.3 at twice the window, and stays there."""
    if days_waiting <= window:
        return 1.0
    return max(0.3, 1.0 - 0.7 * (days_waiting - window) / window)


def today_probability(p_sent: float, days_waiting: int, signal: str | None = None) -> float:
    return min(CAP_TODAY, p_sent * clock_factor(days_waiting) * M_SIGNAL[signal])


def brier(pairs: list[tuple[float, bool]]) -> float:
    """Mean squared error of probabilities against outcomes (0 = perfect; 0.25 = always saying 50 %)."""
    return sum((p - float(called)) ** 2 for p, called in pairs) / len(pairs)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pipeline", nargs="?", default=PIPELINE, type=pathlib.Path)
    ap.add_argument("--brier", action="store_true")
    args = ap.parse_args(argv)
    data = yaml.safe_load(args.pipeline.read_text(encoding="utf-8"))
    entries = data["entries"] if isinstance(data, dict) else data
    today = (data.get("as_of") if isinstance(data, dict) else None) or dt.date.today()
    sent = [e for e in entries if e.get("state") in SENT_STATES and "call_probability" in e]

    if args.brier:
        # Only entries with an outcome; a closure for pay, location or contract is not a verdict on the
        # profile, so it stays out of the calibration (closure_reason: conditions).
        pairs = [(e["call_probability"] / 100, was_called(e)) for e in sent
                 if (e["state"] != "sent" or was_called(e)) and e.get("closure_reason") != "conditions"]
        if not pairs:
            print("no outcomes yet: nothing to calibrate")
            return 0
        print(f"Brier score over {len(pairs)} outcomes: {brier(pairs):.3f}  (0.25 = a constant 50 %)")
        return 0

    print(f"{'id':6} {'fit':>4} band {'channel':13} {'at sub.':>7} {'waiting':>7} {'today':>6}  signal")
    for e in sorted(sent, key=lambda e: -e["fit"]):
        if e["state"] != "sent":
            continue
        fit = fit_score(e["fit_detail"])
        waiting = (today - as_date(e["sent"])).days
        p_today = today_probability(e["call_probability"] / 100, waiting, e.get("portal_signal"))
        print(f"{e['id']:6} {fit:4d}   {band(fit)}  {e['channel_type']:13} {e['call_probability']:6d}% "
              f"{waiting:6d}d {p_today:6.1%}  {e.get('portal_signal') or '—'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
