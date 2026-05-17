import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Dashboard TKD 2025",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
.main-header {
    background: linear-gradient(135deg, #1a237e 0%, #0d47a1 50%, #01579b 100%);
    padding: 2rem; border-radius: 16px; margin-bottom: 1.5rem;
    color: white; text-align: center;
}
.main-header h1 { font-size: 2rem; font-weight: 800; margin: 0; }
.main-header p { opacity: 0.85; margin: 0.5rem 0 0 0; font-size: 0.95rem; }
.metric-card {
    background: white; border-radius: 12px; padding: 1.25rem 1.5rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08); border-left: 4px solid #1565c0;
    margin-bottom: 1rem;
}
.metric-card.green { border-left-color: #2e7d32; }
.metric-card.orange { border-left-color: #e65100; }
.metric-card.purple { border-left-color: #6a1b9a; }
.metric-label { font-size: 0.78rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.8px; color: #546e7a; margin-bottom: 0.3rem; }
.metric-value { font-size: 1.6rem; font-weight: 800; color: #1a237e; line-height: 1; }
.metric-sub { font-size: 0.82rem; color: #78909c; margin-top: 0.25rem; }
.section-title { font-size: 1rem; font-weight: 700; color: #1a237e;
    margin: 1.5rem 0 0.75rem 0; padding-bottom: 0.4rem; border-bottom: 2px solid #e3f2fd; }
.alert-box { padding: 0.9rem 1.2rem; border-radius: 10px; margin: 0.5rem 0;
    font-size: 0.88rem; font-weight: 500; }
.alert-danger { background: #ffebee; color: #b71c1c; border-left: 4px solid #e53935; }
.alert-warning { background: #fff8e1; color: #e65100; border-left: 4px solid #ff8f00; }
.alert-success { background: #e8f5e9; color: #1b5e20; border-left: 4px solid #43a047; }
</style>
""", unsafe_allow_html=True)

BULAN = ['JAN','FEB','MAR','APR','MEI','JUN','JUL','AGS','SEP','OKT','NOV','DES']

def format_rp(value):
    if abs(value) >= 1e12:
        return f"Rp {value/1e12:.2f} T"
    elif abs(value) >= 1e9:
        return f"Rp {value/1e9:.1f} M"
    elif abs(value) >= 1e6:
        return f"Rp {value/1e6:.1f} Jt"
    return f"Rp {value:,.0f}"

def detect_columns(df):
    cols = {c.upper().strip(): c for c in df.columns}
    mapping = {}
    for key, candidates in {
        'PAGU': ['PAGU_DIPA','PAGU','ANGGARAN','PAGU DIPA'],
        'REALISASI': ['TOTAL REALISASI 10','TOTAL_REALISASI_10','REALISASI','TOTAL REALISASI','REAL'],
        'KABKOTA': ['NMKABKOTA','KABKOTA','KAB_KOTA','NAMA KABKOTA','WILAYAH','DAERAH'],
        'AKUN': ['NMAKUN','AKUN','NAMA AKUN','JENIS'],
        'BLOKIR': ['BLOKIR'],
    }.items():
        for c in candidates:
            if c in cols:
                mapping[key] = cols[c]
                break
    month_found = {}
    for b in BULAN:
        if b in cols:
            month_found[b] = cols[b]
    mapping['BULAN'] = month_found
    return mapping

def load_data(file):
    try:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            xf = pd.ExcelFile(file)
            best = xf.sheet_names[0]
            for s in xf.sheet_names:
                if any(k in s.lower() for k in ['pagu','real','data','tkd']):
                    best = s
                    break
            df = pd.read_excel(file, sheet_name=best)
        df.columns = df.columns.astype(str).str.strip()
        df = df.dropna(how='all')
        return df, None
    except Exception as e:
        return None, str(e)

# HEADER
st.markdown("""
<div class="main-header">
    <h1>🏛️ Dashboard Transfer ke Daerah (TKD) 2025</h1>
    <p>Analisis Pagu & Realisasi Anggaran Transfer ke Daerah secara Interaktif</p>
</div>
""", unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.markdown("### 📂 Upload Data")
    uploaded = st.file_uploader("Upload file Excel atau CSV", type=['xlsx','xls','csv'])
    st.markdown("---")
    st.markdown("**Format kolom yang dikenali:**")
    st.markdown("- Pagu: `PAGU_DIPA`, `PAGU`")
    st.markdown("- Realisasi: `Total realisasi 10`")
    st.markdown("- Wilayah: `NMKABKOTA`")
    st.markdown("- Akun: `NMAKUN`")
    st.markdown("- Bulan: `JAN` s/d `DES`")

if uploaded is None:
    st.info("👈 Silakan upload file Excel atau CSV di panel kiri untuk memulai analisis.")
    st.stop()

df_raw, err = load_data(uploaded)
if err:
    st.error(f"❌ Gagal membaca file: {err}")
    st.stop()

cm = detect_columns(df_raw)
pagu_col = cm.get('PAGU')
real_col = cm.get('REALISASI')
kab_col = cm.get('KABKOTA')
akun_col = cm.get('AKUN')
blokir_col = cm.get('BLOKIR')
bulan_cols = cm.get('BULAN', {})

if not pagu_col or not real_col:
    st.warning("⚠️ Kolom PAGU atau REALISASI tidak ditemukan.")
    st.dataframe(df_raw.head())
    st.stop()

for c in [pagu_col, real_col] + list(bulan_cols.values()) + ([blokir_col] if blokir_col else []):
    if c and c in df_raw.columns:
        df_raw[c] = pd.to_numeric(df_raw[c], errors='coerce').fillna(0)

df = df_raw.copy()

# FILTER
st.markdown('<div class="section-title">🔍 Filter Data</div>', unsafe_allow_html=True)
fc = st.columns(2)
if kab_col:
    with fc[0]:
        sel_kab = st.multiselect("🗺️ Kabupaten/Kota", sorted(df[kab_col].dropna().unique()), placeholder="Semua wilayah")
    if sel_kab:
        df = df[df[kab_col].isin(sel_kab)]
if akun_col:
    with fc[1]:
        sel_akun = st.multiselect("📋 Jenis Akun", sorted(df[akun_col].dropna().unique()), placeholder="Semua akun")
    if sel_akun:
        df = df[df[akun_col].isin(sel_akun)]

# KPI
total_pagu = df[pagu_col].sum()
total_real = df[real_col].sum()
blokir = df[blokir_col].sum() if blokir_col else 0
pagu_efektif = total_pagu - blokir
persen = (total_real / pagu_efektif * 100) if pagu_efektif > 0 else 0
sisa = pagu_efektif - total_real

st.markdown('<div class="section-title">📊 Ringkasan Anggaran</div>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="metric-card"><div class="metric-label">Total Pagu DIPA</div><div class="metric-value">{format_rp(total_pagu)}</div><div class="metric-sub">{df.shape[0]:,} record</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-card green"><div class="metric-label">Total Realisasi</div><div class="metric-value">{format_rp(total_real)}</div><div class="metric-sub">dari pagu efektif</div></div>', unsafe_allow_html=True)
with c3:
    color = "green" if persen >= 80 else "orange" if persen >= 50 else ""
    status = "🟢 Baik" if persen >= 80 else "🟡 Sedang" if persen >= 50 else "🔴 Rendah"
    st.markdown(f'<div class="metric-card {color}"><div class="metric-label">Penyerapan</div><div class="metric-value">{persen:.1f}%</div><div class="metric-sub">{status}</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="metric-card purple"><div class="metric-label">Sisa Anggaran</div><div class="metric-value">{format_rp(sisa)}</div><div class="metric-sub">belum terserap</div></div>', unsafe_allow_html=True)

st.markdown(f"""
<div style="margin:1rem 0;background:#e3f2fd;border-radius:8px;height:24px;overflow:hidden;">
  <div style="width:{min(persen,100):.1f}%;background:linear-gradient(90deg,#1565c0,#42a5f5);
       height:100%;display:flex;align-items:center;justify-content:center;
       color:white;font-size:0.8rem;font-weight:700;">
    {persen:.1f}% Terserap
  </div>
</div>""", unsafe_allow_html=True)

# CHART PER KAB
if kab_col:
    st.markdown('<div class="section-title">📍 Realisasi per Kabupaten/Kota</div>', unsafe_allow_html=True)
    grp = df.groupby(kab_col)[[pagu_col, real_col]].sum()
    grp.columns = ['Pagu DIPA', 'Realisasi']
    grp['Penyerapan (%)'] = (grp['Realisasi'] / grp['Pagu DIPA'] * 100).round(1)
    grp = grp.sort_values('Realisasi', ascending=False)
    st.bar_chart(grp[['Pagu DIPA', 'Realisasi']])

    st.markdown('<div class="section-title">📋 Tabel Rekap per Kabupaten/Kota</div>', unsafe_allow_html=True)
    st.dataframe(
        grp.style.format({'Pagu DIPA': '{:,.0f}', 'Realisasi': '{:,.0f}', 'Penyerapan (%)': '{:.1f}%'}),
        use_container_width=True
    )

# TREND BULANAN
if bulan_cols:
    st.markdown('<div class="section-title">📈 Trend Realisasi Bulanan</div>', unsafe_allow_html=True)
    bulan_data = {b: df[c].sum() for b, c in bulan_cols.items() if c in df.columns}
    df_bln = pd.DataFrame({'Realisasi Bulanan': bulan_data})
    df_bln['Kumulatif'] = df_bln['Realisasi Bulanan'].cumsum()
    st.line_chart(df_bln)

# AKUN
if akun_col:
    st.markdown('<div class="section-title">🏷️ Realisasi per Jenis Akun (Top 10)</div>', unsafe_allow_html=True)
    grp_a = df.groupby(akun_col)[real_col].sum().sort_values(ascending=False).head(10)
    grp_a.name = 'Realisasi'
    st.bar_chart(grp_a)

# ANALISIS OTOMATIS
st.markdown('<div class="section-title">🤖 Analisis Otomatis</div>', unsafe_allow_html=True)
alerts = []
if persen < 50:
    alerts.append(("danger", f"⚠️ Penyerapan sangat rendah ({persen:.1f}%) — perlu evaluasi mendesak"))
elif persen < 80:
    alerts.append(("warning", f"🔶 Penyerapan cukup ({persen:.1f}%) — masih ada ruang peningkatan"))
else:
    alerts.append(("success", f"✅ Penyerapan baik ({persen:.1f}%) — target tercapai"))

if kab_col:
    grp_kab = df.groupby(kab_col)[[pagu_col, real_col]].sum()
    grp_kab['persen'] = grp_kab[real_col] / grp_kab[pagu_col] * 100
    rendah = grp_kab[grp_kab['persen'] < 50]
    if len(rendah) > 0:
        alerts.append(("warning", f"📍 {len(rendah)} wilayah penyerapan <50%: {', '.join(rendah.index[:3].tolist())}"))
    top = grp_kab['persen'].idxmax()
    bot = grp_kab['persen'].idxmin()
    alerts.append(("success", f"🏆 Tertinggi: {top} ({grp_kab.loc[top,'persen']:.1f}%)"))
    alerts.append(("warning", f"📉 Terendah: {bot} ({grp_kab.loc[bot,'persen']:.1f}%)"))

if blokir > 0:
    alerts.append(("warning", f"🔒 Anggaran diblokir: {format_rp(blokir)} — perlu pencairan"))

for level, msg in alerts:
    st.markdown(f'<div class="alert-box alert-{level}">{msg}</div>', unsafe_allow_html=True)

st.markdown("---")
st.caption("Dashboard TKD 2025 | Data: DJPB Kemenkeu RI")
