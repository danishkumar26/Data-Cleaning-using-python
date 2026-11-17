"""Type-casting transform."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .base import CleanResult


def _cast_int(value: Any) -> Any:
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return None
    try:
        return int(float(str(value)))
    except (ValueError, TypeError):
        return value


def _cast_float(value: Any) -> Any:
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return None
    try:
        return float(str(value))
    except (ValueError, TypeError):
        return value


def _cast_str(value: Any) -> Any:
    if value is None:
        return ""
    return str(value)


def _cast_bool(value: Any) -> Any:
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return None
    if isinstance(value, bool):
        return value
    s = str(value).strip().lower()
    if s in {"true", "1", "yes", "y", "t"}:
        return True
    if s in {"false", "0", "no", "n", "f"}:
        return False
    return value


_CASTERS = {
    "int": _cast_int,
    "float": _cast_float,
    "str": _cast_str,
    "bool": _cast_bool,
    "date": lambda v: v,  # dates handled by the date cleaner
}


@dataclass
class TypeCastResult(CleanResult):
    cast: dict[str, int] = field(default_factory=dict)
    failed: dict[str, list[str]] = field(default_factory=dict)


def cast_types(
    rows: list[dict[str, Any]],
    type_map: dict[str, str],
) -> tuple[list[dict[str, Any]], TypeCastResult]:
    """Cast columns to the declared types."""
    rows_before = len(rows)
    cleaned = [dict(r) for r in rows]
    cast_counts: dict[str, int] = {}
    failed: dict[str, list[str]] = {}
    changes: list[str] = []

    for col, target_type in type_map.items():
        caster = _CASTERS[target_type]
        count = 0
        bad: list[str] = []
        for row in cleaned:
            raw = row.get(col)
            if raw is None or (isinstance(raw, str) and raw.strip() == ""):
                continue
            original = str(raw)
            casted = caster(raw)
            if target_type != "str" and casted == original:
                # Could not cast (returned unchanged)
                bad.append(original)
            else:
                row[col] = casted
                count += 1
        if count:
            cast_counts[col] = count
            changes.append(f"Cast {count} value(s) in '{col}' to {target_type}")
        if bad:
            failed[col] = bad
            changes.append(
                f"Could not cast {len(bad)} value(s) in '{col}' to {target_type} (left unchanged)"
            )

    rows_after = len(cleaned)
    changes.insert(
        0,
        f"Type casting: {rows_before} rows -> {rows_after} rows "
        f"({sum(cast_counts.values())} values cast)",
    )
    result = TypeCastResult(
        name="type_cast",
        rows_before=rows_before,
        rows_after=rows_after,
        changes=changes,
        removed_count=0,
        cast=cast_counts,
        failed=failed,
    )
    return cleaned, result
