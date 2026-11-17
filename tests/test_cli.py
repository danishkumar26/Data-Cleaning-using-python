"""Tests for the dataclean CLI using typer.testing."""

from typer.testing import CliRunner

from dataclean.cli import app

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "dataclean" in result.output


def test_cli_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "dataclean v" in result.output


def test_cli_config():
    result = runner.invoke(app, ["config"])
    assert result.exit_code == 0
    assert "report_format" in result.output


def test_cli_clean_missing_rules():
    result = runner.invoke(app, ["clean", "samples/employee_data.txt"])
    assert result.exit_code != 0  # --rules is required


def test_cli_clean_end_to_end(tmp_path):
    out = tmp_path / "cleaned.csv"
    rep = tmp_path / "report.md"
    result = runner.invoke(
        app,
        [
            "clean",
            "samples/employee_data.txt",
            "--rules",
            "samples/rules.yaml",
            "--out",
            str(out),
            "--report-out",
            str(rep),
        ],
    )
    assert result.exit_code == 0
    assert out.exists()
    assert rep.exists()
    report_text = rep.read_text()
    assert "Data Cleaning Report" in report_text
