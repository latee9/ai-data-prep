import streamlit as st
import io
import os
import pandas as pd

from ui.styles import (
    inject_css, render_hero,
    render_sidebar_brand, render_sidebar_user,
    render_sidebar_section, render_recording_badge,
    render_sidebar_stats
)
from core.data_loader import load_file
from core.data_analyzer import get_basic_info
from core.data_cleaner import (
    remove_duplicates, fill_missing_numeric, fill_missing_text,
    standardize_dates, trim_whitespace, normalize_text_case
)
from core.smart_cleaner import smart_clean
from core.pipeline import (
    init_pipeline, start_recording, stop_recording, record_step,
    get_current_pipeline, save_pipeline, load_pipelines,
    delete_pipeline, apply_pipeline
)
from core.pii_masker import detect_pii_columns, mask_column, mask_pii_in_column, PII_LABELS
from ui.chat_component import render_chat_interface
from ui.confidence_display import render_confidence_display
from ui.data_table import render_data_table
from ui.column_ops import render_column_ops
from core.history_manager import save_snapshot, undo, get_history_list
from core.advanced_analysis import show_advanced_stats, plot_numeric_columns, show_correlation_heatmap
from core.memory_store import apply_saved_rules, save_rule, delete_rule, load_rules
from ui.batch_processor import render_batch_ui
from utils.i18n import get_text, set_language, get_languages, DEFAULT_LANGUAGE
from utils.auth import check_password, logout, change_password
from utils.user_manager import migrate_plain_passwords

# ── بدء التطبيق ──────────────────────────────────────────────────────────────
migrate_plain_passwords()
init_pipeline()

if not check_password():
    st.stop()

if "language" not in st.session_state:
    st.session_state.language = DEFAULT_LANGUAGE

st.set_page_config(
    page_title="AI Data Prep",
    page_icon="🧹",
    layout="wide",
    initial_sidebar_state="expanded"
)
inject_css()

