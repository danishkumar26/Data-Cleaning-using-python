"""Tests for the dataclean pipeline and CLI."""

from dataclean.cli import app
from dataclean.config import Settings, load_rules
from dataclean.pipeline import Pipeline
from dataclean.report import format_report
from dataclean.rules import CleaningRules

ROWS = [
    {"name": "Alice", "age": "25", "email": "a@x.com"},
    {"name": "Alice", "age": "25", "email": "a@x.com"},
    {"name": "Bob", "age": "", "email": "b@x.com"},
]


def test_settings_defaults():
    s = Settings.load()
    assert s.report_format == "markdown"
    assert s.dry_run is False


def test_load_rules(tmp_path):
    rules_file = tmp_path / "rules.yaml"
    rules_file.write_text("drop_duplicates: true\nmissing_values:\n  age: \"strategy=mean\"\n")
    data = load_rules(str(rules_file))
    assert data["drop_duplicates"] is True


def test_pipeline_dedupe():
    rules = CleaningRules(drop_duplicates=True)
    result, cleaned = Pipeline(rules).run(ROWS)
    assert result.rows_after == 2
    assert result.removed == 1


def test_pipeline_full():
    rules = CleaningRules(
        drop_duplicates=True,
        type_cast={"age": "int"},
    )
    result, cleaned = Pipeline(rules).run(ROWS)
    assert result.rows_after == 2
    assert result.columns_before == 3


def test_report_markdown():
    rules = CleaningRules(drop_duplicates=True)
    result, _ = Pipeline(rules).run(ROWS)
    md = format_report(result, "markdown")
    assert "Data Cleaning Report" in md
    assert "Rows:" in md


def test_report_json():
    rules = CleaningRules(drop_duplicates=True)
    result, _ = Pipeline(rules).run(ROWS)
    js = format_report(result, "json")
    assert "rows_before" in js
    assert "rows_after" in js


def test_cli_version():
    from typer.testing import CliRunner
    runner = CliRunner()
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "dataclean v" in result.output
