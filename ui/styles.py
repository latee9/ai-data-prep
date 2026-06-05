# ui/styles.py
import streamlit as st


def inject_css():
    st.markdown("""
<style>
/* ── Google Font ─────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ══════════════════════════════════════════════════════════════════════
   SIDEBAR
══════════════════════════════════════════════════════════════════════ */

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D0F1E 0%, #131629 60%, #0D0F1E 100%) !important;
    border-right: 1px solid rgba(108,99,255,0.18) !important;
    padding-top: 0 !important;
}

/* Sidebar inner content padding */
[data-testid="stSidebar"] > div:first-child {
    padding-top: 0 !important;
}

/* ── Sidebar brand logo ───────────────────────────────────────────────*/
.sb-brand {
    background: linear-gradient(135deg, #6C63FF 0%, #A78BFA 100%);
    margin: 0 0 1.2rem 0;
    padding: 1.4rem 1.2rem 1.2rem 1.2rem;
    position: relative;
    overflow: hidden;
}
.sb-brand::before {
    content: '';
    position: absolute;
    top: -30px; right: -30px;
    width: 100px; height: 100px;
    background: rgba(255,255,255,0.08);
    border-radius: 50%;
}
.sb-brand::after {
    content: '';
    position: absolute;
    bottom: -20px; left: -20px;
    width: 70px; height: 70px;
    background: rgba(255,255,255,0.05);
    border-radius: 50%;
}
.sb-brand-icon {
    font-size: 2rem;
    line-height: 1;
    margin-bottom: 0.3rem;
}
.sb-brand-name {
    font-size: 1.1rem;
    font-weight: 700;
    color: white;
    letter-spacing: -0.02em;
}
.sb-brand-tag {
    font-size: 0.68rem;
    color: rgba(255,255,255,0.65);
    font-weight: 400;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* ── User profile card ────────────────────────────────────────────────*/
.sb-user {
    background: rgba(108,99,255,0.1);
    border: 1px solid rgba(108,99,255,0.2);
    border-radius: 12px;
    padding: 0.75rem 1rem;
    margin: 0 0.8rem 1rem 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.7rem;
}
.sb-avatar {
    width: 36px; height: 36px;
    background: linear-gradient(135deg, #6C63FF, #A78BFA);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem; font-weight: 700; color: white;
    flex-shrink: 0;
    box-shadow: 0 0 10px rgba(108,99,255,0.4);
}
.sb-user-info { flex: 1; min-width: 0; }
.sb-username {
    font-size: 0.85rem; font-weight: 600;
    color: white; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.sb-role {
    font-size: 0.68rem; color: rgba(255,255,255,0.45);
    text-transform: uppercase; letter-spacing: 0.05em;
}
.sb-online {
    width: 8px; height: 8px;
    background: #00C878;
    border-radius: 50%;
    box-shadow: 0 0 6px #00C878;
    flex-shrink: 0;
}

/* ── Section label ────────────────────────────────────────────────────*/
.sb-section {
    font-size: 0.65rem;
    font-weight: 600;
    color: rgba(255,255,255,0.3);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    padding: 0.6rem 1.2rem 0.3rem 1.2rem;
}

/* ── Nav radio items (Data Source) ───────────────────────────────────*/
[data-testid="stSidebar"] .stRadio > div {
    gap: 2px !important;
}
[data-testid="stSidebar"] .stRadio label {
    background: transparent;
    border-radius: 10px !important;
    padding: 0.55rem 0.9rem !important;
    font-size: 0.86rem !important;
    font-weight: 500 !important;
    color: rgba(255,255,255,0.55) !important;
    transition: all 0.18s ease !important;
    cursor: pointer !important;
    border: 1px solid transparent !important;
    margin: 0 0.3rem !important;
    display: flex !important;
    align-items: center !important;
    gap: 0.5rem !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(108,99,255,0.12) !important;
    color: rgba(255,255,255,0.85) !important;
    border-color: rgba(108,99,255,0.2) !important;
}
[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"] span:first-child,
[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p {
    color: inherit !important;
}
/* Hide default radio circle */
[data-testid="stSidebar"] .stRadio [data-testid="stWidgetLabel"] { display: none !important; }
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label > div:first-child {
    display: none !important;
}

/* ── Language selectbox ───────────────────────────────────────────────*/
[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
    background: rgba(108,99,255,0.08) !important;
    border: 1px solid rgba(108,99,255,0.25) !important;
    border-radius: 10px !important;
    color: white !important;
}

/* ── Recording badge ──────────────────────────────────────────────────*/
.rec-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: rgba(255,60,60,0.12);
    border: 1px solid rgba(255,60,60,0.3);
    border-radius: 20px;
    padding: 0.3rem 0.8rem;
    font-size: 0.75rem;
    font-weight: 600;
    color: #FF6B6B;
    margin: 0 0.8rem 0.5rem 0.8rem;
    animation: pulse-rec 1.5s infinite;
}
@keyframes pulse-rec {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.65; }
}
.rec-dot {
    width: 7px; height: 7px;
    background: #FF4444;
    border-radius: 50%;
    box-shadow: 0 0 6px #FF4444;
}

/* ── Sidebar buttons ──────────────────────────────────────────────────*/
[data-testid="stSidebar"] .stButton > button {
    border-radius: 10px !important;
    font-size: 0.84rem !important;
    font-weight: 500 !important;
    border: 1px solid rgba(108,99,255,0.2) !important;
    background: rgba(108,99,255,0.08) !important;
    color: rgba(255,255,255,0.7) !important;
    transition: all 0.18s !important;
    width: 100% !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(108,99,255,0.18) !important;
    border-color: rgba(108,99,255,0.4) !important;
    color: white !important;
    transform: none !important;
}

/* ── Sidebar mini stats ───────────────────────────────────────────────*/
.sb-stats {
    background: rgba(108,99,255,0.07);
    border: 1px solid rgba(108,99,255,0.15);
    border-radius: 12px;
    padding: 0.8rem 1rem;
    margin: 0.5rem 0.8rem;
}
.sb-stats-title {
    font-size: 0.65rem;
    color: rgba(255,255,255,0.35);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.5rem;
}
.sb-stat-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.2rem 0;
}
.sb-stat-label {
    font-size: 0.76rem;
    color: rgba(255,255,255,0.45);
}
.sb-stat-val {
    font-size: 0.82rem;
    font-weight: 600;
    color: #A78BFA;
}

/* ── Divider ──────────────────────────────────────────────────────────*/
[data-testid="stSidebar"] hr {
    border-color: rgba(108,99,255,0.12) !important;
    margin: 0.6rem 0 !important;
}

/* ══════════════════════════════════════════════════════════════════════
   HERO HEADER
══════════════════════════════════════════════════════════════════════ */
.hero {
    background: linear-gradient(135deg, #6C63FF 0%, #3B37CC 45%, #1a1d2e 100%);
    border-radius: 18px;
    padding: 2.4rem 2.2rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 8px 40px rgba(108,99,255,0.28);
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 180px; height: 180px;
    background: rgba(255,255,255,0.06);
    border-radius: 50%;
}
.hero::after {
    content: '';
    position: absolute;
    bottom: -50px; right: 120px;
    width: 120px; height: 120px;
    background: rgba(255,255,255,0.04);
    border-radius: 50%;
}
.hero h1 {
    font-size: 2rem; font-weight: 800;
    color: #FFFFFF !important;
    margin: 0 0 0.5rem 0;
    letter-spacing: -0.03em;
    position: relative; z-index: 1;
}
.hero p {
    font-size: 0.95rem;
    color: rgba(255,255,255,0.7);
    margin: 0; position: relative; z-index: 1;
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 20px;
    padding: 0.2rem 0.7rem;
    font-size: 0.7rem;
    font-weight: 600;
    color: white;
    margin-bottom: 0.8rem;
    letter-spacing: 0.05em;
    position: relative; z-index: 1;
}

/* ══════════════════════════════════════════════════════════════════════
   METRIC CARDS
══════════════════════════════════════════════════════════════════════ */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #1A1D2E 0%, #22263A 100%);
    border: 1px solid rgba(108,99,255,0.2);
    border-radius: 14px;
    padding: 1rem 1.2rem;
    box-shadow: 0 4px 16px rgba(0,0,0,0.25);
    transition: transform 0.2s, box-shadow 0.2s;
}
[data-testid="metric-container"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 28px rgba(108,99,255,0.22);
}
[data-testid="metric-container"] label {
    color: rgba(255,255,255,0.5) !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 1.9rem !important;
    font-weight: 800 !important;
    color: #FFFFFF !important;
    letter-spacing: -0.03em;
}

/* ══════════════════════════════════════════════════════════════════════
   BUTTONS
══════════════════════════════════════════════════════════════════════ */
.stButton > button {
    border-radius: 10px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
    border: 1px solid rgba(108,99,255,0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 5px 15px rgba(108,99,255,0.3) !important;
    border-color: #6C63FF !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6C63FF, #3B37CC) !important;
    border: none !important;
    color: white !important;
    box-shadow: 0 4px 14px rgba(108,99,255,0.35) !important;
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 6px 22px rgba(108,99,255,0.5) !important;
}

/* ══════════════════════════════════════════════════════════════════════
   TABS
══════════════════════════════════════════════════════════════════════ */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 3px;
    background: #1A1D2E;
    border-radius: 14px;
    padding: 5px;
    border: 1px solid rgba(255,255,255,0.06);
    flex-wrap: wrap;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    border-radius: 9px !important;
    padding: 0.38rem 0.85rem !important;
    font-weight: 500 !important;
    font-size: 0.8rem !important;
    color: rgba(255,255,255,0.5) !important;
    transition: all 0.2s !important;
}
[data-testid="stTabs"] [data-baseweb="tab"]:hover {
    color: rgba(255,255,255,0.85) !important;
    background: rgba(108,99,255,0.1) !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    background: linear-gradient(135deg, #6C63FF, #3B37CC) !important;
    color: white !important;
    box-shadow: 0 2px 10px rgba(108,99,255,0.4) !important;
}

/* ══════════════════════════════════════════════════════════════════════
   MISC COMPONENTS
══════════════════════════════════════════════════════════════════════ */
[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    overflow: hidden;
    border: 1px solid rgba(108,99,255,0.15) !important;
}
[data-testid="stExpander"] {
    border: 1px solid rgba(108,99,255,0.18) !important;
    border-radius: 12px !important;
    background: #1A1D2E !important;
    margin-bottom: 0.5rem;
}
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    border-radius: 9px !important;
    border-color: rgba(108,99,255,0.25) !important;
    background: rgba(108,99,255,0.04) !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: #6C63FF !important;
    box-shadow: 0 0 0 3px rgba(108,99,255,0.18) !important;
}
[data-testid="stSuccess"] {
    background: rgba(0,200,120,0.08) !important;
    border: 1px solid rgba(0,200,120,0.25) !important;
    border-radius: 10px !important;
}
[data-testid="stWarning"] {
    background: rgba(255,180,0,0.08) !important;
    border: 1px solid rgba(255,180,0,0.25) !important;
    border-radius: 10px !important;
}
[data-testid="stError"] {
    background: rgba(255,80,80,0.08) !important;
    border: 1px solid rgba(255,80,80,0.25) !important;
    border-radius: 10px !important;
}
[data-testid="stInfo"] {
    background: rgba(108,99,255,0.08) !important;
    border: 1px solid rgba(108,99,255,0.22) !important;
    border-radius: 10px !important;
}
[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #6C63FF, #A78BFA) !important;
    border-radius: 4px !important;
}
hr { border-color: rgba(108,99,255,0.12) !important; }
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #0F1117; }
::-webkit-scrollbar-thumb { background: #6C63FF; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #8B85FF; }
[data-testid="stFileUploader"] {
    border: 2px dashed rgba(108,99,255,0.35) !important;
    border-radius: 16px !important;
    background: rgba(108,99,255,0.03) !important;
    transition: all 0.2s !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: #6C63FF !important;
    background: rgba(108,99,255,0.07) !important;
}
[data-testid="stCode"] {
    border-radius: 10px !important;
    border: 1px solid rgba(108,99,255,0.18) !important;
}
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Sidebar Components ────────────────────────────────────────────────────────

def render_sidebar_brand():
    st.markdown("""
<div class="sb-brand">
    <div class="sb-brand-icon">🧹</div>
    <div class="sb-brand-name">AI Data Prep</div>
    <div class="sb-brand-tag">✦ Intelligent Cleaning Suite</div>
</div>
""", unsafe_allow_html=True)


def render_sidebar_user(username: str):
    initial = username[0].upper() if username else "?"
    st.markdown(f"""
<div class="sb-user">
    <div class="sb-avatar">{initial}</div>
    <div class="sb-user-info">
        <div class="sb-username">{username}</div>
        <div class="sb-role">Administrator</div>
    </div>
    <div class="sb-online"></div>
</div>
""", unsafe_allow_html=True)


def render_sidebar_section(label: str):
    st.markdown(f'<div class="sb-section">{label}</div>', unsafe_allow_html=True)


def render_recording_badge():
    st.markdown("""
<div class="rec-badge">
    <div class="rec-dot"></div>
    Recording Pipeline...
</div>
""", unsafe_allow_html=True)


def render_sidebar_stats(df):
    import pandas as pd
    rows = f"{len(df):,}"
    cols = str(df.shape[1])
    missing = str(df.isnull().sum().sum())
    dups = str(df.duplicated().sum())
    st.markdown(f"""
<div class="sb-stats">
    <div class="sb-stats-title">📊 Dataset Overview</div>
    <div class="sb-stat-row">
        <span class="sb-stat-label">Rows</span>
        <span class="sb-stat-val">{rows}</span>
    </div>
    <div class="sb-stat-row">
        <span class="sb-stat-label">Columns</span>
        <span class="sb-stat-val">{cols}</span>
    </div>
    <div class="sb-stat-row">
        <span class="sb-stat-label">Missing</span>
        <span class="sb-stat-val">{missing}</span>
    </div>
    <div class="sb-stat-row">
        <span class="sb-stat-label">Duplicates</span>
        <span class="sb-stat-val">{dups}</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ── Main Area Components ──────────────────────────────────────────────────────

def render_hero(title: str, subtitle: str):
    st.markdown(f"""
<div class="hero">
    <div class="hero-badge">✦ AI-POWERED</div>
    <h1>{title}</h1>
    <p>{subtitle}</p>
</div>
""", unsafe_allow_html=True)


def render_stat_card(label: str, value: str, color: str = "#6C63FF"):
    st.markdown(f"""
<div style="
    background: linear-gradient(135deg,#1A1D2E,#22263A);
    border:1px solid {color}33;
    border-left:4px solid {color};
    border-radius:12px;
    padding:1rem 1.2rem;
    margin-bottom:0.5rem;
">
    <div style="color:rgba(255,255,255,0.45);font-size:0.72rem;text-transform:uppercase;letter-spacing:0.08em;">{label}</div>
    <div style="color:#FFF;font-size:1.6rem;font-weight:800;margin-top:0.2rem;letter-spacing:-0.02em;">{value}</div>
</div>
""", unsafe_allow_html=True)
