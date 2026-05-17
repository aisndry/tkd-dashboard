import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

st.set_page_config(
    page_title="Dashboard TKD 2025",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

.main-header {
    background: linear-gradient(135deg, #1a237e 0%, #0d47a1 50%, #01579b 100%);
    padding: 2rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    color: white;
    text-align: center;
}

.main-header h1 {
    font-size: 2rem;
    font-weight: 800;
    margin: 0;
    letter-spacing: -0.5px;
}

.main-header p {
    opacity: 0.85;
    margin: 0.5rem 0 0 0;
    font-size: 0.95rem;
}

.metric-card {
    background: white;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    border-left: 4px solid #1565c0;
    margin-bottom: 1rem;
}

.metric-card.green { border-left-color: #2e7d32; }
.metric-card.orange { border-left-color: #e65100; }
.metric-card.purple { border-left-color: #6a1b9a; }

.metric-label {
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #546e7a;
    margin-bottom: 0.3rem;
}

.metric-value {
    font-size: 1.6rem;
    font-weight: 800;
    color: #1a237e;
    line-height: 1;
}

.metric-sub {
    font-size: 0.82rem;
    color: #78909c;
    margin-top: 0.25rem;
}

.section-title {
    font-size: 1rem;
    font-weight: 700;
    color: #1a237e;
    margin: 1.5rem 0 0.75rem 0;
    padding-bottom: 0.4rem;
    border-bottom: 2px solid #e3f2fd;
}

.alert-box {
    padding: 0.9rem 1.2rem;
    border-radius: 10px;
    margin: 0.5rem 0;
    font-size: 0.88rem;
    font-weight: 500;
}

.alert-danger { background: #ffebee; color: #b71c1c; border-left: 4px solid #e53935; }
.alert-warning { background: #fff8e1; color: #e65100; border-left: 4px solid #ff8f00; }
.alert-success { background: #e8f5e9; color: #1b5e20; border-left: 4px solid #43a047; }

.upload-hint {
    text-align: center;
    padding: 3rem;
    background: #f8faff;
    border-radius: 16px;
    border: 2px dashed #90caf9;
    color: #546e7a;
}
</style>
""", unsafe_allow_html=True)

BULAN = ['JAN','FEB','MAR','APR','MEI','JUN','JUL','AGS','SEP','OKT','NOV','DES']

def format_rp(value, short=False):
    if short:
        if abs(value) >= 1e12:
            return f"Rp {value/1e12:.2f} T"
        elif abs(value) >= 1e9:
            return f"Rp {value/1e9:.1f} M"
        elif abs(value) >= 1e6:
            return f"Rp {value/1e6:.1f} Jt"
        return f"Rp {value:,.0f}"
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
        'SATKER': ['NMSATKER','SATKER','NAMA SATKER'],
        'KPPN': ['NMKPPN','KPPN','NAMA KPPN'],
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
            # Cari sheet dengan data terbanyak
            best = None
            best_n = 0
            for s in xf.sheet_names:
                try:
                    tmp = pd.read_excel(file, sheet_name=s, nrows=3)
                    n = len(tmp.columns)
                    if n > best_n:
                        best_n = n
                        best = s
                except:
                    pass
            # Coba sheet yang mengandung kata 'pagu' atau 'real'
            for s in xf.sheet_names:
                if any(k in s.lower() for k in ['pagu','real','data','tkd']):
                    best = s
                    break
            df = pd.read_excel(file, sheet_name=best)
        # Bersihkan
        df.columns = df.columns.astype(str).str.strip()
        df = df.dropna(how='all')
        return df, None
    except Exception as e:
        return None, str(e)

# ─── HEADER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🏛️ Dashboard Transfer ke Daerah (TKD) 2025</h1>
    <p>Analisis Pagu & Realisasi Anggaran Transfer ke Daerah secara Interaktif</p>
</div>
""", unsafe_allow_html=True)

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📂 Upload Data")
    uploaded = st.file_uploader(
        "Upload file Excel atau CSV",
        type=['xlsx','xls','csv'],
        help="Format: kolom wajib ada PAGU_DIPA, Total Realisasi, NMKABKOTA, NMAKUN"
    )
    st.markdown("---")
    st.markdown("**Format data yang didukung:**")
    st.markdown("- ✅ Excel (.xlsx / .xls)")
    st.markdown("- ✅ CSV (.csv)")
    st.markdown("- Kolom bulan: JAN, FEB, MAR, ...")
    st.markdown("- Kolom pagu, realisasi, wilayah")
    st.markdown("---")
    st.caption("Dibuat untuk analisis TKD Kemenkeu RI")

# ─── MAIN CONTENT ─────────────────────────────────────────────────────────────
if uploaded is None:
    st.markdown("""
    <div class="upload-hint">
        <h2>📤 Upload File Excel / CSV</h2>
        <p>Silakan upload file data TKD di panel kiri untuk memulai analisis dashboard</p>
        <br>
        <p><strong>Data yang dibutuhkan:</strong> Pagu DIPA, Realisasi per bulan, Nama Kabupaten/Kota, Nama Akun</p>
    </div>
    """, unsafe_allow_html=True)
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
    st.warning("⚠️ Kolom PAGU atau REALISASI tidak ditemukan. Pastikan format data sesuai.")
    st.dataframe(df_raw.head())
    st.stop()

# Konversi numerik
for c in [pagu_col, real_col] + list(bulan_cols.values()) + ([blokir_col] if blokir_col else []):
    if c and c in df_raw.columns:
        df_raw[c] = pd.to_numeric(df_raw[c], errors='coerce').fillna(0)

df = df_raw.copy()

# ─── FILTER ───────────────────────────────────────────────────────────────────
filter_cols = st.columns(3)
if kab_col:
    kabupatens = sorted(df[kab_col].dropna().unique().tolist())
    with filter_cols[0]:
        sel_kab = st.multiselect("🗺️ Kabupaten/Kota", kabupatens, placeholder="Semua wilayah")
    if sel_kab:
        df = df[df[kab_col].isin(sel_kab)]

if akun_col:
    akuns = sorted(df[akun_col].dropna().unique().tolist())
    with filter_cols[1]:
        sel_akun = st.multiselect("📋 Jenis Akun", akuns, placeholder="Semua akun")
    if sel_akun:
        df = df[df[akun_col].isin(sel_akun)]

if bulan_cols:
    with filter_cols[2]:
        available_bulan = list(bulan_cols.keys())
        sel_bulan = st.multiselect("📅 Bulan Realisasi", available_bulan, placeholder="Semua bulan")

# ─── KPI CARDS ────────────────────────────────────────────────────────────────
total_pagu = df[pagu_col].sum()
total_real = df[real_col].sum()
blokir = df[blokir_col].sum() if blokir_col else 0
pagu_efektif = total_pagu - blokir
persen = (total_real / pagu_efektif * 100) if pagu_efektif > 0 else 0
sisa = pagu_efektif - total_real

st.markdown('<div class="section-title">📊 Ringkasan Anggaran</div>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Pagu DIPA</div>
        <div class="metric-value">{format_rp(total_pagu, True)}</div>
        <div class="metric-sub">{df.shape[0]:,} record</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="metric-card green">
        <div class="metric-label">Total Realisasi</div>
        <div class="metric-value">{format_rp(total_real, True)}</div>
        <div class="metric-sub">dari pagu efektif</div>
    </div>""", unsafe_allow_html=True)
with c3:
    color = "green" if persen >= 80 else ("orange" if persen >= 50 else "")
    st.markdown(f"""
    <div class="metric-card {color}">
        <div class="metric-label">Persentase Penyerapan</div>
        <div class="metric-value">{persen:.1f}%</div>
        <div class="metric-sub">{"🟢 Baik" if persen>=80 else "🟡 Sedang" if persen>=50 else "🔴 Rendah"}</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""
    <div class="metric-card purple">
        <div class="metric-label">Sisa Anggaran</div>
        <div class="metric-value">{format_rp(sisa, True)}</div>
        <div class="metric-sub">belum terserap</div>
    </div>""", unsafe_allow_html=True)

# ─── PROGRESS BAR ─────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="margin: 1rem 0; background: #e3f2fd; border-radius: 8px; height: 20px; overflow: hidden;">
    <div style="width: {min(persen,100):.1f}%; background: linear-gradient(90deg, #1565c0, #42a5f5); 
         height: 100%; border-radius: 8px; display: flex; align-items: center; 
         justify-content: center; color: white; font-size: 0.75rem; font-weight: 700;">
        {persen:.1f}% Terserap
    </div>
</div>
""", unsafe_allow_html=True)

# ─── CHARTS ROW 1 ─────────────────────────────────────────────────────────────
col_left, col_right = st.columns([1.4, 1])

with col_left:
    if kab_col:
        st.markdown('<div class="section-title">📍 Pagu vs Realisasi per Kabupaten/Kota</div>', unsafe_allow_html=True)
        grp = df.groupby(kab_col)[[pagu_col, real_col]].sum().reset_index()
        grp['persen'] = (grp[real_col] / grp[pagu_col] * 100).round(1)
        grp = grp.sort_values(real_col, ascending=True)
        grp['kab_short'] = grp[kab_col].str.replace('KAB. ','').str.replace('KOTA ','KOTA ').str.title()

        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=grp['kab_short'], x=grp[pagu_col],
            name='Pagu DIPA', orientation='h',
            marker_color='#bbdefb', marker_line_width=0
        ))
        fig.add_trace(go.Bar(
            y=grp['kab_short'], x=grp[real_col],
            name='Realisasi', orientation='h',
            marker_color='#1565c0', marker_line_width=0,
            text=[f"{p}%" for p in grp['persen']],
            textposition='outside'
        ))
        fig.update_layout(
            barmode='overlay', height=420,
            margin=dict(l=0, r=40, t=10, b=10),
            legend=dict(orientation='h', y=1.05),
            xaxis=dict(tickformat=',.0f', title='Rupiah'),
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family='Plus Jakarta Sans')
        )
        st.plotly_chart(fig, use_container_width=True)

with col_right:
    if akun_col:
        st.markdown('<div class="section-title">🏷️ Komposisi Realisasi per Jenis</div>', unsafe_allow_html=True)
        grp_a = df.groupby(akun_col)[real_col].sum().reset_index()
        grp_a = grp_a[grp_a[real_col] > 0].sort_values(real_col, ascending=False).head(10)
        grp_a['akun_short'] = grp_a[akun_col].str[:40]
        fig2 = px.pie(grp_a, values=real_col, names='akun_short',
                      color_discrete_sequence=px.colors.sequential.Blues_r)
        fig2.update_traces(textposition='inside', textinfo='percent+label',
                           textfont_size=10)
        fig2.update_layout(
            height=420, margin=dict(l=0, r=0, t=10, b=10),
            showlegend=False,
            paper_bgcolor='white',
            font=dict(family='Plus Jakarta Sans')
        )
        st.plotly_chart(fig2, use_container_width=True)

# ─── TREND BULANAN ────────────────────────────────────────────────────────────
if bulan_cols:
    st.markdown('<div class="section-title">📈 Trend Realisasi Bulanan</div>', unsafe_allow_html=True)
    bulan_data = []
    for b, c in bulan_cols.items():
        if c in df.columns:
            bulan_data.append({'Bulan': b, 'Realisasi': df[c].sum()})
    if bulan_data:
        df_bln = pd.DataFrame(bulan_data)
        df_bln['Kumulatif'] = df_bln['Realisasi'].cumsum()
        df_bln['Bulan_idx'] = range(len(df_bln))

        fig3 = make_subplots(specs=[[{"secondary_y": True}]])
        fig3.add_trace(go.Bar(
            x=df_bln['Bulan'], y=df_bln['Realisasi'],
            name='Realisasi Bulanan',
            marker_color='#42a5f5'
        ), secondary_y=False)
        fig3.add_trace(go.Scatter(
            x=df_bln['Bulan'], y=df_bln['Kumulatif'],
            name='Kumulatif', mode='lines+markers',
            line=dict(color='#1a237e', width=3),
            marker=dict(size=8)
        ), secondary_y=True)
        fig3.update_layout(
            height=320, margin=dict(l=0, r=0, t=10, b=10),
            plot_bgcolor='white', paper_bgcolor='white',
            legend=dict(orientation='h', y=1.08),
            font=dict(family='Plus Jakarta Sans')
        )
        fig3.update_yaxes(title_text="Realisasi Bulanan", secondary_y=False, tickformat=',.0f')
        fig3.update_yaxes(title_text="Kumulatif", secondary_y=True, tickformat=',.0f')
        st.plotly_chart(fig3, use_container_width=True)

# ─── ANALISIS OTOMATIS ────────────────────────────────────────────────────────
st.markdown('<div class="section-title">🤖 Analisis Otomatis</div>', unsafe_allow_html=True)

alerts = []
if persen < 50:
    alerts.append(("danger", f"⚠️ Penyerapan sangat rendah ({persen:.1f}%) — perlu evaluasi mendesak"))
elif persen < 80:
    alerts.append(("warning", f"🔶 Penyerapan cukup ({persen:.1f}%) — masih ada ruang peningkatan"))
else:
    alerts.append(("success", f"✅ Penyerapan baik ({persen:.1f}%) — target terlampaui"))

if kab_col and real_col:
    grp_kab = df.groupby(kab_col)[[pagu_col, real_col]].sum()
    grp_kab['persen'] = grp_kab[real_col] / grp_kab[pagu_col] * 100
    rendah = grp_kab[grp_kab['persen'] < 50]
    if len(rendah) > 0:
        nama = ', '.join(rendah.index[:3].tolist())
        alerts.append(("warning", f"📍 {len(rendah)} wilayah dengan penyerapan <50%: {nama}"))
    top = grp_kab.sort_values('persen', ascending=False).index[0]
    bot = grp_kab.sort_values('persen').index[0]
    alerts.append(("success", f"🏆 Penyerapan tertinggi: {top} ({grp_kab.loc[top,'persen']:.1f}%)"))
    alerts.append(("warning", f"📉 Penyerapan terendah: {bot} ({grp_kab.loc[bot,'persen']:.1f}%)"))

if blokir_col and blokir > 0:
    alerts.append(("warning", f"🔒 Anggaran diblokir: {format_rp(blokir, True)} — perlu pencairan"))

for level, msg in alerts:
    st.markdown(f'<div class="alert-box alert-{level}">{msg}</div>', unsafe_allow_html=True)

# ─── TABEL DETAIL ─────────────────────────────────────────────────────────────
with st.expander("📋 Lihat Tabel Detail"):
    if kab_col:
        show_cols = [kab_col]
        if akun_col: show_cols.append(akun_col)
        show_cols += [pagu_col, real_col]
        if blokir_col: show_cols.append(blokir_col)
        tbl = df[show_cols].copy()
        tbl['Penyerapan (%)'] = (tbl[real_col] / tbl[pagu_col] * 100).round(1)
        st.dataframe(
            tbl.style.format({pagu_col: '{:,.0f}', real_col: '{:,.0f}',
                              'Penyerapan (%)': '{:.1f}%'}),
            use_container_width=True, height=400
        )

st.markdown("---")
st.caption("Dashboard TKD 2025 | Data: DJPB Kemenkeu RI | Upload ulang file untuk refresh data")
