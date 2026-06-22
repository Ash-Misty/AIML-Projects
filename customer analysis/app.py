import streamlit as st
import pandas as pd
import pickle
import plotly.express as px
import plotly.graph_objects as go

# PAGE CONFIG
st.set_page_config(
    page_title="CustomerIQ · Intelligence Dashboard",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded",
)


# CSS
@st.cache_data
def _css() -> str:
    return """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;0,800;1,600&family=Lato:ital,wght@0,300;0,400;0,700;1,400&display=swap');

/* ── Root tokens ── */
:root{
    --bg:#0d0f1a; --surface:#141728; --surface2:#1b1f35;
    --border:rgba(255,255,255,0.07);
    --accent:#7c6af7; --accent2:#f76aac; --accent3:#4af7c4;
    --text:#e8eaf6; --muted:#7b80a0;
    --success:#4af7a0; --danger:#f76a7c; --warn:#f7c74a;
}

/* ── Global ── */
html,body,[class*="css"]{
    font-family:'Lato',Georgia,serif !important;
    background-color:var(--bg) !important;
    color:var(--text) !important;
    overflow-x:hidden !important;
}

/* ── Responsive block container ── */
.main .block-container{
    padding:clamp(1rem,3vw,2rem) clamp(0.75rem,3vw,2.5rem) clamp(1.5rem,4vw,3rem) !important;
    max-width:1400px;
    width:100% !important;
    box-sizing:border-box;
}

/* ── Fade-in & slide-up animations ── */
@keyframes fadeInUp{
    from{opacity:0;transform:translateY(22px);}
    to{opacity:1;transform:translateY(0);}
}
@keyframes fadeIn{from{opacity:0;}to{opacity:1;}}
@keyframes shimmer{
    0%{background-position:-200% center;}
    100%{background-position:200% center;}
}
@keyframes pulse{
    0%,100%{box-shadow:0 0 0 0 rgba(124,106,247,0.4);}
    50%{box-shadow:0 0 0 10px rgba(124,106,247,0);}
}
@keyframes spin{from{transform:rotate(0deg);}to{transform:rotate(360deg);}}
@keyframes floatY{
    0%,100%{transform:translateY(0);}
    50%{transform:translateY(-6px);}
}

.anim-fadein      {animation:fadeIn .55s ease both;}
.anim-fadeup      {animation:fadeInUp .55s ease both;}
.anim-fadeup-d1   {animation:fadeInUp .55s .1s ease both;}
.anim-fadeup-d2   {animation:fadeInUp .55s .2s ease both;}
.anim-fadeup-d3   {animation:fadeInUp .55s .3s ease both;}
.anim-fadeup-d4   {animation:fadeInUp .55s .4s ease both;}
.anim-float       {animation:floatY 3s ease-in-out infinite;}

/* ── Sidebar ── */
section[data-testid="stSidebar"]{
    background:linear-gradient(180deg,#10132a 0%,#0d0f1a 100%) !important;
    border-right:1px solid var(--border) !important;
    min-width:220px !important;
}
section[data-testid="stSidebar"] *{color:var(--text) !important;}
section[data-testid="stSidebar"] .stRadio label{
    padding:10px 14px;border-radius:10px;
    transition:background .2s,transform .15s;cursor:pointer;
    font-size:clamp(0.78rem,1.5vw,0.9rem) !important;
    white-space:normal;word-break:break-word;
}
section[data-testid="stSidebar"] .stRadio label:hover{
    background:rgba(124,106,247,.15);transform:translateX(4px);
}

/* ── Headings ── */
h1,h2,h3,h4{
    font-family:'Playfair Display',Georgia,serif !important;
    font-weight:800 !important;
    letter-spacing:-.01em;
    word-break:break-word;
    overflow-wrap:break-word;
}
h1{
    font-size:clamp(1.6rem,4vw,2.6rem) !important;
    background:linear-gradient(135deg,#a89cff,#f76aac);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
    background-size:200%;animation:shimmer 4s linear infinite;
    line-height:1.25 !important;
}
h2{font-size:clamp(1.1rem,2.5vw,1.6rem) !important;color:var(--text) !important;-webkit-text-fill-color:var(--text) !important;}
h3{font-size:clamp(0.95rem,2vw,1.15rem) !important;color:var(--accent) !important;-webkit-text-fill-color:var(--accent) !important;}

/* ── Metric cards ── */
div[data-testid="metric-container"]{
    background:var(--surface) !important;border:1px solid var(--border) !important;
    border-radius:16px !important;padding:clamp(12px,2vw,20px) clamp(14px,2.5vw,22px) !important;
    position:relative;overflow:hidden;
    transition:transform .2s,box-shadow .2s;
    animation:fadeInUp .5s ease both;
    min-width:0;
    box-sizing:border-box;
}
div[data-testid="metric-container"]:hover{
    transform:translateY(-3px);
    box-shadow:0 8px 32px rgba(124,106,247,.18);
}
div[data-testid="metric-container"]::before{
    content:'';position:absolute;top:0;left:0;right:0;height:3px;
    background:linear-gradient(90deg,var(--accent),var(--accent2));
    border-radius:16px 16px 0 0;
}
[data-testid="stMetricLabel"]{
    color:var(--muted) !important;
    font-size:clamp(0.68rem,1.2vw,0.8rem) !important;
    text-transform:uppercase;letter-spacing:.08em;
    white-space:normal !important;
    word-break:break-word;
}
[data-testid="stMetricValue"]{
    font-family:'Playfair Display',Georgia,serif !important;
    font-size:clamp(1.2rem,2.5vw,2rem) !important;
    color:var(--text) !important;
}
[data-testid="stMetricDelta"]{font-size:clamp(0.7rem,1.2vw,0.8rem) !important;}

/* ── Columns: stack on small screens ── */
[data-testid="column"]{
    min-width:0 !important;
    overflow-wrap:break-word;
    word-break:break-word;
}

/* ── Buttons ── */
.stButton>button{
    background:linear-gradient(135deg,var(--accent),#5d52d4) !important;
    color:white !important;border:none !important;border-radius:12px !important;
    padding:clamp(10px,1.5vw,14px) clamp(18px,3vw,28px) !important;
    font-family:'Playfair Display',Georgia,serif !important;
    font-weight:700 !important;
    font-size:clamp(0.82rem,1.5vw,0.95rem) !important;
    transition:all .25s !important;
    box-shadow:0 4px 24px rgba(124,106,247,.35) !important;
    width:100% !important;
    white-space:normal !important;
    word-break:break-word;
}
.stButton>button:hover{
    transform:translateY(-3px) scale(1.02) !important;
    box-shadow:0 10px 36px rgba(124,106,247,.55) !important;
}
.stButton>button:active{transform:translateY(0) scale(.98) !important;}

/* ── Inputs ── */
.stNumberInput input,.stSelectbox select,.stTextInput input{
    background:var(--surface2) !important;
    border:1px solid rgba(124,106,247,.3) !important;
    border-radius:10px !important;color:var(--text) !important;
    font-family:'Lato',Georgia,serif !important;
    font-size:clamp(0.8rem,1.5vw,0.9rem) !important;
    transition:border-color .2s,box-shadow .2s !important;
    max-width:100% !important;
    box-sizing:border-box;
}
.stNumberInput input:focus,.stSelectbox select:focus{
    border-color:var(--accent) !important;
    box-shadow:0 0 0 3px rgba(124,106,247,.2) !important;
}

/* ── Number input container width fix ── */
.stNumberInput{
    max-width:100% !important;
}
.stNumberInput > div{
    max-width:100% !important;
}

/* ── Dataframe ── */
.stDataFrame{
    border-radius:14px !important;
    overflow:hidden !important;
    max-width:100% !important;
}
/* Allow dataframes to scroll horizontally on small screens */
.stDataFrame > div{
    overflow-x:auto !important;
}

/* ── Alerts ── */
.stSuccess,.stInfo,.stWarning,.stError{
    border-radius:14px !important;border:none !important;
    padding:clamp(10px,2vw,16px) clamp(12px,2.5vw,20px) !important;
}
.stSuccess{background:rgba(74,247,160,.12) !important;border-left:4px solid var(--success) !important;}
.stInfo   {background:rgba(124,106,247,.12) !important;border-left:4px solid var(--accent)  !important;}
.stError  {background:rgba(247,106,124,.12) !important;border-left:4px solid var(--danger)  !important;}

/* ── Cards ── */
.card{
    background:var(--surface);border:1px solid var(--border);
    border-radius:18px;
    padding:clamp(14px,2.5vw,24px) clamp(16px,3vw,28px);
    margin-bottom:16px;
    transition:border-color .25s,transform .2s;
    overflow-wrap:break-word;
    word-break:break-word;
}
.card:hover{border-color:rgba(124,106,247,.4);transform:translateY(-2px);}
.card-accent{
    background:linear-gradient(135deg,rgba(124,106,247,.15),rgba(247,106,172,.08));
    border:1px solid rgba(124,106,247,.3);border-radius:18px;
    padding:clamp(14px,2.5vw,24px) clamp(16px,3vw,28px);
    margin-bottom:16px;
    overflow-wrap:break-word;
}

/* ── Tooltip system ── */
.tooltip-wrap{position:relative;display:inline-block;cursor:help;}
.tooltip-wrap .tt{
    visibility:hidden;opacity:0;
    background:#1b1f35;color:var(--text);
    border:1px solid rgba(124,106,247,.4);
    border-radius:10px;padding:10px 14px;
    font-size:clamp(0.7rem,1.2vw,0.78rem);line-height:1.5;
    width:clamp(180px,40vw,240px);
    position:absolute;bottom:calc(100% + 8px);left:50%;
    transform:translateX(-50%);
    transition:opacity .2s,transform .2s;
    transform:translateX(-50%) translateY(6px);
    z-index:9999;
    pointer-events:none;
    box-shadow:0 8px 24px rgba(0,0,0,.4);
    /* Prevent tooltip from going off-screen */
    max-width:min(240px,calc(100vw - 32px));
}
.tooltip-wrap .tt::after{
    content:'';position:absolute;top:100%;left:50%;transform:translateX(-50%);
    border:6px solid transparent;border-top-color:#1b1f35;
}
.tooltip-wrap:hover .tt{visibility:visible;opacity:1;transform:translateX(-50%) translateY(0);}
/* Clamp tooltip to right side near right edge */
.tooltip-wrap:last-child .tt,
.tooltip-wrap:nth-last-child(-n+2) .tt{
    left:auto;right:0;transform:translateX(0) translateY(6px);
}
.tooltip-wrap:last-child .tt::after,
.tooltip-wrap:nth-last-child(-n+2) .tt::after{
    left:auto;right:16px;transform:none;
}
.tooltip-wrap:last-child:hover .tt,
.tooltip-wrap:nth-last-child(-n+2):hover .tt{
    transform:translateX(0) translateY(0);
}
.tt-label{
    color:var(--accent);font-weight:700;
    font-family:'Playfair Display',Georgia,serif;
    font-size:clamp(0.72rem,1.2vw,0.8rem);display:block;margin-bottom:4px;
}

/* ── Badges & tags ── */
.badge-row{display:flex;flex-wrap:wrap;gap:8px;margin-top:16px;}
.badge{
    padding:6px 12px;border-radius:30px;
    font-size:clamp(0.7rem,1.2vw,0.8rem);font-weight:700;
    font-family:'Playfair Display',Georgia,serif;letter-spacing:.05em;
    transition:transform .15s,box-shadow .15s;
    white-space:nowrap;
}
.badge:hover{transform:translateY(-2px);box-shadow:0 4px 12px rgba(0,0,0,.3);}
.badge-purple{background:rgba(124,106,247,.2);color:#a89cff;border:1px solid rgba(124,106,247,.4);}
.badge-pink  {background:rgba(247,106,172,.2);color:#f7a8d0;border:1px solid rgba(247,106,172,.4);}
.badge-teal  {background:rgba(74,247,196,.15);color:#4af7c4;border:1px solid rgba(74,247,196,.35);}
.badge-orange{background:rgba(247,199,74,.15);color:#f7c74a;border:1px solid rgba(247,199,74,.35);}

/* ── Section title ── */
.section-title{
    font-family:'Playfair Display',Georgia,serif;
    font-size:clamp(0.62rem,1.2vw,0.7rem);font-weight:700;
    letter-spacing:.18em;text-transform:uppercase;color:var(--muted);
    margin-bottom:20px;padding-bottom:10px;border-bottom:1px solid var(--border);
}

/* ── Hero subtitle ── */
.hero-sub{
    font-size:clamp(0.88rem,1.8vw,1.05rem);color:var(--muted);
    line-height:1.7;max-width:720px;
    word-break:break-word;overflow-wrap:break-word;
}

/* ── Step circle ── */
.step-circle{
    display:inline-flex;
    width:clamp(26px,4vw,32px);height:clamp(26px,4vw,32px);
    border-radius:50%;
    background:linear-gradient(135deg,var(--accent),var(--accent2));
    color:white;font-weight:800;font-family:'Playfair Display',Georgia,serif;
    font-size:clamp(0.78rem,1.5vw,0.9rem);
    align-items:center;justify-content:center;
    margin-right:12px;flex-shrink:0;
    animation:pulse 2.5s ease-in-out infinite;
}

/* ── Insight cards ── */
.insight-card{
    background:var(--surface);border:1px solid var(--border);
    border-radius:16px;
    padding:clamp(14px,2.5vw,20px) clamp(14px,2.5vw,22px);
    margin-bottom:16px;
    transition:border-color .2s,transform .2s,box-shadow .2s;
    animation:fadeInUp .5s ease both;
    overflow-wrap:break-word;
    word-break:break-word;
}
.insight-card:hover{
    border-color:rgba(124,106,247,.5);
    transform:translateY(-3px);
    box-shadow:0 12px 36px rgba(0,0,0,.25);
}

/* ── Result card ── */
.result-card{
    background:var(--surface);border-radius:20px;
    padding:clamp(18px,3vw,32px);
    text-align:center;border:2px solid;margin:20px 0;
    animation:fadeInUp .5s ease both;
    box-sizing:border-box;
    width:100%;
}
.result-high{border-color:var(--success);background:rgba(74,247,160,.07);}
.result-low {border-color:var(--danger); background:rgba(247,106,124,.07);}
.result-label{
    font-family:'Playfair Display',Georgia,serif;
    font-size:clamp(1rem,2.5vw,1.5rem);font-weight:800;
}
.result-prob{
    font-size:clamp(2rem,5vw,3rem);
    font-family:'Playfair Display',Georgia,serif;font-weight:800;
}

/* ── Guide item ── */
.guide-item{
    display:flex;align-items:flex-start;gap:14px;
    padding:14px 0;border-bottom:1px solid var(--border);
    transition:background .15s;border-radius:8px;padding-left:8px;
    overflow-wrap:break-word;
}
.guide-item:hover{background:rgba(124,106,247,.06);}
.guide-icon{
    width:36px;height:36px;border-radius:10px;
    display:flex;align-items:center;justify-content:center;
    font-size:1rem;flex-shrink:0;
}
.guide-label{font-family:'Playfair Display',Georgia,serif;font-weight:700;font-size:clamp(0.8rem,1.5vw,0.9rem);color:var(--text);}
.guide-desc {font-size:clamp(0.72rem,1.2vw,0.8rem);color:var(--muted);margin-top:2px;}
.guide-range{font-size:clamp(0.68rem,1.1vw,0.75rem);color:var(--accent3);margin-top:4px;font-weight:600;}

/* ── Progress bar container ── */
.prog-track{background:#1b1f35;border-radius:20px;height:6px;overflow:hidden;}
.prog-fill{height:100%;border-radius:20px;background:linear-gradient(90deg,#f76aac,#7c6af7);
           transition:width .6s cubic-bezier(.4,0,.2,1);}

/* ── Plotly chart wrapper: ensure charts scale ── */
.js-plotly-plot,.plotly,.plot-container{
    max-width:100% !important;
    overflow:hidden !important;
}

/* ── Tabs styling ── */
.stTabs [data-baseweb="tab-list"]{
    gap:8px;flex-wrap:wrap;
}
.stTabs [data-baseweb="tab"]{
    font-size:clamp(0.78rem,1.5vw,0.9rem) !important;
    padding:8px clamp(10px,2vw,16px) !important;
    white-space:nowrap;
}

/* ── Scrollbar ── */
::-webkit-scrollbar{width:6px;height:6px;}
::-webkit-scrollbar-track{background:var(--bg);}
::-webkit-scrollbar-thumb{background:rgba(124,106,247,.4);border-radius:6px;}

/* ── Footer ── */
.caption-bar{
    text-align:center;color:var(--muted);
    font-size:clamp(0.7rem,1.2vw,0.78rem);
    padding:24px 0 8px;
    word-break:break-word;
}

/* ── Glow dot decoration ── */
.glow-dot{
    display:inline-block;width:8px;height:8px;border-radius:50%;
    background:var(--accent);box-shadow:0 0 8px var(--accent);
    animation:pulse 2s ease-in-out infinite;margin-right:8px;
}

/* ── Responsive: small screens (≤768px) ── */
@media (max-width:768px){
    .main .block-container{
        padding:1rem 0.75rem 2rem !important;
    }
    h1{font-size:1.7rem !important;line-height:1.2 !important;}
    h2{font-size:1.15rem !important;}
    h3{font-size:0.95rem !important;}
    .hero-sub{font-size:0.88rem;}
    .badge{font-size:0.68rem;padding:5px 10px;}

    /* Stack columns on mobile */
    [data-testid="column"]{
        width:100% !important;
        min-width:100% !important;
    }

    /* Card padding tighten */
    .card,.card-accent,.insight-card{
        padding:14px 16px;
        border-radius:14px;
    }

    /* Metric value smaller */
    [data-testid="stMetricValue"]{font-size:1.3rem !important;}

    /* Result card adjustments */
    .result-prob{font-size:2.2rem;}
    .result-label{font-size:1rem;}

    /* Section title */
    .section-title{font-size:0.62rem;letter-spacing:.12em;}

    /* Step circle */
    .step-circle{width:26px;height:26px;font-size:0.78rem;margin-right:10px;}

    /* Sidebar stats font */
    section[data-testid="stSidebar"] div[style*="font-size:.75rem"]{
        font-size:0.72rem !important;
    }
}

/* ── Responsive: very small screens (≤480px) ── */
@media (max-width:480px){
    h1{font-size:1.45rem !important;}
    .hero-sub{font-size:0.82rem;}
    .badge-row{gap:6px;}
    .badge{font-size:0.65rem;padding:4px 9px;}
    .card,.card-accent,.insight-card{padding:12px 14px;}
    [data-testid="stMetricValue"]{font-size:1.15rem !important;}
    [data-testid="stMetricLabel"]{font-size:0.62rem !important;}

    /* Stack Streamlit columns on very narrow */
    div[data-testid="stHorizontalBlock"]{
        flex-wrap:wrap !important;
    }
    div[data-testid="stHorizontalBlock"] > div{
        flex:0 0 100% !important;
        min-width:100% !important;
    }

    /* Tighten padding */
    .main .block-container{padding:0.75rem 0.6rem 1.5rem !important;}
}

/* ── Fix Streamlit horizontal blocks overflow ── */
div[data-testid="stHorizontalBlock"]{
    gap:clamp(8px,2vw,16px) !important;
    flex-wrap:wrap;
    align-items:stretch;
}
div[data-testid="stHorizontalBlock"] > div{
    min-width:0;
    overflow:hidden;
    box-sizing:border-box;
}

/* ── Fix selectbox overflow ── */
.stSelectbox > div > div{
    max-width:100% !important;
    overflow:hidden;
}

/* ── Fix number input spinners on small screens ── */
@media (max-width:480px){
    .stNumberInput input{font-size:0.82rem !important;}
    .stNumberInput button{padding:4px !important;}
}
</style>
"""


