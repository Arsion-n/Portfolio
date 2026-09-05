from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

KEY_RE = re.compile(r"^[a-z][a-z0-9_]*$")
ALLOWED_TYPES = {"enum", "string", "number", "date"}


class SchemaError(ValueError):
    pass


def load_schema(path: Path) -> dict[str, Any]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    columns = raw.get("columns")
    if not isinstance(columns, list) or not columns:
        raise SchemaError("schema/columns.yaml 缺少 columns 清單")

    by_key: dict[str, dict[str, Any]] = {}
    for i, col in enumerate(columns):
        if not isinstance(col, dict):
            raise SchemaError(f"columns[{i}] 格式錯誤")
        key = str(col.get("key") or "").strip()
        if not key:
            raise SchemaError(f"columns[{i}] 缺少 key")
        if not KEY_RE.match(key):
            raise SchemaError(f"{key}: key 只可用小寫英文、數字、底線")
        if key in by_key:
            raise SchemaError(f"重複 key: {key}")
        col_type = str(col.get("type") or "string")
        if col_type not in ALLOWED_TYPES:
            raise SchemaError(f"{key}: 未知 type {col_type}")
        if col_type == "enum":
            values = col.get("values") or []
            if not isinstance(values, list) or not values:
                raise SchemaError(f"{key}: enum 需要 values")
            col["values"] = [str(v) for v in values]
        by_key[key] = col
    return {"columns": columns, "by_key": by_key}


def public_schema(schema: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for col in schema["columns"]:
        item = {
            "key": col["key"],
            "label": col.get("label") or col["key"],
            "type": col.get("type") or "string",
            "required": bool(col.get("required")),
            "shortcut": bool(col.get("shortcut")),
            "default": col.get("default"),
            "description": col.get("description"),
        }
        if col.get("type") == "enum":
            item["values"] = col.get("values") or []
        out.append(item)
    return out
