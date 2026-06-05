# ui/data_table.py
import streamlit as st
import pandas as pd


def render_data_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    عرض جدول بيانات تفاعلي مع:
    - فلترة الصفوف حسب قيمة عمود
    - البحث في النصوص
    - إعادة تسمية الأعمدة
    - حذف الأعمدة
    يُرجع df بعد أي تعديلات.
    """
    if df is None or df.empty:
        st.info("لا توجد بيانات لعرضها.")
        return df

    st.subheader("📋 عرض وتحرير البيانات")

    # ─── أدوات التعديل ───────────────────────────────────────────────────────
    with st.expander("✏️ إعادة تسمية عمود أو حذفه", expanded=False):
        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("**إعادة تسمية عمود**")
            old_name = st.selectbox("اختر العمود", df.columns.tolist(), key="rename_col")
            new_name = st.text_input("الاسم الجديد", key="new_col_name")
            if st.button("إعادة التسمية", key="btn_rename"):
                if new_name and new_name != old_name:
                    if new_name in df.columns:
                        st.error(f"الاسم '{new_name}' موجود بالفعل")
                    else:
                        df = df.rename(columns={old_name: new_name})
                        st.success(f"تمت إعادة التسمية: '{old_name}' → '{new_name}'")
                        st.rerun()
                else:
                    st.warning("أدخل اسماً مختلفاً")

        with col_b:
            st.markdown("**حذف عمود**")
            col_to_drop = st.selectbox("اختر العمود للحذف", df.columns.tolist(), key="drop_col")
            if st.button("🗑️ حذف العمود", key="btn_drop"):
                df = df.drop(columns=[col_to_drop])
                st.success(f"تم حذف العمود '{col_to_drop}'")
                st.rerun()

    # ─── فلترة الصفوف ────────────────────────────────────────────────────────
    with st.expander("🔎 فلترة الصفوف", expanded=False):
        filter_col = st.selectbox("اختر عمود للفلترة", ["(بدون فلترة)"] + df.columns.tolist(), key="filter_col")
        filtered_df = df.copy()

        if filter_col != "(بدون فلترة)":
            unique_vals = df[filter_col].dropna().unique().tolist()
            if len(unique_vals) <= 50:
                selected_vals = st.multiselect(
                    f"اختر القيم من '{filter_col}'",
                    options=unique_vals,
                    default=unique_vals[:5] if len(unique_vals) > 5 else unique_vals,
                    key="filter_vals"
                )
                if selected_vals:
                    filtered_df = df[df[filter_col].isin(selected_vals)]
            else:
                search_val = st.text_input(f"ابحث في '{filter_col}'", key="filter_text")
                if search_val:
                    filtered_df = df[df[filter_col].astype(str).str.contains(search_val, case=False, na=False)]

        st.caption(f"عرض {len(filtered_df):,} من أصل {len(df):,} صف")
        st.dataframe(filtered_df, use_container_width=True)

    # ─── عرض الجدول الرئيسي ──────────────────────────────────────────────────
    st.caption(f"إجمالي: {df.shape[0]:,} صف × {df.shape[1]} عمود")
    st.dataframe(df.head(100), use_container_width=True)
    if len(df) > 100:
        st.info(f"يُعرض أول 100 صف فقط من أصل {len(df):,}")

    return df
