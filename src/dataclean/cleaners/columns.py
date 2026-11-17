"""Column operations transform (keep/drop/rename)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .base import CleanResult


@dataclass
class ColumnOpsResult(CleanResult):
    dropped_columns: list[str] = field(default_factory=list)
    renamed_columns: dict[str, str] = field(default_factory=dict)


def column_ops(
    rows: list[dict[str, Any]],
    *,
    keep: list[str] | None = None,
    drop: list[str] | None = None,
    rename: dict[str, str] | None = None,
) -> tuple[list[dict[str, Any]], ColumnOpsResult]:
    """Apply column keep/drop/rename operations."""
    rows_before = len(rows)
    cleaned = [dict(r) for r in rows]
    drop = drop or []
    rename = rename or {}
    changes: list[str] = []

    # Determine all columns present
    all_columns: list[str] = []
    for row in cleaned:
        for col in row:
            if col not in all_columns:
                all_columns.append(col)

    # Determine which columns to drop
    to_drop: set[str] = set(drop)
    if keep is not None:
        keep_set = set(keep)
        to_drop.update(col for col in all_columns if col not in keep_set)

    dropped_columns = [col for col in all_columns if col in to_drop]
    if dropped_columns:
        for row in cleaned:
            for col in dropped_columns:
                row.pop(col, None)
        changes.append(f"Dropped columns: {', '.join(dropped_columns)}")

    # Rename columns
    renamed_columns: dict[str, str] = {}
    for row in cleaned:
        for old_name, new_name in rename.items():
            if old_name in row:
                row[new_name] = row.pop(old_name)
                renamed_columns[old_name] = new_name
    if renamed_columns:
        changes.append(f"Renamed columns: {renamed_columns}")

    rows_after = len(cleaned)
    changes.insert(
        0,
        f"Column operations: {len(all_columns)} columns -> "
        f"{len(all_columns) - len(dropped_columns)} columns "
        f"({len(dropped_columns)} dropped, {len(renamed_columns)} renamed)",
    )
    result = ColumnOpsResult(
        name="column_ops",
        rows_before=rows_before,
        rows_after=rows_after,
        changes=changes,
        removed_count=0,
        dropped_columns=dropped_columns,
        renamed_columns=renamed_columns,
    )
    return cleaned, result
