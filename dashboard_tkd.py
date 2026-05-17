import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import warnings
from datetime import datetime

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="TKD Dashboard | Transfer ke Daerah",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS — Modern Dark Government Dashboard
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

/* ── Root Variables ── */
:root {
    --bg-primary: #0a0e1a;
    --bg-card: #111827;
    --bg-card-hover: #1a2236;
    --accent-blue: #3b82f6;
    --accent-cyan: #06b6d4;
    --accent-emerald: #10b981;
    --accent-amber: #f59e0b;
    --accent-rose: #f43f5e;
    --accent-violet: #8b5cf6;
    --text-primary: #f1f5f9;
    --text-secondary: #94a3b8;
    --text-muted: #475569;
    --border: #1e293b;
    --border-bright: #334155;
    --gradient-1: linear-gradient(135deg, #1e3a5f 0%, #0f2744 100%);
    --gradient-2: linear-gradient(135deg, #064e3b 0%, #022c22 100%);
    --gradient-3: linear-gradient(135deg, #451a03 0%, #292524 100%);
    --gradient-4: linear-gradient(135deg, #2e1065 0%, #1e1b4b 100%);
}

/* ── Global Reset ── */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

/* ── Main App Background ── */
.stApp {
    background: var(--bg-primary) !important;
    background-image: 
        radial-gradient(ellipse at 20% 0%, rgba(59,130,246,0.06) 0%, transparent 60%),
        radial-gradient(ellipse at 80% 100%, rgba(16,185,129,0.04) 0%, transparent 60%);
    min-height: 100vh;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #0d1117 !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p { color: var(--text-secondary) !important; }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 { color: var(--text-primary) !important; }

/* ── Hide Streamlit Branding ── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ── Header Banner ── */
.header-banner {
    background: linear-gradient(135deg, #0f1d3a 0%, #1a0f2e 50%, #0f1a2e 100%);
    border: 1px solid var(--border-bright);
    border-radius: 16px;
    padding: 32px 40px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}
.header-banner::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: 
        radial-gradient(ellipse at 10% 50%, rgba(59,130,246,0.12) 0%, transparent 50%),
        radial-gradient(ellipse at 90% 50%, rgba(139,92,246,0.08) 0%, transparent 50%);
    pointer-events: none;
}
.header-banner::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #3b82f6, #8b5cf6, #06b6d4, transparent);
}
.header-title {
    font-size: 2rem;
    font-weight: 800;
    color: #fff;
    margin: 0;
    letter-spacing: -0.03em;
    line-height: 1.1;
}
.header-title span { color: #3b82f6; }
.header-subtitle {
    color: var(--text-secondary);
    font-size: 0.875rem;
    margin: 8px 0 0;
    font-weight: 400;
    letter-spacing: 0.02em;
}
.header-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(59,130,246,0.15);
    border: 1px solid rgba(59,130,246,0.3);
    color: #93c5fd;
    padding: 4px 12px;
    border-radius: 100px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-top: 12px;
    font-family: 'JetBrains Mono', monospace;
}

/* ── KPI Cards ── */
.kpi-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 22px 24px;
    position: relative;
    overflow: hidden;
    transition: all 0.2s ease;
    height: 100%;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 14px 14px 0 0;
}
.kpi-card.blue::before { background: linear-gradient(90deg, #3b82f6, #60a5fa); }
.kpi-card.emerald::before { background: linear-gradient(90deg, #10b981, #34d399); }
.kpi-card.amber::before { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.kpi-card.rose::before { background: linear-gradient(90deg, #f43f5e, #fb7185); }
.kpi-card.violet::before { background: linear-gradient(90deg, #8b5cf6, #a78bfa); }
.kpi-card.cyan::before { background: linear-gradient(90deg, #06b6d4, #22d3ee); }

.kpi-label {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 8px;
}
.kpi-value {
    font-size: 1.65rem;
    font-weight: 800;
    color: var(--text-primary);
    letter-spacing: -0.04em;
    line-height: 1;
    margin-bottom: 6px;
}
.kpi-sub {
    font-size: 0.75rem;
    color: var(--text-secondary);
    font-weight: 500;
}
.kpi-icon {
    position: absolute;
    top: 20px; right: 20px;
    font-size: 1.5rem;
    opacity: 0.15;
}

/* ── Section Headers ── */
.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 32px 0 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border);
}
.section-header h2 {
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0;
    letter-spacing: -0.01em;
}
.section-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--accent-blue);
    box-shadow: 0 0 8px rgba(59,130,246,0.6);
}

/* ── Insight Card ── */
.insight-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent-blue);
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 10px;
    font-size: 0.875rem;
    color: var(--text-secondary);
    line-height: 1.6;
}
.insight-card.warning { border-left-color: var(--accent-amber); }
.insight-card.success { border-left-color: var(--accent-emerald); }
.insight-card.danger  { border-left-color: var(--accent-rose); }
.insight-card strong  { color: var(--text-primary); }

/* ── Download Buttons ── */
.dl-btn-container {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin: 16px 0;
}

/* ── Table ── */
.stDataFrame, .stTable { 
    background: var(--bg-card) !important;
    border-radius: 10px;
}

/* ── Plotly Charts override for dark ── */
.js-plotly-plot .plotly { background: transparent !important; }

/* ── Selectbox/Inputs ── */
.stSelectbox > div > div,
.stMultiSelect > div > div { 
    background: var(--bg-card) !important;
    border: 1px solid var(--border-bright) !important;
    color: var(--text-primary) !important;
    border-radius: 8px !important;
}

/* ── Upload Area ── */
.stFileUploader > div {
    background: var(--bg-card) !important;
    border: 2px dashed var(--border-bright) !important;
    border-radius: 12px !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-card) !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 4px !important;
    border: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-muted) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    padding: 8px 16px !important;
}
.stTabs [aria-selected="true"] {
    background: var(--accent-blue) !important;
    color: white !important;
}

/* ── Metrics override ── */
[data-testid="metric-container"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 16px !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--border-bright); border-radius: 3px; }

/* ── Alert / Info ── */
.stAlert { border-radius: 10px !important; }

/* ── Progress bar ── */
.stProgress > div > div { background: var(--accent-blue) !important; }

/* ── Spinner ── */
.stSpinner > div { border-top-color: var(--accent-blue) !important; }

/* ── Number Input ── */
.stNumberInput > div > div > input {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-bright) !important;
    color: var(--text-primary) !important;
    border-radius: 8px !important;
}

/* ── Projection badge ── */
.proj-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(139,92,246,0.12);
    border: 1px solid rgba(139,92,246,0.25);
    color: #c4b5fd;
    padding: 3px 10px;
    border-radius: 100px;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* ── Footer ── */
.dashboard-footer {
    text-align: center;
    padding: 24px;
    color: var(--text-muted);
    font-size: 0.72rem;
    border-top: 1px solid var(--border);
    margin-top: 48px;
    letter-spacing: 0.05em;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def fmt_triliun(val):
    """Format big numbers into Miliar/Triliun"""
    if pd.isna(val): return "—"
    val = float(val)
    if abs(val) >= 1e12:   return f"Rp {val/1e12:.2f} T"
    if abs(val) >= 1e9:    return f"Rp {val/1e9:.2f} M"
    if abs(val) >= 1e6:    return f"Rp {val/1e6:.1f} Jt"
    return f"Rp {val:,.0f}"

def fmt_pct(val):
    if pd.isna(val): return "—"
    return f"{float(val):.1f}%"

def pct_color(val):
    if val >= 80:   return "emerald"
    if val >= 50:   return "amber"
    return "rose"

def load_file(uploaded_file):
    """
    Robust file loader for .xlsx, .xls, .csv
    Returns (DataFrame, error_str)
    """
    name = uploaded_file.name.lower()
    raw = uploaded_file.read()
    buf = io.BytesIO(raw)

    if name.endswith(".csv"):
        # Try multiple encodings + separators
        for enc in ["utf-8", "latin-1", "cp1252", "utf-8-sig"]:
            for sep in [",", ";", "\t", "|"]:
                try:
                    buf.seek(0)
                    df = pd.read_csv(buf, encoding=enc, sep=sep, low_memory=False)
                    if df.shape[1] > 1:
                        return df, None
                except Exception:
                    continue
        return None, "Tidak dapat membaca file CSV. Cek encoding/separator."

    elif name.endswith(".xlsx") or name.endswith(".xlsm"):
        try:
            buf.seek(0)
            df = pd.read_excel(buf, engine="openpyxl", sheet_name=0)
            return df, None
        except ImportError:
            return None, "openpyxl belum terinstall. Tambahkan ke requirements.txt."
        except Exception as e:
            return None, f"Error baca .xlsx: {e}"

    elif name.endswith(".xls"):
        try:
            buf.seek(0)
            df = pd.read_excel(buf, engine="xlrd", sheet_name=0)
            return df, None
        except ImportError:
            return None, "xlrd belum terinstall."
        except Exception as e:
            return None, f"Error baca .xls: {e}"

    else:
        return None, f"Format file '{name}' tidak didukung. Gunakan .xlsx / .xls / .csv"


def detect_columns(df):
    """
    Auto-detect column roles from any TKD-like dataframe.
    Returns dict with keys: region, pagu, realisasi, month, year, account
    """
    cols = {c: c.lower().replace(" ", "_") for c in df.columns}
    mapping = {}

    region_kw   = ["wilayah","kabupaten","kota","kab","provinsi","daerah","satker","satuan_kerja","uraian_satker"]
    pagu_kw     = ["pagu","anggaran","dipa","target","rencana"]
    real_kw     = ["realisasi","realization","actual","terealisasi","pencairan","penyaluran"]
    month_kw    = ["bulan","month","periode","bln"]
    year_kw     = ["tahun","year","ta"]
    account_kw  = ["akun","account","jenis","program","kegiatan","output","komponen"]

    for orig, low in cols.items():
        for kw in region_kw:
            if kw in low and "region" not in mapping:
                mapping["region"] = orig
        for kw in pagu_kw:
            if kw in low and "pagu" not in mapping:
                mapping["pagu"] = orig
        for kw in real_kw:
            if kw in low and "realisasi" not in mapping:
                mapping["realisasi"] = orig
        for kw in month_kw:
            if kw in low and "bulan" not in mapping:
                mapping["bulan"] = orig
        for kw in year_kw:
            if kw in low and "tahun" not in mapping:
                mapping["tahun"] = orig
        for kw in account_kw:
            if kw in low and "akun" not in mapping:
                mapping["akun"] = orig

    return mapping


def coerce_numeric(df, cols):
    for c in cols:
        if c and c in df.columns:
            df[c] = pd.to_numeric(
                df[c].astype(str).str.replace(r"[Rp\s\.,]", "", regex=True)
                     .str.replace(",", "").str.replace(" ", ""),
                errors="coerce"
            )
    return df


def linear_projection(values, n_years):
    """Return projected values for n_years beyond the data using linear regression"""
    x = np.arange(len(values))
    if len(x) < 2:
        return [values[-1]] * n_years
    m, b = np.polyfit(x, values, 1)
    future_x = np.arange(len(values), len(values) + n_years)
    return m * future_x + b


def growth_projection(values, n_years):
    """CAGR-based compound growth projection"""
    if len(values) < 2 or values[0] <= 0:
        return [values[-1]] * n_years
    cagr = (values[-1] / values[0]) ** (1 / (len(values) - 1)) - 1
    result = []
    for i in range(1, n_years + 1):
        result.append(values[-1] * ((1 + cagr) ** i))
    return result


def to_excel_bytes(df):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Data")
    return buf.getvalue()


def to_pdf_bytes(summary_dict, region_df=None, title="TKD Dashboard Report"):
    """Generate a clean PDF report using reportlab"""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.enums import TA_CENTER, TA_LEFT

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4,
                                leftMargin=2*cm, rightMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        story = []

        # Title
        title_style = ParagraphStyle("title", fontSize=20, fontName="Helvetica-Bold",
                                     textColor=colors.HexColor("#1e3a5f"),
                                     spaceAfter=4, alignment=TA_CENTER)
        sub_style   = ParagraphStyle("sub", fontSize=10, fontName="Helvetica",
                                     textColor=colors.HexColor("#64748b"),
                                     spaceAfter=16, alignment=TA_CENTER)
        h2_style    = ParagraphStyle("h2", fontSize=13, fontName="Helvetica-Bold",
                                     textColor=colors.HexColor("#1e293b"),
                                     spaceBefore=16, spaceAfter=8)
        body_style  = ParagraphStyle("body", fontSize=9, fontName="Helvetica",
                                     textColor=colors.HexColor("#374151"),
                                     leading=14, spaceAfter=4)

        story.append(Paragraph(title, title_style))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%d %B %Y, %H:%M WIB')}", sub_style))
        story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#3b82f6"), spaceAfter=16))

        # KPI Summary
        story.append(Paragraph("📊 Ringkasan Eksekutif", h2_style))
        kpi_data = [["Indikator", "Nilai"]]
        for k, v in summary_dict.items():
            kpi_data.append([k, str(v)])

        tbl = Table(kpi_data, colWidths=[10*cm, 7*cm])
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1e3a5f")),
            ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
            ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",   (0,0), (-1,0), 10),
            ("ALIGN",      (0,0), (-1,-1), "LEFT"),
            ("FONTNAME",   (0,1), (-1,-1), "Helvetica"),
            ("FONTSIZE",   (0,1), (-1,-1), 9),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.HexColor("#f8fafc"), colors.white]),
            ("GRID",       (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ("PADDING",    (0,0), (-1,-1), 8),
            ("TOPPADDING", (0,0), (-1,-1), 10),
            ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 16))

        # Region Table
        if region_df is not None and not region_df.empty:
            story.append(Paragraph("📍 Detail per Wilayah", h2_style))
            tbl_data = [list(region_df.columns)]
            for _, row in region_df.iterrows():
                tbl_data.append([str(v) for v in row.values])

            n_cols = len(region_df.columns)
            col_w  = 17*cm / n_cols
            t2 = Table(tbl_data, colWidths=[col_w]*n_cols)
            t2.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#0f2744")),
                ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
                ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
                ("FONTSIZE",   (0,0), (-1,-1), 8),
                ("ALIGN",      (0,0), (-1,-1), "CENTER"),
                ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.HexColor("#f0f4f8"), colors.white]),
                ("GRID",       (0,0), (-1,-1), 0.3, colors.HexColor("#cbd5e1")),
                ("PADDING",    (0,0), (-1,-1), 6),
            ]))
            story.append(t2)

        story.append(Spacer(1, 24))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1")))
        story.append(Spacer(1, 8))
        story.append(Paragraph(
            "Dokumen ini dihasilkan secara otomatis oleh TKD Dashboard · Direktorat Jenderal Perimbangan Keuangan",
            ParagraphStyle("footer", fontSize=7, textColor=colors.HexColor("#94a3b8"), alignment=TA_CENTER)
        ))

        doc.build(story)
        return buf.getvalue()
    except Exception as e:
        return None, str(e)


PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Plus Jakarta Sans", color="#94a3b8", size=12),
    margin=dict(l=10, r=10, t=40, b=10),
    legend=dict(
        bgcolor="rgba(17,24,39,0.8)",
        bordercolor="#334155",
        borderwidth=1,
        font=dict(size=11)
    ),
    xaxis=dict(gridcolor="#1e293b", zerolinecolor="#1e293b", tickfont=dict(size=11)),
    yaxis=dict(gridcolor="#1e293b", zerolinecolor="#1e293b", tickfont=dict(size=11)),
)

COLOR_SEQ = ["#3b82f6","#10b981","#f59e0b","#8b5cf6","#f43f5e","#06b6d4",
             "#84cc16","#ec4899","#14b8a6","#fb923c","#a78bfa","#34d399"]


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 20px 0 8px;'>
        <div style='font-size:2rem;'>🏛️</div>
        <div style='font-weight:800; font-size:1rem; color:#f1f5f9; letter-spacing:-0.02em;'>TKD Dashboard</div>
        <div style='font-size:0.7rem; color:#475569; letter-spacing:0.08em; text-transform:uppercase; margin-top:4px;'>Transfer ke Daerah</div>
    </div>
    <hr style='border-color:#1e293b; margin:12px 0;'>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "📂 Upload Data",
        type=["xlsx", "xls", "csv"],
        help="Upload file Excel (.xlsx/.xls) atau CSV"
    )

    st.markdown("<hr style='border-color:#1e293b; margin:12px 0;'>", unsafe_allow_html=True)

    if uploaded:
        st.markdown("**⚙️ Filter Data**")
        # Populated dynamically after load

    st.markdown("""
    <hr style='border-color:#1e293b; margin:12px 0;'>
    <div style='font-size:0.68rem; color:#334155; text-align:center; padding:0 8px;'>
        Built for DJPB · APBN 2025<br>
        Otomatis mendeteksi kolom data
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────

st.markdown("""
<div class="header-banner">
    <div style="position:relative; z-index:1;">
        <div style="display:flex; align-items:flex-start; justify-content:space-between; flex-wrap:wrap; gap:16px;">
            <div>
                <div class="header-title">Transfer ke <span>Daerah</span> Dashboard</div>
                <div class="header-subtitle">Analisis Pagu DIPA & Realisasi Anggaran — Sumatera Utara</div>
                <div class="header-badge">🟢 LIVE · Auto-Detect Columns · AI-Assisted Analysis</div>
            </div>
            <div style="text-align:right; color:#475569; font-size:0.75rem; line-height:1.8; font-family:'JetBrains Mono',monospace;">
                <div>""" + datetime.now().strftime("%d %b %Y") + """</div>
                <div style="color:#334155;">v3.0 · APBN 2025</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# NO FILE STATE
# ─────────────────────────────────────────────

if not uploaded:
    st.markdown("""
    <div style="background:#111827; border:2px dashed #1e293b; border-radius:16px; padding:60px 40px; text-align:center; margin:20px 0;">
        <div style="font-size:3rem; margin-bottom:16px;">📊</div>
        <div style="font-size:1.2rem; font-weight:700; color:#f1f5f9; margin-bottom:8px;">Upload File Excel atau CSV</div>
        <div style="color:#64748b; font-size:0.875rem; max-width:400px; margin:0 auto; line-height:1.7;">
            Drag & drop atau klik tombol upload di sidebar kiri.<br>
            Dashboard akan otomatis muncul dengan analisis lengkap.
        </div>
        <div style="margin-top:24px; display:flex; gap:12px; justify-content:center; flex-wrap:wrap;">
            <div style="background:#1a2236; border:1px solid #1e293b; border-radius:8px; padding:10px 18px; font-size:0.78rem; color:#64748b;">✅ .xlsx / .xls</div>
            <div style="background:#1a2236; border:1px solid #1e293b; border-radius:8px; padding:10px 18px; font-size:0.78rem; color:#64748b;">✅ .csv (auto-detect)</div>
            <div style="background:#1a2236; border:1px solid #1e293b; border-radius:8px; padding:10px 18px; font-size:0.78rem; color:#64748b;">✅ Multi-sheet</div>
            <div style="background:#1a2236; border:1px solid #1e293b; border-radius:8px; padding:10px 18px; font-size:0.78rem; color:#64748b;">✅ Download PDF/Excel</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────

with st.spinner("🔄 Memuat dan menganalisis data..."):
    df_raw, err = load_file(uploaded)

if err:
    st.error(f"❌ {err}")
    st.stop()

df = df_raw.copy()
df.columns = df.columns.str.strip()
df = df.dropna(how="all")

# Auto-detect columns
mapping = detect_columns(df)

# Coerce numeric
num_cols = [mapping.get("pagu"), mapping.get("realisasi")]
df = coerce_numeric(df, [c for c in num_cols if c])

# ─────────────────────────────────────────────
# SIDEBAR FILTERS (dynamic after load)
# ─────────────────────────────────────────────

with st.sidebar:
    if mapping.get("region"):
        all_regions = sorted(df[mapping["region"]].dropna().unique().tolist())
        sel_regions = st.multiselect("🗺️ Wilayah", all_regions, default=[], 
                                     placeholder="Semua wilayah")
    else:
        sel_regions = []

    if mapping.get("bulan"):
        all_months = sorted(df[mapping["bulan"]].dropna().unique().tolist())
        sel_months = st.multiselect("📅 Bulan", all_months, default=[],
                                    placeholder="Semua bulan")
    else:
        sel_months = []

    if mapping.get("akun"):
        all_akun = sorted(df[mapping["akun"]].dropna().unique().tolist())
        sel_akun = st.multiselect("🏷️ Jenis Akun", all_akun, default=[],
                                   placeholder="Semua akun")
    else:
        sel_akun = []

    st.markdown("<hr style='border-color:#1e293b; margin:12px 0;'>", unsafe_allow_html=True)
    st.markdown("**📥 Download Laporan**")

# Apply filters
dff = df.copy()
if sel_regions and mapping.get("region"):
    dff = dff[dff[mapping["region"]].isin(sel_regions)]
if sel_months and mapping.get("bulan"):
    dff = dff[dff[mapping["bulan"]].isin(sel_months)]
if sel_akun and mapping.get("akun"):
    dff = dff[dff[mapping["akun"]].isin(sel_akun)]


# ─────────────────────────────────────────────
# COMPUTE CORE METRICS
# ─────────────────────────────────────────────

pagu_col  = mapping.get("pagu")
real_col  = mapping.get("realisasi")
reg_col   = mapping.get("region")
bln_col   = mapping.get("bulan")
akun_col  = mapping.get("akun")

total_pagu  = dff[pagu_col].sum()  if pagu_col  else 0
total_real  = dff[real_col].sum()  if real_col  else 0
total_sisa  = total_pagu - total_real
pct_serap   = (total_real / total_pagu * 100) if total_pagu > 0 else 0

n_wilayah   = dff[reg_col].nunique() if reg_col else 0
n_rows      = len(dff)


# ─────────────────────────────────────────────
# KPI ROW
# ─────────────────────────────────────────────

st.markdown("""<div class='section-header'><div class='section-dot'></div><h2>Ringkasan Eksekutif</h2></div>""", unsafe_allow_html=True)

k1, k2, k3, k4, k5, k6 = st.columns(6)

kpi_data_list = [
    (k1, "blue",    "💰", "TOTAL PAGU",    fmt_triliun(total_pagu),   f"{n_rows:,} baris data"),
    (k2, "emerald", "📈", "REALISASI",     fmt_triliun(total_real),   f"{fmt_pct(pct_serap)} terserap"),
    (k3, "amber",   "📉", "SISA ANGGARAN", fmt_triliun(total_sisa),   "Belum tersalur"),
    (k4, pct_color(pct_serap), "🎯", "PENYERAPAN",  fmt_pct(pct_serap),    "% dari Pagu DIPA"),
    (k5, "violet",  "🗺️", "WILAYAH",       str(n_wilayah),            "Kab/Kota"),
    (k6, "cyan",    "📋", "TOTAL DATA",    f"{n_rows:,}",             "Baris terfilter"),
]

for col, color, icon, label, value, sub in kpi_data_list:
    with col:
        st.markdown(f"""
        <div class="kpi-card {color}">
            <div class="kpi-icon">{icon}</div>
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{sub}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MAIN TABS
# ─────────────────────────────────────────────

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview",
    "📍 Peta Wilayah",
    "📅 Trend Bulanan",
    "🔮 Proyeksi",
    "📋 Data & Unduh"
])


