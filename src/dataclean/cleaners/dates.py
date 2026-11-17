"""Date normalization transform."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from dateutil import parser as dateparser

from ..rules import DateColumnRule
from .base import CleanResult


def _parse_date(value: str, formats: list[str]) -> str | None:
    """Try each format; fall back to dateutil.parser."""
    for fmt in formats:
        try:
            dt = datetime.strptime(value, fmt)
            return dt.strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            continue
    try:
        dt = dateparser.parse(value, dayfirst=False)
        if dt:
            return str(dt.strftime("%Y-%m-%d"))
    except (ValueError, TypeError, OverflowError):
        pass
    return None


@dataclass
class DateNormalizationResult(CleanResult):
    normalized: dict[str, int] = field(default_factory=dict)
    unparseable: dict[str, list[str]] = field(default_factory=dict)


def normalize_dates(
    rows: list[dict[str, Any]],
    rules: dict[str, DateColumnRule],
) -> tuple[list[dict[str, Any]], DateNormalizationResult]:
    """Normalize date columns to ISO 8601 (YYYY-MM-DD)."""
    rows_before = len(rows)
    cleaned = [dict(r) for r in rows]
    normalized: dict[str, int] = {}
    unparseable: dict[str, list[str]] = {}
    changes: list[str] = []

    for col, rule in rules.items():
        count = 0
        bad: list[str] = []
        for row in cleaned:
            raw = row.get(col)
            if raw is None or (isinstance(raw, str) and raw.strip() == ""):
                continue
            raw_str = str(raw)
            iso = _parse_date(raw_str, rule.input_formats)
            if iso is None:
                bad.append(raw_str)
                continue
            row[col] = iso
            count += 1
        if count:
            normalized[col] = count
            changes.append(
                f"Normalized {count} date value(s) in '{col}' to {rule.output_format}"
            )
        if bad:
            unparseable[col] = bad
            changes.append(
                f"Could not parse {len(bad)} value(s) in '{col}' (left unchanged)"
            )

    rows_after = len(cleaned)
    changes.insert(
        0,
        f"Date normalization: {rows_before} rows -> {rows_after} rows "
        f"({sum(normalized.values())} dates normalized)",
    )
    result = DateNormalizationResult(
        name="date_normalization",
        rows_before=rows_before,
        rows_after=rows_after,
        changes=changes,
        removed_count=0,
        normalized=normalized,
        unparseable=unparseable,
    )
    return cleaned, result
