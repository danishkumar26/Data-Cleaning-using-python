"""Command-line interface for dataclean."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from .config import Settings, load_rules
from .io import detect_format, read_csv, read_json, write_csv, write_json
from .pipeline import Pipeline
from .report import format_report
from .rules import CleaningRules

app = typer.Typer(
    name="dataclean",
    help="Lightweight, config-driven data cleaning for Python.",
    rich_markup_mode="rich",
)
console = Console()


def _load_rows(path: str, fmt: str | None) -> list[dict]:
    detected = fmt or detect_format(path)
    if detected == "json":
        return read_json(path)
    return read_csv(path)


def _write_rows(rows: list[dict], path: str, fmt: str | None) -> None:
    detected = fmt or detect_format(path)
    if detected == "json":
        write_json(rows, path)
    else:
        write_csv(rows, path)


@app.command()
def clean(
    input: str = typer.Argument(..., help="Input file (CSV or JSON)"),
    rules: str = typer.Option(..., "--rules", "-r", help="Cleaning rules YAML file"),
    out: str = typer.Option("cleaned.csv", "--out", "-o", help="Output file"),
    report: str = typer.Option("markdown", "--report", "-f", help="Report format: markdown or json"),
    report_out: str = typer.Option(None, "--report-out", help="Write report to file instead of stdout"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would change without writing output"),
) -> None:
    """Clean a dataset according to a rules file and produce a quality report."""
    rules_data = load_rules(rules)
    cleaning_rules = CleaningRules.from_dict(rules_data)

    rows = _load_rows(input, None)
    pipeline = Pipeline(cleaning_rules)
    result, cleaned = pipeline.run(rows)

    report_text = format_report(result, report)
    if report_out:
        Path(report_out).write_text(report_text, encoding="utf-8")
        console.print(f"[green]Report written to[/green] {report_out}")
    else:
        console.print(report_text)

    if dry_run:
        console.print("[yellow]Dry run — output file not written.[/yellow]")
        return

    _write_rows(cleaned, out, None)
    console.print(f"[green]Cleaned data written to[/green] {out}")


@app.command()
def version() -> None:
    """Show the dataclean version."""
    from . import __version__

    console.print(f"dataclean v{__version__}")


@app.command()
def config() -> None:
    """Show the effective settings."""
    settings = Settings.load()
    for field in [
        "rules_path", "input_path", "output_path", "report_path",
        "report_format", "input_format", "dry_run",
    ]:
        console.print(f"{field}: {getattr(settings, field)}")


if __name__ == "__main__":
    app()
