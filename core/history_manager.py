# core/history_manager.py
import streamlit as st
import pandas as pd

def init_history():
    if "history" not in st.session_state:
        st.session_state.history = []  # قائمة من الـ snapshots
    if "current_index" not in st.session_state:
        st.session_state.current_index = -1

def save_snapshot(df: pd.DataFrame, operation_name: str):
    init_history()
    # نحذف أي "مستقبل" إذا كنا في منتصف التاريخ (بعد تراجع ثم عملية جديدة)
    st.session_state.history = st.session_state.history[:st.session_state.current_index + 1]
    st.session_state.history.append({
        "df": df.copy(),
        "name": operation_name,
        "timestamp": pd.Timestamp.now()
    })
    st.session_state.current_index = len(st.session_state.history) - 1

def undo(df: pd.DataFrame) -> pd.DataFrame:
    init_history()
    if st.session_state.current_index > 0:
        st.session_state.current_index -= 1
        return st.session_state.history[st.session_state.current_index]["df"].copy()
    return df

def get_history_list():
    init_history()
    return st.session_state.history