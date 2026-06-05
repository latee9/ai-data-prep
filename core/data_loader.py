# core/data_loader.py
import pandas as pd
from pathlib import Path


def load_file(uploaded_file) -> pd.DataFrame:
    """
    Loads CSV or Excel file from Streamlit's UploadedFile object.
    Supports multiple encodings for CSV files.
    Returns pandas DataFrame.
    """
    if uploaded_file is None:
        return None

    file_extension = Path(uploaded_file.name).suffix.lower()

    if file_extension == ".csv":
        # محاولة عدة encodings لدعم الملفات العربية
        for encoding in ["utf-8", "utf-8-sig", "cp1256", "latin-1"]:
            try:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding=encoding)
                return df
            except (UnicodeDecodeError, Exception):
                continue
        raise ValueError("تعذّر قراءة الملف — جرّب حفظه بترميز UTF-8")

    elif file_extension in [".xlsx", ".xls"]:
        engine = "openpyxl" if file_extension == ".xlsx" else "xlrd"
        df = pd.read_excel(uploaded_file, engine=engine)
        return df

    else:
        raise ValueError(f"نوع الملف '{file_extension}' غير مدعوم. استخدم CSV أو Excel.")