#!/usr/bin/env python3
"""Validate a pipeline file against the entry schema and the rules a schema cannot express.

    python3 reference/pipeline_check.py                                  # the example pipeline
    python3 reference/pipeline_check.py path/to/pipeline.yaml

Reference implementation of ADR 0005 (closed vocabularies, validated by script). The schema is the single
source of the vocabularies: this script interprets the subset of JSON Schema that the schema uses, so the
vocabularies are never written twice. Standard library + PyYAML only.

Exit 1 on any error; warnings are printed but do not fail.
"""
from __future__ import annotations

import datetime as dt
import json
import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCHEMA = ROOT / "examples" / "schemas" / "pipeline-entry.schema.json"
EXAMPLE = ROOT / "examples" / "data" / "pipeline.example.yaml"


def load_entries(path: pathlib.Path) -> list[dict]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data["entries"] if isinstance(data, dict) else (data or [])


def _type_ok(value, kind: str) -> bool:
    return {"object": isinstance(value, dict),
            "array": isinstance(value, list),
            "string": isinstance(value, (str, dt.date)),       # YAML turns 2026-01-10 into a date
            "integer": isinstance(value, int) and not isinstance(value, bool),
            "boolean": isinstance(value, bool)}[kind]


def validate(value, schema: dict, where: str) -> list[str]:
    """Errors of `value` against the schema subset used here: type, enum, const, required,
    additionalProperties, properties, items, minimum, maximum, minLength, pattern, format=date, allOf/if/then."""
    errors = []
    if "type" in schema and not _type_ok(value, schema["type"]):
        return [f"{where}: expected {schema['type']}, got {type(value).__name__}"]
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{where}: '{value}' is not one of {schema['enum']}")
    if "const" in schema and value != schema["const"]:
        errors.append(f"{where}: must be '{schema['const']}'")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{where}: {value} < {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"{where}: {value} > {schema['maximum']}")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            errors.append(f"{where}: empty")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errors.append(f"{where}: '{value}' does not match {schema['pattern']}")
        if schema.get("format") == "date":
            try:
                dt.date.fromisoformat(value)
            except ValueError:
                errors.append(f"{where}: '{value}' is not a YYYY-MM-DD date")
    if isinstance(value, dict):
        props = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{where}: missing '{key}'")
        if schema.get("additionalProperties") is False:
            errors += [f"{where}: unknown field '{k}'" for k in value if k not in props]
        for key, sub in props.items():
            if key in value:
                errors += validate(value[key], sub, f"{where}.{key}")
    if isinstance(value, list) and "items" in schema:
        for i, item in enumerate(value):
            errors += validate(item, schema["items"], f"{where}[{i}]")
    for rule in schema.get("allOf", []):
        if not validate(value, rule["if"], where):          # the condition holds
            errors += validate(value, rule["then"], where)
    return errors


def cross_checks(entries: list[dict]) -> tuple[list[str], list[str]]:
    """Rules between entries, or between a field and the history, that the schema cannot say."""
    errors, warnings = [], []
    ids = [e.get("id") for e in entries]
    errors += [f"duplicated id: {i}" for i in sorted({i for i in ids if ids.count(i) > 1})]
    seen: dict[tuple, str] = {}
    for i, e in enumerate(entries):
        e = {**e, "id": e.get("id", f"entry {i}")}
        events = {ev.get("type") for ev in e.get("history") or []}
        # A direct contact is the field the channel is measured with: it needs an event that backs it.
        if e.get("direct_contact") is True and "connection" not in events:
            errors.append(f"{e['id']}: direct_contact is true without a 'connection' event")
        if "connection" in events and "direct_contact" not in e:
            warnings.append(f"{e['id']}: has a 'connection' event and does not declare direct_contact")
        try:
            order_wrong = bool(e.get("sent") and e.get("published")
                               and dt.date.fromisoformat(str(e["sent"])) < dt.date.fromisoformat(str(e["published"])))
        except ValueError:
            order_wrong = False                               # a malformed date is already a schema error
        if order_wrong:
            errors.append(f"{e['id']}: sent before it was published")
        # The same vacancy on two boards has two URLs; employer + role is the fingerprint that remains.
        key = (str(e.get("employer", "")).lower().strip(), str(e.get("role", "")).lower().strip())
        if key in seen:
            warnings.append(f"{e['id']}: same employer and role as {seen[key]} — the same vacancy twice?")
        seen.setdefault(key, e["id"])
    return errors, warnings


def check(path: pathlib.Path) -> tuple[list[str], list[str]]:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    entries = load_entries(path)
    errors = []
    for i, e in enumerate(entries):
        errors += validate(e, schema, str(e.get("id", f"entry {i}")))
    more, warnings = cross_checks(entries)
    return errors + more, warnings


def main(argv: list[str]) -> int:
    path = pathlib.Path(argv[0]) if argv else EXAMPLE
    errors, warnings = check(path)
    for w in warnings:
        print("!", w)
    for e in errors:
        print("✗", e)
    if errors:
        return 1
    print(f"✓ {path.name}: {len(load_entries(path))} entries valid")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
