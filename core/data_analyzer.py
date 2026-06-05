# core/data_analyzer.py
import pandas as pd

def get_basic_info(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns a DataFrame with column names, data types, missing count, unique count.
    """
    info = pd.DataFrame({
        "Column": df.columns,
        "Data Type": df.dtypes.values,
        "Missing Values": df.isnull().sum().values,
        "Missing %": (df.isnull().sum() / len(df) * 100).values,
        "Unique Values": df.nunique().values
    })
    return info

def detect_date_columns(df: pd.DataFrame) -> list:
    """
    Tries to guess which columns contain dates.
    Skips numeric columns to avoid false positives.
    """
    date_cols = []
    for col in df.select_dtypes(exclude="number").columns:
        try:
            sample = df[col].dropna().head(50)
            converted = pd.to_datetime(sample, errors="coerce")
            # نعتبره عمود تواريخ إذا تحوّل 80%+ بنجاح
            if converted.notna().mean() >= 0.8:
                date_cols.append(col)
        except Exception:
            pass
    return date_cols