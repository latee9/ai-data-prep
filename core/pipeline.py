# core/pipeline.py
"""
Pipeline Builder: تسجيل خطوات التنظيف وإعادة تطبيقها على ملفات جديدة.
"""
import json
import os
import pandas as pd
import streamlit as st

PIPELINE_FILE = "pipelines.json"

# ─── تسجيل الخطوات ─────────────────────────────────────────────────────────

def init_pipeline():
    if "current_pipeline" not in st.session_state:
        st.session_state.current_pipeline = []
    if "pipeline_recording" not in st.session_state:
        st.session_state.pipeline_recording = False

def record_step(operation: str, params: dict = None):
    """تسجيل خطوة في الـ pipeline الحالي"""
    init_pipeline()
    if st.session_state.pipeline_recording:
        st.session_state.current_pipeline.append({
            "operation": operation,
            "params": params or {}
        })

def start_recording():
    init_pipeline()
    st.session_state.current_pipeline = []
    st.session_state.pipeline_recording = True

def stop_recording():
    init_pipeline()
    st.session_state.pipeline_recording = False

def get_current_pipeline() -> list:
    init_pipeline()
    return st.session_state.current_pipeline

# ─── حفظ وتحميل ────────────────────────────────────────────────────────────

def load_pipelines() -> dict:
    if os.path.exists(PIPELINE_FILE):
        with open(PIPELINE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_pipeline(name: str, steps: list) -> tuple:
    if not name or not name.strip():
        return False, "Pipeline name cannot be empty"
    if not steps:
        return False, "No steps recorded yet"
    pipelines = load_pipelines()
    pipelines[name.strip()] = steps
    with open(PIPELINE_FILE, "w", encoding="utf-8") as f:
        json.dump(pipelines, f, ensure_ascii=False, indent=2)
    return True, f"Pipeline '{name}' saved with {len(steps)} steps"

def delete_pipeline(name: str):
    pipelines = load_pipelines()
    if name in pipelines:
        del pipelines[name]
        with open(PIPELINE_FILE, "w", encoding="utf-8") as f:
            json.dump(pipelines, f, ensure_ascii=False, indent=2)

# ─── تطبيق pipeline ─────────────────────────────────────────────────────────

def apply_pipeline(df: pd.DataFrame, steps: list) -> tuple:
    """
    تطبيق قائمة الخطوات على df.
    يُرجع (df_result, applied_steps, failed_steps)
    """
    from core.data_cleaner import (
        remove_duplicates, fill_missing_numeric, fill_missing_text,
        standardize_dates, trim_whitespace, normalize_text_case
    )

    OPERATIONS = {
        "remove_duplicates":    lambda df, p: remove_duplicates(df)[0],
        "fill_missing_numeric": lambda df, p: fill_missing_numeric(df, p.get("strategy", "median")),
        "fill_missing_text":    lambda df, p: fill_missing_text(df, p.get("fill_value", "Unknown")),
        "standardize_dates":    lambda df, p: standardize_dates(df),
        "trim_whitespace":      lambda df, p: trim_whitespace(df),
        "normalize_case":       lambda df, p: normalize_text_case(df, mode=p.get("mode", "title")),
    }

    applied, failed = [], []
    for step in steps:
        op = step.get("operation")
        params = step.get("params", {})
        if op in OPERATIONS:
            try:
                df = OPERATIONS[op](df, params)
                applied.append(op)
            except Exception as e:
                failed.append(f"{op}: {e}")
        else:
            failed.append(f"Unknown operation: {op}")

    return df, applied, failed
