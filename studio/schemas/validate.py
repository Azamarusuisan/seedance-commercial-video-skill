#!/usr/bin/env python3
"""Small dependency-free schema validator for Studio JSON contracts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


class SchemaError(ValueError):
    pass


SCHEMA_DIR = Path(__file__).resolve().parent


def load_schema(name: str) -> dict[str, Any]:
    path = Path(name)
    if not path.suffix:
        path = SCHEMA_DIR / f"{name}.schema.json"
    if not path.is_file():
        raise SchemaError(f"schema not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def validate_value(value: Any, schema: dict[str, Any], path: str = "$") -> None:
    expected = schema.get("type")
    if expected:
        checks = {
            "object": isinstance(value, dict),
            "array": isinstance(value, list),
            "string": isinstance(value, str),
            "number": isinstance(value, (int, float)) and not isinstance(value, bool),
            "integer": isinstance(value, int) and not isinstance(value, bool),
            "boolean": isinstance(value, bool),
        }
        if expected in checks and not checks[expected]:
            raise SchemaError(f"{path}: expected {expected}, got {type(value).__name__}")
    if "enum" in schema and value not in schema["enum"]:
        raise SchemaError(f"{path}: invalid value {value!r}; expected one of {schema['enum']}")
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                raise SchemaError(f"{path}: missing required key {key!r}")
        props = schema.get("properties", {})
        for key, child_schema in props.items():
            if key in value:
                validate_value(value[key], child_schema, f"{path}.{key}")
    if isinstance(value, list) and "items" in schema:
        for index, item in enumerate(value):
            validate_value(item, schema["items"], f"{path}[{index}]")


def validate_document(document: dict[str, Any], schema_name: str) -> None:
    validate_value(document, load_schema(schema_name))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("schema")
    parser.add_argument("json_file")
    args = parser.parse_args()
    document = json.loads(Path(args.json_file).read_text(encoding="utf-8"))
    validate_document(document, args.schema)
    print(f"ok: {args.json_file} matches {args.schema}")


if __name__ == "__main__":
    main()
