# core/advanced_analysis.py
import pandas as pd
import plotly.express as px
import streamlit as st


def show_advanced_stats(df: pd.DataFrame):
    """عرض إحصائيات وصفية شاملة"""
    st.subheader("📈 إحصائيات وصفية")
    st.dataframe(df.describe(include='all'), use_container_width=True)


def detect_outliers_iqr(df: pd.DataFrame, column: str) -> tuple:
    """اكتشاف القيم الشاذة باستخدام IQR"""
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    outliers = df[(df[column] < lower) | (df[column] > upper)]
    return outliers, lower, upper


def plot_numeric_columns(df: pd.DataFrame):
    """رسم بياني لتوزيع الأعمدة الرقمية مع اكتشاف القيم الشاذة"""
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    if not numeric_cols:
        st.info("لا توجد أعمدة رقمية للرسم البياني")
        return

    col1, col2 = st.columns([2, 1])
    with col1:
        selected = st.selectbox("اختر عموداً رقمياً", numeric_cols, key="plot_col")
    with col2:
        chart_type = st.selectbox("نوع الرسم", ["Histogram", "Box Plot"], key="chart_type")

    if chart_type == "Histogram":
        fig = px.histogram(df, x=selected, title=f"توزيع {selected}", nbins=30)
    else:
        fig = px.box(df, y=selected, title=f"Box Plot - {selected}")

    st.plotly_chart(fig, use_container_width=True)

    outliers, low, up = detect_outliers_iqr(df, selected)
    if not outliers.empty:
        st.warning(f"⚠️ عدد القيم الشاذة في '{selected}': **{len(outliers)}** (النطاق: {low:.2f} – {up:.2f})")
        with st.expander("عرض القيم الشاذة"):
            st.dataframe(outliers[[selected]], use_container_width=True)
    else:
        st.success(f"✅ لا توجد قيم شاذة في '{selected}'")


def show_correlation_heatmap(df: pd.DataFrame):
    """عرض خريطة الارتباط بين الأعمدة الرقمية"""
    numeric_df = df.select_dtypes(include='number')
    if numeric_df.shape[1] < 2:
        st.info("يلزم عمودان رقميان على الأقل لعرض الارتباط")
        return
    corr = numeric_df.corr()
    fig = px.imshow(
        corr, text_auto=".2f", color_continuous_scale="RdBu_r",
        title="خريطة الارتباط (Correlation Heatmap)", zmin=-1, zmax=1
    )
    st.plotly_chart(fig, use_container_width=True)
