"""Deduplication transform."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .base import CleanResult


@dataclass
class DedupeResult(CleanResult):
    duplicate_keys: list[Any] = field(default_factory=list)


def dedupe(
    rows: list[dict[str, Any]],
    subset: list[str] | None = None,
) -> tuple[list[dict[str, Any]], DedupeResult]:
    """Remove duplicate rows.

    If ``subset`` is given, only those columns are compared; the first
    occurrence of each key is kept.
    """
    rows_before = len(rows)
    seen: set[Any] = set()
    cleaned: list[dict[str, Any]] = []
    duplicate_keys: list[Any] = []
    changes: list[str] = []

    for row in rows:
        if subset is not None:
            key = tuple(row.get(col) for col in subset)
        else:
            key = tuple(sorted((k, v) for k, v in row.items()))

        if key in seen:
            duplicate_keys.append(key)
            changes.append(f"Removed duplicate row with key {key!r}")
            continue
        seen.add(key)
        cleaned.append(dict(row))

    rows_after = len(cleaned)
    changes.insert(
        0,
        f"Deduplication: {rows_before} rows -> {rows_after} rows "
        f"({rows_before - rows_after} duplicates removed)",
    )
    result = DedupeResult(
        name="dedupe",
        rows_before=rows_before,
        rows_after=rows_after,
        changes=changes,
        removed_count=rows_before - rows_after,
        duplicate_keys=duplicate_keys,
    )
    return cleaned, result