st.markdown(_css(), unsafe_allow_html=True)

# TOOLTIP HELPER
ML_TERMS = {
    "RFM": (
        "RFM Analysis",
        "Recency-Frequency-Monetary: a marketing technique that scores customers on how recently they bought, how often, and how much they spend.",
    ),
    "KMeans": (
        "KMeans Clustering",
        "An unsupervised algorithm that groups similar data points into K clusters by minimising the distance between each point and its cluster centre.",
    ),
    "Clustering": (
        "Clustering",
        "Grouping data points so that items in the same group are more similar to each other than to those in other groups — no labels needed.",
    ),
    "Random Forest": (
        "Random Forest",
        "An ensemble of decision trees that each vote on the outcome. Combining many trees reduces errors and overfitting compared to a single tree.",
    ),
    "ROC-AUC": (
        "ROC-AUC Score",
        "Area Under the ROC Curve — measures how well the model separates classes. 1.0 = perfect, 0.5 = random guessing.",
    ),
    "Feature Importance": (
        "Feature Importance",
        "How much each input variable contributed to the model's predictions. Higher = that feature had more influence.",
    ),
    "Recency": (
        "Recency",
        "Days since the customer's last purchase. Lower = more recently active, which generally predicts higher future value.",
    ),
    "Frequency": (
        "Frequency",
        "Total number of unique orders a customer has placed. More orders = stronger engagement.",
    ),
    "Monetary": (
        "Monetary",
        "Total amount spent by a customer. Used to identify high-spend vs low-spend buyers.",
    ),
    "AOV": (
        "Average Order Value",
        "Total revenue divided by number of orders. Higher AOV customers spend more per transaction.",
    ),
    "Predict": (
        "Prediction",
        "The model's output — based on input features it classifies whether this customer is likely High Value or Low Value.",
    ),
    "Probability": (
        "Probability Score",
        "A 0–100% confidence score from the model. Above 50% = predicted High Value; the higher the number, the more confident the model is.",
    ),
    "Stratify": (
        "Stratified Split",
        "Splitting data so that the class balance (High/Low) is preserved equally in both training and test sets.",
    ),
    "Overfitting": (
        "Overfitting",
        "When a model learns the training data too well, including noise, and performs poorly on new unseen data.",
    ),
    "Baseline": (
        "Baseline Accuracy",
        "The simplest possible benchmark — e.g. always predicting the majority class. A good model must beat this.",
    ),
}


