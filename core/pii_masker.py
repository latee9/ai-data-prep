# core/pii_masker.py
"""
PII Detection & Masking: كشف وإخفاء البيانات الشخصية الحساسة (GDPR-ready).
"""
import re
import hashlib
import pandas as pd

# ─── أنماط الكشف ────────────────────────────────────────────────────────────

PII_PATTERNS = {
    "email":   r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
    "phone":   r"(\+?\d[\d\s\-\(\)]{7,14}\d)",
    "credit_card": r"\b(?:\d[ -]?){13,16}\b",
    "ip_address":  r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    "national_id": r"\b\d{10,14}\b",
}

PII_LABELS = {
    "email":       "📧 Email",
    "phone":       "📱 Phone",
    "credit_card": "💳 Credit Card",
    "ip_address":  "🌐 IP Address",
    "national_id": "🪪 National ID",
}

# ─── كشف ────────────────────────────────────────────────────────────────────

def detect_pii_columns(df: pd.DataFrame) -> dict:
    """
    يفحص كل عمود نصي ويُرجع:
    { col_name: [list of detected PII types] }
    """
    results = {}
    for col in df.select_dtypes(include="object").columns:
        sample = df[col].dropna().astype(str).head(100)
        found_types = []
        for pii_type, pattern in PII_PATTERNS.items():
            matches = sample.str.contains(pattern, regex=True, na=False).sum()
            if matches >= max(1, len(sample) * 0.1):  # 10% أو أكثر
                found_types.append(pii_type)
        if found_types:
            results[col] = found_types
    return results

# ─── إخفاء ───────────────────────────────────────────────────────────────────

def mask_column(df: pd.DataFrame, col: str, method: str = "mask") -> pd.DataFrame:
    """
    إخفاء قيم عمود بأحد الأساليب:
    - mask:  استبدال بـ ***
    - hash:  تشفير SHA-256 (مفيد للمقارنة)
    - remove: حذف العمود كلياً
    - partial: إظهار أول 2 وآخر 2 حرف فقط
    """
    df_out = df.copy()
    if col not in df_out.columns:
        return df_out

    if method == "mask":
        df_out[col] = df_out[col].apply(
            lambda x: "***" if pd.notna(x) else x
        )
    elif method == "hash":
        df_out[col] = df_out[col].apply(
            lambda x: hashlib.sha256(str(x).encode()).hexdigest()[:12] if pd.notna(x) else x
        )
    elif method == "remove":
        df_out = df_out.drop(columns=[col])
    elif method == "partial":
        def partial_mask(val):
            s = str(val)
            if len(s) <= 4:
                return "***"
            return s[:2] + "*" * (len(s) - 4) + s[-2:]
        df_out[col] = df_out[col].apply(
            lambda x: partial_mask(x) if pd.notna(x) else x
        )

    return df_out


def mask_pii_in_column(df: pd.DataFrame, col: str, pii_types: list, method: str = "mask") -> pd.DataFrame:
    """إخفاء أنماط PII محددة داخل عمود (بدلاً من مسح القيمة كلها)"""
    df_out = df.copy()
    for pii_type in pii_types:
        if pii_type not in PII_PATTERNS:
            continue
        pattern = PII_PATTERNS[pii_type]
        if method == "mask":
            df_out[col] = df_out[col].astype(str).str.replace(pattern, "***", regex=True)
        elif method == "partial":
            def partial_replace(m):
                s = m.group()
                return s[:2] + "*" * max(0, len(s)-4) + s[-2:] if len(s) > 4 else "***"
            df_out[col] = df_out[col].astype(str).str.replace(pattern, partial_replace, regex=True)
    return df_out
