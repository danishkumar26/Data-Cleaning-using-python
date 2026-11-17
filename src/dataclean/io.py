"""CSV / JSON readers and writers."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def detect_format(path: str) -> str:
    """Detect file format from extension."""
    suffix = Path(path).suffix.lower()
    if suffix in {".json"}:
        return "json"
    if suffix in {".csv", ".tsv", ".txt"}:
        return "csv"
    raise ValueError(f"Cannot detect format for {path!r}: unknown extension {suffix}")


def read_csv(path: str, delimiter: str = ",") -> list[dict[str, Any]]:
    """Read a CSV file into a list of dicts."""
    rows: list[dict[str, Any]] = []
    with open(path, "r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, delimiter=delimiter)
        for row in reader:
            rows.append({k: v for k, v in row.items() if k is not None})
    return rows


def read_json(path: str) -> list[dict[str, Any]]:
    """Read a JSON file (list of objects or single object) into a list of dicts."""
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    if isinstance(data, list):
        return [dict(r) for r in data]
    if isinstance(data, dict):
        return [data]
    raise ValueError(f"JSON file {path} must contain a list or an object")


def write_csv(rows: list[dict[str, Any]], path: str) -> None:
    """Write a list of dicts to a CSV file."""
    if not rows:
        Path(path).write_text("", encoding="utf-8")
        return
    columns: list[str] = []
    for row in rows:
        for col in row:
            if col not in columns:
                columns.append(col)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_json(rows: list[dict[str, Any]], path: str) -> None:
    """Write a list of dicts to a JSON file."""
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=2)