def tt(term: str, display: str | None = None) -> str:
    """Return an HTML tooltip span for a known ML term."""
    label, desc = ML_TERMS.get(term, (term, ""))
    shown = display or term
    return (
        f'<span class="tooltip-wrap">'
        f'<span style="border-bottom:1px dashed rgba(124,106,247,.6);color:var(--accent3);">{shown}</span>'
        f'<span class="tt"><span class="tt-label">📖 {label}</span>{desc}</span>'
        f"</span>"
    )


# PLOTLY THEME
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Lato", color="#7b80a0"),
    title_font=dict(family="Playfair Display", color="#e8eaf6", size=16),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(255,255,255,0.05)"),
    colorway=["#7c6af7", "#f76aac", "#4af7c4", "#f7c74a", "#f76a7c", "#7cf7f7"],
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.05)"
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.05)"
    ),
    autosize=True,
    margin=dict(l=40, r=20, t=50, b=40),
)


# DATA LOADERS
@st.cache_resource
def load_model():
    with open("model.pkl", "rb") as f:
        return pickle.load(f)


@st.cache_data
def load_rfm():
    return pd.read_csv("rfm_data.csv")


@st.cache_data
def load_feature_importance():
    return pd.read_csv("feature_importance.csv")


# ── Pre-computed aggregates (cached so reruns are instant) ──
@st.cache_data
def get_sidebar_stats(rfm: pd.DataFrame) -> dict:
    return {
        "total": len(rfm),
        "high": int(rfm["HighValueCustomer"].sum()),
        "low": int((rfm["HighValueCustomer"] == 0).sum()),
    }


