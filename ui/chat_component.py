# ui/chat_component.py
import streamlit as st
from core.llm_interface import get_python_code_from_query, execute_code_safely
from core.history_manager import save_snapshot
from core.chat_memory import add_to_memory
from utils.i18n import get_text

def render_chat_interface(df):
    st.markdown(f"## {get_text('chat_tab')}")
    st.caption("Type your command in any language (English, Arabic, French, etc.)")

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    for msg in st.session_state.chat_messages:
        avatar = "🧑‍💻" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    if prompt := st.chat_input(get_text("chat_placeholder")):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner(get_text("chat_processing")):
                code = get_python_code_from_query(prompt, df)
                new_df = execute_code_safely(code, df)
                if new_df is not None and not new_df.equals(df):
                    add_to_memory(prompt, code, success=True)
                    save_snapshot(new_df, f"Chat: {prompt[:50]}")
                    st.session_state.df = new_df
                    df = new_df
                    st.success(get_text("chat_success"))
                    st.write(f"**{get_text('chat_code_executed')}**")
                    st.code(code, language='python')
                else:
                    add_to_memory(prompt, code, success=False)
                    st.warning(get_text("chat_no_change"))
                    st.code(code, language='python')
        st.session_state.chat_messages.append({"role": "assistant", "content": "Done."})
        st.rerun()
    return df