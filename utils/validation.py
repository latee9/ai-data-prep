# utils/validation.py
import pandas as pd
from typing import Optional

def validate_dataframe(df: pd.DataFrame) -> dict:
    """
    تحقق شامل من جودة DataFrame.
    يُرجع dict يحتوي على:
      - is_valid: هل البيانات مقبولة؟
      - issues: قائمة بالمشاكل المكتشفة
      - warnings: تحذيرات غير حرجة
      - score: نسبة جودة البيانات (0-100)
    """
    issues = []
    warnings = []

    if df is None or df.empty:
        return {"is_valid": False, "issues": ["DataFrame فارغ أو None"], "warnings": [], "score": 0}

    total_cells = df.shape[0] * df.shape[1]

    # --- مشاكل حرجة ---
    if df.shape[0] == 0:
        issues.append("لا توجد صفوف في البيانات")
    if df.shape[1] == 0:
        issues.append("لا توجد أعمدة في البيانات")

    # --- قيم مفقودة ---
    missing_pct = df.isnull().sum().sum() / total_cells * 100
    if missing_pct > 50:
        issues.append(f"نسبة القيم المفقودة مرتفعة جداً: {missing_pct:.1f}%")
    elif missing_pct > 20:
        warnings.append(f"نسبة القيم المفقودة: {missing_pct:.1f}%")

    # --- مكررات ---
    dup_count = df.duplicated().sum()
    dup_pct = dup_count / len(df) * 100
    if dup_pct > 30:
        warnings.append(f"نسبة الصفوف المكررة: {dup_pct:.1f}% ({dup_count} صف)")
    elif dup_count > 0:
        warnings.append(f"يوجد {dup_count} صف مكرر")

    # --- أعمدة بدون بيانات ---
    empty_cols = df.columns[df.isnull().all()].tolist()
    if empty_cols:
        warnings.append(f"أعمدة فارغة تماماً: {empty_cols}")

    # --- أعمدة بنوع object فيها أرقام ---
    for col in df.select_dtypes(include="object").columns:
        try:
            pd.to_numeric(df[col].dropna(), errors="raise")
            warnings.append(f"العمود '{col}' يحتوي أرقاماً لكنه من نوع text")
        except Exception:
            pass

    # --- احتساب نقاط الجودة ---
    deductions = len(issues) * 20 + len(warnings) * 5 + min(missing_pct, 40)
    score = max(0, 100 - deductions)

    return {
        "is_valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "score": round(score, 1),
        "rows": df.shape[0],
        "cols": df.shape[1],
        "missing_pct": round(missing_pct, 2),
        "duplicates": int(dup_count),
    }


def validate_column_name(name: str) -> tuple:
    """التحقق من أن اسم العمود صالح"""
    if not name or not name.strip():
        return False, "اسم العمود لا يمكن أن يكون فارغاً"
    if len(name) > 100:
        return False, "اسم العمود طويل جداً (الحد 100 حرف)"
    return True, ""


def validate_python_code(code: str) -> tuple:
    """التحقق من صياغة كود Python قبل تنفيذه"""
    if not code or not code.strip():
        return False, "الكود فارغ"
    try:
        compile(code, "<string>", "exec")
        return True, ""
    except SyntaxError as e:
        return False, f"خطأ في الصياغة: {e}"