@st.cache_data
def get_cluster_summary(rfm: pd.DataFrame) -> pd.DataFrame:
    return (
        rfm.groupby("Cluster")[
            ["Recency", "Frequency", "Monetary", "AvgOrderValue", "UniqueProducts"]
        ]
        .mean()
        .round(1)
        .reset_index()
    )


@st.cache_data
def get_cluster_revenue(rfm: pd.DataFrame) -> pd.DataFrame:
    return rfm.groupby("Cluster")["Monetary"].sum().reset_index()


# ── Cached chart builders ──
@st.cache_data
def fig_recency_hist(rfm):
    f = px.histogram(
        rfm,
        x="Recency",
        nbins=40,
        title="Recency Distribution",
        color_discrete_sequence=["#7c6af7"],
    )
    f.update_layout(**PLOTLY_LAYOUT)
    return f


@st.cache_data
def fig_frequency_hist(rfm):
    f = px.histogram(
        rfm,
        x="Frequency",
        nbins=40,
        title="Frequency Distribution",
        color_discrete_sequence=["#f76aac"],
    )
    f.update_layout(**PLOTLY_LAYOUT)
    return f


@st.cache_data
def fig_monetary_hist(rfm):
    f = px.histogram(
        rfm,
        x="Monetary",
        nbins=40,
        title="Monetary Distribution",
        color_discrete_sequence=["#4af7c4"],
    )
    f.update_layout(**PLOTLY_LAYOUT)
    return f


@st.cache_data
def fig_pie_split(rfm):
    f = px.pie(
        rfm,
        names="HighValueCustomer",
        title="High vs Low Value Split",
        color_discrete_sequence=["#7c6af7", "#f76aac"],
        hole=0.55,
    )
    f.update_layout(**PLOTLY_LAYOUT)
    return f


@st.cache_data
def fig_scatter(rfm):
    sample = rfm.sample(min(1200, len(rfm)), random_state=42)
    f = px.scatter(
        sample,
        x="Frequency",
        y="Monetary",
        color="Cluster",
        size="AvgOrderValue",
        hover_data=["Recency", "UniqueProducts", "CustomerLifetime"],
        title="Customer Segments — Frequency vs Monetary Value",
        color_discrete_sequence=["#7c6af7", "#f76aac", "#4af7c4", "#f7c74a"],
    )
    f.update_layout(**PLOTLY_LAYOUT, height=480)
    return f


@st.cache_data
def fig_cluster_bar(cluster_summary):
    f = go.Figure(
        data=[
            go.Bar(
                name="Avg Recency",
                x=cluster_summary["Cluster"].astype(str),
                y=cluster_summary["Recency"],
                marker_color="#7c6af7",
            ),
            go.Bar(
                name="Avg Frequency",
                x=cluster_summary["Cluster"].astype(str),
                y=cluster_summary["Frequency"],
                marker_color="#f76aac",
            ),
            go.Bar(
                name="Avg Order Value",
                x=cluster_summary["Cluster"].astype(str),
                y=cluster_summary["AvgOrderValue"],
                marker_color="#4af7c4",
            ),
            go.Bar(
                name="Unique Products",
                x=cluster_summary["Cluster"].astype(str),
                y=cluster_summary["UniqueProducts"],
                marker_color="#f7c74a",
            ),
        ]
    )
    f.update_layout(
        **PLOTLY_LAYOUT, barmode="group", title="Cluster Feature Averages", height=400
    )
    return f


