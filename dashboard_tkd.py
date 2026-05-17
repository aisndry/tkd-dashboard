"""
Dashboard TKD - Transfer ke Daerah
Kementerian Keuangan RI - DJPB
Production-grade dashboard: Excel/CSV reader, PDF/Excel export, Proyeksi 1/3/5/10 tahun
NO plotly dependency - uses matplotlib + altair + streamlit native
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import FancyBboxPatch
import matplotlib.gridspec as gridspec
import io
import os
import warnings
from datetime import datetime

warnings.filterwarnings("ignore")

# ---------------------------------------------
# PAGE CONFIG
# ---------------------------------------------
st.set_page_config(
    page_title="Dashboard TKD · DJPB Kemenkeu",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------
# GLOBAL CSS -- Modern Government Dark Theme
# ---------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Space+Mono:wght@400;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* -- Root palette -- */
:root {
    --bg-base:       #0a0e1a;
    --bg-card:       #111827;
    --bg-card2:      #1a2235;
    --accent-gold:   #f5a623;
    --accent-blue:   #3b82f6;
    --accent-green:  #10b981;
    --accent-red:    #ef4444;
    --accent-purple: #8b5cf6;
    --text-primary:  #f1f5f9;
    --text-muted:    #94a3b8;
    --border:        rgba(255,255,255,0.07);
}

/* -- App background -- */
.stApp {
    background: var(--bg-base) !important;
    background-image:
        radial-gradient(ellipse at 20% 0%, rgba(59,130,246,0.08) 0%, transparent 60%),
        radial-gradient(ellipse at 80% 100%, rgba(245,166,35,0.06) 0%, transparent 60%) !important;
}

/* -- Sidebar -- */
[data-testid="stSidebar"] {
    background: #0d1220 !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label {
    color: var(--text-muted) !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}

/* -- KPI cards -- */
.kpi-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 20px 24px;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
}
.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 40px rgba(0,0,0,0.4);
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 16px 16px 0 0;
}
.kpi-card.gold::before  { background: var(--accent-gold); }
.kpi-card.blue::before  { background: var(--accent-blue); }
.kpi-card.green::before { background: var(--accent-green); }
.kpi-card.purple::before{ background: var(--accent-purple); }
.kpi-label {
    color: var(--text-muted);
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.kpi-value {
    color: var(--text-primary);
    font-size: 1.9rem;
    font-weight: 800;
    line-height: 1;
    margin-bottom: 4px;
}
.kpi-sub {
    color: var(--text-muted);
    font-size: 0.75rem;
    font-weight: 500;
}
.kpi-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 99px;
    font-size: 0.7rem;
    font-weight: 700;
    margin-top: 8px;
}
.badge-up   { background: rgba(16,185,129,0.15); color: #10b981; }
.badge-down { background: rgba(239,68,68,0.15);  color: #ef4444; }
.badge-flat { background: rgba(148,163,184,0.1); color: #94a3b8; }

/* -- Section headers -- */
.section-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 32px 0 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border);
}
.section-icon {
    width: 36px; height: 36px;
    background: rgba(59,130,246,0.15);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
}
.section-title {
    color: var(--text-primary);
    font-size: 1.05rem;
    font-weight: 700;
    margin: 0;
}

/* -- Tables -- */
.stDataFrame { border-radius: 12px !important; overflow: hidden !important; }
[data-testid="stDataFrame"] thead th {
    background: var(--bg-card2) !important;
    color: var(--text-muted) !important;
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}

/* -- Buttons -- */
.stDownloadButton > button {
    background: linear-gradient(135deg, #1d4ed8, #2563eb) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    padding: 10px 20px !important;
    transition: all 0.2s !important;
}
.stDownloadButton > button:hover {
    background: linear-gradient(135deg, #1e40af, #1d4ed8) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(37,99,235,0.35) !important;
}

/* -- File uploader -- */
[data-testid="stFileUploader"] {
    background: var(--bg-card) !important;
    border: 2px dashed rgba(59,130,246,0.3) !important;
    border-radius: 16px !important;
    padding: 24px !important;
}

/* -- Metrics -- */
[data-testid="metric-container"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 16px !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: var(--text-primary) !important;
}
[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    color: var(--text-muted) !important;
}

/* -- Tabs -- */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-card) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    color: var(--text-muted) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
}
.stTabs [aria-selected="true"] {
    background: var(--accent-blue) !important;
    color: white !important;
}

/* -- Selectbox / inputs -- */
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: var(--bg-card) !important;
    border-color: var(--border) !important;
    color: var(--text-primary) !important;
}

/* -- Alert boxes -- */
.info-box {
    background: rgba(59,130,246,0.08);
    border-left: 4px solid var(--accent-blue);
    border-radius: 0 12px 12px 0;
    padding: 14px 18px;
    margin: 12px 0;
    color: var(--text-primary);
    font-size: 0.85rem;
}
.warn-box {
    background: rgba(245,166,35,0.08);
    border-left: 4px solid var(--accent-gold);
    border-radius: 0 12px 12px 0;
    padding: 14px 18px;
    margin: 12px 0;
    color: var(--text-primary);
    font-size: 0.85rem;
}

/* -- Hero header -- */
.hero-header {
    background: linear-gradient(135deg, #111827 0%, #1a2235 100%);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 28px 36px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}
.hero-header::after {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 240px; height: 240px;
    background: radial-gradient(circle, rgba(245,166,35,0.1) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-title {
    color: var(--text-primary);
    font-size: 1.7rem;
    font-weight: 800;
    margin: 0 0 4px;
    line-height: 1.2;
}
.hero-subtitle {
    color: var(--text-muted);
    font-size: 0.9rem;
    font-weight: 400;
    margin: 0;
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(245,166,35,0.12);
    border: 1px solid rgba(245,166,35,0.25);
    color: var(--accent-gold);
    border-radius: 99px;
    padding: 4px 14px;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------
# MATPLOTLIB STYLE -- matches dark theme
# ---------------------------------------------
plt.style.use("dark_background")
MCOLOR = {
    "bg":     "#111827",
    "bg2":    "#1a2235",
    "gold":   "#f5a623",
    "blue":   "#3b82f6",
    "green":  "#10b981",
    "red":    "#ef4444",
    "purple": "#8b5cf6",
    "text":   "#f1f5f9",
    "muted":  "#94a3b8",
    "grid":   "#1e293b",
}

def mpl_fig(w=10, h=4.5):
    fig, ax = plt.subplots(figsize=(w, h), facecolor=MCOLOR["bg"])
    ax.set_facecolor(MCOLOR["bg"])
    ax.tick_params(colors=MCOLOR["muted"], labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor(MCOLOR["grid"])
    ax.grid(axis="y", color=MCOLOR["grid"], linewidth=0.8, alpha=0.6)
    ax.grid(axis="x", visible=False)
    return fig, ax

def fmt_rp(v):
    """Format angka ke Rupiah singkat (T / M / B)"""
    if pd.isna(v):
        return "-"
    v = float(v)
    if abs(v) >= 1e12:
        return f"Rp {v/1e12:.2f} T"
    if abs(v) >= 1e9:
        return f"Rp {v/1e9:.1f} M"
    if abs(v) >= 1e6:
        return f"Rp {v/1e6:.1f} jt"
    return f"Rp {v:,.0f}"

def fmt_pct(v):
    if pd.isna(v):
        return "-"
    return f"{float(v):.1f}%"

# ---------------------------------------------
# DATA LOADING -- rock-solid Excel/CSV reader
# ---------------------------------------------
@st.cache_data(show_spinner=False)
def load_file(uploaded_file):
    name = uploaded_file.name.lower()
    errors = []

    if name.endswith(".csv"):
        raw = uploaded_file.read()
        for enc in ["utf-8", "utf-8-sig", "latin-1", "cp1252", "iso-8859-1"]:
            try:
                text = raw.decode(enc)
                for sep in [",", ";", "\t", "|"]:
                    try:
                        df = pd.read_csv(io.StringIO(text), sep=sep)
                        if len(df.columns) > 1:
                            return df, None
                    except Exception:
                        pass
            except Exception as e:
                errors.append(str(e))
        return None, f"CSV tidak bisa dibaca. Coba simpan ulang sebagai UTF-8. Detail: {'; '.join(errors)}"

    elif name.endswith(".xlsx") or name.endswith(".xlsm"):
        data = uploaded_file.read()
        try:
            xf = pd.ExcelFile(io.BytesIO(data), engine="openpyxl")
            sheets = xf.sheet_names
            if len(sheets) > 1:
                sheet = st.sidebar.selectbox("Sheet Excel", sheets)
            else:
                sheet = sheets[0]
            df = pd.read_excel(io.BytesIO(data), sheet_name=sheet, engine="openpyxl")
            return df, None
        except Exception as e:
            errors.append(f"openpyxl: {e}")

    elif name.endswith(".xls"):
        data = uploaded_file.read()
        try:
            df = pd.read_excel(io.BytesIO(data), engine="xlrd")
            return df, None
        except Exception as e:
            errors.append(f"xlrd: {e}")

    else:
        return None, f"Format '{name}' tidak didukung. Upload .xlsx, .xls, atau .csv"

    return None, f"File tidak bisa dibaca: {'; '.join(errors)}"


def detect_columns(df: pd.DataFrame) -> dict:
    """Auto-detect kolom pagu, realisasi, wilayah, tahun dari nama kolom."""
    cols = {c.lower(): c for c in df.columns}
    result = {}

    # Pagu
    for k in ["pagu", "anggaran", "alokasi", "budget", "target", "pagu_anggaran"]:
        if k in cols:
            result["pagu"] = cols[k]; break
    # Realisasi
    for k in ["realisasi", "realization", "actual", "pencairan", "penyerapan"]:
        if k in cols:
            result["real"] = cols[k]; break
    # Wilayah / daerah
    for k in ["wilayah", "daerah", "provinsi", "kab", "kota", "kabupaten", "region", "satker", "kode_wilayah"]:
        if k in cols:
            result["wilayah"] = cols[k]; break
    # Tahun
    for k in ["tahun", "year", "ta", "tp"]:
        if k in cols:
            result["tahun"] = cols[k]; break

    return result


def clean_numeric(series: pd.Series) -> pd.Series:
    """Clean kolom numerik: hapus Rp, koma, titik ribuan, dll."""
    if pd.api.types.is_numeric_dtype(series):
        return series
    s = series.astype(str)
    s = s.str.replace(r"[Rp\s]", "", regex=True)
    s = s.str.replace(r"[^\d.,-]", "", regex=True)
    # Handle format 1.000.000,00 (ID) vs 1,000,000.00 (US)
    if s.str.contains(",").any() and s.str.contains(r"\.", regex=True).any():
        # If last separator is comma → ID format
        has_comma_last = s.str.match(r"^[\d.]+,\d{1,2}$")
        if has_comma_last.mean() > 0.3:
            s = s.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
        else:
            s = s.str.replace(",", "", regex=False)
    elif s.str.contains(",").any():
        s = s.str.replace(",", ".", regex=False)
    return pd.to_numeric(s, errors="coerce")


# ---------------------------------------------
# FORECASTING ENGINE
# ---------------------------------------------
def forecast_series(values: np.ndarray, years_out: list) -> dict:
    """
    Ensemble forecast: Linear regression + CAGR weighted average.
    Returns dict {year_out: {"min","mid","max"}} as absolute values.
    """
    v = np.array([x for x in values if not np.isnan(x)], dtype=float)
    n = len(v)
    if n < 2:
        last = v[-1] if n == 1 else np.nan
        return {y: {"min": last, "mid": last, "max": last} for y in years_out}

    # 1) Linear regression
    x = np.arange(n)
    A = np.vstack([x, np.ones(n)]).T
    slope, intercept = np.linalg.lstsq(A, v, rcond=None)[0]

    # 2) CAGR (first to last)
    cagr = (v[-1] / v[0]) ** (1 / (n - 1)) - 1 if v[0] > 0 else 0.0

    results = {}
    for y in years_out:
        lin = intercept + slope * (n - 1 + y)
        cagr_val = v[-1] * ((1 + cagr) ** y)

        # Ensemble: weight linear 60%, cagr 40%
        mid = 0.60 * lin + 0.40 * cagr_val
        # Uncertainty ±15% expanding with horizon
        ci = 0.10 + 0.02 * y
        results[y] = {
            "min": mid * (1 - ci),
            "mid": mid,
            "max": mid * (1 + ci),
        }
    return results


def calc_cagr(values: np.ndarray) -> float:
    v = np.array([x for x in values if x and not np.isnan(x)], dtype=float)
    if len(v) < 2 or v[0] <= 0:
        return np.nan
    return ((v[-1] / v[0]) ** (1 / (len(v) - 1)) - 1) * 100


# ---------------------------------------------
# PDF EXPORT (reportlab)
# ---------------------------------------------
def generate_pdf(df: pd.DataFrame, kpi: dict, cols: dict, filters: dict) -> bytes:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4,
                                leftMargin=2*cm, rightMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)

        styles = getSampleStyleSheet()
        NAVY  = colors.HexColor("#0d1220")
        GOLD  = colors.HexColor("#f5a623")
        BLUE  = colors.HexColor("#3b82f6")
        LGRAY = colors.HexColor("#f1f5f9")
        MGRAY = colors.HexColor("#94a3b8")
        WHITE = colors.white

        title_style = ParagraphStyle("title", parent=styles["Normal"],
            fontSize=18, textColor=WHITE, fontName="Helvetica-Bold",
            alignment=TA_CENTER, spaceAfter=4)
        sub_style = ParagraphStyle("sub", parent=styles["Normal"],
            fontSize=9, textColor=MGRAY, fontName="Helvetica",
            alignment=TA_CENTER, spaceAfter=2)
        h2_style = ParagraphStyle("h2", parent=styles["Normal"],
            fontSize=12, textColor=BLUE, fontName="Helvetica-Bold",
            spaceBefore=14, spaceAfter=6)
        body_style = ParagraphStyle("body", parent=styles["Normal"],
            fontSize=8, textColor=colors.HexColor("#1e293b"),
            fontName="Helvetica", spaceAfter=4)

        story = []

        # -- Title block --
        story.append(Spacer(1, 0.2*cm))
        story.append(Paragraph("LAPORAN DASHBOARD TKD", title_style))
        story.append(Paragraph("Transfer ke Daerah -- DJPB Kemenkeu RI", sub_style))
        story.append(Paragraph(f"Dicetak: {datetime.now().strftime('%d %B %Y, %H:%M')}", sub_style))
        story.append(HRFlowable(width="100%", thickness=2, color=GOLD, spaceAfter=12))

        # -- Filter info --
        if any(filters.values()):
            ftext = "  |  ".join([f"{k}: {v}" for k, v in filters.items() if v])
            story.append(Paragraph(f"<b>Filter Aktif:</b> {ftext}", body_style))
            story.append(Spacer(1, 0.2*cm))

        # -- KPI table --
        story.append(Paragraph("Ringkasan KPI", h2_style))
        kpi_data = [
            ["Indikator", "Nilai"],
            ["Total Pagu",       fmt_rp(kpi.get("total_pagu", 0))],
            ["Total Realisasi",  fmt_rp(kpi.get("total_real", 0))],
            ["% Penyerapan",     fmt_pct(kpi.get("pct_real", 0))],
            ["Jumlah Wilayah",   str(kpi.get("n_wilayah", "-"))],
            ["Jumlah Record",    f"{kpi.get('n_rows', 0):,}"],
        ]
        kpi_tbl = Table(kpi_data, colWidths=[9*cm, 7*cm])
        kpi_tbl.setStyle(TableStyle([
            ("BACKGROUND",   (0,0), (-1,0), BLUE),
            ("TEXTCOLOR",    (0,0), (-1,0), WHITE),
            ("FONTNAME",     (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",     (0,0), (-1,-1), 9),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [LGRAY, WHITE]),
            ("GRID",         (0,0), (-1,-1), 0.3, colors.HexColor("#cbd5e1")),
            ("PADDING",      (0,0), (-1,-1), 6),
        ]))
        story.append(kpi_tbl)
        story.append(Spacer(1, 0.4*cm))

        # -- Data table (max 100 rows) --
        story.append(Paragraph("Data Detail (maks. 100 baris)", h2_style))
        show_df = df.head(100)
        tbl_data = [list(show_df.columns)]
        for _, row in show_df.iterrows():
            tbl_data.append([str(v)[:30] if pd.notna(v) else "" for v in row])

        col_w = 17 / len(show_df.columns)
        data_tbl = Table(tbl_data, colWidths=[col_w*cm]*len(show_df.columns), repeatRows=1)
        data_tbl.setStyle(TableStyle([
            ("BACKGROUND",   (0,0), (-1,0), NAVY),
            ("TEXTCOLOR",    (0,0), (-1,0), WHITE),
            ("FONTNAME",     (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",     (0,0), (-1,-1), 7),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [LGRAY, WHITE]),
            ("GRID",         (0,0), (-1,-1), 0.2, colors.HexColor("#e2e8f0")),
            ("PADDING",      (0,0), (-1,-1), 4),
            ("ALIGN",        (0,0), (-1,-1), "LEFT"),
            ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
        ]))
        story.append(data_tbl)

        # -- Footer --
        story.append(Spacer(1, 0.5*cm))
        story.append(HRFlowable(width="100%", thickness=0.5, color=MGRAY))
        story.append(Paragraph(
            "Dashboard TKD · DJPB Kementerian Keuangan RI · Rahasia / Internal",
            ParagraphStyle("footer", parent=styles["Normal"],
                fontSize=7, textColor=MGRAY, fontName="Helvetica",
                alignment=TA_CENTER)
        ))

        doc.build(story)
        return buf.getvalue()
    except ImportError:
        return None


def generate_excel(df: pd.DataFrame, kpi: dict, forecast_df=None) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Data", index=False)

        # KPI sheet
        kpi_df = pd.DataFrame([
            {"Indikator": "Total Pagu",       "Nilai": kpi.get("total_pagu", 0)},
            {"Indikator": "Total Realisasi",  "Nilai": kpi.get("total_real", 0)},
            {"Indikator": "% Penyerapan",     "Nilai": kpi.get("pct_real", 0)},
            {"Indikator": "Jumlah Wilayah",   "Nilai": kpi.get("n_wilayah", "-")},
            {"Indikator": "Jumlah Record",    "Nilai": kpi.get("n_rows", 0)},
        ])
        kpi_df.to_excel(writer, sheet_name="Ringkasan KPI", index=False)

        if forecast_df is not None and not forecast_df.empty:
            forecast_df.to_excel(writer, sheet_name="Proyeksi", index=False)

    return buf.getvalue()


# ---------------------------------------------
# CHART FUNCTIONS
# ---------------------------------------------
def chart_bar_pagu_real(df_agg, col_pagu, col_real, col_wilayah, top_n=15):
    """Bar chart grouped: Pagu vs Realisasi per wilayah."""
    data = df_agg.nlargest(top_n, col_pagu)
    labels = data[col_wilayah].astype(str).str[:18].tolist()
    pagu   = data[col_pagu].tolist()
    real   = data[col_real].tolist() if col_real else [0] * len(pagu)

    fig, ax = mpl_fig(10, 4.5)
    x = np.arange(len(labels))
    w = 0.38
    b1 = ax.bar(x - w/2, pagu, w, label="Pagu", color=MCOLOR["blue"], alpha=0.9, zorder=3)
    b2 = ax.bar(x + w/2, real, w, label="Realisasi", color=MCOLOR["green"], alpha=0.9, zorder=3)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=35, ha="right", fontsize=7.5, color=MCOLOR["muted"])
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda v, _: f"{v/1e12:.1f}T" if v >= 1e12 else (f"{v/1e9:.0f}M" if v >= 1e9 else f"{v/1e6:.0f}jt")
    ))
    ax.legend(framealpha=0, labelcolor=MCOLOR["muted"], fontsize=8)
    ax.set_title("Pagu vs Realisasi per Wilayah", color=MCOLOR["text"], fontsize=10, fontweight="bold", pad=10)
    fig.tight_layout()
    return fig


def chart_trend(years, pagu_vals, real_vals):
    """Line chart trend tahun."""
    fig, ax = mpl_fig(10, 4)
    ax.plot(years, pagu_vals, "o-", color=MCOLOR["blue"],  linewidth=2.5, markersize=7, label="Pagu")
    ax.plot(years, real_vals, "s-", color=MCOLOR["green"], linewidth=2.5, markersize=7, label="Realisasi")
    ax.fill_between(years, pagu_vals, real_vals, alpha=0.06, color=MCOLOR["gold"])
    ax.set_xticks(years)
    ax.set_xticklabels([str(int(y)) for y in years], color=MCOLOR["muted"], fontsize=8.5)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda v, _: f"{v/1e12:.1f}T" if v >= 1e12 else f"{v/1e9:.0f}M"
    ))
    ax.legend(framealpha=0, labelcolor=MCOLOR["muted"], fontsize=8)
    ax.set_title("Tren Pagu & Realisasi per Tahun", color=MCOLOR["text"], fontsize=10, fontweight="bold", pad=10)
    fig.tight_layout()
    return fig


def chart_pct_bar(df_agg, col_real, col_pagu, col_wilayah, top_n=20):
    """Horizontal bar: % penyerapan per wilayah."""
    data = df_agg.copy()
    data["pct"] = (data[col_real] / data[col_pagu] * 100).clip(0, 200)
    data = data.dropna(subset=["pct"]).nlargest(top_n, "pct")

    fig, ax = plt.subplots(figsize=(9, max(3.5, len(data)*0.38)), facecolor=MCOLOR["bg"])
    ax.set_facecolor(MCOLOR["bg"])

    colors_bar = [MCOLOR["green"] if p >= 90 else (MCOLOR["gold"] if p >= 70 else MCOLOR["red"])
                  for p in data["pct"]]
    bars = ax.barh(data[col_wilayah].astype(str).str[:22], data["pct"],
                   color=colors_bar, alpha=0.9, height=0.65, zorder=3)
    ax.axvline(100, color=MCOLOR["muted"], linewidth=1, linestyle="--", alpha=0.5)
    ax.set_xlabel("% Penyerapan", color=MCOLOR["muted"], fontsize=8)
    ax.tick_params(colors=MCOLOR["muted"], labelsize=7.5)
    for spine in ax.spines.values():
        spine.set_edgecolor(MCOLOR["grid"])
    ax.grid(axis="x", color=MCOLOR["grid"], linewidth=0.7, alpha=0.5)
    ax.set_title("% Penyerapan per Wilayah", color=MCOLOR["text"], fontsize=10, fontweight="bold", pad=10)
    fig.tight_layout()
    return fig


def chart_forecast(years_hist, vals_hist, fore_dict, label="Pagu", color=MCOLOR["blue"]):
    """Forecast chart dengan confidence band."""
    fig, ax = mpl_fig(10, 4.5)

    ax.plot(years_hist, vals_hist, "o-", color=color, linewidth=2.5, markersize=7,
            label=f"Historis {label}", zorder=4)

    last_year = int(years_hist[-1]) if len(years_hist) else datetime.now().year
    fore_years = [last_year + y for y in sorted(fore_dict.keys())]
    fore_mid   = [fore_dict[y]["mid"] for y in sorted(fore_dict.keys())]
    fore_min   = [fore_dict[y]["min"] for y in sorted(fore_dict.keys())]
    fore_max   = [fore_dict[y]["max"] for y in sorted(fore_dict.keys())]

    # Bridge from last historical point
    bridge_x = [years_hist[-1]] + fore_years
    bridge_y = [vals_hist[-1]] + fore_mid
    ax.plot(bridge_x, bridge_y, "--o", color=MCOLOR["gold"], linewidth=2, markersize=6,
            label=f"Proyeksi {label}", zorder=4)
    ax.fill_between(fore_years, fore_min, fore_max, alpha=0.15, color=MCOLOR["gold"],
                    label="Confidence Band (±CI)")

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda v, _: f"{v/1e12:.1f}T" if abs(v) >= 1e12 else f"{v/1e9:.0f}M"
    ))
    ax.legend(framealpha=0, labelcolor=MCOLOR["muted"], fontsize=8)
    ax.set_title(f"Proyeksi {label}", color=MCOLOR["text"], fontsize=10, fontweight="bold", pad=10)
    ax.axvline(years_hist[-1], color=MCOLOR["muted"], linewidth=0.8, linestyle=":", alpha=0.6)
    fig.tight_layout()
    return fig


def chart_scatter(df_agg, col_pagu, col_real, col_wilayah):
    """Scatter: Pagu vs Realisasi dengan diagonal reference."""
    fig, ax = mpl_fig(8, 5)
    x = df_agg[col_pagu].values
    y = df_agg[col_real].values
    labels = df_agg[col_wilayah].astype(str).values

    scatter = ax.scatter(x, y, c=MCOLOR["blue"], s=70, alpha=0.8, edgecolors=MCOLOR["bg2"], linewidth=0.8, zorder=4)

    # Diagonal
    lim_max = max(x.max(), y.max()) * 1.05
    ax.plot([0, lim_max], [0, lim_max], "--", color=MCOLOR["gold"], linewidth=1.2, alpha=0.7, label="100% serap")

    for i, (xi, yi, lbl) in enumerate(zip(x, y, labels)):
        if i < 12:
            ax.annotate(lbl[:12], (xi, yi), textcoords="offset points", xytext=(5, 4),
                        fontsize=6, color=MCOLOR["muted"])

    ax.set_xlabel("Pagu", color=MCOLOR["muted"], fontsize=8)
    ax.set_ylabel("Realisasi", color=MCOLOR["muted"], fontsize=8)
    ax.legend(framealpha=0, labelcolor=MCOLOR["muted"], fontsize=8)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(
        lambda v, _: f"{v/1e12:.1f}T" if abs(v) >= 1e12 else f"{v/1e9:.0f}M"
    ))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda v, _: f"{v/1e12:.1f}T" if abs(v) >= 1e12 else f"{v/1e9:.0f}M"
    ))
    ax.set_title("Scatter: Pagu vs Realisasi", color=MCOLOR["text"], fontsize=10, fontweight="bold", pad=10)
    fig.tight_layout()
    return fig


# ---------------------------------------------
# MAIN APP
# ---------------------------------------------
def main():
    # -- HERO HEADER --
    st.markdown("""
    <div class="hero-header">
      <div class="hero-badge">🏛️ &nbsp;DJPB · Kementerian Keuangan RI</div>
      <div class="hero-title">Dashboard Transfer ke Daerah</div>
      <div class="hero-subtitle">Monitoring Pagu, Realisasi, Penyerapan &amp; Proyeksi Anggaran · Real-time Analytics</div>
    </div>
    """, unsafe_allow_html=True)

    # -- SIDEBAR --
    with st.sidebar:
        st.markdown("### 📂 Upload Data")
        uploaded = st.file_uploader(
            "Upload Excel (.xlsx/.xls) atau CSV",
            type=["xlsx", "xls", "csv"],
            help="Mendukung .xlsx, .xls, dan .csv dengan berbagai encoding & separator"
        )

        st.markdown("---")
        st.markdown("### ⚙️ Konfigurasi Kolom")
        col_pagu_inp    = st.text_input("Nama kolom Pagu",       value="pagu",      key="c_pagu")
        col_real_inp    = st.text_input("Nama kolom Realisasi",  value="realisasi", key="c_real")
        col_wil_inp     = st.text_input("Nama kolom Wilayah",    value="wilayah",   key="c_wil")
        col_tahun_inp   = st.text_input("Nama kolom Tahun",      value="tahun",     key="c_thn")

        st.markdown("---")
        st.markdown("### 🔮 Proyeksi")
        forecast_horizon = st.multiselect(
            "Horizon proyeksi",
            options=[1, 3, 5, 10],
            default=[1, 3, 5],
            format_func=lambda x: f"+{x} Tahun"
        )

        st.markdown("---")
        st.markdown(f"<div style='color:#475569;font-size:0.72rem;'>v3.0 · {datetime.now().strftime('%Y')}</div>", unsafe_allow_html=True)

    # -- NO DATA STATE --
    if not uploaded:
        st.markdown("""
        <div class="info-box">
        📌 <b>Cara mulai:</b> Upload file Excel (.xlsx / .xls) atau CSV dari sidebar kiri untuk memulai analisis.
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        features = [
            ("📊", "Multi-format Reader", "Excel (.xlsx/.xls) & CSV dengan auto-detect encoding & separator"),
            ("📈", "Analisis Mendalam", "KPI, tren, perbandingan wilayah, scatter, treemap"),
            ("🔮", "Proyeksi Cerdas", "Linear + CAGR ensemble, confidence interval, horizon 1/3/5/10 tahun"),
            ("📄", "Export PDF & Excel", "Laporan eksekutif siap cetak dengan branding DJPB"),
        ]
        for i, (icon, title, desc) in enumerate(features):
            col = [c1, c2, c3][i % 3]
            with col:
                st.markdown(f"""
                <div class="kpi-card {'gold' if i==0 else 'blue' if i==1 else 'green' if i==2 else 'purple'}">
                  <div style="font-size:1.8rem;margin-bottom:8px">{icon}</div>
                  <div class="kpi-label">{title}</div>
                  <div style="color:#94a3b8;font-size:0.82rem;margin-top:6px">{desc}</div>
                </div>
                """, unsafe_allow_html=True)
        return

    # -- LOAD DATA --
    with st.spinner("Membaca file..."):
        df, err = load_file(uploaded)

    if err:
        st.error(f"❌ {err}")
        return

    if df is None or df.empty:
        st.error("File kosong atau tidak ada data yang bisa dibaca.")
        return

    # -- AUTO-DETECT COLUMNS --
    detected = detect_columns(df)
    col_pagu  = col_pagu_inp  if col_pagu_inp  in df.columns else detected.get("pagu")
    col_real  = col_real_inp  if col_real_inp  in df.columns else detected.get("real")
    col_wil   = col_wil_inp   if col_wil_inp   in df.columns else detected.get("wilayah")
    col_tahun = col_tahun_inp if col_tahun_inp in df.columns else detected.get("tahun")

    has_pagu  = col_pagu  is not None
    has_real  = col_real  is not None
    has_wil   = col_wil   is not None
    has_tahun = col_tahun is not None

    # Clean numerics
    if has_pagu:  df[col_pagu]  = clean_numeric(df[col_pagu])
    if has_real:  df[col_real]  = clean_numeric(df[col_real])
    if has_tahun: df[col_tahun] = pd.to_numeric(df[col_tahun], errors="coerce")

    # -- SIDEBAR FILTERS --
    with st.sidebar:
        st.markdown("### 🔍 Filter Data")
        df_f = df.copy()

        if has_tahun:
            tahun_opts = sorted(df_f[col_tahun].dropna().unique().astype(int).tolist())
            tahun_sel = st.multiselect("Tahun", tahun_opts, default=tahun_opts, key="f_thn")
            if tahun_sel:
                df_f = df_f[df_f[col_tahun].isin(tahun_sel)]

        if has_wil:
            wil_opts = sorted(df_f[col_wil].dropna().unique().tolist())
            wil_sel = st.multiselect("Wilayah", wil_opts, key="f_wil")
            if wil_sel:
                df_f = df_f[df_f[col_wil].isin(wil_sel)]

        search_q = st.text_input("🔍 Cari teks bebas", key="search")
        if search_q:
            mask = df_f.apply(lambda r: r.astype(str).str.contains(search_q, case=False, na=False).any(), axis=1)
            df_f = df_f[mask]

    # -- COMPUTE KPIs --
    total_pagu = df_f[col_pagu].sum() if has_pagu else 0
    total_real = df_f[col_real].sum() if has_real else 0
    pct_real   = (total_real / total_pagu * 100) if (has_pagu and total_pagu > 0) else 0
    n_rows     = len(df_f)
    n_wilayah  = df_f[col_wil].nunique() if has_wil else "-"

    cagr_pagu = calc_cagr(df_f.groupby(col_tahun)[col_pagu].sum().values) if (has_tahun and has_pagu) else np.nan
    cagr_real = calc_cagr(df_f.groupby(col_tahun)[col_real].sum().values) if (has_tahun and has_real) else np.nan

    kpi = {"total_pagu": total_pagu, "total_real": total_real,
           "pct_real": pct_real, "n_wilayah": n_wilayah, "n_rows": n_rows}

    # -- KPI CARDS --
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        badge = "badge-flat" if pct_real == 0 else ("badge-up" if pct_real >= 90 else "badge-down")
        trend = "▲" if pct_real >= 90 else "▼"
        st.markdown(f"""
        <div class="kpi-card gold">
          <div class="kpi-label">Total Pagu</div>
          <div class="kpi-value">{fmt_rp(total_pagu)}</div>
          <div class="kpi-sub">Alokasi Anggaran</div>
          <span class="kpi-badge badge-flat">{n_rows:,} record</span>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="kpi-card green">
          <div class="kpi-label">Total Realisasi</div>
          <div class="kpi-value">{fmt_rp(total_real)}</div>
          <div class="kpi-sub">Pencairan Dana</div>
          <span class="kpi-badge {badge}">{trend} {fmt_pct(pct_real)} diserap</span>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        cagr_color = "badge-up" if (not np.isnan(cagr_pagu) and cagr_pagu > 0) else "badge-down"
        st.markdown(f"""
        <div class="kpi-card blue">
          <div class="kpi-label">CAGR Pagu</div>
          <div class="kpi-value">{fmt_pct(cagr_pagu) if not np.isnan(cagr_pagu) else '--'}</div>
          <div class="kpi-sub">Pertumbuhan Historis</div>
          <span class="kpi-badge {cagr_color}">per tahun</span>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="kpi-card purple">
          <div class="kpi-label">Jumlah Wilayah</div>
          <div class="kpi-value">{n_wilayah}</div>
          <div class="kpi-sub">Cakupan Daerah</div>
          <span class="kpi-badge badge-flat">aktif</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # -- TABS --
    tab_overview, tab_wilayah, tab_trend, tab_forecast, tab_data, tab_export = st.tabs([
        "📊 Overview", "🗺️ Wilayah", "📈 Tren", "🔮 Proyeksi", "📋 Data", "⬇️ Export"
    ])

    # -- OVERVIEW TAB --
    with tab_overview:
        st.markdown('<div class="section-header"><div class="section-icon">📊</div><div class="section-title">Ringkasan Distribusi Anggaran</div></div>', unsafe_allow_html=True)

        if has_pagu and has_real and has_wil:
            df_agg = df_f.groupby(col_wil, as_index=False).agg(
                pagu=(col_pagu, "sum"),
                real=(col_real, "sum")
            ).rename(columns={"pagu": col_pagu, "real": col_real})

            col_l, col_r = st.columns([3, 2])
            with col_l:
                fig = chart_bar_pagu_real(df_agg, col_pagu, col_real, col_wil)
                st.pyplot(fig, use_container_width=True)
                plt.close(fig)
            with col_r:
                fig2 = chart_pct_bar(df_agg, col_real, col_pagu, col_wil)
                st.pyplot(fig2, use_container_width=True)
                plt.close(fig2)

            st.markdown('<div class="section-header"><div class="section-icon">🔵</div><div class="section-title">Scatter: Pagu vs Realisasi</div></div>', unsafe_allow_html=True)
            col_sc, col_info = st.columns([2, 1])
            with col_sc:
                fig3 = chart_scatter(df_agg, col_pagu, col_real, col_wil)
                st.pyplot(fig3, use_container_width=True)
                plt.close(fig3)
            with col_info:
                st.markdown("""
                <div class="info-box">
                <b>Cara baca grafik:</b><br>
                Titik di <b>atas garis diagonal</b> = realisasi melebihi pagu (perlu verifikasi).<br><br>
                Titik di <b>bawah garis</b> = masih ada sisa pagu yang belum dicairkan.
                </div>
                """, unsafe_allow_html=True)

                # Top 5 penyerapan
                df_agg["pct"] = (df_agg[col_real] / df_agg[col_pagu] * 100).clip(0, 200)
                top5 = df_agg.nlargest(5, "pct")[[col_wil, "pct"]].reset_index(drop=True)
                top5.columns = ["Wilayah", "% Serap"]
                top5["% Serap"] = top5["% Serap"].map("{:.1f}%".format)
                st.dataframe(top5, hide_index=True, use_container_width=True)
        else:
            st.markdown("""
            <div class="warn-box">
            ⚠️ Kolom <b>pagu</b>, <b>realisasi</b>, atau <b>wilayah</b> tidak terdeteksi otomatis.<br>
            Masukkan nama kolom yang benar di sidebar kiri → Konfigurasi Kolom.
            </div>
            """, unsafe_allow_html=True)
            st.dataframe(df_f.head(20), use_container_width=True)

    # -- WILAYAH TAB --
    with tab_wilayah:
        st.markdown('<div class="section-header"><div class="section-icon">🗺️</div><div class="section-title">Analisis per Wilayah</div></div>', unsafe_allow_html=True)

        if has_pagu and has_wil:
            df_agg_w = df_f.groupby(col_wil, as_index=False).agg(
                pagu_sum=(col_pagu, "sum"),
                **({f"real_sum": (col_real, "sum")} if has_real else {})
            )

            if has_real:
                df_agg_w["pct_serap"] = (df_agg_w["real_sum"] / df_agg_w["pagu_sum"] * 100).clip(0, 200)
                df_agg_w = df_agg_w.sort_values("pagu_sum", ascending=False)
                df_display = df_agg_w.rename(columns={
                    col_wil: "Wilayah",
                    "pagu_sum": "Pagu",
                    "real_sum": "Realisasi",
                    "pct_serap": "% Serap"
                })
                df_display["Pagu"]       = df_display["Pagu"].map(fmt_rp)
                df_display["Realisasi"]  = df_display["Realisasi"].map(fmt_rp)
                df_display["% Serap"]    = df_display["% Serap"].map("{:.1f}%".format)
            else:
                df_agg_w = df_agg_w.sort_values("pagu_sum", ascending=False)
                df_display = df_agg_w.rename(columns={col_wil: "Wilayah", "pagu_sum": "Pagu"})
                df_display["Pagu"] = df_display["Pagu"].map(fmt_rp)

            search_w = st.text_input("🔍 Cari wilayah", key="s_wil")
            if search_w:
                df_display = df_display[df_display["Wilayah"].str.contains(search_w, case=False, na=False)]

            st.dataframe(df_display, use_container_width=True, hide_index=True)
            st.caption(f"Menampilkan {len(df_display)} wilayah")
        else:
            st.info("Kolom wilayah/pagu belum dikonfigurasi.")

    # -- TREN TAB --
    with tab_trend:
        st.markdown('<div class="section-header"><div class="section-icon">📈</div><div class="section-title">Tren Historis per Tahun</div></div>', unsafe_allow_html=True)

        if has_tahun and has_pagu:
            df_yr = df_f.groupby(col_tahun).agg(
                pagu_sum=(col_pagu, "sum"),
                **({f"real_sum": (col_real, "sum")} if has_real else {})
            ).reset_index().sort_values(col_tahun)

            years     = df_yr[col_tahun].values
            pagu_vals = df_yr["pagu_sum"].values
            real_vals = df_yr["real_sum"].values if has_real else np.zeros(len(years))

            fig = chart_trend(years, pagu_vals, real_vals)
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

            # Summary table
            df_yr_disp = df_yr.copy()
            df_yr_disp[col_tahun] = df_yr_disp[col_tahun].astype(int)
            df_yr_disp["pagu_sum"] = df_yr_disp["pagu_sum"].map(fmt_rp)
            if has_real:
                df_yr_disp["real_sum"] = df_yr_disp["real_sum"].map(fmt_rp)
                df_yr_disp["% Serap"]  = (df_yr["real_sum"] / df_yr["pagu_sum"] * 100).map("{:.1f}%".format)
            df_yr_disp.rename(columns={
                col_tahun: "Tahun",
                "pagu_sum": "Total Pagu",
                "real_sum": "Total Realisasi"
            }, inplace=True)
            st.dataframe(df_yr_disp, use_container_width=True, hide_index=True)
        else:
            st.info("Kolom tahun/pagu belum dikonfigurasi. Setel di sidebar → Konfigurasi Kolom.")

    # -- FORECAST TAB --
    with tab_forecast:
        st.markdown('<div class="section-header"><div class="section-icon">🔮</div><div class="section-title">Proyeksi Anggaran ke Depan</div></div>', unsafe_allow_html=True)

        if not forecast_horizon:
            st.info("Pilih horizon proyeksi di sidebar.")
        elif not (has_tahun and has_pagu):
            st.warning("Proyeksi membutuhkan kolom **tahun** dan **pagu**. Konfigurasi di sidebar.")
        else:
            df_yr = df_f.groupby(col_tahun).agg(
                pagu_sum=(col_pagu, "sum"),
                **({f"real_sum": (col_real, "sum")} if has_real else {})
            ).reset_index().sort_values(col_tahun)

            years     = df_yr[col_tahun].values
            pagu_vals = df_yr["pagu_sum"].values
            real_vals = df_yr["real_sum"].values if has_real else None

            fore_pagu = forecast_series(pagu_vals, forecast_horizon)
            fore_real = forecast_series(real_vals, forecast_horizon) if real_vals is not None else None

            col_fp, col_fr = st.columns(2)
            with col_fp:
                st.pyplot(chart_forecast(years, pagu_vals, fore_pagu, "Pagu", MCOLOR["blue"]),
                          use_container_width=True)
                plt.close()
            with col_fr:
                if fore_real:
                    st.pyplot(chart_forecast(years, real_vals, fore_real, "Realisasi", MCOLOR["green"]),
                              use_container_width=True)
                    plt.close()

            # -- Forecast table --
            st.markdown("#### 📋 Tabel Proyeksi Detail")
            last_year = int(years[-1])
            rows = []
            for h in sorted(forecast_horizon):
                target_year = last_year + h
                fp = fore_pagu[h]
                row = {
                    "Horizon":    f"+{h} Tahun",
                    "Tahun":      target_year,
                    "Pagu Min":   fmt_rp(fp["min"]),
                    "Pagu Tengah":fmt_rp(fp["mid"]),
                    "Pagu Max":   fmt_rp(fp["max"]),
                }
                if fore_real:
                    fr = fore_real[h]
                    row["Real. Min"]   = fmt_rp(fr["min"])
                    row["Real. Tengah"]= fmt_rp(fr["mid"])
                    row["Real. Max"]   = fmt_rp(fr["max"])
                    row["Est. % Serap"]= fmt_pct(fr["mid"] / fp["mid"] * 100) if fp["mid"] > 0 else "-"
                rows.append(row)

            forecast_df = pd.DataFrame(rows)
            st.dataframe(forecast_df, use_container_width=True, hide_index=True)

            # -- CAGR summary --
            st.markdown("#### 📐 CAGR Historis")
            c_cagr1, c_cagr2, c_cagr3 = st.columns(3)
            with c_cagr1:
                st.metric("CAGR Pagu", fmt_pct(cagr_pagu) if not np.isnan(cagr_pagu) else "--")
            with c_cagr2:
                if not np.isnan(cagr_real):
                    st.metric("CAGR Realisasi", fmt_pct(cagr_real))
            with c_cagr3:
                n_yr = len(years)
                st.metric("Data Historis", f"{n_yr} Tahun", f"{int(years[0])}-{int(years[-1])}" if n_yr > 0 else "")

            # Store for export
            st.session_state["forecast_df"] = forecast_df

    # -- DATA TAB --
    with tab_data:
        st.markdown('<div class="section-header"><div class="section-icon">📋</div><div class="section-title">Data Mentah</div></div>', unsafe_allow_html=True)

        # Data quality
        n_missing = df_f.isnull().sum().sum()
        n_dup     = df_f.duplicated().sum()
        c_dq1, c_dq2, c_dq3, c_dq4 = st.columns(4)
        c_dq1.metric("Total Baris",   f"{len(df_f):,}")
        c_dq2.metric("Total Kolom",   f"{len(df_f.columns)}")
        c_dq3.metric("Missing Values",f"{n_missing:,}", delta="masalah" if n_missing > 0 else None,
                     delta_color="inverse" if n_missing > 0 else "normal")
        c_dq4.metric("Duplikat",      f"{n_dup:,}", delta="masalah" if n_dup > 0 else None,
                     delta_color="inverse" if n_dup > 0 else "normal")

        st.dataframe(df_f, use_container_width=True, hide_index=True)

    # -- EXPORT TAB --
    with tab_export:
        st.markdown('<div class="section-header"><div class="section-icon">⬇️</div><div class="section-title">Export & Download</div></div>', unsafe_allow_html=True)

        forecast_df_export = st.session_state.get("forecast_df", pd.DataFrame())
        filters_active = {}
        if has_tahun and "f_thn" in st.session_state and st.session_state["f_thn"]:
            filters_active["Tahun"] = ", ".join(str(x) for x in st.session_state["f_thn"])
        if has_wil and "f_wil" in st.session_state and st.session_state["f_wil"]:
            filters_active["Wilayah"] = f"{len(st.session_state['f_wil'])} dipilih"

        col_e1, col_e2, col_e3 = st.columns(3)

        with col_e1:
            st.markdown("**📄 Laporan PDF**")
            pdf_bytes = generate_pdf(df_f, kpi, {}, filters_active)
            if pdf_bytes:
                st.download_button(
                    "⬇️ Download PDF",
                    data=pdf_bytes,
                    file_name=f"laporan_tkd_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.markdown('<div class="warn-box">reportlab belum terinstall. Tambahkan <code>reportlab</code> ke requirements.txt</div>', unsafe_allow_html=True)

        with col_e2:
            st.markdown("**📊 Excel -- Data Terfilter**")
            excel_data = generate_excel(df_f, kpi, forecast_df_export if not forecast_df_export.empty else None)
            st.download_button(
                "⬇️ Download Excel",
                data=excel_data,
                file_name=f"data_tkd_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        with col_e3:
            st.markdown("**📑 CSV -- Data Terfilter**")
            csv_data = df_f.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Download CSV",
                data=csv_data,
                file_name=f"data_tkd_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True
            )

        st.markdown("---")
        st.markdown("**📌 Info Ringkasan**")
        c_inf1, c_inf2 = st.columns(2)
        with c_inf1:
            st.markdown(f"""
            <div class="info-box">
            <b>Data aktif:</b> {len(df_f):,} baris · {len(df_f.columns)} kolom<br>
            <b>Total Pagu:</b> {fmt_rp(total_pagu)}<br>
            <b>Total Realisasi:</b> {fmt_rp(total_real)}<br>
            <b>% Penyerapan:</b> {fmt_pct(pct_real)}
            </div>
            """, unsafe_allow_html=True)
        with c_inf2:
            if filters_active:
                ftext = "<br>".join([f"<b>{k}:</b> {v}" for k, v in filters_active.items()])
                st.markdown(f'<div class="info-box"><b>Filter Aktif:</b><br>{ftext}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="info-box">Tidak ada filter aktif -- semua data ditampilkan.</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
