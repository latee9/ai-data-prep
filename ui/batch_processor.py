import streamlit as st
import pandas as pd
import zipfile
import io
from pathlib import Path

def process_batch(uploaded_files, cleaning_function):
    results = {}
    for file in uploaded_files:
        try:
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            cleaned_df = cleaning_function(df)
            results[file.name] = cleaned_df
        except Exception as e:
            results[file.name] = str(e)
    return results

def render_batch_ui(cleaning_function):
    st.subheader("📁 معالجة دفعات (مجموعة ملفات)")
    uploaded_files = st.file_uploader("اختر عدة ملفات CSV/Excel", type=["csv","xlsx","xls"], accept_multiple_files=True)
    if uploaded_files and st.button("معالجة الكل"):
        with st.spinner("جاري معالجة الملفات..."):
            results = process_batch(uploaded_files, cleaning_function)
            for name, data in results.items():
                if isinstance(data, pd.DataFrame):
                    st.success(f"{name}: {data.shape}")
                    csv = data.to_csv(index=False).encode()
                    st.download_button(f"تحميل {name}", data=csv, file_name=f"cleaned_{name}", mime="text/csv")
                else:
                    st.error(f"{name}: {data}")