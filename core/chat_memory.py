# core/chat_memory.py
import streamlit as st

def init_chat_memory():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []  # يخزن الأوامر السابقة والنتائج

def add_to_memory(user_query: str, executed_code: str, success: bool):
    init_chat_memory()
    st.session_state.chat_history.append({
        "query": user_query,
        "code": executed_code,
        "success": success
    })
    # الاحتفاظ بآخر 5 محادثات فقط للسياق
    if len(st.session_state.chat_history) > 5:
        st.session_state.chat_history.pop(0)

def get_chat_context() -> str:
    init_chat_memory()
    if not st.session_state.chat_history:
        return ""
    context = "Previous commands and their generated code:\n"
    for item in st.session_state.chat_history[-3:]:  # آخر 3
        context += f"- User: {item['query']}\n  Code: {item['code']}\n"
    return context