# core/data_cleaner.py
import pandas as pd


def remove_duplicates(df: pd.DataFrame, subset=None, keep='first') -> tuple:
    """إزالة الصفوف المكررة مع إعادة ضبط الـ index"""
    before = len(df)
    df_clean = df.drop_duplicates(subset=subset, keep=keep).reset_index(drop=True)
    after = len(df_clean)
    return df_clean, {"removed_duplicates": before - after}


def fill_missing_numeric(df: pd.DataFrame, strategy: str = 'median') -> pd.DataFrame:
    """ملء القيم المفقودة في الأعمدة الرقمية — يتخطى الأعمدة الكاملة"""
    df_filled = df.copy()
    numeric_cols = df_filled.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        if df_filled[col].isnull().any():
            if strategy == 'median':
                df_filled[col] = df_filled[col].fillna(df_filled[col].median())
            elif strategy == 'mean':
                df_filled[col] = df_filled[col].fillna(df_filled[col].mean())
            else:
                df_filled[col] = df_filled[col].fillna(0)
    return df_filled


def fill_missing_text(df: pd.DataFrame, fill_value: str = "Unknown") -> pd.DataFrame:
    """ملء القيم المفقودة في الأعمدة النصية"""
    df_filled = df.copy()
    for col in df_filled.select_dtypes(include=["object", "string"]).columns:
        df_filled[col] = df_filled[col].fillna(fill_value)
    return df_filled


def standardize_dates(df: pd.DataFrame, date_cols=None) -> pd.DataFrame:
    """تحويل أعمدة التواريخ إلى تنسيق موحد — اكتشاف تلقائي أو محدد"""
    df_dates = df.copy()
    if date_cols is None:
        for col in df_dates.select_dtypes(exclude="number").columns:
            try:
                converted = pd.to_datetime(df_dates[col], errors="coerce")
                if converted.notna().mean() >= 0.8:
                    df_dates[col] = converted
            except Exception:
                pass
    else:
        for col in date_cols:
            if col in df_dates.columns:
                df_dates[col] = pd.to_datetime(df_dates[col], errors='coerce')
    return df_dates


def trim_whitespace(df: pd.DataFrame) -> pd.DataFrame:
    """إزالة المسافات الزائدة من القيم النصية"""
    df_trimmed = df.copy()
    for col in df_trimmed.select_dtypes(include=["object"]).columns:
        df_trimmed[col] = df_trimmed[col].str.strip()
    return df_trimmed


def normalize_text_case(df: pd.DataFrame, columns: list = None, mode: str = "title") -> pd.DataFrame:
    """توحيد حالة الأحرف النصية (title / lower / upper)"""
    df_norm = df.copy()
    cols = columns if columns else df_norm.select_dtypes(include=["object"]).columns.tolist()
    for col in cols:
        if col in df_norm.columns:
            if mode == "title":
                df_norm[col] = df_norm[col].str.title()
            elif mode == "lower":
                df_norm[col] = df_norm[col].str.lower()
            elif mode == "upper":
                df_norm[col] = df_norm[col].str.upper()
    return df_norm
