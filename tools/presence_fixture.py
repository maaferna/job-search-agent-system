"""Invented presence data for the board's "Presencia" view — used only by tools/board_screenshots.py.

The private presence view reads the owner's own metrics on external platforms (a professional network,
a credentials platform, a code host and a portfolio site). Here every series is generated: deterministic,
smooth, and relative to the day the screenshots are taken, so the "read N days ago" chips stay green.

Files are written in the PRIVATE schema (Spanish field names), because they feed the private loaders as
they are. Values are chosen so that no alert of the private loaders is triggered: alerts are written for
the real profile and would not make sense on invented data.
"""
from __future__ import annotations

import datetime as dt
import math
import pathlib

import yaml


def _weekly(today: dt.date, n: int) -> list[dt.date]:
    return [today - dt.timedelta(days=7 * (n - 1 - i)) - dt.timedelta(days=1) for i in range(n)]


def _wave(i: int, base: float, growth: float, amp: float) -> int:
    return max(0, round(base + growth * i + amp * math.sin(i * 1.3)))


def write(perfil: pathlib.Path, today: dt.date) -> None:
    weeks = _weekly(today, 10)

    # Weekly signals log (Markdown table read by the board). The job-board column stays empty.
    rows = ["| fecha | visitas | búsquedas | impresiones | vistas portal | mensajes | nota |",
            "|---|---|---|---|---|---|---|"]
    for i, d in enumerate(weeks):
        rows.append(f"| {d} | {_wave(i, 18, 3, 4)} | {_wave(i, 9, 2, 3)} | {_wave(i, 140, 25, 40)} |  | "
                    f"{_wave(i, 0.4, 0.15, 0.8)} | invented |")
    (perfil / "senales-perfil.md").write_text("# Invented signals log\n\n" + "\n".join(rows) + "\n", encoding="utf-8")

    linkedin = {
        "perfil": {
            "url": "https://example.com/profile/demo-owner", "leido": weeks[-1], "titular": "Demo owner",
            "secciones": {"acerca_de": True, "destacado": 3, "experiencia": 6, "educacion": 2, "licencias": 9,
                          "proyectos": 4, "aptitudes": 30, "publicaciones": 8, "recomendaciones_recibidas": 3,
                          "recomendaciones_enviadas": 2, "idiomas": 2},
            "cargo_actual": True, "certificaciones_sin_fecha": 0,
            "pendientes": [
                {"accion": "Invented example: add a featured post with a measured result", "quien": "Owner",
                 "fecha": today + dt.timedelta(days=4)},
                {"accion": "Invented example: ask for one recommendation from a former team", "quien": "Owner",
                 "fecha": today + dt.timedelta(days=10)},
            ],
        },
        "metas": {"desde": weeks[0], "hasta": today + dt.timedelta(days=30), "items": [
            {"metrica": "apariciones_busqueda_7d", "meta": 30, "texto": "Search appearances, 7 d"},
            {"metrica": "visitas_perfil_90d", "meta": 150, "texto": "Profile visits, 90 d"},
            {"metrica": "publicaciones_desde", "meta": 6, "texto": "Own posts since the start"},
        ]},
        "lecturas": [{"fecha": d, "fuente": "invented", "seguidores": 300 + 6 * i,
                      "visitas_perfil_90d": _wave(i, 60, 9, 6), "apariciones_busqueda_7d": _wave(i, 10, 2.2, 3),
                      "impresiones_7d": _wave(i, 150, 30, 50), "mensajes_reclutador_semana": _wave(i, 0.3, 0.1, 0.7),
                      "comentarios_hechos_semana": 2 + i % 3, "contactos": 900 + 12 * i,
                      "impresiones_365d": 9000 + 400 * i, "interacciones_365d": 210 + 9 * i}
                     for i, d in enumerate(weeks)],
        "publicaciones": [{"urn": f"invented-{i}", "fecha_aprox": weeks[2 * i + 1 if 2 * i + 1 < 10 else 9],
                           "tipo": t, "tema": f"Invented example post {i + 1}", "impresiones": imp,
                           "reacciones": r, "comentarios": c, "compartidos": s}
                          for i, (t, imp, r, c, s) in enumerate([
                              ("proyecto", 820, 31, 6, 2), ("articulo", 1340, 44, 9, 5),
                              ("certificado", 410, 18, 2, 0), ("proyecto", 960, 37, 7, 3),
                              ("aprendizaje", 1210, 40, 11, 4)])],
    }
    (perfil / "linkedin-metricas.yaml").write_text(yaml.safe_dump(linkedin, allow_unicode=True, sort_keys=False),
                                                   encoding="utf-8")

    months = [today - dt.timedelta(days=30 * (5 - i)) - dt.timedelta(days=2) for i in range(6)]
    credly = {
        "perfil": {"url": "https://example.com/credentials/demo-owner", "title": "Demo owner", "summary_ok": True,
                   "profile_strength": {"nivel": "Strong", "completados": 6, "total": 6, "pendientes": []},
                   "work_history": {"estado": "complete", "visibilidad": "public", "cargos": 6}},
        "lecturas": [{"fecha": d, "badges": 5 + i // 2, "skills": 40 + 2 * i, "views": 120 + 22 * i + 3 * (i % 2),
                      "shares": 18 + i, "nota": "invented"} for i, d in enumerate(months)],
    }
    (perfil / "credly-metricas.yaml").write_text(yaml.safe_dump(credly, allow_unicode=True, sort_keys=False),
                                                 encoding="utf-8")

    days = [today - dt.timedelta(days=59 - i) for i in range(60)]
    repos = {}
    for k, name in enumerate(["example-vision-pipeline", "example-scheduling-optimizer", "example-data-api",
                              "example-portfolio"]):
        repos[name] = {"visitas": {str(d): [_wave(i, 4 - k, 0.03, 3), _wave(i + k, 2 - k / 2, 0.02, 1.5)]
                                   for i, d in enumerate(days)},
                       "clones": {str(d): [_wave(i, 1, 0, 2), _wave(i, 0.5, 0, 1)] for i, d in enumerate(days)}}
    technical = {
        "github": {"perfil": [{"fecha": str(days[-1]), "seguidores": 24, "repos_publicos": 18}],
                   "repos": repos,
                   "referrers": [{"fecha": str(days[-1]), "repo": "example-vision-pipeline", "origen": "example.com",
                                  "visitas_14d": 9, "unicos_14d": 5}],
                   "capturas": [str(today - dt.timedelta(days=1))]},
        "heroku": {"app": "example-portfolio",
                   "dias": {str(d): {"paginas_vistas": _wave(i, 20, 0.4, 8), "ips_distintas_max": _wave(i, 6, 0.1, 2),
                                     "ruido": _wave(i, 30, 0, 10), "errores_5xx": 0, "servicio_ms_mediana": 45,
                                     "paginas": {"/": _wave(i, 9, 0.2, 3), "/projects/": _wave(i, 5, 0.1, 2),
                                                 "/cv/": _wave(i, 3, 0.1, 1)}}
                            for i, d in enumerate(days[-30:])},
                   "capturas": [str(today - dt.timedelta(days=1))]},
    }
    (perfil / "presencia-tecnica.yaml").write_text(yaml.safe_dump(technical, allow_unicode=True, sort_keys=False),
                                                   encoding="utf-8")
