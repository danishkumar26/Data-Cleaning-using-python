"""Cleaning pipeline — orchestrates transforms in order and tracks results."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .cleaners.base import CleanResult
from .cleaners.columns import column_ops
from .cleaners.dates import normalize_dates
from .cleaners.dedupe import dedupe
from .cleaners.missing import handle_missing_values
from .cleaners.types import cast_types
from .rules import CleaningRules


@dataclass
class PipelineResult:
    """Outcome of running the full cleaning pipeline."""

    rows_before: int
    rows_after: int
    columns_before: int
    columns_after: int
    results: list[CleanResult] = field(default_factory=list)
    changes: list[str] = field(default_factory=list)

    @property
    def removed(self) -> int:
        return self.rows_before - self.rows_after


class Pipeline:
    """Run cleaning transforms in a fixed, deterministic order.

    Each cleaner returns ``(cleaned_rows, CleanResult)`` so the pipeline can
    thread rows through stages while collecting reports.
    """

    def __init__(self, rules: CleaningRules) -> None:
        self.rules = rules

    def run(self, rows: list[dict[str, Any]]) -> tuple[PipelineResult, list[dict[str, Any]]]:
        columns_before = len({col for row in rows for col in row})
        cleaned = [dict(r) for r in rows]
        results: list[CleanResult] = []
        all_changes: list[str] = []
        rows_before = len(cleaned)

        # 1. Dedupe
        if self.rules.drop_duplicates:
            cleaned, dedupe_res = dedupe(cleaned, subset=self.rules.subset)
            results.append(dedupe_res)
            all_changes.extend(dedupe_res.changes)

        # 2. Missing values
        if self.rules.missing_values:
            cleaned, missing_res = handle_missing_values(cleaned, self.rules.missing_values)
            results.append(missing_res)
            all_changes.extend(missing_res.changes)

        # 3. Date normalization
        if self.rules.date_columns:
            cleaned, date_res = normalize_dates(cleaned, self.rules.date_columns)
            results.append(date_res)
            all_changes.extend(date_res.changes)

        # 4. Type casting
        if self.rules.type_cast:
            cleaned, type_res = cast_types(cleaned, self.rules.type_cast)
            results.append(type_res)
            all_changes.extend(type_res.changes)

        # 5. Column ops
        if self.rules.columns_keep or self.rules.columns_drop or self.rules.columns_rename:
            cleaned, col_res = column_ops(
                cleaned,
                keep=self.rules.columns_keep,
                drop=self.rules.columns_drop,
                rename=self.rules.columns_rename,
            )
            results.append(col_res)
            all_changes.extend(col_res.changes)

        columns_after = len({col for row in cleaned for col in row})
        rows_after = len(cleaned)

        result = PipelineResult(
            rows_before=rows_before,
            rows_after=rows_after,
            columns_before=columns_before,
            columns_after=columns_after,
            results=results,
            changes=all_changes,
        )
        return result, cleaned