@st.cache_data
def fig_feature_bar(feature_df):
    f = px.bar(
        feature_df.sort_values("Importance"),
        x="Importance",
        y="Feature",
        orientation="h",
        title="Feature Importance (Random Forest)",
        color="Importance",
        color_continuous_scale=["#1b1f35", "#7c6af7", "#f76aac"],
    )
    f.update_layout(
        **PLOTLY_LAYOUT, height=360, showlegend=False, coloraxis_showscale=False
    )
    return f


@st.cache_data
def fig_radar(feature_df):
    feat = feature_df.set_index("Feature")["Importance"]
    f = go.Figure(
        go.Scatterpolar(
            r=feat.values,
            theta=feat.index.tolist(),
            fill="toself",
            fillcolor="rgba(124,106,247,0.15)",
            line=dict(color="#7c6af7", width=2),
            name="Importance",
        )
    )
    f.update_layout(
        **PLOTLY_LAYOUT,
        polar=dict(
            radialaxis=dict(visible=True, color="#7b80a0"), bgcolor="rgba(0,0,0,0)"
        ),
        title="Feature Importance Radar",
        height=360,
    )
    return f


@st.cache_data
def fig_revenue_pie(cluster_revenue):
    f = px.pie(
        cluster_revenue,
        values="Monetary",
        names="Cluster",
        hole=0.6,
        title="Revenue Share by Cluster",
        color_discrete_sequence=["#7c6af7", "#f76aac", "#4af7c4", "#f7c74a"],
    )
    f.update_layout(**PLOTLY_LAYOUT, height=340)
    return f


# LOAD DATA
try:
    model = load_model()
    rfm = load_rfm()
    feature_df = load_feature_importance()
except Exception as e:
    st.error(f"Could not load required files: {e}")
    st.caption(
        "Make sure **model.pkl**, **rfm_data.csv**, and **feature_importance.csv** are in the same directory."
    )
    st.stop()

stats = get_sidebar_stats(rfm)
cluster_summary = get_cluster_summary(rfm)
cluster_revenue = get_cluster_revenue(rfm)