# ── الشريط الجانبي ────────────────────────────────────────────────────────────
with st.sidebar:
    # ── Brand ────────────────────────────────────────────────────────────
    render_sidebar_brand()

    # ── Language ──────────────────────────────────────────────────────────
    render_sidebar_section("🌐 Language")
    lang = st.selectbox(
        "", get_languages(),
        index=get_languages().index(st.session_state.language),
        label_visibility="collapsed"
    )
    if lang != st.session_state.language:
        set_language(lang)
        st.rerun()

    st.divider()

    # ── User profile ─────────────────────────────────────────────────────
    if st.session_state.get("authenticated", False):
        render_sidebar_user(st.session_state.username)

        c1, c2 = st.columns(2)
        with c1:
            with st.popover("🔑 Password"):
                old_pw = st.text_input("Current", type="password", key="old_pw")
                new_pw = st.text_input("New", type="password", key="new_pw")
                conf_pw = st.text_input("Confirm", type="password", key="conf_pw")
                if st.button("Update", use_container_width=True):
                    ok, msg = change_password(st.session_state.username, old_pw, new_pw, conf_pw)
                    (st.success if ok else st.error)(msg)
                    if ok:
                        logout()
        with c2:
            if st.button("🚪 Logout", use_container_width=True):
                logout()

        st.divider()

    # ── Dataset mini-stats ────────────────────────────────────────────────
    if st.session_state.get("df") is not None:
        render_sidebar_stats(st.session_state.df)
        st.divider()

    # ── Pipeline recording ────────────────────────────────────────────────
    render_sidebar_section("⚡ Pipeline")
    if st.session_state.get("pipeline_recording", False):
        render_recording_badge()
        steps_count = len(get_current_pipeline())
        st.caption(f"{steps_count} step(s) recorded")
        if st.button("⏹ Stop Recording", use_container_width=True):
            stop_recording()
            st.rerun()
    else:
        if st.button("⏺ Start Recording", use_container_width=True):
            start_recording()
            st.rerun()

    st.divider()

    # ── Data Source ───────────────────────────────────────────────────────
    render_sidebar_section(f"📂 {get_text('data_source')}")
    source = st.radio(
        "",
        [
            get_text("upload_file"),
            get_text("database"),
            "Google Sheets",
            "BigQuery",
            "MongoDB",
            "REST API",
            get_text("batch_processing"),
        ],
        label_visibility="collapsed"
    )

    # ── Feedback ──────────────────────────────────────────────────────────
    st.divider()
    render_sidebar_section("💬 Feedback")
    FORM_URL = st.secrets.get(
        "FEEDBACK_FORM_URL",
        "https://docs.google.com/forms/d/e/1FAIpQLSdU0Gu2RJdLwDgEisTgl2bd_8TDJOQSNelywwaQuN2IFIY99g/viewform",
    )
    st.markdown(f"""
<a href="{FORM_URL}" target="_blank" style="
    display:flex; align-items:center; justify-content:center; gap:.5rem;
    background:linear-gradient(135deg,rgba(108,99,255,.15),rgba(108,99,255,.05));
    border:1px solid rgba(108,99,255,.3); border-radius:10px;
    padding:.55rem 1rem; color:rgba(255,255,255,.75);
    font-size:.84rem; font-weight:500; text-decoration:none;
    transition:all .2s; margin:.2rem .3rem;
">
    ⭐ Rate & Give Feedback
</a>
""", unsafe_allow_html=True)

    with st.expander("📝 Quick feedback", expanded=False):
        rating = st.select_slider(
            "How would you rate the app?",
            options=["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"],
            value="⭐⭐⭐⭐⭐",
            key="rating_slider"
        )
        feedback_text = st.text_area(
            "Your feedback (optional)",
            placeholder="What do you love? What's missing?",
            key="feedback_text", height=80
        )
        if st.button("Send Feedback ✉️", use_container_width=True, key="send_feedback"):
            import json, datetime
            fb = {"rating": rating, "text": feedback_text,
                  "time": str(datetime.datetime.now())}
            feedbacks = []
            if os.path.exists("feedbacks.json"):
                with open("feedbacks.json") as f:
                    feedbacks = json.load(f)
            feedbacks.append(fb)
            with open("feedbacks.json", "w") as f:
                json.dump(feedbacks, f, ensure_ascii=False, indent=2)
            st.success("Thank you! 🙏")

# ── عنوان التطبيق ─────────────────────────────────────────────────────────────
render_hero(get_text("app_title"), get_text("app_subtitle"))

# ── تهيئة الجلسة ──────────────────────────────────────────────────────────────
for key in ["df", "file_name"]:
    if key not in st.session_state:
        st.session_state[key] = None

# ── تحميل البيانات ────────────────────────────────────────────────────────────

if source == get_text("upload_file"):
    uploaded_file = st.file_uploader(get_text("upload_prompt"), type=["csv", "xlsx", "xls"])
    if uploaded_file and st.session_state.file_name != uploaded_file.name:
        with st.spinner(get_text("loading")):
            st.session_state.df = load_file(uploaded_file)
            st.session_state.file_name = uploaded_file.name
            st.session_state.df = apply_saved_rules(st.session_state.df)
            save_snapshot(st.session_state.df, f"Upload: {uploaded_file.name}")

elif source == get_text("database"):
    with st.sidebar:
        st.subheader("Database Connection")
        db_type = st.selectbox("Type", ["PostgreSQL", "MySQL"])
        host = st.text_input("Host", "localhost")
        port = st.text_input("Port", "5432" if db_type == "PostgreSQL" else "3306")
        db_name = st.text_input("Database Name")
        user = st.text_input("User")
        password = st.text_input("Password", type="password")
        tq = st.radio("", ["Table", "SQL Query"])
        if tq == "Table":
            table_name = st.text_input("Table Name")
            if st.button("Load Table"):
                try:
                    from connectors.database_connector import connect_db, load_table
                    engine = connect_db(db_type, host, port, db_name, user, password)
                    st.session_state.df = load_table(engine, table_name)
                    save_snapshot(st.session_state.df, "Loaded from DB")
                    st.success(get_text("success")); st.rerun()
                except Exception as e:
                    st.error(f"{get_text('error')}: {e}")
        else:
            query = st.text_area("SQL Query")
            if st.button("Execute"):
                try:
                    from connectors.database_connector import connect_db, load_query
                    engine = connect_db(db_type, host, port, db_name, user, password)
                    st.session_state.df = load_query(engine, query)
                    save_snapshot(st.session_state.df, "SQL Query")
                    st.success(get_text("success")); st.rerun()
                except Exception as e:
                    st.error(f"{get_text('error')}: {e}")

