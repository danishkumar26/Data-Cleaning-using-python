"""Missing-value handling transform."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..rules import MissingValueRule
from .base import CleanResult


def _is_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    return False


def _column_values(rows: list[dict[str, Any]], column: str) -> list[Any]:
    return [row.get(column) for row in rows if not _is_missing(row.get(column))]


def _mean(values: list[Any]) -> float:
    nums: list[float] = []
    for v in values:
        n = _coerce_number(v)
        if n is not None:
            nums.append(n)
    return sum(nums) / len(nums) if nums else 0.0


def _median(values: list[Any]) -> float:
    nums: list[float] = []
    for v in values:
        n = _coerce_number(v)
        if n is not None:
            nums.append(n)
    nums.sort()
    if not nums:
        return 0.0
    n = len(nums)
    mid = n // 2
    if n % 2 == 1:
        return nums[mid]
    return (nums[mid - 1] + nums[mid]) / 2.0


def _mode(values: list[Any]) -> Any:
    counts: dict[Any, int] = {}
    for v in values:
        if not _is_missing(v):
            counts[v] = counts.get(v, 0) + 1
    if not counts:
        return None
    return max(counts, key=lambda k: counts[k])


def _is_number(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, (int, float)):
        return True
    if isinstance(value, str):
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False
    return False


def _coerce_number(value: Any) -> float | None:
    if not _is_number(value):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


@dataclass
class MissingValuesResult(CleanResult):
    filled: dict[str, int] = field(default_factory=dict)
    dropped_rows: int = 0


def handle_missing_values(
    rows: list[dict[str, Any]],
    rules: dict[str, MissingValueRule],
) -> tuple[list[dict[str, Any]], MissingValuesResult]:
    """Fill or drop rows with missing values per-column rules."""
    rows_before = len(rows)
    cleaned = [dict(r) for r in rows]
    filled: dict[str, int] = {}
    dropped_rows = 0
    changes: list[str] = []

    # First pass: handle drop-strategy columns (remove entire rows)
    drop_columns = [col for col, rule in rules.items() if rule.strategy == "drop"]
    if drop_columns:
        kept: list[dict[str, Any]] = []
        for row in cleaned:
            if any(_is_missing(row.get(col)) for col in drop_columns):
                dropped_rows += 1
                changes.append(
                    f"Dropped row due to missing value in {', '.join(drop_columns)}"
                )
                continue
            kept.append(row)
        cleaned = kept

    # Second pass: fill-strategy columns
    for col, rule in rules.items():
        if rule.strategy == "drop":
            continue
        values = _column_values(cleaned, col)
        fill_value: Any = None
        if rule.strategy == "mean":
            fill_value = _mean(values)
        elif rule.strategy == "median":
            fill_value = _median(values)
        elif rule.strategy == "mode":
            fill_value = _mode(values)
        elif rule.strategy == "constant":
            fill_value = rule.constant

        fill_count = 0
        for row in cleaned:
            if _is_missing(row.get(col)):
                row[col] = fill_value
                fill_count += 1
        if fill_count:
            filled[col] = fill_count
            changes.append(
                f"Filled {fill_count} missing value(s) in '{col}' using {rule.strategy}"
            )

    rows_after = len(cleaned)
    changes.insert(
        0,
        f"Missing values: {rows_before} rows -> {rows_after} rows "
        f"({dropped_rows} dropped, {sum(filled.values())} filled)",
    )
    result = MissingValuesResult(
        name="missing_values",
        rows_before=rows_before,
        rows_after=rows_after,
        changes=changes,
        removed_count=rows_before - rows_after,
        filled=filled,
        dropped_rows=dropped_rows,
    )
    return cleaned, result
