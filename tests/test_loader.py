import io

import pandas as pd
import pytest

from core.data_loader import load_file


class FakeUploadedFile(io.BytesIO):
    """Minimal stand-in for Streamlit's UploadedFile: a seekable byte
    stream with a `.name` attribute (used to sniff the extension)."""

    def __init__(self, content: bytes, name: str):
        super().__init__(content)
        self.name = name


def _csv_file(text: str, name: str = "data.csv", encoding: str = "utf-8") -> FakeUploadedFile:
    return FakeUploadedFile(text.encode(encoding), name)


def _xlsx_file(df: pd.DataFrame, name: str = "data.xlsx") -> FakeUploadedFile:
    buf = io.BytesIO()
    df.to_excel(buf, index=False, engine="openpyxl")
    return FakeUploadedFile(buf.getvalue(), name)


# ─── general ───────────────────────────────────────────────────────────────

def test_load_file_none_returns_none():
    assert load_file(None) is None


def test_load_file_unsupported_extension_raises():
    f = FakeUploadedFile(b"whatever", "data.txt")
    with pytest.raises(ValueError):
        load_file(f)


# ─── CSV ───────────────────────────────────────────────────────────────────

def test_load_csv_utf8():
    f = _csv_file("name,age\nAlice,30\nBob,25\n")
    df = load_file(f)
    assert list(df.columns) == ["name", "age"]
    assert df["name"].tolist() == ["Alice", "Bob"]
    assert df["age"].tolist() == [30, 25]


def test_load_csv_utf8_sig_bom():
    text = "name,age\nAlice,30\n"
    f = FakeUploadedFile(text.encode("utf-8-sig"), "data.csv")
    df = load_file(f)
    # BOM must not leak into the first column name
    assert list(df.columns) == ["name", "age"]


def test_load_csv_arabic_cp1256_fallback():
    # utf-8 / utf-8-sig will fail to decode these bytes, so load_file
    # must fall back to cp1256 to read Arabic content correctly.
    text = "name,city\nأحمد,القاهرة\n"
    f = _csv_file(text, encoding="cp1256")
    df = load_file(f)
    assert df["name"].iloc[0] == "أحمد"
    assert df["city"].iloc[0] == "القاهرة"


def test_load_csv_case_insensitive_extension():
    f = _csv_file("a,b\n1,2\n", name="DATA.CSV")
    df = load_file(f)
    assert df["a"].tolist() == [1]


# ─── Excel ─────────────────────────────────────────────────────────────────

def test_load_xlsx():
    original = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
    f = _xlsx_file(original)
    df = load_file(f)
    pd.testing.assert_frame_equal(df, original)
