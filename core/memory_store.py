# core/memory_store.py
import json
import os
import pandas as pd

RULES_FILE = "user_rules.json"

# ─── الكلمات الخطرة المحظورة في القواعد المحفوظة ────────────────────────────
_FORBIDDEN = ["import os", "import sys", "import subprocess", "open(", "__import__"]


def load_rules() -> dict:
    if os.path.exists(RULES_FILE):
        with open(RULES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_rule(rule_name: str, rule_code: str) -> tuple:
    """حفظ قاعدة مع فحص أمان بسيط"""
    if not rule_name or not rule_name.strip():
        return False, "اسم القاعدة لا يمكن أن يكون فارغاً"
    for pattern in _FORBIDDEN:
        if pattern in rule_code:
            return False, f"الكود يحتوي عملية غير مسموحة: `{pattern}`"
    try:
        compile(rule_code, "<string>", "exec")
    except SyntaxError as e:
        return False, f"خطأ في صياغة الكود: {e}"
    rules = load_rules()
    rules[rule_name.strip()] = rule_code
    with open(RULES_FILE, 'w', encoding='utf-8') as f:
        json.dump(rules, f, ensure_ascii=False, indent=2)
    return True, "تم حفظ القاعدة"


def delete_rule(rule_name: str) -> tuple:
    rules = load_rules()
    if rule_name not in rules:
        return False, "القاعدة غير موجودة"
    del rules[rule_name]
    with open(RULES_FILE, 'w', encoding='utf-8') as f:
        json.dump(rules, f, ensure_ascii=False, indent=2)
    return True, "تم حذف القاعدة"


def apply_saved_rules(df: pd.DataFrame) -> pd.DataFrame:
    """تطبيق القواعد المحفوظة على DataFrame — يتخطى أي قاعدة فاشلة"""
    rules = load_rules()
    for name, code in rules.items():
        try:
            env = {'df': df.copy(), 'pd': pd}
            exec(code, env)
            result = env.get('df')
            if isinstance(result, pd.DataFrame):
                df = result
        except Exception:
            pass  # تجاهل القواعد الفاشلة
    return df