elif source == "Google Sheets":
    with st.sidebar:
        st.subheader("Google Sheets")
        sheet_url = st.text_input("Sheet URL or ID")
        worksheet = st.text_input("Worksheet", "Sheet1")
        if st.button("Load Sheet"):
            try:
                from connectors.google_sheets_connector import load_google_sheet
                df_gs = load_google_sheet(sheet_url, worksheet)
                if df_gs is not None:
                    st.session_state.df = df_gs
                    save_snapshot(st.session_state.df, "Google Sheets")
                    st.success(get_text("success")); st.rerun()
            except Exception as e:
                st.error(f"{get_text('error')}: {e}")

elif source == "BigQuery":
    with st.sidebar:
        st.subheader("BigQuery")
        query = st.text_area("SQL Query")
        if st.button("Run Query"):
            try:
                from connectors.bigquery_connector import run_bigquery_query
                df_bq = run_bigquery_query(query)
                if df_bq is not None:
                    st.session_state.df = df_bq
                    save_snapshot(st.session_state.df, "BigQuery")
                    st.success(get_text("success")); st.rerun()
            except Exception as e:
                st.error(f"{get_text('error')}: {e}")

elif source == "MongoDB":
    with st.sidebar:
        st.subheader("MongoDB")
        uri = st.text_input("URI", "mongodb://localhost:27017")
        db_mg = st.text_input("Database")
        coll = st.text_input("Collection")
        if st.button("Load"):
            try:
                from connectors.mongodb_connector import load_mongodb_collection
                df_mg = load_mongodb_collection(uri, db_mg, coll)
                if df_mg is not None:
                    st.session_state.df = df_mg
                    save_snapshot(st.session_state.df, "MongoDB")
                    st.success(get_text("success")); st.rerun()
            except Exception as e:
                st.error(f"{get_text('error')}: {e}")

elif source == "REST API":
    from connectors.api_connector import render_api_ui
    df_api = render_api_ui()
    if df_api is not None:
        st.session_state.df = df_api
        save_snapshot(st.session_state.df, "REST API")
        st.rerun()

elif source == get_text("batch_processing"):
    render_batch_ui(lambda df: df.drop_duplicates())
    st.stop()

