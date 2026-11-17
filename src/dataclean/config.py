"""Application settings — cleaning-rules.yaml with environment overrides."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

import yaml


@dataclass
class Settings:
    """Runtime configuration for dataclean."""

    rules_path: Optional[str] = None
    input_path: Optional[str] = None
    output_path: Optional[str] = None
    report_path: Optional[str] = None
    report_format: str = "markdown"
    input_format: Optional[str] = None  # csv | json | auto
    dry_run: bool = False

    @classmethod
    def load(
        cls,
        rules_path: Optional[str] = None,
        input_path: Optional[str] = None,
        output_path: Optional[str] = None,
        report_path: Optional[str] = None,
        report_format: str = "markdown",
        input_format: Optional[str] = None,
        dry_run: bool = False,
    ) -> "Settings":
        return cls(
            rules_path=rules_path,
            input_path=input_path,
            output_path=output_path,
            report_path=report_path,
            report_format=report_format,
            input_format=input_format,
            dry_run=dry_run,
        )


def load_rules(path: str) -> dict[str, Any]:
    """Load cleaning rules from a YAML file."""
    with open(path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Rules file {path} must contain a YAML mapping, got {type(data).__name__}")
    return data
