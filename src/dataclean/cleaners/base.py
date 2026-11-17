"""Base classes for cleaning transforms."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CleanResult:
    """Outcome of a single cleaning transform."""

    name: str
    rows_before: int
    rows_after: int
    changes: list[str]
    removed_count: int = 0

    @property
    def removed(self) -> int:
        return self.rows_before - self.rows_after


PIPELINE_ORDER = [
    "dedupe",
    "missing_values",
    "date_normalization",
    "type_cast",
    "column_ops",
]