# ── التبويبات الرئيسية ────────────────────────────────────────────────────────
if st.session_state.df is not None:
    df = st.session_state.df

    tabs = st.tabs([
        get_text("analyze_tab"),
        get_text("quality_tab"),
        get_text("smart_tab"),
        get_text("clean_tab"),
        get_text("columns_tab"),
        get_text("pii_tab"),
        get_text("pipeline_tab"),
        get_text("history_tab"),
        get_text("chat_tab"),
        get_text("rules_tab"),
    ])
    tab_analysis, tab_quality, tab_smart, tab_clean, tab_cols, tab_pii, tab_pipeline, tab_history, tab_chat, tab_rules = tabs

    # ── 1. تحليل ─────────────────────────────────────────────────────────────
    with tab_analysis:
        st.subheader(get_text("advanced_stats"))
        c1, c2 = st.columns([1, 2])
        with c1:
            st.dataframe(get_basic_info(df), use_container_width=True, hide_index=True)
        with c2:
            st.dataframe(df.head(10), use_container_width=True)
        show_advanced_stats(df)
        plot_numeric_columns(df)
        show_correlation_heatmap(df)

    # ── 2. جودة البيانات ──────────────────────────────────────────────────────
    with tab_quality:
        render_confidence_display(df)
        st.divider()
        new_df = render_data_table(df)
        if new_df is not None and not new_df.equals(df):
            save_snapshot(new_df, "Table Edit")
            st.session_state.df = new_df
            st.rerun()

    # ── 3. Smart Auto-Clean ───────────────────────────────────────────────────
    with tab_smart:
        st.subheader("⚡ Smart Auto-Clean")
        st.markdown("One click to analyze your data and apply all relevant cleaning automatically.")

        col_before, col_after = st.columns(2)
        with col_before:
            st.metric("Rows before", f"{len(df):,}")
            st.metric("Missing values", f"{df.isnull().sum().sum():,}")
            st.metric("Duplicates", f"{df.duplicated().sum():,}")

        if st.button("⚡ Run Smart Clean", type="primary", use_container_width=True):
            with st.spinner("Analyzing and cleaning..."):
                df_clean, report = smart_clean(df)
                save_snapshot(df_clean, "Smart Auto-Clean")
                record_step("remove_duplicates")
                record_step("trim_whitespace")
                record_step("standardize_dates")
                record_step("fill_missing_numeric", {"strategy": "median"})
                record_step("fill_missing_text", {"fill_value": "Unknown"})
                st.session_state.df = df_clean

            with col_after:
                st.metric("Rows after", f"{len(df_clean):,}")
                st.metric("Missing values", f"{df_clean.isnull().sum().sum():,}")
                st.metric("Duplicates", f"{df_clean.duplicated().sum():,}")

            st.divider()
            for line in report:
                st.markdown(line)
            st.rerun()

    # ── 4. تنظيف يدوي ────────────────────────────────────────────────────────
    with tab_clean:
        st.subheader("🧹 Manual Cleaning Tools")
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button(get_text("remove_duplicates"), use_container_width=True):
                df_c, rep = remove_duplicates(df)
                save_snapshot(df_c, get_text("remove_duplicates"))
                record_step("remove_duplicates")
                st.session_state.df = df_c
                st.success(f"{get_text('success')} — removed {rep['removed_duplicates']} rows")
                st.rerun()
        with c2:
            if st.button(get_text("standardize_dates"), use_container_width=True):
                df_c = standardize_dates(df)
                save_snapshot(df_c, get_text("standardize_dates"))
                record_step("standardize_dates")
                st.session_state.df = df_c
                st.success(get_text("success")); st.rerun()
        with c3:
            if st.button(get_text("fill_missing"), use_container_width=True):
                df_c = fill_missing_numeric(df, strategy='median')
                save_snapshot(df_c, get_text("fill_missing"))
                record_step("fill_missing_numeric", {"strategy": "median"})
                st.session_state.df = df_c
                st.success(get_text("success")); st.rerun()

        c4, c5, c6 = st.columns(3)
        with c4:
            if st.button("✂️ Trim Whitespace", use_container_width=True):
                df_c = trim_whitespace(df)
                save_snapshot(df_c, "Trim Whitespace")
                record_step("trim_whitespace")
                st.session_state.df = df_c
                st.success(get_text("success")); st.rerun()
        with c5:
            fill_val = st.text_input("Fill text missing with", "Unknown", key="fill_tv")
            if st.button("📝 Fill Text Missing", use_container_width=True):
                df_c = fill_missing_text(df, fill_value=fill_val)
                save_snapshot(df_c, "Fill Missing Text")
                record_step("fill_missing_text", {"fill_value": fill_val})
                st.session_state.df = df_c
                st.success(get_text("success")); st.rerun()
        with c6:
            case_mode = st.selectbox("Case mode", ["title", "lower", "upper"], key="case_m")
            if st.button("🔤 Normalize Case", use_container_width=True):
                df_c = normalize_text_case(df, mode=case_mode)
                save_snapshot(df_c, f"Normalize Case ({case_mode})")
                record_step("normalize_case", {"mode": case_mode})
                st.session_state.df = df_c
                st.success(get_text("success")); st.rerun()

    # ── 5. عمليات الأعمدة ────────────────────────────────────────────────────
    with tab_cols:
        new_df = render_column_ops(df)
        if new_df is not None and not new_df.equals(df):
            save_snapshot(new_df, "Column Operation")
            st.session_state.df = new_df

    # ── 6. PII Masking ────────────────────────────────────────────────────────
    with tab_pii:
        st.subheader("🔒 PII Detection & Masking")
        st.markdown("Automatically detect and mask sensitive personal data (GDPR-ready).")

        with st.spinner("Scanning for PII..."):
            pii_found = detect_pii_columns(df)

        if not pii_found:
            st.success("✅ No PII detected in your dataset.")
        else:
            st.warning(f"⚠️ PII detected in **{len(pii_found)}** column(s):")
            for col, types in pii_found.items():
                labels = " · ".join([PII_LABELS.get(t, t) for t in types])
                st.markdown(f"- **`{col}`** → {labels}")

            st.divider()
            st.subheader("Apply Masking")
            col_to_mask = st.selectbox("Select column", list(pii_found.keys()), key="pii_col")
            mask_method = st.radio(
                "Masking method",
                ["mask (replace with ***)", "partial (keep first/last 2)", "hash (SHA-256)", "remove column"],
                horizontal=True, key="pii_method"
            )
            method_map = {
                "mask (replace with ***)": "mask",
                "partial (keep first/last 2)": "partial",
                "hash (SHA-256)": "hash",
                "remove column": "remove"
            }

            # معاينة
            method_key = method_map[mask_method]
            preview_df = mask_column(df[[col_to_mask]].head(5).copy(), col_to_mask, method_key)
            st.caption("Preview (5 rows):")
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                st.markdown("**Before**")
                st.dataframe(df[[col_to_mask]].head(5), use_container_width=True)
            with col_p2:
                st.markdown("**After**")
                st.dataframe(preview_df, use_container_width=True)

            if st.button("🔒 Apply Masking", type="primary", use_container_width=True):
                df_c = mask_column(df, col_to_mask, method_key)
                save_snapshot(df_c, f"PII Mask: {col_to_mask}")
                st.session_state.df = df_c
                st.success(f"Masked '{col_to_mask}' using '{method_key}'")
                st.rerun()

    # ── 7. Pipeline Builder ───────────────────────────────────────────────────
    with tab_pipeline:
        st.subheader("🔁 Pipeline Builder")
        st.markdown("Record your cleaning steps and replay them on any new file.")

        current_steps = get_current_pipeline()
        recording = st.session_state.get("pipeline_recording", False)

        c_status, c_steps = st.columns([1, 2])
        with c_status:
            if recording:
                st.success("🔴 Recording in progress")
                st.metric("Steps recorded", len(current_steps))
            else:
                st.info("⏸ Not recording")

        with c_steps:
            if current_steps:
                st.markdown("**Current pipeline steps:**")
                for i, step in enumerate(current_steps):
                    p = step.get("params", {})
                    params_str = f" `{p}`" if p else ""
                    st.markdown(f"`{i+1}.` **{step['operation']}**{params_str}")
            else:
                st.caption("No steps recorded yet. Click 'Start Pipeline Recording' in the sidebar, then perform cleaning operations.")

        st.divider()

        # حفظ pipeline
        if current_steps:
            save_col, _ = st.columns([1, 2])
            with save_col:
                pipeline_name = st.text_input("Pipeline name", key="pipeline_name")
                if st.button("💾 Save Pipeline", use_container_width=True):
                    ok, msg = save_pipeline(pipeline_name, current_steps)
                    (st.success if ok else st.error)(msg)

        # تطبيق pipeline محفوظ
        st.subheader("Saved Pipelines")
        pipelines = load_pipelines()
        if pipelines:
            for pname, psteps in pipelines.items():
                with st.expander(f"📋 {pname} ({len(psteps)} steps)"):
                    for i, s in enumerate(psteps):
                        st.markdown(f"`{i+1}.` {s['operation']}")
                    colA, colB = st.columns(2)
                    with colA:
                        if st.button(f"▶️ Apply to current data", key=f"apply_{pname}"):
                            df_c, applied, failed = apply_pipeline(df, psteps)
                            save_snapshot(df_c, f"Pipeline: {pname}")
                            st.session_state.df = df_c
                            st.success(f"Applied {len(applied)} steps")
                            if failed:
                                st.warning(f"Failed: {failed}")
                            st.rerun()
                    with colB:
                        if st.button(f"🗑️ Delete", key=f"del_pipe_{pname}"):
                            delete_pipeline(pname)
                            st.rerun()
        else:
            st.info("No saved pipelines yet.")

        # تطبيق pipeline على ملف جديد
        st.divider()
        st.subheader("Apply Pipeline to New File")
        if pipelines:
            chosen_pipeline = st.selectbox("Select pipeline", list(pipelines.keys()), key="apply_new_pipe")
            new_file = st.file_uploader("Upload new file", type=["csv", "xlsx", "xls"], key="new_pipe_file")
            if new_file and st.button("▶️ Apply & Download"):
                with st.spinner("Applying pipeline..."):
                    new_df = load_file(new_file)
                    new_df_clean, applied, failed = apply_pipeline(new_df, pipelines[chosen_pipeline])
                    csv_out = new_df_clean.to_csv(index=False).encode("utf-8-sig")
                    st.download_button(
                        "⬇️ Download cleaned file",
                        csv_out,
                        f"cleaned_{new_file.name}",
                        "text/csv"
                    )
                    st.success(f"Applied {len(applied)} steps to {len(new_df_clean):,} rows")

    # ── 8. السجل والتراجع ────────────────────────────────────────────────────
    with tab_history:
        if st.button(get_text("undo"), use_container_width=False):
            new_df = undo(st.session_state.df)
            if not new_df.equals(st.session_state.df):
                st.session_state.df = new_df
                st.success(get_text("success")); st.rerun()
            else:
                st.info("Nothing to undo.")
        with st.expander(get_text("history_expander")):
            history = get_history_list()
            for i, h in enumerate(history):
                st.write(f"{i+1}. **{h['name']}** — {h['timestamp'].strftime('%H:%M:%S')}")

    # ── 9. AI Chat ────────────────────────────────────────────────────────────
    with tab_chat:
        st.session_state.df = render_chat_interface(st.session_state.df)

    # ── 10. Saved Rules ───────────────────────────────────────────────────────
    with tab_rules:
        st.subheader(get_text("save_rule"))
        rule_name = st.text_input(get_text("rule_name"))
        rule_code = st.text_area(get_text("rule_code"), "df['city'] = df['city'].str.strip().str.title()", height=100)
        if st.button(get_text("save_button")):
            ok, msg = save_rule(rule_name, rule_code)
            (st.success if ok else st.error)(msg)
        st.subheader(get_text("saved_rules_header"))
        rules = load_rules()
        if rules:
            for rname, rcode in rules.items():
                r1, r2 = st.columns([4, 1])
                with r1:
                    st.code(f"# {rname}\n{rcode}", language="python")
                with r2:
                    if st.button("🗑️", key=f"del_{rname}"):
                        delete_rule(rname); st.rerun()
        else:
            st.info("No saved rules yet.")

    # ── تصدير ────────────────────────────────────────────────────────────────
    st.divider()
    st.subheader(get_text("export_label"))
    fmt = st.radio(get_text("export_format"), ["CSV", "Excel", "JSON"], horizontal=True)
    if fmt == "CSV":
        st.download_button("⬇️ Download CSV",
            st.session_state.df.to_csv(index=False).encode("utf-8-sig"),
            "cleaned_data.csv", "text/csv")
    elif fmt == "Excel":
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='openpyxl') as w:
            st.session_state.df.to_excel(w, index=False)
        st.download_button("⬇️ Download Excel", buf.getvalue(),
            "cleaned_data.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.download_button("⬇️ Download JSON",
            st.session_state.df.to_json(orient="records", force_ascii=False),
            "cleaned_data.json", "application/json")

else:
    st.info(get_text("waiting_for_file"))
