# ui/confidence_display.py
import streamlit as st
import pandas as pd
from utils.validation import validate_dataframe


def render_confidence_display(df: pd.DataFrame):
    """
    عرض لوحة جودة البيانات مع نقاط الثقة ومؤشرات بصرية.
    """
    if df is None or df.empty:
        st.warning("لا توجد بيانات لعرض تقرير الجودة.")
        return

    result = validate_dataframe(df)
    score = result["score"]

    # ─── عنوان اللوحة ───────────────────────────────────────────────────────
    st.subheader("🎯 تقرير جودة البيانات")

    # ─── نقاط الجودة الكلية ──────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        color = "🟢" if score >= 80 else "🟡" if score >= 50 else "🔴"
        st.metric(f"{color} نقاط الجودة", f"{score}/100")
    with col2:
        st.metric("📋 عدد الصفوف", f"{result['rows']:,}")
    with col3:
        st.metric("📊 عدد الأعمدة", result["cols"])
    with col4:
        st.metric("🔁 مكررات", result["duplicates"])

    # ─── شريط التقدم ─────────────────────────────────────────────────────────
    st.progress(int(score) / 100)

    # ─── المشاكل الحرجة ───────────────────────────────────────────────────────
    if result["issues"]:
        with st.expander("🔴 مشاكل حرجة", expanded=True):
            for issue in result["issues"]:
                st.error(f"❌ {issue}")

    # ─── التحذيرات ────────────────────────────────────────────────────────────
    if result["warnings"]:
        with st.expander("🟡 تحذيرات", expanded=False):
            for warning in result["warnings"]:
                st.warning(f"⚠️ {warning}")

    # ─── تفصيل القيم المفقودة لكل عمود ──────────────────────────────────────
    missing_series = df.isnull().sum()
    missing_cols = missing_series[missing_series > 0]
    if not missing_cols.empty:
        with st.expander(f"🔍 تفصيل القيم المفقودة ({len(missing_cols)} عمود)", expanded=False):
            missing_df = pd.DataFrame({
                "العمود": missing_cols.index,
                "مفقود": missing_cols.values,
                "النسبة %": (missing_cols.values / len(df) * 100).round(1)
            }).sort_values("مفقود", ascending=False)
            st.dataframe(missing_df, use_container_width=True, hide_index=True)

    if not result["issues"] and not result["warnings"]:
        st.success("✅ البيانات نظيفة — لا توجد مشاكل مكتشفة!")
