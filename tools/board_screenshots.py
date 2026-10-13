#!/usr/bin/env python3
"""Screenshots of the private board, rendered from INVENTED data, safe to publish.

    python3 tools/board_screenshots.py              # writes docs/img/board-*.png and their manifests
    python3 tools/board_screenshots.py --keep       # keeps the temporary sandbox to inspect it

Why it works this way (ADR 0009). The board generator is private code, and its generated HTML embeds
strings from the private repository in its JavaScript even when the data is invented, so neither the
code nor the HTML is published. What is published is a picture of a page built from invented data:

  1. the generator and its three helpers are COPIED (read only) from the private source into a temporary
     sandbox; they resolve every path from their own location, so they write only inside the sandbox;
  2. the invented pipeline in examples/data/ (public schema, English) is translated to the private schema
     and its dates are shifted to today, so the "today" alerts mean something;
  3. the owner's name in the page header becomes "Demo owner", and the presence view gets invented series
     (tools/presence_fixture.py) instead of the owner's metrics on external platforms;
  4. a headless browser opens each published view, hides the location map, replaces job-board names with
     a generic label (the patterns come from the local denylist, never from this file), and extracts the
     VISIBLE text;
  5. that text goes through the same patterns and denylist as scripts/sanitize_check.py: one hit and
     nothing is written;
  6. only then the PNGs are written (metadata chunks stripped) with a manifest per view holding the
     SHA-256 of each image and its visible text, which the sanitization gate checks on every run.

The private source is never written: nothing here runs inside it, and nothing is imported from it except
the browser driver (playwright-core), loaded from its node_modules if this repository has none.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import sanitize_check  # noqa: E402

sys.path.insert(0, str(ROOT / "tools"))
import imaging  # noqa: E402
import presence_fixture  # noqa: E402

EXAMPLE = ROOT / "examples" / "data" / "pipeline.example.yaml"
GOALS = ROOT / "examples" / "data" / "goals.example.yaml"
# The board and what it imports, including the three loaders of the presence view.
GENERATOR = ["tablero.py", "embudo.py", "probabilidad.py", "triage.py",
             "linkedin_metricas.py", "credly_metricas.py", "presencia_tecnica.py"]

# Views that are published ("vivas" repeats the pipeline). The presence view is captured only because its
# data is replaced by invented series; with real data it would never be.
VIEWS = {"hoy": "today", "pipeline": "pipeline", "embudo": "funnel", "presencia": "presence"}
# Local-denylist labels whose matches are replaced on the page by a generic label before capturing.
REDACT = {"job-board URL or name": "job board"}

# ── Public schema (docs/state-machine.md) → private schema. The private field names are Spanish. ──
FIELDS = {"id": "id", "employer": "empresa", "role": "cargo", "family": "familia", "profile": "perfil",
          "state": "estado", "priority": "prioridad", "url": "url", "modality": "modalidad",
          "published": "publicado", "sent": "enviado", "next_action": "proxima_accion",
          "action_date": "fecha_accion", "reason": "motivo", "closed_by": "cierre_origen",
          "closure_reason": "motivo_cierre", "channel_type": "canal_tipo", "submitted_via": "portal",
          "fit": "calce", "fit_detail": "calce_detalle", "call_probability": "prob_llamada",
          "gaps": "brechas", "direct_contact": "contacto_directo", "portal_signal": "senal_portal",
          "signal_date": "senal_fecha", "history": "historial",
          "closes": "vence"}
VALUES = {
    "estado": {"prospect": "prospecto", "invitation": "invitacion", "outreach": "contactado",
               "prepared": "preparada", "sent": "enviada", "contact": "contacto", "interview": "entrevista",
               "offer": "oferta", "rejected": "rechazada", "no_response": "sin_respuesta",
               "discarded": "descartada"},
    "modalidad": {"onsite": "presencial", "hybrid": "hibrido", "remote": "remoto",
                  "unresolved": "sin_resolver", "not_stated": "no_informada"},
    "cierre_origen": {"board": "portal", "employer": "empresa", "own": "propio"},
    "motivo_cierre": {"generic_board": "generico_portal", "with_feedback": "con_feedback",
                      "other_candidate": "otro_candidato", "conditions": "condiciones",
                      "posting_down": "aviso_caido", "silence": "silencio"},
    "canal_tipo": {"board": "portal", "ats": "ats", "public_sector": "estado", "direct": "directo"},
    # Only the generic channels of the private closed vocabulary: no job board is ever named.
    "portal": {"company_site": "Portal corporativo", "email": "Correo directo",
               "agency_site": "Sitio de consultora", "other": "Otro"},
    "senal_portal": {"Viewed": "Visto", "CV downloaded": "CV descargado", "In process": "En proceso"},
}
EVENTS = {"connection": "conexion", "reply": "respuesta", "interview": "entrevista", "offer": "oferta",
          "rejection": "rechazo"}


def private_source() -> pathlib.Path:
    local = sanitize_check.load_local() or {}
    src = os.environ.get("PRIVATE_SOURCE") or local.get("private_source")
    if not src or not pathlib.Path(src, "scripts", "tablero.py").exists():
        sys.exit("✗ private source not found: set PRIVATE_SOURCE or private_source in .sanitize-local.yaml")
    return pathlib.Path(src)


def shift(value, days):
    return value + dt.timedelta(days=days) if isinstance(value, dt.date) else value


def translate(example: dict, today: dt.date) -> list[dict]:
    """Public example → private pipeline entries, with every date moved by (today − as_of)."""
    days = (today - example["as_of"]).days
    out = []
    for e in example["entries"]:
        x = {}
        for key, value in e.items():
            if key not in FIELDS:
                sys.exit(f"✗ {e['id']}: field '{key}' has no translation in FIELDS")
            target = FIELDS[key]
            if key == "history":
                value = [{"fecha": shift(ev["date"], days), "tipo": EVENTS[ev["type"]]} for ev in value]
            elif target in VALUES:
                if value not in VALUES[target]:
                    sys.exit(f"✗ {e['id']}: {key}='{value}' is outside the closed vocabulary")
                value = VALUES[target][value]
            x[target] = shift(value, days)
        out.append(x)
    return out


def goals() -> dict:
    g = yaml.safe_load(GOALS.read_text(encoding="utf-8"))
    w = g["weekly"]
    return {"vigencia_desde": g["valid_since"], "latencia_max_dias": g["latency_max_days"],
            "plazo_respuesta_default_dias": g["response_window_default_days"],
            "semanal": {"envios_min": w["submissions_min"], "envios_max": w["submissions_max"],
                        "envios_directos_min": w["direct_contacts_min"]}}


def build_sandbox(src: pathlib.Path, sandbox: pathlib.Path, today: dt.date) -> pathlib.Path:
    (sandbox / "scripts").mkdir(parents=True)
    (sandbox / "postulaciones" / "busqueda").mkdir(parents=True)
    (sandbox / "perfil").mkdir()
    for name in GENERATOR:
        shutil.copy2(src / "scripts" / name, sandbox / "scripts" / name)
    board = sandbox / "scripts" / "tablero.py"
    code = board.read_text(encoding="utf-8")
    # The page header is the only line that STARTS with this div; the others live inside JS templates.
    code, n = re.subn(r'^(<div class="sub">)[^<·$]+·', r"\1Demo owner ·", code, count=1, flags=re.M)
    if n != 1:
        sys.exit("✗ the page header changed in the private generator: update the owner-name replacement")
    board.write_text(code, encoding="utf-8")
    example = yaml.safe_load(EXAMPLE.read_text(encoding="utf-8"))
    (sandbox / "postulaciones" / "pipeline.yaml").write_text(
        "# invented data, generated by tools/board_screenshots.py\n"
        + yaml.safe_dump(translate(example, today), allow_unicode=True, sort_keys=False), encoding="utf-8")
    (sandbox / "postulaciones" / "README.md").write_text("<!-- pipeline:inicio -->\n<!-- pipeline:fin -->\n")
    (sandbox / "perfil" / "metas.yaml").write_text(yaml.safe_dump(goals(), sort_keys=False), encoding="utf-8")
    presence_fixture.write(sandbox / "perfil", today)
    run = subprocess.run([sys.executable, str(board)], cwd=sandbox, capture_output=True, text=True)
    if run.returncode:
        sys.exit("✗ the generator failed on the example data:\n" + run.stdout + run.stderr)
    return sandbox / "postulaciones" / "tablero.html"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--keep", action="store_true", help="keep the temporary sandbox")
    args = ap.parse_args()

    src = private_source()
    sandbox = pathlib.Path(tempfile.mkdtemp(prefix="board-demo-"))
    shots = sandbox / "shots"
    shots.mkdir()
    try:
        html = build_sandbox(src, sandbox / "repo", dt.date.today())
        local = sanitize_check.load_local() or {}
        redact = [{"patterns": local.get("deny_patterns", {}).get(label, []), "label": generic}
                  for label, generic in REDACT.items()]
        # Fixed strings of the private interface that cite real things (local only: pattern → label).
        redact += [{"patterns": [pattern], "label": label}
                   for pattern, label in (local.get("screenshot_redactions") or {}).items()]
        env = dict(os.environ, PLAYWRIGHT_FALLBACK=str(src / "node_modules" / "playwright-core" / "index.mjs"),
                   BOARD_REDACT=json.dumps(redact))
        subprocess.run(["node", str(ROOT / "tools" / "board_screenshots.mjs"), str(html), str(shots),
                        json.dumps(VIEWS)], check=True, env=env)

        # Gate BEFORE anything reaches docs/img: the visible text of every view.
        texts = {view: (shots / f"{view}.txt").read_text(encoding="utf-8") for view in VIEWS.values()}
        imaging.gate(texts)
        for view, text in texts.items():
            images = {png.name: png.read_bytes() for png in shots.glob(f"board-{view}-*.png")}
            imaging.write(f"board-{view}", images, "invented data (examples/data/pipeline.example.yaml), "
                          "rendered by tools/board_screenshots.py", text,
                          "the board's interface is in Spanish")
            print(f"✓ {view}: {len(images)} image(s) + manifest")
    finally:
        if args.keep:
            print(f"sandbox kept at {sandbox}")
        else:
            shutil.rmtree(sandbox, ignore_errors=True)


if __name__ == "__main__":
    main()
