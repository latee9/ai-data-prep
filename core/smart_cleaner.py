# core/smart_cleaner.py
"""
Smart Auto-Clean: يحلل البيانات تلقائياً ويطبق كل التنظيف المناسب بزر واحد.
"""
import pandas as pd
from core.data_cleaner import (
    remove_duplicates, fill_missing_numeric, fill_missing_text,
    standardize_dates, trim_whitespace
)
from utils.validation import validate_dataframe


def smart_clean(df: pd.DataFrame) -> tuple:
    """
    يحلل df ويطبق كل خطوات التنظيف المناسبة تلقائياً.
    يُرجع (df_clean, report) حيث report قائمة بما تم.
    """
    report = []
    df_clean = df.copy()
    before_rows = len(df_clean)

    # ── 1. إزالة المسافات الزائدة من النصوص ──────────────────────────────────
    # (تُنفَّذ قبل إزالة التكرار حتى لا تُخفي المسافات الزائدة صفوفاً مكررة فعلياً)
    text_cols = df_clean.select_dtypes(include="object").columns
    if len(text_cols) > 0:
        df_clean = trim_whitespace(df_clean)
        report.append(f"✅ Trimmed whitespace in **{len(text_cols)}** text columns")

    # ── 2. إزالة الصفوف المكررة ──────────────────────────────────────────────
    dup_count = df_clean.duplicated().sum()
    if dup_count > 0:
        df_clean, _ = remove_duplicates(df_clean)
        report.append(f"✅ Removed **{dup_count}** duplicate rows")

    # ── 3. توحيد التواريخ ─────────────────────────────────────────────────────
    date_cols_found = []
    for col in df_clean.select_dtypes(exclude="number").columns:
        try:
            converted = pd.to_datetime(df_clean[col], errors="coerce")
            if converted.notna().mean() >= 0.8 and df_clean[col].dtype == object:
                df_clean[col] = converted
                date_cols_found.append(col)
        except Exception:
            pass
    if date_cols_found:
        report.append(f"✅ Standardized dates in: **{', '.join(date_cols_found)}**")

    # ── 4. ملء القيم المفقودة الرقمية (median) ───────────────────────────────
    missing_numeric = df_clean.select_dtypes(include="number").isnull().sum()
    cols_with_missing = missing_numeric[missing_numeric > 0]
    if not cols_with_missing.empty:
        df_clean = fill_missing_numeric(df_clean, strategy="median")
        report.append(
            f"✅ Filled missing numeric values (median) in: **{', '.join(cols_with_missing.index.tolist())}**"
        )

    # ── 5. ملء القيم المفقودة النصية بـ "Unknown" ────────────────────────────
    missing_text = df_clean.select_dtypes(include="object").isnull().sum()
    text_cols_missing = missing_text[missing_text > 0]
    if not text_cols_missing.empty:
        df_clean = fill_missing_text(df_clean, fill_value="Unknown")
        report.append(
            f"✅ Filled missing text values with 'Unknown' in: **{', '.join(text_cols_missing.index.tolist())}**"
        )

    # ── 6. تقرير النتيجة ──────────────────────────────────────────────────────
    after_rows = len(df_clean)
    if not report:
        report.append("✨ Data is already clean — no issues found!")
    else:
        report.insert(0, f"**Smart Clean Summary** ({before_rows} → {after_rows} rows):")

    return df_clean, report