# SIDEBAR
with st.sidebar:
    st.markdown(
        """
    <div class="anim-fadein" style="padding:10px 0 24px;">
        <div class="anim-float" style="font-family:'Playfair Display',Georgia,serif;font-size:clamp(1.1rem,2vw,1.3rem);font-weight:800;
                    background:linear-gradient(135deg,#a89cff,#f76aac);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            🔮 CustomerIQ
        </div>
        <div style="color:#7b80a0;font-size:clamp(0.68rem,1.2vw,0.75rem);margin-top:4px;letter-spacing:.06em;">
            INTELLIGENCE DASHBOARD
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    page = st.radio(
        "Navigate",
        [
            "🏠  Home",
            "📁  Dataset Overview",
            "🔵  Customer Segmentation",
            "🔮  Purchase Prediction",
            "📈  Model Performance",
            "💡  Business Insights",
            "👤  About Project",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown(
        f"""
    <div class="anim-fadeup" style="font-size:clamp(0.7rem,1.2vw,0.75rem);color:#7b80a0;line-height:2.2;">
        <b style="color:#a89cff">Customers:</b> {stats["total"]:,}<br>
        <b style="color:#f76aac">High Value:</b> {stats["high"]:,}<br>
        <b style="color:#4af7c4">Model Acc:</b> 95.39%<br>
        <b style="color:#f7c74a">ROC-AUC:</b> 0.9908
    </div>
    """,
        unsafe_allow_html=True,
    )

# PAGE: HOME
if "Home" in page:
    st.markdown(
        """
    <div class="anim-fadeup" style="padding:10px 0 32px;">
        <h1>Customer Intelligence<br>Dashboard</h1>
        <p class="hero-sub">
            A machine-learning powered system that segments customers by behavior and predicts
            high-value buyers — helping businesses run smarter retention and marketing campaigns.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Customers", f"{stats['total']:,}")
    c2.metric("High Value", f"{stats['high']:,}")
    c3.metric("Model Accuracy", "95.39%")
    c4.metric("ROC-AUC Score", "0.9908")

    st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
    col1, col2 = st.columns([3, 2], gap="large")

    with col1:
        st.markdown(
            "<div class='section-title'>HOW IT WORKS</div>", unsafe_allow_html=True
        )
        steps = [
            (
                "1",
                "RFM Analysis",
                "RFM",
                "Recency, Frequency & Monetary metrics computed per customer from transactional history.",
            ),
            (
                "2",
                "Feature Engineering",
                None,
                "Customer lifetime, average order value, unique products, and quantity derived.",
            ),
            (
                "3",
                "KMeans Clustering",
                "KMeans",
                "Customers split into 4 behavioral segments using scaled RFM features.",
            ),
            (
                "4",
                "Random Forest Prediction",
                "Random Forest",
                "Trained on labeled data to classify High Value vs Low Value customers with 95%+ accuracy.",
            ),
        ]
        for i, (num, title, term, desc) in enumerate(steps):
            title_html = tt(term, title) if term else f"<span>{title}</span>"
            st.markdown(
                f"""
            <div class="anim-fadeup-d{min(i + 1, 4)}" style="display:flex;align-items:flex-start;gap:14px;
                 padding:16px 0;border-bottom:1px solid rgba(255,255,255,.06);">
                <span class="step-circle">{num}</span>
                <div style="min-width:0;flex:1;">
                    <div style="font-family:'Playfair Display',Georgia,serif;font-weight:700;font-size:clamp(0.85rem,1.5vw,0.95rem);word-break:break-word;">
                        {title_html}
                    </div>
                    <div style="color:#7b80a0;font-size:clamp(0.76rem,1.3vw,0.82rem);margin-top:4px;line-height:1.5;">{desc}</div>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

    with col2:
        st.markdown(
            "<div class='section-title'>TECH STACK</div>", unsafe_allow_html=True
        )
        techs = [
            ("🐼", "Pandas", "Data wrangling & RFM"),
            ("🤖", "Scikit-Learn", "KMeans + Random Forest"),
            ("📊", "Plotly", "Interactive charts"),
            ("🌐", "Streamlit", "Dashboard interface"),
            ("🔢", "NumPy", "Numerical computation"),
        ]
        for i, (icon, name, role) in enumerate(techs):
            st.markdown(
                f"""
            <div class="anim-fadeup-d{min(i + 1, 4)}" style="display:flex;align-items:center;gap:12px;
                 padding:12px 0;border-bottom:1px solid rgba(255,255,255,.05);">
                <span style="font-size:clamp(1.1rem,2vw,1.4rem);flex-shrink:0;">{icon}</span>
                <div style="min-width:0;">
                    <div style="font-family:'Playfair Display',Georgia,serif;font-weight:700;font-size:clamp(0.82rem,1.5vw,0.9rem);">{name}</div>
                    <div style="color:#7b80a0;font-size:clamp(0.7rem,1.2vw,0.78rem);">{role}</div>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown(
        """
    <div class="card-accent anim-fadeup-d4">
        <div style="font-family:'Playfair Display',Georgia,serif;font-weight:800;font-size:clamp(0.9rem,1.8vw,1rem);margin-bottom:10px;">💼 Business Value</div>
        <div class="badge-row">
            <span class="badge badge-purple">Customer Retention</span>
            <span class="badge badge-pink">Personalized Marketing</span>
            <span class="badge badge-teal">Revenue Optimization</span>
            <span class="badge badge-orange">Loyalty Campaigns</span>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

# PAGE: DATASET OVERVIEW
elif "Dataset" in page:
    st.markdown("<h1 class='anim-fadeup'>Dataset Overview</h1>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Customers", f"{stats['total']:,}")
    c2.metric("Total Features", len(rfm.columns))
    c3.metric("High Value Customers", f"{stats['high']:,}")
    c4.metric("Low Value Customers", f"{stats['low']:,}")

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📋 Data Preview", "📊 Statistics", "🔍 Distributions"])

    with tab1:
        st.dataframe(rfm.head(25), use_container_width=True, height=400)

    with tab2:
        st.dataframe(
            rfm.describe().style.background_gradient(cmap="Blues"),
            use_container_width=True,
        )

    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig_recency_hist(rfm), use_container_width=True)
            st.plotly_chart(fig_frequency_hist(rfm), use_container_width=True)
        with col2:
            st.plotly_chart(fig_monetary_hist(rfm), use_container_width=True)
            st.plotly_chart(fig_pie_split(rfm), use_container_width=True)

# PAGE: CUSTOMER SEGMENTATION
elif "Segmentation" in page:
    st.markdown(
        f"""
    <h1 class='anim-fadeup'>Customer Segmentation</h1>
    <p class="anim-fadeup-d1" style="color:#7b80a0;font-size:clamp(0.8rem,1.5vw,0.9rem);margin-bottom:24px;">
        {tt("KMeans", "KMeans clustering")} (k=4) groups customers by {tt("RFM")} behavior.
        Each bubble is a customer — size = {tt("AOV", "average order value")}, color = cluster.
    </p>
    """,
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3 = st.tabs(
        ["🫧 Scatter Map", "📊 Cluster Profiles", "📦 Box Plots"]
    )

    with tab1:
        st.plotly_chart(fig_scatter(rfm), use_container_width=True)

    with tab2:
        st.plotly_chart(fig_cluster_bar(cluster_summary), use_container_width=True)
        st.dataframe(cluster_summary, use_container_width=True)

    with tab3:
        metric = st.selectbox(
            "Select metric", ["Monetary", "Frequency", "Recency", "AvgOrderValue"]
        )
        fig3 = px.box(
            rfm,
            x="Cluster",
            y=metric,
            color="Cluster",
            title=f"{metric} by Cluster",
            color_discrete_sequence=["#7c6af7", "#f76aac", "#4af7c4", "#f7c74a"],
        )
        fig3.update_layout(**PLOTLY_LAYOUT, height=400)
        st.plotly_chart(fig3, use_container_width=True)

# PAGE: PURCHASE PREDICTION
elif "Prediction" in page:
    st.markdown(
        "<h1 class='anim-fadeup'>High Value Customer Predictor</h1>",
        unsafe_allow_html=True,
    )

    # ── Tooltip glossary strip ──
    st.markdown(
        f"""
    <div class="anim-fadeup-d1" style="display:flex;flex-wrap:wrap;gap:8px;
         background:#141728;border:1px solid rgba(124,106,247,.2);
         border-radius:12px;padding:14px 18px;margin-bottom:20px;
         font-size:clamp(0.72rem,1.3vw,0.8rem);">
        <span style="color:#7b80a0;margin-right:6px;">📖 Hover to learn:</span>
        {tt("Recency")} &nbsp;
        {tt("Frequency")} &nbsp;
        {tt("Monetary")} &nbsp;
        {tt("AOV")} &nbsp;
        {tt("KMeans", "Cluster")} &nbsp;
        {tt("Probability")} &nbsp;
        {tt("Random Forest")}
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-title'>ENTER CUSTOMER DATA</div>", unsafe_allow_html=True
    )

    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown("**🕐 Behavioral Signals**")
        recency = st.number_input(
            "Recency (days since last purchase)",
            min_value=0,
            max_value=1000,
            value=20,
            help="Lower is better — means customer bought recently",
        )
        customer_lifetime = st.number_input(
            "Customer Lifetime (days)",
            min_value=0,
            max_value=3000,
            value=200,
            help="Days between first and last purchase",
        )
        frequency = st.number_input(
            "Frequency (unique orders)",
            min_value=1,
            max_value=1000,
            value=15,
            help="Total number of unique orders",
        )

        recency_bar = max(0, min(100, 100 - recency / 3.65))
        st.markdown(
            f"""
        <div style="margin:-8px 0 16px;">
            <div style="font-size:clamp(0.65rem,1.2vw,0.72rem);color:#7b80a0;margin-bottom:4px;">{tt("Recency", "Recency score")} (higher = better)</div>
            <div class="prog-track"><div class="prog-fill" style="width:{recency_bar:.0f}%;"></div></div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown("**💳 Value Signals**")
        avg_order_value = st.number_input(
            "Average Order Value (£)",
            min_value=0.0,
            max_value=10000.0,
            value=280.0,
            step=10.0,
            help="Average total spend per order",
        )
        avg_quantity = st.number_input(
            "Average Quantity per Order",
            min_value=0.0,
            max_value=500.0,
            value=10.0,
            help="Average number of items in each order",
        )
        unique_products = st.number_input(
            "Unique Products Purchased",
            min_value=1,
            max_value=5000,
            value=14,
            help="Number of distinct products the customer has bought",
        )
        cluster = st.selectbox(
            "Customer Cluster (from Segmentation tab)",
            options=[0, 1, 2, 3],
            format_func=lambda x: f"Cluster {x}",
            help="The KMeans cluster this customer belongs to",
        )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    if st.button("🔮  Predict Customer Value", use_container_width=True):
        with st.spinner("Running model…"):
            input_data = pd.DataFrame(
                [
                    {
                        "Recency": recency,
                        "CustomerLifetime": customer_lifetime,
                        "Frequency": frequency,
                        "AvgOrderValue": avg_order_value,
                        "AvgQuantity": avg_quantity,
                        "UniqueProducts": unique_products,
                        "Cluster": cluster,
                    }
                ]
            )
            pred = model.predict(input_data)[0]
            prob = model.predict_proba(input_data)[0][1]

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        r1, r2, r3 = st.columns([2, 1, 1])

        with r1:
            if pred == 1:
                st.markdown(
                    f"""
                <div class="result-card result-high">
                    <div style="font-size:clamp(1.8rem,4vw,2.5rem)">🏆</div>
                    <div class="result-label" style="color:#4af7a0;">HIGH VALUE CUSTOMER</div>
                    <div class="result-prob" style="color:#4af7a0;">{prob * 100:.1f}%</div>
                    <div style="color:#7b80a0;font-size:clamp(0.72rem,1.3vw,0.82rem);">{tt("Probability", "probability")} of being high value</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )
                st.success(
                    "✅ Recommend: Premium loyalty program, VIP offers, early access campaigns."
                )
            else:
                st.markdown(
                    f"""
                <div class="result-card result-low">
                    <div style="font-size:clamp(1.8rem,4vw,2.5rem)">📌</div>
                    <div class="result-label" style="color:#f76a7c;">LOW VALUE CUSTOMER</div>
                    <div class="result-prob" style="color:#f76a7c;">{prob * 100:.1f}%</div>
                    <div style="color:#7b80a0;font-size:clamp(0.72rem,1.3vw,0.82rem);">{tt("Probability", "probability")} of being high value</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )
                st.warning(
                    "📌 Recommend: Re-engagement campaigns, discount nudges, onboarding journey."
                )

        with r2:
            st.metric("Probability", f"{prob * 100:.2f}%")
            st.metric("Prediction", "High ✅" if pred == 1 else "Low ❌")
        with r3:
            st.metric("Frequency", frequency)
            st.metric("AOV", f"£{avg_order_value:,.0f}")

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='section-title'>INPUT SUMMARY</div>", unsafe_allow_html=True
        )
        st.dataframe(input_data, use_container_width=True)

        fig_gauge = go.Figure(
            go.Indicator(
                mode="gauge+number+delta",
                value=prob * 100,
                title={
                    "text": "High Value Probability",
                    "font": {
                        "family": "Playfair Display",
                        "size": 15,
                        "color": "#e8eaf6",
                    },
                },
                delta={
                    "reference": 50,
                    "increasing": {"color": "#4af7a0"},
                    "decreasing": {"color": "#f76a7c"},
                },
                gauge={
                    "axis": {"range": [0, 100], "tickcolor": "#7b80a0"},
                    "bar": {"color": "#7c6af7"},
                    "bgcolor": "#141728",
                    "bordercolor": "rgba(255,255,255,0.05)",
                    "steps": [
                        {"range": [0, 40], "color": "rgba(247,106,124,0.15)"},
                        {"range": [40, 65], "color": "rgba(247,199,74,0.1)"},
                        {"range": [65, 100], "color": "rgba(74,247,160,0.12)"},
                    ],
                    "threshold": {
                        "line": {"color": "#f76aac", "width": 2},
                        "thickness": 0.75,
                        "value": 50,
                    },
                },
            )
        )
        fig_gauge.update_layout(**PLOTLY_LAYOUT, height=260)
        st.plotly_chart(fig_gauge, use_container_width=True)

# PAGE: MODEL PERFORMANCE
elif "Performance" in page:
    st.markdown(
        "<h1 class='anim-fadeup'>Model Performance</h1>", unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Accuracy", "95.39%", "+5.4% vs baseline")
    c2.metric("ROC-AUC ↗", "0.9908", "Near-perfect")
    c3.metric("Estimators", "300", "Trees in forest")
    c4.metric("Max Depth", "12", "Tree depth limit")

    st.markdown(
        f"""
    <div style="display:flex;flex-wrap:wrap;gap:8px;
         background:#141728;border:1px solid rgba(124,106,247,.2);
         border-radius:12px;padding:12px 18px;margin:8px 0 20px;
         font-size:clamp(0.72rem,1.3vw,0.8rem);">
        <span style="color:#7b80a0;margin-right:6px;">📖 Hover to learn:</span>
        {tt("ROC-AUC")} &nbsp; {tt("Baseline")} &nbsp;
        {tt("Feature Importance")} &nbsp; {tt("Random Forest")} &nbsp;
        {tt("Overfitting")} &nbsp; {tt("Stratify", "Stratified Split")}
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    col1, col2 = st.columns([3, 2], gap="large")

    with col1:
        st.plotly_chart(fig_feature_bar(feature_df), use_container_width=True)

    with col2:
        st.markdown(
            "<div class='section-title'>MODEL CONFIG</div>", unsafe_allow_html=True
        )
        params = [
            ("Algorithm", "Random Forest Classifier"),
            ("n_estimators", "300"),
            ("max_depth", "12"),
            ("min_samples_split", "5"),
            ("min_samples_leaf", "2"),
            (tt("Stratify", "stratify"), "Yes (train/test split)"),
            ("test_size", "20%"),
            ("random_state", "42"),
        ]
        for k, v in params:
            st.markdown(
                f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
                        padding:10px 0;border-bottom:1px solid rgba(255,255,255,.05);
                        font-size:clamp(0.76rem,1.3vw,0.84rem);gap:8px;">
                <span style="color:#7b80a0;flex-shrink:0;">{k}</span>
                <span style="color:#e8eaf6;font-weight:600;text-align:right;word-break:break-word;">{v}</span>
            </div>
            """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.markdown(
        f"""
    <p class="anim-fadeup" style="color:#7b80a0;font-size:clamp(0.78rem,1.3vw,0.85rem);margin-bottom:8px;">
        The radar below shows {tt("Feature Importance")} — which signals the
        {tt("Random Forest")} relied on most.
    </p>
    """,
        unsafe_allow_html=True,
    )
    st.plotly_chart(fig_radar(feature_df), use_container_width=True)

# PAGE: BUSINESS INSIGHTS
elif "Insights" in page:
    st.markdown(
        "<h1 class='anim-fadeup'>Business Insights</h1>", unsafe_allow_html=True
    )
    st.markdown(
        f"""
    <p class="anim-fadeup-d1" style="color:#7b80a0;margin-bottom:28px;font-size:clamp(0.8rem,1.5vw,0.9rem);">
        Translate {tt("Predict", "model predictions")} into real marketing actions.
        Each {tt("Clustering", "customer segment")} needs a different strategy.
    </p>
    """,
        unsafe_allow_html=True,
    )

    segments = [
        (
            "👑",
            "VIP Customers",
            "High recency + high frequency + high monetary",
            "These are your top 25% most profitable customers. They buy often, spend big, and are recently active.",
            [
                "Premium loyalty rewards",
                "Exclusive early access",
                "Personal account manager",
                "Anniversary gifts",
            ],
            "#7c6af7",
        ),
        (
            "🏷️",
            "Discount Buyers",
            "High frequency + low AOV",
            "They shop often but primarily respond to deals. Price-sensitive but loyal to savings.",
            [
                "Coupon campaigns",
                "Seasonal bundle offers",
                "Flash sale notifications",
                "Volume discounts",
            ],
            "#f76aac",
        ),
        (
            "⚠️",
            "At-Risk Customers",
            "High recency + previously high value",
            "They used to buy frequently but haven't returned. Needs win-back strategy before permanent churn.",
            [
                "Win-back email sequences",
                "Personalised reminders",
                "Re-engagement discounts",
                "Surveys to understand drop-off",
            ],
            "#f7c74a",
        ),
        (
            "🆕",
            "One-Time Buyers",
            "Frequency = 1, low lifetime",
            "Bought once but never returned. Crucial to convert to repeat buyers in the first 30–60 days.",
            [
                "Onboarding email series",
                "First purchase follow-up",
                "Cross-sell recommendations",
                "Review request + reward",
            ],
            "#4af7c4",
        ),
    ]

    for i, (icon, title, subtitle, desc, actions, color) in enumerate(segments):
        badges = "".join(
            f'<span style="background:{color}18;color:{color};border:1px solid {color}33;'
            f"padding:5px 11px;border-radius:20px;font-size:clamp(0.68rem,1.2vw,0.75rem);"
            f'font-weight:600;transition:transform .15s;white-space:nowrap;" '
            f"onmouseover=\"this.style.transform='translateY(-2px)'\" "
            f"onmouseout=\"this.style.transform=''\">{a}</span>"
            for a in actions
        )
        st.markdown(
            f"""
        <div class="insight-card anim-fadeup-d{min(i + 1, 4)}" style="border-left:4px solid {color};margin-bottom:16px;">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;flex-wrap:wrap;">
                <span style="font-size:clamp(1.4rem,3vw,1.8rem);flex-shrink:0;">{icon}</span>
                <div style="min-width:0;">
                    <div style="font-family:'Playfair Display',Georgia,serif;font-weight:800;font-size:clamp(0.95rem,2vw,1.1rem);word-break:break-word;">{title}</div>
                    <div style="color:{color};font-size:clamp(0.68rem,1.2vw,0.75rem);letter-spacing:.05em;font-weight:600;word-break:break-word;">{subtitle}</div>
                </div>
            </div>
            <p style="color:#9b9fbb;font-size:clamp(0.78rem,1.4vw,0.85rem);line-height:1.6;margin-bottom:14px;">{desc}</p>
            <div class="badge-row">{badges}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    if "Cluster" in rfm.columns:
        st.markdown(
            "<div class='section-title'>CLUSTER REVENUE CONTRIBUTION</div>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig_revenue_pie(cluster_revenue), use_container_width=True)

# PAGE: ABOUT PROJECT
elif "About" in page:
    st.markdown(
        "<h1 class='anim-fadeup'>About This Project</h1>", unsafe_allow_html=True
    )
    st.markdown(
        """
    <div class="card-accent anim-fadeup-d1" style="margin-bottom:24px;">
        <div style="font-family:'Playfair Display',Georgia,serif;font-weight:800;font-size:clamp(0.95rem,2vw,1.15rem);margin-bottom:8px;">
            🔮 CustomerIQ — Customer Segmentation & Value Prediction
        </div>
        <p style="color:#9b9fbb;font-size:clamp(0.78rem,1.4vw,0.88rem);line-height:1.7;margin:0;">
        Built to solve a real business problem: most companies can't tell which customers are truly valuable
        until it's too late. This project uses behavioral data — not demographics — to classify customers
        with 95%+ accuracy, segment them into actionable groups, and guide marketing decisions with data.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown(
            "<div class='section-title'>THE PROBLEM</div>", unsafe_allow_html=True
        )
        st.markdown(
            f"""
        <div class="card anim-fadeup-d1">
        <p style="color:#9b9fbb;font-size:clamp(0.78rem,1.4vw,0.85rem);line-height:1.8;margin:0;">
        Businesses using the <b style="color:#a89cff">Online Retail dataset</b> (541K+ rows of UK transaction data)
        often spend equal effort on all customers — wasting resources on one-time buyers while under-investing
        in high-value repeat customers.<br><br>
        The challenge: <b style="color:#f76aac">identify high-value customers early</b> from
        {tt("RFM", "behavioral patterns")} alone.
        </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown("<div class='section-title'>DATASET</div>", unsafe_allow_html=True)
        st.markdown(
            """
        <div class="card anim-fadeup-d2">
        <div style="font-size:clamp(0.76rem,1.3vw,0.83rem);color:#9b9fbb;line-height:2.2;">
        📦 Source: <b style="color:#e8eaf6">UCI ML Repository — Online Retail</b><br>
        🗺️ Country focus: <b style="color:#e8eaf6">United Kingdom (80%+ transactions)</b><br>
        📅 Period: <b style="color:#e8eaf6">Dec 2010 — Dec 2011</b><br>
        🧹 After cleaning: <b style="color:#e8eaf6">~4,300 unique customers</b><br>
        🎯 Target: <b style="color:#e8eaf6">Top 25% by Monetary value = High Value</b>
        </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            "<div class='section-title'>ML PIPELINE</div>", unsafe_allow_html=True
        )
        pipeline = [
            (
                "📥",
                "Load & Explore",
                None,
                "541K+ rows loaded, missing/cancelled orders identified",
            ),
            (
                "🧹",
                "Clean",
                None,
                "Removed null CustomerIDs, cancellations (C prefix), negative quantities",
            ),
            (
                "📐",
                "RFM Engineering",
                "RFM",
                "7 features derived: Recency, Lifetime, Frequency, AOV, Quantity, Products, Cluster",
            ),
            (
                "🔵",
                "KMeans Clustering",
                "KMeans",
                "4 segments on scaled RFM — no target leakage",
            ),
            (
                "🎯",
                "Label Creation",
                None,
                "75th percentile Monetary = High Value threshold",
            ),
            (
                "🌲",
                "Random Forest",
                "Random Forest",
                "300 trees, depth 12, 80/20 split, stratified",
            ),
            (
                "📊",
                "Evaluation",
                "ROC-AUC",
                "95.39% accuracy, 0.9908 ROC-AUC on held-out test set",
            ),
        ]
        for i, (icon, step, term, detail) in enumerate(pipeline):
            step_html = tt(term, step) if term else step
            st.markdown(
                f"""
            <div class="anim-fadeup-d{min(i + 1, 4)}" style="display:flex;gap:14px;padding:12px 0;border-bottom:1px solid rgba(255,255,255,.05);align-items:flex-start;">
                <span style="font-size:clamp(1rem,2vw,1.2rem);flex-shrink:0;">{icon}</span>
                <div style="min-width:0;flex:1;">
                    <div style="font-family:'Playfair Display',Georgia,serif;font-weight:700;font-size:clamp(0.8rem,1.4vw,0.88rem);word-break:break-word;">{step_html}</div>
                    <div style="color:#7b80a0;font-size:clamp(0.7rem,1.2vw,0.78rem);margin-top:2px;line-height:1.5;">{detail}</div>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# FOOTER
st.markdown(
    """
<div class="caption-bar anim-fadein">
    <span class="glow-dot"></span>
    CustomerIQ · Built with Streamlit, Random Forest, KMeans & RFM Analysis ·
    <span style="color:#7c6af7;">scikit-learn</span> ·
    <span style="color:#f76aac;">plotly</span> ·
    <span style="color:#4af7c4;">pandas</span>
</div>
""",
    unsafe_allow_html=True,
)
