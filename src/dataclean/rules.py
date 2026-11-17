"""Cleaning rules schema and validation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

VALID_STRATEGIES = {"drop", "mean", "median", "mode", "constant"}
VALID_TYPES = {"int", "float", "str", "bool", "date"}


@dataclass
class MissingValueRule:
    column: str
    strategy: str = "drop"
    constant: Any = None

    @classmethod
    def parse(cls, column: str, value: str) -> "MissingValueRule":
        # Accept "strategy=<name>" or bare "<name>"
        if value.startswith("strategy="):
            value = value[len("strategy="):]
        if value == "drop":
            return cls(column, strategy="drop")
        if value == "mean":
            return cls(column, strategy="mean")
        if value == "median":
            return cls(column, strategy="median")
        if value == "mode":
            return cls(column, strategy="mode")
        if value.startswith("constant="):
            return cls(column, strategy="constant", constant=value[len("constant="):])
        raise ValueError(
            f"Invalid missing-values strategy for {column!r}: {value!r}. "
            f"Use drop|mean|median|mode|constant=<value>."
        )


@dataclass
class DateColumnRule:
    column: str
    input_formats: list[str] = field(default_factory=lambda: ["%Y-%m-%d"])
    output_format: str = "%Y-%m-%d"


@dataclass
class CleaningRules:
    drop_duplicates: bool = False
    subset: list[str] | None = None
    missing_values: dict[str, MissingValueRule] = field(default_factory=dict)
    date_columns: dict[str, DateColumnRule] = field(default_factory=dict)
    type_cast: dict[str, str] = field(default_factory=dict)
    columns_keep: list[str] | None = None
    columns_drop: list[str] = field(default_factory=list)
    columns_rename: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CleaningRules":
        rules = cls()
        rules.drop_duplicates = bool(data.get("drop_duplicates", False))
        subset = data.get("subset")
        rules.subset = list(subset) if subset is not None else None

        mv = data.get("missing_values", {}) or {}
        for col, spec in mv.items():
            if isinstance(spec, str):
                rules.missing_values[col] = MissingValueRule.parse(col, spec)
            elif isinstance(spec, dict):
                rules.missing_values[col] = MissingValueRule(
                    col,
                    strategy=spec.get("strategy", "drop"),
                    constant=spec.get("constant"),
                )
            else:
                raise ValueError(f"Invalid missing_values spec for {col!r}: {spec!r}")

        dc = data.get("date_columns", {}) or {}
        for col, spec in dc.items():
            if isinstance(spec, str):
                rules.date_columns[col] = DateColumnRule(column=col)
            elif isinstance(spec, dict):
                rules.date_columns[col] = DateColumnRule(
                    column=col,
                    input_formats=list(spec.get("input_formats", ["%Y-%m-%d"])),
                    output_format=spec.get("output_format", "%Y-%m-%d"),
                )
            else:
                raise ValueError(f"Invalid date_columns spec for {col!r}: {spec!r}")

        tc = data.get("type_cast", {}) or {}
        for col, t in tc.items():
            if t not in VALID_TYPES:
                raise ValueError(
                    f"Invalid type cast for {col!r}: {t!r}. Use {', '.join(sorted(VALID_TYPES))}."
                )
            rules.type_cast[col] = t

        cols = data.get("columns", {}) or {}
        rules.columns_keep = cols.get("keep")
        rules.columns_drop = list(cols.get("drop", []) or [])
        rules.columns_rename = dict(cols.get("rename", {}) or {})

        return rules
