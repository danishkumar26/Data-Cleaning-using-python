"""Tests for dataclean cleaners."""

import pytest

from dataclean.cleaners.columns import column_ops
from dataclean.cleaners.dates import normalize_dates
from dataclean.cleaners.dedupe import dedupe
from dataclean.cleaners.missing import handle_missing_values
from dataclean.cleaners.types import cast_types
from dataclean.rules import CleaningRules, DateColumnRule, MissingValueRule

ROWS = [
    {"name": "Alice", "age": "25", "dob": "12-05-1998", "email": "a@x.com"},
    {"name": "Bob", "age": "", "dob": "1992-09-21", "email": "b@x.com"},
    {"name": "Alice", "age": "25", "dob": "12-05-1998", "email": "a@x.com"},  # duplicate
    {"name": "Carol", "age": "30", "dob": "invalid-date", "email": ""},
]


def test_dedupe_removes_exact_duplicates():
    cleaned, res = dedupe(ROWS)
    assert len(cleaned) == 3
    assert res.rows_after == 3
    assert res.removed == 1


def test_dedupe_subset():
    cleaned, res = dedupe(ROWS, subset=["email"])
    assert len(cleaned) == 3  # a@x.com duplicated


def test_missing_fill_mean():
    rules = {"age": MissingValueRule("age", strategy="mean")}
    cleaned, res = handle_missing_values(ROWS, rules)
    # Bob's age is missing; mean of 25, 25, 30 = 26.66...
    assert res.filled.get("age", 0) >= 1
    bob = next(r for r in cleaned if r["name"] == "Bob")
    assert isinstance(bob["age"], float)


def test_missing_drop_column():
    rules = {"email": MissingValueRule("email", strategy="drop")}
    cleaned, res = handle_missing_values(ROWS, rules)
    # Carol has empty email -> dropped
    assert res.dropped_rows >= 1
    assert all(r["email"] for r in cleaned)


def test_date_normalization():
    rules = {
        "dob": DateColumnRule(
            "dob", input_formats=["%d-%m-%Y", "%Y-%m-%d"], output_format="%Y-%m-%d"
        )
    }
    cleaned, res = normalize_dates(ROWS, rules)
    # Alice x2 (12-05-1998) and Bob (1992-09-21) parse; Carol's invalid doesn't
    assert res.normalized.get("dob", 0) == 3
    alice = next(r for r in cleaned if r["name"] == "Alice")
    assert alice["dob"] == "1998-05-12"


def test_type_cast_int():
    cleaned, res = cast_types(ROWS, {"age": "int"})
    assert res.cast.get("age", 0) >= 1
    alice = next(r for r in cleaned if r["name"] == "Alice")
    assert isinstance(alice["age"], int)


def test_column_ops_rename_and_drop():
    cleaned, res = column_ops(
        ROWS, keep=["name", "age"], drop=["dob"], rename={"name": "full_name"}
    )
    assert "full_name" in res.renamed_columns.values()
    # keep=["name","age"] drops dob and email; dob also in drop list
    assert "dob" in res.dropped_columns
    assert "email" in res.dropped_columns
    assert all("full_name" in r and "dob" not in r for r in cleaned)


def test_cleaning_rules_from_dict():
    data = {
        "drop_duplicates": True,
        "missing_values": {"age": "strategy=mean"},
        "type_cast": {"age": "int"},
    }
    rules = CleaningRules.from_dict(data)
    assert rules.drop_duplicates is True
    assert rules.missing_values["age"].strategy == "mean"
    assert rules.type_cast["age"] == "int"


def test_column_ops_rename_rejects_existing_target():
    # Renaming onto an existing column must fail instead of overwriting data.
    rows = [{"a": 1, "b": 2}]
    with pytest.raises(ValueError, match="already exists"):
        column_ops(rows, rename={"a": "b"})
    # No data lost and no partial rename applied.
    assert rows == [{"a": 1, "b": 2}]


def test_column_ops_rename_still_works_for_new_target():
    cleaned, res = column_ops([{"a": 1}], rename={"a": "b"})
    assert cleaned == [{"b": 1}]
    assert res.renamed_columns == {"a": "b"}
