# ui/column_ops.py
"""
Column Operations: تقسيم عمود، دمج أعمدة، استخراج patterns، تغيير نوع البيانات.
"""
import streamlit as st
import pandas as pd
import re


def render_column_ops(df: pd.DataFrame) -> pd.DataFrame:
    st.subheader("🔧 Column Operations")

    op = st.radio(
        "Choose operation:",
        ["Split Column", "Merge Columns", "Extract Pattern (Regex)", "Change Data Type", "Remove Outliers"],
        horizontal=True,
        key="col_op_choice"
    )

    st.divider()

    # ── 1. تقسيم عمود ──────────────────────────────────────────────────────
    if op == "Split Column":
        col = st.selectbox("Column to split", df.select_dtypes(include="object").columns.tolist(), key="split_col")
        delimiter = st.text_input("Delimiter", value=",", key="split_delim")
        new_col_1 = st.text_input("Name for part 1", value=f"{col}_1", key="split_name1")
        new_col_2 = st.text_input("Name for part 2", value=f"{col}_2", key="split_name2")
        keep_original = st.checkbox("Keep original column", value=False, key="split_keep")

        if st.button("✂️ Split", use_container_width=True):
            try:
                split_df = df[col].astype(str).str.split(delimiter, n=1, expand=True)
                df = df.copy()
                df[new_col_1] = split_df[0].str.strip()
                df[new_col_2] = split_df[1].str.strip() if 1 in split_df.columns else ""
                if not keep_original:
                    df = df.drop(columns=[col])
                st.success(f"Split '{col}' into '{new_col_1}' and '{new_col_2}'")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    # ── 2. دمج عمودين ──────────────────────────────────────────────────────
    elif op == "Merge Columns":
        col_options = df.columns.tolist()
        col_a = st.selectbox("First column", col_options, key="merge_a")
        col_b = st.selectbox("Second column", col_options, index=min(1, len(col_options)-1), key="merge_b")
        separator = st.text_input("Separator", value=" ", key="merge_sep")
        new_name = st.text_input("New column name", value=f"{col_a}_{col_b}", key="merge_name")
        keep_originals = st.checkbox("Keep original columns", value=False, key="merge_keep")

        if st.button("🔗 Merge", use_container_width=True):
            try:
                df = df.copy()
                df[new_name] = df[col_a].astype(str) + separator + df[col_b].astype(str)
                if not keep_originals:
                    df = df.drop(columns=[c for c in [col_a, col_b] if c != new_name])
                st.success(f"Merged '{col_a}' + '{col_b}' into '{new_name}'")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    # ── 3. استخراج نمط Regex ──────────────────────────────────────────────
    elif op == "Extract Pattern (Regex)":
        col = st.selectbox("Column to extract from", df.select_dtypes(include="object").columns.tolist(), key="regex_col")
        pattern = st.text_input("Regex pattern", value=r"\d+", key="regex_pattern",
                                help="e.g. \\d+ for numbers, [A-Z]+ for uppercase words")
        new_col = st.text_input("New column name", value=f"{col}_extracted", key="regex_name")

        if pattern:
            try:
                preview = df[col].astype(str).str.extract(f"({pattern})", expand=False).head(5)
                st.caption("Preview (first 5 rows):")
                st.write(preview.tolist())
            except Exception:
                st.caption("Invalid pattern")

        if st.button("🔍 Extract", use_container_width=True):
            try:
                df = df.copy()
                df[new_col] = df[col].astype(str).str.extract(f"({pattern})", expand=False)
                st.success(f"Extracted pattern into '{new_col}'")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    # ── 4. تغيير نوع البيانات ──────────────────────────────────────────────
    elif op == "Change Data Type":
        col = st.selectbox("Column", df.columns.tolist(), key="cast_col")
        current_type = str(df[col].dtype)
        st.caption(f"Current type: `{current_type}`")
        target_type = st.selectbox("Cast to", ["int", "float", "string", "datetime", "boolean"], key="cast_type")

        if st.button("🔄 Convert", use_container_width=True):
            try:
                df = df.copy()
                if target_type == "int":
                    df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
                elif target_type == "float":
                    df[col] = pd.to_numeric(df[col], errors="coerce")
                elif target_type == "string":
                    df[col] = df[col].astype(str)
                elif target_type == "datetime":
                    df[col] = pd.to_datetime(df[col], errors="coerce")
                elif target_type == "boolean":
                    df[col] = df[col].map({"true": True, "false": False, "1": True, "0": False,
                                           "yes": True, "no": False, True: True, False: False})
                st.success(f"Converted '{col}' to {target_type}")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    # ── 5. إزالة القيم الشاذة ─────────────────────────────────────────────
    elif op == "Remove Outliers":
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        if not numeric_cols:
            st.info("No numeric columns available.")
        else:
            col = st.selectbox("Column", numeric_cols, key="outlier_col")
            method = st.radio("Method", ["Remove rows", "Cap (Winsorize)"], horizontal=True, key="outlier_method")

            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            outlier_count = ((df[col] < lower) | (df[col] > upper)).sum()

            st.info(f"Outliers in '{col}': **{outlier_count}** rows (range: {lower:.2f} – {upper:.2f})")

            if st.button("🎯 Apply", use_container_width=True, disabled=(outlier_count == 0)):
                df = df.copy()
                if method == "Remove rows":
                    df = df[(df[col] >= lower) & (df[col] <= upper)].reset_index(drop=True)
                    st.success(f"Removed {outlier_count} outlier rows from '{col}'")
                else:
                    df[col] = df[col].clip(lower=lower, upper=upper)
                    st.success(f"Capped outliers in '{col}' to [{lower:.2f}, {upper:.2f}]")
                st.rerun()

    return df