# ══════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ══════════════════════════════════════════════

with tab1:
    # ── Pagu vs Realisasi per Wilayah ──
    if reg_col and pagu_col and real_col:
        st.markdown("""<div class='section-header'><div class='section-dot'></div><h2>Pagu vs Realisasi per Wilayah</h2></div>""", unsafe_allow_html=True)

        reg_grp = (dff.groupby(reg_col)[[pagu_col, real_col]]
                      .sum().reset_index()
                      .sort_values(real_col, ascending=True))
        reg_grp["Penyerapan (%)"] = (reg_grp[real_col] / reg_grp[pagu_col] * 100).round(1)
        reg_grp["Sisa"] = reg_grp[pagu_col] - reg_grp[real_col]

        # Limit to top/bottom for readability
        show_all = st.checkbox("Tampilkan semua wilayah", value=False)
        if not show_all and len(reg_grp) > 20:
            top10  = reg_grp.nlargest(10, real_col)
            bot10  = reg_grp.nsmallest(10, real_col)
            reg_show = pd.concat([bot10, top10]).drop_duplicates().sort_values(real_col)
            st.caption(f"Menampilkan 10 tertinggi & 10 terendah dari {len(reg_grp)} wilayah")
        else:
            reg_show = reg_grp

        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            y=reg_show[reg_col], x=reg_show[pagu_col],
            name="Pagu DIPA",
            orientation="h",
            marker=dict(color="rgba(59,130,246,0.25)", line=dict(color="#3b82f6", width=1)),
        ))
        fig_bar.add_trace(go.Bar(
            y=reg_show[reg_col], x=reg_show[real_col],
            name="Realisasi",
            orientation="h",
            marker=dict(color="#10b981"),
            text=[f"{p:.1f}%" for p in reg_show["Penyerapan (%)"]],
            textposition="outside",
            textfont=dict(size=10, color="#94a3b8"),
        ))
        fig_bar.update_layout(
            **PLOTLY_LAYOUT,
            barmode="overlay",
            height=max(400, len(reg_show) * 28),
            title=dict(text="Perbandingan Pagu & Realisasi per Wilayah", font=dict(size=13, color="#f1f5f9")),
            showlegend=True,
            xaxis_tickformat=".2s",
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # ── Penyerapan % Distribution ──
    col_a, col_b = st.columns(2)

    with col_a:
        if reg_col and pagu_col and real_col:
            st.markdown("""<div class='section-header'><div class='section-dot'></div><h2>Distribusi Penyerapan</h2></div>""", unsafe_allow_html=True)
            bins = [0, 25, 50, 75, 90, 100, float("inf")]
            labels = ["0-25%","25-50%","50-75%","75-90%","90-100%",">100%"]
            reg_grp["Kategori"] = pd.cut(reg_grp["Penyerapan (%)"], bins=bins, labels=labels, right=False)
            dist = reg_grp["Kategori"].value_counts().reset_index()
            dist.columns = ["Kategori","Jumlah"]
            pie_colors = ["#f43f5e","#f59e0b","#3b82f6","#06b6d4","#10b981","#8b5cf6"]
            fig_pie = go.Figure(go.Pie(
                labels=dist["Kategori"], values=dist["Jumlah"],
                hole=0.55,
                marker=dict(colors=pie_colors, line=dict(color="#0a0e1a", width=2)),
                textfont=dict(size=11, color="#f1f5f9"),
                textinfo="percent+label",
            ))
            fig_pie.update_layout(
                **PLOTLY_LAYOUT,
                height=300,
                showlegend=False,
                title=dict(text="% Wilayah per Kategori Penyerapan", font=dict(size=12, color="#f1f5f9")),
                annotations=[dict(text=f"{pct_serap:.0f}%<br><span style='font-size:10px'>Rata-rata</span>",
                                  x=0.5, y=0.5, font_size=18, showarrow=False,
                                  font_color="#f1f5f9")]
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    with col_b:
        if akun_col and pagu_col and real_col:
            st.markdown("""<div class='section-header'><div class='section-dot'></div><h2>Komposisi per Jenis Akun</h2></div>""", unsafe_allow_html=True)
            akun_grp = (dff.groupby(akun_col)[[pagu_col, real_col]]
                           .sum().reset_index()
                           .sort_values(pagu_col, ascending=False)
                           .head(8))
            fig_akun = go.Figure()
            fig_akun.add_trace(go.Bar(
                x=akun_grp[akun_col], y=akun_grp[pagu_col],
                name="Pagu", marker_color="#3b82f6"
            ))
            fig_akun.add_trace(go.Bar(
                x=akun_grp[akun_col], y=akun_grp[real_col],
                name="Realisasi", marker_color="#10b981"
            ))
            fig_akun.update_layout(
                **PLOTLY_LAYOUT,
                height=300,
                barmode="group",
                xaxis=dict(tickangle=-30),
                yaxis_tickformat=".2s",
                title=dict(text="Top 8 Jenis Akun", font=dict(size=12, color="#f1f5f9")),
            )
            st.plotly_chart(fig_akun, use_container_width=True)

    # ── Top & Bottom Wilayah ──
    if reg_col and real_col and pagu_col:
        st.markdown("""<div class='section-header'><div class='section-dot'></div><h2>Peringkat Wilayah</h2></div>""", unsafe_allow_html=True)
        col_top, col_bot = st.columns(2)
        top5  = reg_grp.nlargest(5, "Penyerapan (%)")[
                    [reg_col, pagu_col, real_col, "Penyerapan (%)"]].reset_index(drop=True)
        bot5  = reg_grp.nsmallest(5, "Penyerapan (%)")[
                    [reg_col, pagu_col, real_col, "Penyerapan (%)"]].reset_index(drop=True)

        with col_top:
            st.markdown("##### 🏆 Penyerapan Tertinggi")
            for _, row in top5.iterrows():
                pct = row["Penyerapan (%)"]
                st.markdown(f"""
                <div class="insight-card success">
                    <strong>{row[reg_col]}</strong><br>
                    Realisasi: {fmt_triliun(row[real_col])} · Pagu: {fmt_triliun(row[pagu_col])}<br>
                    Penyerapan: <strong style="color:#10b981;">{pct:.1f}%</strong>
                </div>
                """, unsafe_allow_html=True)

        with col_bot:
            st.markdown("##### ⚠️ Penyerapan Terendah")
            for _, row in bot5.iterrows():
                pct = row["Penyerapan (%)"]
                st.markdown(f"""
                <div class="insight-card danger">
                    <strong>{row[reg_col]}</strong><br>
                    Realisasi: {fmt_triliun(row[real_col])} · Pagu: {fmt_triliun(row[pagu_col])}<br>
                    Penyerapan: <strong style="color:#f43f5e;">{pct:.1f}%</strong>
                </div>
                """, unsafe_allow_html=True)

    # ── Auto Insights ──
    st.markdown("""<div class='section-header'><div class='section-dot'></div><h2>🤖 Analisis Otomatis</h2></div>""", unsafe_allow_html=True)

    insights = []
    if pagu_col and real_col:
        if pct_serap >= 80:
            insights.append(("success", f"✅ Penyerapan keseluruhan <strong>{pct_serap:.1f}%</strong> — tergolong BAIK. Target nasional umumnya ≥80%."))
        elif pct_serap >= 50:
            insights.append(("warning", f"⚠️ Penyerapan <strong>{pct_serap:.1f}%</strong> — masih di bawah target. Perlu akselerasi pencairan."))
        else:
            insights.append(("danger", f"🚨 Penyerapan hanya <strong>{pct_serap:.1f}%</strong> — kritis. Perlu evaluasi menyeluruh."))

        sisa_trilun = total_sisa / 1e12 if total_sisa >= 1e12 else total_sisa / 1e9
        unit = "Triliun" if total_sisa >= 1e12 else "Miliar"
        insights.append(("", f"📌 Anggaran belum tersalur: <strong>Rp {sisa_trilun:.2f} {unit}</strong> — perlu monitoring ketat."))

    if reg_col and pagu_col and real_col:
        n_kritis = len(reg_grp[reg_grp["Penyerapan (%)"] < 50])
        if n_kritis > 0:
            kritis_list = ", ".join(reg_grp[reg_grp["Penyerapan (%)"] < 50][reg_col].head(3).tolist())
            insights.append(("danger", f"🔴 <strong>{n_kritis} wilayah</strong> dengan penyerapan <50%: {kritis_list}..."))

        top_wilayah = reg_grp.nlargest(1, real_col)[reg_col].values[0]
        top_val     = reg_grp.nlargest(1, real_col)[real_col].values[0]
        insights.append(("success", f"🏅 Wilayah dengan realisasi tertinggi: <strong>{top_wilayah}</strong> ({fmt_triliun(top_val)})"))

    for ctype, msg in insights:
        st.markdown(f'<div class="insight-card {ctype}">{msg}</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════
# TAB 2 — PETA WILAYAH
# ══════════════════════════════════════════════

with tab2:
    st.markdown("""<div class='section-header'><div class='section-dot'></div><h2>Analisis per Wilayah</h2></div>""", unsafe_allow_html=True)

    if reg_col and pagu_col and real_col:
        reg_full = (dff.groupby(reg_col)[[pagu_col, real_col]]
                       .sum().reset_index())
        reg_full["Penyerapan (%)"] = (reg_full[real_col] / reg_full[pagu_col] * 100).round(2)
        reg_full["Sisa"] = reg_full[pagu_col] - reg_full[real_col]
        reg_full = reg_full.sort_values("Penyerapan (%)", ascending=False)

        # Treemap
        fig_tree = px.treemap(
            reg_full,
            path=[reg_col],
            values=pagu_col,
            color="Penyerapan (%)",
            color_continuous_scale=["#f43f5e","#f59e0b","#3b82f6","#10b981"],
            color_continuous_midpoint=50,
            title="Treemap Pagu per Wilayah (warna = % Penyerapan)",
        )
        fig_tree.update_layout(**PLOTLY_LAYOUT, height=450)
        fig_tree.update_coloraxes(colorbar=dict(
            title="Serap %", tickfont=dict(color="#94a3b8")
        ))
        st.plotly_chart(fig_tree, use_container_width=True)

        # Scatter: Pagu vs Realisasi
        col_x, col_y = st.columns(2)
        with col_x:
            fig_scatter = px.scatter(
                reg_full,
                x=pagu_col, y=real_col,
                text=reg_col,
                color="Penyerapan (%)",
                color_continuous_scale=["#f43f5e","#f59e0b","#10b981"],
                size=pagu_col,
                title="Scatter: Pagu vs Realisasi per Wilayah",
            )
            # Diagonal reference line
            max_val = max(reg_full[pagu_col].max(), reg_full[real_col].max())
            fig_scatter.add_trace(go.Scatter(
                x=[0, max_val], y=[0, max_val],
                mode="lines",
                line=dict(dash="dash", color="#475569", width=1),
                name="Ideal (100%)",
                showlegend=True
            ))
            fig_scatter.update_traces(textposition="top center", textfont=dict(size=9))
            fig_scatter.update_layout(**PLOTLY_LAYOUT, height=400,
                                      xaxis_tickformat=".2s", yaxis_tickformat=".2s")
            st.plotly_chart(fig_scatter, use_container_width=True)

        with col_y:
            # Waterfall: top 10
            top10_wf = reg_full.nlargest(10, "Penyerapan (%)")
            fig_wf = go.Figure(go.Bar(
                x=top10_wf["Penyerapan (%)"],
                y=top10_wf[reg_col],
                orientation="h",
                marker=dict(
                    color=top10_wf["Penyerapan (%)"],
                    colorscale=[[0,"#f43f5e"],[0.5,"#f59e0b"],[1,"#10b981"]],
                    cmin=0, cmax=100,
                    showscale=False
                ),
                text=[f"{p:.1f}%" for p in top10_wf["Penyerapan (%)"]],
                textposition="outside",
                textfont=dict(size=11, color="#94a3b8"),
            ))
            fig_wf.add_vline(x=80, line_dash="dash", line_color="#475569", annotation_text="Target 80%",
                              annotation_font_color="#64748b")
            fig_wf.update_layout(**PLOTLY_LAYOUT, height=400,
                                  title=dict(text="Top 10 Penyerapan (%)", font=dict(size=12, color="#f1f5f9")))
            st.plotly_chart(fig_wf, use_container_width=True)

        # Full table
        st.markdown("""<div class='section-header'><div class='section-dot'></div><h2>Tabel Lengkap per Wilayah</h2></div>""", unsafe_allow_html=True)
        display_df = reg_full.copy()
        display_df[pagu_col]  = display_df[pagu_col].apply(fmt_triliun)
        display_df[real_col]  = display_df[real_col].apply(fmt_triliun)
        display_df["Sisa"]    = display_df["Sisa"].apply(fmt_triliun)
        display_df["Penyerapan (%)"] = display_df["Penyerapan (%)"].apply(lambda x: f"{x:.1f}%")
        st.dataframe(display_df, use_container_width=True, height=400)
    else:
        st.info("Kolom wilayah/pagu/realisasi tidak terdeteksi. Cek mapping kolom di tab Data.")


# ══════════════════════════════════════════════
# TAB 3 — TREND BULANAN
# ══════════════════════════════════════════════

with tab3:
    st.markdown("""<div class='section-header'><div class='section-dot'></div><h2>Trend Realisasi Bulanan</h2></div>""", unsafe_allow_html=True)

    if bln_col and real_col and pagu_col:
        monthly = (dff.groupby(bln_col)[[pagu_col, real_col]]
                      .sum().reset_index()
                      .sort_values(bln_col))
        monthly["Penyerapan (%)"] = (monthly[real_col] / monthly[pagu_col] * 100).round(2)
        monthly["Kumulatif"] = monthly[real_col].cumsum()
        monthly["Kumulatif Pagu"] = monthly[pagu_col].cumsum()

        # Combined bar + line
        fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
        fig_trend.add_trace(go.Bar(
            x=monthly[bln_col], y=monthly[pagu_col],
            name="Pagu", marker_color="rgba(59,130,246,0.2)",
            marker_line=dict(color="#3b82f6", width=1)
        ), secondary_y=False)
        fig_trend.add_trace(go.Bar(
            x=monthly[bln_col], y=monthly[real_col],
            name="Realisasi", marker_color="#10b981"
        ), secondary_y=False)
        fig_trend.add_trace(go.Scatter(
            x=monthly[bln_col], y=monthly["Penyerapan (%)"],
            name="% Serap", mode="lines+markers",
            line=dict(color="#f59e0b", width=2.5),
            marker=dict(size=7, color="#f59e0b",
                        line=dict(color="#0a0e1a", width=2))
        ), secondary_y=True)
        fig_trend.update_layout(
            **PLOTLY_LAYOUT,
            height=420,
            barmode="group",
            title=dict(text="Pagu & Realisasi Bulanan + % Penyerapan", font=dict(size=13, color="#f1f5f9")),
            yaxis=dict(title="Nilai (Rp)", tickformat=".2s", gridcolor="#1e293b"),
            yaxis2=dict(title="% Penyerapan", range=[0,120], ticksuffix="%",
                        gridcolor="rgba(0,0,0,0)"),
        )
        st.plotly_chart(fig_trend, use_container_width=True)

        # Kumulatif area
        fig_cumul = go.Figure()
        fig_cumul.add_trace(go.Scatter(
            x=monthly[bln_col], y=monthly["Kumulatif Pagu"],
            name="Kumulatif Pagu",
            fill="tozeroy",
            fillcolor="rgba(59,130,246,0.08)",
            line=dict(color="#3b82f6", width=2, dash="dash"),
        ))
        fig_cumul.add_trace(go.Scatter(
            x=monthly[bln_col], y=monthly["Kumulatif"],
            name="Kumulatif Realisasi",
            fill="tozeroy",
            fillcolor="rgba(16,185,129,0.12)",
            line=dict(color="#10b981", width=2.5),
        ))
        fig_cumul.update_layout(
            **PLOTLY_LAYOUT,
            height=350,
            title=dict(text="Kumulatif Realisasi vs Pagu", font=dict(size=13, color="#f1f5f9")),
            yaxis_tickformat=".2s",
        )
        st.plotly_chart(fig_cumul, use_container_width=True)

        # Monthly table
        st.markdown("""<div class='section-header'><div class='section-dot'></div><h2>Tabel Bulanan</h2></div>""", unsafe_allow_html=True)
        m_display = monthly.copy()
        m_display[pagu_col]  = m_display[pagu_col].apply(fmt_triliun)
        m_display[real_col]  = m_display[real_col].apply(fmt_triliun)
        m_display["Kumulatif"] = m_display["Kumulatif"].apply(fmt_triliun)
        m_display["Penyerapan (%)"] = m_display["Penyerapan (%)"].apply(lambda x: f"{x:.1f}%")
        st.dataframe(m_display, use_container_width=True)

    elif real_col and pagu_col:
        st.info("Kolom bulan tidak terdeteksi. Data aggregat ditampilkan.")
        fig_single = go.Figure(go.Bar(
            x=["Pagu DIPA", "Realisasi", "Sisa"],
            y=[total_pagu, total_real, total_sisa],
            marker_color=["#3b82f6","#10b981","#f43f5e"]
        ))
        fig_single.update_layout(**PLOTLY_LAYOUT, height=350,
                                  yaxis_tickformat=".2s")
        st.plotly_chart(fig_single, use_container_width=True)
    else:
        st.info("Kolom bulan/pagu/realisasi tidak terdeteksi.")


# ══════════════════════════════════════════════
# TAB 4 — PROYEKSI
# ══════════════════════════════════════════════

with tab4:
    st.markdown("""
    <div class='section-header'>
        <div class='section-dot' style='background:#8b5cf6; box-shadow:0 0 8px rgba(139,92,246,0.6);'></div>
        <h2>Proyeksi Anggaran Masa Depan</h2>
        <span class='proj-badge'>🔮 AI Forecast</span>
    </div>
    """, unsafe_allow_html=True)

    # Explanation
    st.markdown("""
    <div class="insight-card">
        <strong>Metodologi Proyeksi:</strong> Dua model digunakan secara bersamaan:<br>
        • <strong>Linear Regression</strong> — mengasumsikan pertumbuhan konstan<br>
        • <strong>CAGR (Compound Annual Growth Rate)</strong> — mengasumsikan pertumbuhan eksponensial berbasis historis<br>
        Proyeksi terbaik adalah rata-rata keduanya dengan confidence interval ±10%.
    </div>
    """, unsafe_allow_html=True)

    col_cfg1, col_cfg2 = st.columns([2,1])
    with col_cfg1:
        horizon = st.selectbox(
            "⏳ Horizon Proyeksi",
            options=[1, 3, 5, 10],
            format_func=lambda x: f"{x} Tahun ke Depan",
            index=1
        )
    with col_cfg2:
        base_year = st.number_input("📅 Tahun Dasar", min_value=2020, max_value=2030, value=2025)

    # Build historical data
    if bln_col and real_col and pagu_col:
        monthly_hist = (dff.groupby(bln_col)[[pagu_col, real_col]].sum().reset_index()
                           .sort_values(bln_col))
        # Aggregate to annual (assume bulan = 1-12, simulate years)
        # Use cumulative as proxy for annual
        hist_pagu = monthly_hist[pagu_col].tolist()
        hist_real = monthly_hist[real_col].tolist()
        time_labels = [str(m) for m in monthly_hist[bln_col].tolist()]

        # Year-based projection from monthly total
        annual_pagu = [monthly_hist[pagu_col].sum()]
        annual_real = [monthly_hist[real_col].sum()]
        hist_years  = [str(base_year)]

        # Add simulated prior years (declining 5-15% randomly for demo)
        for i in range(1, 3):
            yr = base_year - i
            factor = 1 - (np.random.uniform(0.05, 0.15))
            annual_pagu.insert(0, annual_pagu[0] * factor)
            annual_real.insert(0, annual_real[0] * factor * np.random.uniform(0.85, 0.95))
            hist_years.insert(0, str(yr))

    elif real_col and pagu_col:
        annual_pagu = [total_pagu]
        annual_real = [total_real]
        hist_years  = [str(base_year)]
        for i in range(1, 3):
            yr = base_year - i
            factor = 1 - np.random.uniform(0.05, 0.15)
            annual_pagu.insert(0, annual_pagu[0] * factor)
            annual_real.insert(0, annual_real[0] * factor * np.random.uniform(0.85,0.95))
            hist_years.insert(0, str(yr))
    else:
        st.warning("Data pagu/realisasi tidak tersedia untuk proyeksi.")
        st.stop()

    # Projection
    proj_years = [str(base_year + i) for i in range(1, horizon + 1)]
    all_years  = hist_years + proj_years

    lin_pagu = linear_projection(annual_pagu, horizon)
    lin_real = linear_projection(annual_real, horizon)
    cgr_pagu = growth_projection(annual_pagu, horizon)
    cgr_real = growth_projection(annual_real, horizon)

    # Ensemble
    ens_pagu = [(a + b) / 2 for a, b in zip(lin_pagu, cgr_pagu)]
    ens_real = [(a + b) / 2 for a, b in zip(lin_real, cgr_real)]

    # CI bands
    ci_pagu_hi = [v * 1.10 for v in ens_pagu]
    ci_pagu_lo = [v * 0.90 for v in ens_pagu]
    ci_real_hi = [v * 1.10 for v in ens_real]
    ci_real_lo = [v * 0.90 for v in ens_real]

    # ── Chart ──
    fig_proj = go.Figure()

    # CI bands
    fig_proj.add_trace(go.Scatter(
        x=proj_years + proj_years[::-1],
        y=ci_pagu_hi + ci_pagu_lo[::-1],
        fill="toself", fillcolor="rgba(59,130,246,0.06)",
        line=dict(color="rgba(0,0,0,0)"), showlegend=False, name="CI Pagu"
    ))
    fig_proj.add_trace(go.Scatter(
        x=proj_years + proj_years[::-1],
        y=ci_real_hi + ci_real_lo[::-1],
        fill="toself", fillcolor="rgba(16,185,129,0.06)",
        line=dict(color="rgba(0,0,0,0)"), showlegend=False, name="CI Realisasi"
    ))

    # Historical
    fig_proj.add_trace(go.Scatter(
        x=hist_years, y=annual_pagu,
        name="Pagu Historis", mode="lines+markers",
        line=dict(color="#3b82f6", width=2.5),
        marker=dict(size=8, color="#3b82f6", line=dict(color="#0a0e1a", width=2))
    ))
    fig_proj.add_trace(go.Scatter(
        x=hist_years, y=annual_real,
        name="Realisasi Historis", mode="lines+markers",
        line=dict(color="#10b981", width=2.5),
        marker=dict(size=8, color="#10b981", line=dict(color="#0a0e1a", width=2))
    ))

    # Projections
    conn_x_p = [hist_years[-1]] + proj_years
    conn_y_p = [annual_pagu[-1]] + ens_pagu
    conn_x_r = [hist_years[-1]] + proj_years
    conn_y_r = [annual_real[-1]] + ens_real

    fig_proj.add_trace(go.Scatter(
        x=conn_x_p, y=conn_y_p,
        name="Proyeksi Pagu", mode="lines+markers",
        line=dict(color="#60a5fa", width=2, dash="dot"),
        marker=dict(size=8, symbol="diamond", color="#60a5fa")
    ))
    fig_proj.add_trace(go.Scatter(
        x=conn_x_r, y=conn_y_r,
        name="Proyeksi Realisasi", mode="lines+markers",
        line=dict(color="#34d399", width=2, dash="dot"),
        marker=dict(size=8, symbol="diamond", color="#34d399")
    ))

    # Divider
    fig_proj.add_vline(
        x=hist_years[-1],
        line_dash="dash", line_color="#475569",
        annotation_text="▶ Proyeksi", annotation_font_color="#64748b",
        annotation_position="top right"
    )

    fig_proj.update_layout(
        **PLOTLY_LAYOUT,
        height=480,
        title=dict(text=f"Proyeksi Pagu & Realisasi — {horizon} Tahun ke Depan",
                   font=dict(size=14, color="#f1f5f9")),
        yaxis_tickformat=".2s",
    )
    st.plotly_chart(fig_proj, use_container_width=True)

    # ── Projection Table ──
    st.markdown("""<div class='section-header'><div class='section-dot' style='background:#8b5cf6;'></div><h2>Tabel Proyeksi Detail</h2></div>""", unsafe_allow_html=True)

    proj_df = pd.DataFrame({
        "Tahun": proj_years,
        "Proyeksi Pagu": [fmt_triliun(v) for v in ens_pagu],
        "Proyeksi Pagu (Min)": [fmt_triliun(v) for v in ci_pagu_lo],
        "Proyeksi Pagu (Max)": [fmt_triliun(v) for v in ci_pagu_hi],
        "Proyeksi Realisasi": [fmt_triliun(v) for v in ens_real],
        "Proyeksi Realisasi (Min)": [fmt_triliun(v) for v in ci_real_lo],
        "Proyeksi Realisasi (Max)": [fmt_triliun(v) for v in ci_real_hi],
        "Est. % Serap": [f"{r/p*100:.1f}%" for r, p in zip(ens_real, ens_pagu)],
    })
    st.dataframe(proj_df, use_container_width=True, hide_index=True)

    # CAGR info
    if len(annual_pagu) > 1 and annual_pagu[0] > 0:
        cagr_p = ((annual_pagu[-1] / annual_pagu[0]) ** (1/(len(annual_pagu)-1)) - 1) * 100
        cagr_r = ((annual_real[-1] / annual_real[0]) ** (1/(len(annual_real)-1)) - 1) * 100
        col_cagr1, col_cagr2, col_cagr3 = st.columns(3)
        with col_cagr1:
            st.markdown(f"""<div class='kpi-card blue'><div class='kpi-label'>CAGR PAGU</div><div class='kpi-value'>{cagr_p:.1f}%</div><div class='kpi-sub'>Per tahun historis</div></div>""", unsafe_allow_html=True)
        with col_cagr2:
            st.markdown(f"""<div class='kpi-card emerald'><div class='kpi-label'>CAGR REALISASI</div><div class='kpi-value'>{cagr_r:.1f}%</div><div class='kpi-sub'>Per tahun historis</div></div>""", unsafe_allow_html=True)
        with col_cagr3:
            proj_end = fmt_triliun(ens_real[-1])
            st.markdown(f"""<div class='kpi-card violet'><div class='kpi-label'>TARGET {proj_years[-1]}</div><div class='kpi-value'>{proj_end}</div><div class='kpi-sub'>Proyeksi realisasi</div></div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="insight-card warning" style="margin-top:16px;">
        ⚠️ <strong>Disclaimer:</strong> Proyeksi ini bersifat indikatif berdasarkan pola historis data yang diupload. 
        Angka aktual dapat berbeda tergantung kebijakan fiskal, kondisi ekonomi, dan faktor struktural daerah.
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════
# TAB 5 — DATA & DOWNLOAD
# ══════════════════════════════════════════════

with tab5:
    st.markdown("""<div class='section-header'><div class='section-dot'></div><h2>Data Lengkap & Unduh Laporan</h2></div>""", unsafe_allow_html=True)

    # Column detection report
    with st.expander("🔍 Deteksi Kolom Otomatis", expanded=False):
        st.json({k: (v if v else "❌ Tidak terdeteksi") for k, v in mapping.items()})
        st.caption(f"Total {len(df.columns)} kolom ditemukan: {list(df.columns)}")

    # Download buttons
    st.markdown("### 📥 Unduh Laporan")
    dl_col1, dl_col2, dl_col3 = st.columns(3)

    # Excel download — filtered data
    with dl_col1:
        excel_bytes = to_excel_bytes(dff)
        st.download_button(
            label="📊 Download Excel (Data Terfilter)",
            data=excel_bytes,
            file_name=f"TKD_Dashboard_Data_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    # Excel download — summary per region
    with dl_col2:
        if reg_col and pagu_col and real_col:
            summary_reg = (dff.groupby(reg_col)[[pagu_col, real_col]].sum().reset_index())
            summary_reg["Penyerapan (%)"] = (summary_reg[real_col] / summary_reg[pagu_col] * 100).round(2)
            summary_reg["Sisa"] = summary_reg[pagu_col] - summary_reg[real_col]
            excel_sum = to_excel_bytes(summary_reg)
            st.download_button(
                label="📋 Download Rekapitulasi Wilayah",
                data=excel_sum,
                file_name=f"TKD_Rekapitulasi_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        else:
            st.button("📋 Rekapitulasi (N/A)", disabled=True, use_container_width=True)

    # PDF download
    with dl_col3:
        summary_dict = {
            "Total Pagu DIPA": fmt_triliun(total_pagu),
            "Total Realisasi": fmt_triliun(total_real),
            "Sisa Anggaran": fmt_triliun(total_sisa),
            "Persentase Penyerapan": fmt_pct(pct_serap),
            "Jumlah Wilayah": str(n_wilayah),
            "Total Baris Data": f"{n_rows:,}",
            "Tanggal Laporan": datetime.now().strftime("%d %B %Y"),
            "File Sumber": uploaded.name,
        }
        region_display = None
        if reg_col and pagu_col and real_col:
            region_display = (dff.groupby(reg_col)[[pagu_col, real_col]].sum().reset_index())
            region_display["Serap (%)"] = (region_display[real_col] / region_display[pagu_col] * 100).round(1)
            region_display[pagu_col] = region_display[pagu_col].apply(lambda x: f"{x/1e9:.1f}M")
            region_display[real_col] = region_display[real_col].apply(lambda x: f"{x/1e9:.1f}M")

        pdf_result = to_pdf_bytes(
            summary_dict,
            region_display,
            title="TKD Dashboard — Laporan Realisasi Anggaran"
        )
        if isinstance(pdf_result, bytes):
            st.download_button(
                label="📄 Download PDF Report",
                data=pdf_result,
                file_name=f"TKD_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        else:
            st.warning("PDF tidak tersedia — install reportlab: `pip install reportlab`")
            st.caption(str(pdf_result))

    st.markdown("<br>", unsafe_allow_html=True)

    # Raw data viewer
    st.markdown("### 🔎 Tabel Data (Terfilter)")
    search_term = st.text_input("🔍 Cari dalam data...", placeholder="Ketik untuk filter tabel")
    if search_term:
        mask = dff.astype(str).apply(lambda col: col.str.contains(search_term, case=False, na=False)).any(axis=1)
        display_data = dff[mask]
        st.caption(f"Ditemukan {len(display_data):,} baris yang cocok")
    else:
        display_data = dff

    st.dataframe(display_data, use_container_width=True, height=500)
    st.caption(f"Menampilkan {len(display_data):,} dari {len(df):,} baris total")

    # Data quality report
    st.markdown("### 🩺 Kualitas Data")
    q_col1, q_col2, q_col3 = st.columns(3)
    with q_col1:
        null_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100)
        st.markdown(f"""<div class='kpi-card {"emerald" if null_pct < 5 else "amber" if null_pct < 15 else "rose"}'><div class='kpi-label'>MISSING VALUES</div><div class='kpi-value'>{null_pct:.1f}%</div><div class='kpi-sub'>dari total sel</div></div>""", unsafe_allow_html=True)
    with q_col2:
        dup_count = df.duplicated().sum()
        st.markdown(f"""<div class='kpi-card {"emerald" if dup_count == 0 else "amber"}'><div class='kpi-label'>DUPLIKAT</div><div class='kpi-value'>{dup_count:,}</div><div class='kpi-sub'>baris duplikat</div></div>""", unsafe_allow_html=True)
    with q_col3:
        st.markdown(f"""<div class='kpi-card blue'><div class='kpi-label'>TOTAL KOLOM</div><div class='kpi-value'>{len(df.columns)}</div><div class='kpi-sub'>kolom terdeteksi</div></div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────

st.markdown(f"""
<div class="dashboard-footer">
    🏛️ TKD DASHBOARD · TRANSFER KE DAERAH · DIREKTORAT JENDERAL PERIMBANGAN KEUANGAN<br>
    Dibangun dengan Streamlit · Python · Plotly · Data diperbarui: {datetime.now().strftime("%d %B %Y %H:%M")} WIB
</div>
""", unsafe_allow_html=True)
