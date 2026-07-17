import numpy as np
import pandas as pd
import pytest

from core.data_cleaner import (
    remove_duplicates,
    fill_missing_numeric,
    fill_missing_text,
    standardize_dates,
    trim_whitespace,
    normalize_text_case,
)


# ─── remove_duplicates ────────────────────────────────────────────────────

def test_remove_duplicates_removes_exact_dupes():
    df = pd.DataFrame({"a": [1, 1, 2], "b": ["x", "x", "y"]})
    result, stats = remove_duplicates(df)
    assert len(result) == 2
    assert stats == {"removed_duplicates": 1}
    assert list(result.index) == [0, 1]  # index reset


def test_remove_duplicates_no_dupes():
    df = pd.DataFrame({"a": [1, 2, 3]})
    result, stats = remove_duplicates(df)
    assert stats == {"removed_duplicates": 0}
    pd.testing.assert_frame_equal(result, df)


def test_remove_duplicates_subset_and_keep_last():
    df = pd.DataFrame({"a": [1, 1, 2], "b": ["first", "second", "y"]})
    result, stats = remove_duplicates(df, subset=["a"], keep="last")
    assert stats == {"removed_duplicates": 1}
    assert result.loc[result["a"] == 1, "b"].iloc[0] == "second"


# ─── fill_missing_numeric ─────────────────────────────────────────────────

def test_fill_missing_numeric_median():
    df = pd.DataFrame({"a": [1.0, np.nan, 3.0]})
    result = fill_missing_numeric(df, strategy="median")
    assert result["a"].tolist() == [1.0, 2.0, 3.0]


def test_fill_missing_numeric_mean():
    df = pd.DataFrame({"a": [1.0, np.nan, 5.0]})
    result = fill_missing_numeric(df, strategy="mean")
    assert result["a"].tolist() == [1.0, 3.0, 5.0]


def test_fill_missing_numeric_unknown_strategy_defaults_to_zero():
    df = pd.DataFrame({"a": [1.0, np.nan, 3.0]})
    result = fill_missing_numeric(df, strategy="bogus")
    assert result["a"].tolist() == [1.0, 0.0, 3.0]


def test_fill_missing_numeric_ignores_non_numeric_columns():
    df = pd.DataFrame({"a": [1.0, np.nan], "b": [None, "text"]})
    result = fill_missing_numeric(df, strategy="median")
    assert result["b"].isna().sum() == 1  # untouched


def test_fill_missing_numeric_all_null_column_stays_null():
    # median/mean of an all-NaN column is NaN, so fillna is a no-op —
    # this documents the actual behavior despite the docstring's claim
    # that fully-null columns are "skipped".
    df = pd.DataFrame({"a": [np.nan, np.nan, np.nan]})
    result = fill_missing_numeric(df, strategy="median")
    assert result["a"].isna().all()


def test_fill_missing_numeric_does_not_mutate_input():
    df = pd.DataFrame({"a": [1.0, np.nan]})
    fill_missing_numeric(df, strategy="median")
    assert df["a"].isna().sum() == 1


# ─── fill_missing_text ────────────────────────────────────────────────────

def test_fill_missing_text_default_value():
    df = pd.DataFrame({"a": ["x", None, "y"]})
    result = fill_missing_text(df)
    assert result["a"].tolist() == ["x", "Unknown", "y"]


def test_fill_missing_text_custom_value():
    df = pd.DataFrame({"a": ["x", None]})
    result = fill_missing_text(df, fill_value="N/A")
    assert result["a"].tolist() == ["x", "N/A"]


def test_fill_missing_text_ignores_numeric_columns():
    df = pd.DataFrame({"a": [1.0, np.nan]})
    result = fill_missing_text(df)
    assert result["a"].isna().sum() == 1


# ─── standardize_dates ────────────────────────────────────────────────────

def test_standardize_dates_auto_detect_above_threshold():
    # 4 out of 5 values parse as dates (80%) -> column is converted
    df = pd.DataFrame({
        "d": ["2023-01-01", "2023-02-15", "2023-03-20", "2023-04-10", "abc"],
    })
    result = standardize_dates(df)
    assert pd.api.types.is_datetime64_any_dtype(result["d"])
    assert result["d"].isna().sum() == 1  # "abc" coerced to NaT


def test_standardize_dates_auto_detect_below_threshold_left_untouched():
    # only 2 out of 5 values parse as dates (40%) -> column stays as-is
    df = pd.DataFrame({
        "d": ["2023-01-01", "not-a-date", "nope", "nah", "2023-02-01"],
    })
    result = standardize_dates(df)
    assert not pd.api.types.is_datetime64_any_dtype(result["d"])


def test_standardize_dates_explicit_columns():
    df = pd.DataFrame({"d": ["2023-01-01", "invalid"], "keep": ["x", "y"]})
    result = standardize_dates(df, date_cols=["d"])
    assert pd.api.types.is_datetime64_any_dtype(result["d"])
    assert result["keep"].tolist() == ["x", "y"]


def test_standardize_dates_explicit_columns_ignores_missing_column():
    df = pd.DataFrame({"d": ["2023-01-01"]})
    result = standardize_dates(df, date_cols=["nonexistent"])
    assert result["d"].tolist() == ["2023-01-01"]  # untouched, no KeyError


# ─── trim_whitespace ──────────────────────────────────────────────────────

def test_trim_whitespace_strips_leading_and_trailing_spaces():
    df = pd.DataFrame({"a": ["  x ", "y  ", " z"]})
    result = trim_whitespace(df)
    assert result["a"].tolist() == ["x", "y", "z"]


def test_trim_whitespace_ignores_numeric_columns():
    df = pd.DataFrame({"a": [1, 2, 3]})
    result = trim_whitespace(df)
    assert result["a"].tolist() == [1, 2, 3]


def test_trim_whitespace_preserves_nulls():
    df = pd.DataFrame({"a": [" x ", None]})
    result = trim_whitespace(df)
    assert result["a"].iloc[0] == "x"
    assert pd.isna(result["a"].iloc[1])


# ─── normalize_text_case ──────────────────────────────────────────────────

def test_normalize_text_case_title():
    df = pd.DataFrame({"a": ["john doe", "JANE smith"]})
    result = normalize_text_case(df, mode="title")
    assert result["a"].tolist() == ["John Doe", "Jane Smith"]


def test_normalize_text_case_lower():
    df = pd.DataFrame({"a": ["JOHN"]})
    result = normalize_text_case(df, mode="lower")
    assert result["a"].tolist() == ["john"]


def test_normalize_text_case_upper():
    df = pd.DataFrame({"a": ["john"]})
    result = normalize_text_case(df, mode="upper")
    assert result["a"].tolist() == ["JOHN"]


def test_normalize_text_case_specific_columns_only():
    df = pd.DataFrame({"a": ["john"], "b": ["doe"]})
    result = normalize_text_case(df, columns=["a"], mode="upper")
    assert result["a"].tolist() == ["JOHN"]
    assert result["b"].tolist() == ["doe"]  # untouched


def test_normalize_text_case_preserves_nulls():
    df = pd.DataFrame({"a": ["john", None]})
    result = normalize_text_case(df, mode="upper")
    assert result["a"].iloc[0] == "JOHN"
    assert pd.isna(result["a"].iloc[1])
