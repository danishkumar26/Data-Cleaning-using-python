"""Before/after quality reports (Markdown / JSON)."""

from __future__ import annotations

from .pipeline import PipelineResult


def to_markdown(result: PipelineResult) -> str:
    """Render a pipeline result as a Markdown quality report."""
    lines: list[str] = [
        "# Data Cleaning Report",
        "",
        f"**Rows:** {result.rows_before} → {result.rows_after} "
        f"({result.removed} removed)",
        f"**Columns:** {result.columns_before} → {result.columns_after}",
        "",
        "## Changes by Stage",
        "",
    ]
    for change in result.changes:
        lines.append(f"- {change}")
    lines.extend(
        [
            "",
            "## Stage Details",
            "",
        ]
    )
    for res in result.results:
        lines.append(f"### {res.name}")
        lines.append(f"- Rows: {res.rows_before} → {res.rows_after}")
        lines.append(f"- Removed: {res.removed}")
        lines.append("")
    return "\n".join(lines)


def to_json(result: PipelineResult) -> str:
    """Serialize a pipeline result to JSON."""
    import json

    return json.dumps(
        {
            "rows_before": result.rows_before,
            "rows_after": result.rows_after,
            "rows_removed": result.removed,
            "columns_before": result.columns_before,
            "columns_after": result.columns_after,
            "changes": result.changes,
            "stages": [
                {
                    "name": r.name,
                    "rows_before": r.rows_before,
                    "rows_after": r.rows_after,
                    "removed": r.removed,
                    "changes": r.changes,
                }
                for r in result.results
            ],
        },
        indent=2,
    )


FORMATTERS = {
    "markdown": to_markdown,
    "json": to_json,
}


def format_report(result: PipelineResult, fmt: str = "markdown") -> str:
    """Format a pipeline result as a report."""
    formatter = FORMATTERS.get(fmt)
    if formatter is None:
        raise ValueError(f"Unknown report format: {fmt!r}. Use: {', '.join(FORMATTERS)}")
    return formatter(result)
