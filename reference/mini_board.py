#!/usr/bin/env python3
"""A deliberately small board, to show the rendered-board test (reference/render_test.mjs).

    python3 reference/mini_board.py OUT.html       # writes the page
    python3 reference/mini_board.py --expected     # prints, as JSON, what the page MUST show

The private board computes its numbers in JavaScript, in the browser, from data embedded in the page — so
"today" is the reader's today. That is also why validating the data was not enough: for weeks the page
showed things the data did not say (a modality guessed from free text, two different response rates,
duplicated alerts), and every data check was green.

The test that closed the gap computes the same numbers a second time, in Python and without the
JavaScript (`--expected`), opens the page in a headless browser, reads what it SHOWS, and compares. If they
disagree, one of the two is wrong, and the page is not published. Two independent implementations of one
definition — exactly what the shared definitions below are for.
"""
from __future__ import annotations

import datetime as dt
import html
import json
import math
import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
PIPELINE = ROOT / "examples" / "data" / "pipeline.example.yaml"

# Shared definitions. The JavaScript below must implement the same ones; the test proves it does.
LIVE = {"prospect", "invitation", "outreach", "prepared", "sent", "contact", "interview", "offer"}
SENT = {"sent", "contact", "interview", "offer", "rejected", "no_response"}
ANSWERED = {"contact", "interview", "offer"}   # a "response" has ONE definition, used everywhere:
CALLED_EVENTS = {"reply", "interview", "offer"}  # the state says so, or an event in the history does


def as_date(value) -> dt.date:
    """YAML gives dates for 2026-01-10 and strings for "2026-01-10"; compare dates only."""
    return value if isinstance(value, dt.date) else dt.date.fromisoformat(str(value))


def was_answered(e: dict) -> bool:
    """A rejection after an interview was still an answer: the current state alone would hide it."""
    return e["state"] in ANSWERED or bool(CALLED_EVENTS & {h.get("type") for h in e.get("history") or []})


def percent(part: int, whole: int) -> str:
    """Half-up rounding, as JavaScript's Math.round — Python's round() rounds half to even."""
    return f"{math.floor(100 * part / whole + 0.5)}%" if whole else "—"


def load():
    data = yaml.safe_load(PIPELINE.read_text(encoding="utf-8"))
    return data["entries"], data["as_of"]


def expected(entries: list[dict], today: dt.date) -> dict:
    sent = [e for e in entries if e["state"] in SENT]
    answered = [e for e in sent if was_answered(e)]
    due = [e["id"] for e in entries
           if e["state"] in LIVE and e.get("action_date") and as_date(e["action_date"]) <= today]
    return {"live": sum(e["state"] in LIVE for e in entries),
            "sent": len(sent),
            "response_rate": percent(len(answered), len(sent)),
            "discarded": sum(e["state"] == "discarded" for e in entries),
            "due_today": sorted(due)}


JS = r"""
const DATA = __DATA__, TODAY = __TODAY__;
const LIVE = new Set(["prospect","invitation","outreach","prepared","sent","contact","interview","offer"]);
const SENT = new Set(["sent","contact","interview","offer","rejected","no_response"]);
const ANSWERED = new Set(["contact","interview","offer"]);
const CALLED_EVENTS = new Set(["reply","interview","offer"]);
const wasAnswered = e => ANSWERED.has(e.state) || (e.history || []).some(h => CALLED_EVENTS.has(h.type));
const sent = DATA.filter(e => SENT.has(e.state));
const answered = sent.filter(wasAnswered);
const kpi = (k, v) => { document.querySelector(`[data-kpi="${k}"] b`).textContent = v; };
kpi("live", DATA.filter(e => LIVE.has(e.state)).length);
kpi("sent", sent.length);
kpi("response_rate", sent.length ? Math.round(100 * answered.length / sent.length) + "%" : "—");
kpi("discarded", DATA.filter(e => e.state === "discarded").length);
const due = DATA.filter(e => LIVE.has(e.state) && e.action_date && e.action_date <= TODAY);
const list = document.getElementById("due");
for (const e of due) {                       // textContent, never innerHTML: the data is not trusted markup
  const li = document.createElement("li");
  li.dataset.id = e.id;
  li.textContent = `${e.role} · ${e.employer} — ${e.next_action || ""}`;
  list.appendChild(li);
}
"""


def page(entries: list[dict], today: dt.date) -> str:
    data = json.dumps(entries, default=str, ensure_ascii=False).replace("</", "<\\/")
    tiles = "".join(f'<div class="kpi" data-kpi="{k}"><b>…</b><span>{html.escape(label)}</span></div>'
                    for k, label in [("live", "live"), ("sent", "sent"), ("response_rate", "response rate"),
                                     ("discarded", "discarded")])
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mini board</title>
<style>body{{font:15px/1.5 system-ui,sans-serif;margin:24px}}.kpis{{display:flex;gap:12px;flex-wrap:wrap}}
.kpi{{border:1px solid #ccc;border-radius:6px;padding:8px 14px}}.kpi b{{display:block;font-size:24px}}</style>
</head><body><h1>Mini board</h1><p>Invented data · as of {today}</p><div class="kpis">{tiles}</div>
<h2>Due today or overdue</h2><ul id="due"></ul>
<script>{JS.replace("__DATA__", data).replace("__TODAY__", json.dumps(str(today)))}</script></body></html>
"""


def main(argv: list[str]) -> int:
    entries, today = load()
    if argv == ["--expected"]:
        print(json.dumps(expected(entries, today)))
        return 0
    if len(argv) != 1:
        print(__doc__)
        return 2
    pathlib.Path(argv[0]).write_text(page(entries, today), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
