# core/llm_interface.py
import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
from core.chat_memory import get_chat_context

load_dotenv()

def _get_api_key() -> str:
    """يقرأ الـ API Key من .env (محلي) أو st.secrets (سحابي)"""
    # 1. من .env (للتطوير المحلي)
    key = os.getenv("GEMINI_API_KEY", "")
    if key:
        return key
    # 2. من Streamlit Secrets (للنشر السحابي)
    try:
        key = st.secrets.get("GEMINI_API_KEY", "")
        if key:
            return key
    except Exception:
        pass
    return ""

API_KEY = _get_api_key()
if API_KEY:
    genai.configure(api_key=API_KEY)

# ─── الكلمات الخطرة المحظورة في الكود المُنفَّذ ─────────────────────────────
_FORBIDDEN_PATTERNS = [
    "import os", "import sys", "import subprocess", "import shutil",
    "__import__", "open(", "exec(", "eval(", "compile(",
    "os.remove", "os.rmdir", "shutil.rmtree", "subprocess",
]

def _is_safe_code(code: str) -> tuple:
    """التحقق من أن الكود لا يحتوي عمليات خطرة"""
    code_lower = code.lower()
    for pattern in _FORBIDDEN_PATTERNS:
        if pattern.lower() in code_lower:
            return False, f"الكود يحتوي عملية غير مسموحة: `{pattern}`"
    # فحص صياغة Python
    try:
        compile(code, "<string>", "exec")
    except SyntaxError as e:
        return False, f"خطأ في الصياغة: {e}"
    return True, ""


def _clean_code_response(code: str) -> str:
    """إزالة markdown code fences من الاستجابة"""
    code = code.strip()
    if code.startswith("```python"):
        code = code[9:]
    elif code.startswith("```"):
        code = code[3:]
    if code.endswith("```"):
        code = code[:-3]
    return code.strip()


def get_python_code_from_query(user_query: str, df: pd.DataFrame) -> str:
    if not API_KEY:
        return "# لم يتم ضبط GEMINI_API_KEY في ملف .env\ndf = df"

    sample_columns = ", ".join(df.columns[:10].tolist())
    sample_data = df.head(3).to_string()
    chat_context = get_chat_context()

    prompt = f"""
You are an expert data cleaning assistant. Convert the user's natural language command into Python code using pandas.
The code must only modify a DataFrame variable named 'df' and must be safe to execute.

Previous conversation context (if any):
{chat_context}

Current user command: "{user_query}"

DataFrame info:
- Columns: {sample_columns}
- First 3 rows:
{sample_data}

Rules:
- Return ONLY valid Python code. No explanations. No markdown.
- Only use pandas (pd) and the existing 'df' variable.
- Never import os, sys, subprocess or access the filesystem.
- If the command is ambiguous, make a reasonable guess.
- Keep the code concise.

Examples:
User: "remove duplicate rows"
Code: df = df.drop_duplicates()

User: "convert date column to datetime"
Code: df['date'] = pd.to_datetime(df['date'])

User: "fill missing values in age with median"
Code: df['age'] = df['age'].fillna(df['age'].median())

Now generate the code:
"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        code = _clean_code_response(response.text)
        return code
    except Exception as e:
        return f"# خطأ في الاتصال بـ Gemini: {e}\ndf = df"


def execute_code_safely(code: str, df: pd.DataFrame) -> pd.DataFrame:
    """تنفيذ الكود بعد التحقق من سلامته"""
    is_safe, reason = _is_safe_code(code)
    if not is_safe:
        st.error(f"🚫 تم رفض الكود: {reason}")
        return df

    env = {'pd': pd, 'df': df.copy()}
    try:
        exec(code, env)
        result = env.get('df', df)
        if isinstance(result, pd.DataFrame):
            return result
        return df
    except Exception as e:
        st.error(f"خطأ في تنفيذ الكود: {e}")
        return df
