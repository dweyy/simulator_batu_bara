import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import io

# ─────────────────────────────────────────────
# PAGE CONFIG & STYLE
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Simulator Ekonomi Batu Bara",
    page_icon="⛏️",
    layout="wide",
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem; font-weight: 700;
        color: #fff;
        padding-bottom: 0.3rem;
        text-shadow: 0 2px 12px #0f3460, 0 1px 0 #222;
        border-left: 6px solid #2196f3;
        padding-left: 16px;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background: #f0f4ff; border-radius: 12px;
        padding: 1rem 1.2rem; border-left: 5px solid #0f3460;
    }
    .section-title {
        font-size: 1.25rem; font-weight: 700;
        color: #fff;
        margin-top: 1.5rem; margin-bottom: 0.5rem;
        letter-spacing: 0.5px;
        text-shadow: 0 1px 8px #0f3460, 0 1px 0 #222;
        border-left: 4px solid #2196f3;
        padding-left: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# LOAD DATA 
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    data = {
        "Tahun": [2014,2015,2016,2017,2018,2019,2020,2021,2022,2023,2024],
        "Q": [56.20,51.50,52.64,51.80,54.00,58.00,54.53,52.70,40.88,42.88,45.82],
        "P": [1245070,1030857,1060161,1472956,1696741,1335481,997325,2082617,4741993,1875929,1768058],
        "bpp": [3.545605e10,3.676097e10,3.157563e10,3.634889e10,4.137970e10,
                4.280481e10,3.361886e10,3.816891e10,5.921933e10,6.833660e10,6.617318e10],
        "mc": [1.772803e10,1.838049e10,1.578782e10,1.817445e10,2.068985e10,
               2.140241e10,1.680943e10,1.908446e10,2.960967e10,3.416830e10,3.308659e10],
    }
    df = pd.DataFrame(data)

    # Proses tambahan
    df = df.dropna(subset=["Tahun"]).copy()
    df["Tahun"] = df["Tahun"].astype(int)
    reserves = [1.1 * (0.99 ** i) for i in range(len(df))]
    df["Cadangan"] = reserves
    df["BPP_per_ton"] = df["bpp"] / (df["Q"] * 1e6)
    df["MC_per_ton"]  = df["mc"]  / (df["Q"] * 1e6)
    return df 
df = load_data()

# ─────────────────────────────────────────────
# SIDEBAR – PARAMETER SIMULASI
# ─────────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/fluency/96/coal.png", width=64)
st.sidebar.title("⚙️ Parameter Simulasi")

st.sidebar.markdown("### 📈 Asumsi Permintaan Masa Depan")
demand_growth = st.sidebar.slider(
    "Pertumbuhan Permintaan Tahunan (%)", -10.0, 20.0, 3.0, step=0.5
)

st.sidebar.markdown("### 💰 Pajak & Royalti")
tax_rate = st.sidebar.slider("Tarif Pajak/Royalti (%)", 0.0, 30.0, 13.5, step=0.5)

st.sidebar.markdown("### 🏭 Struktur Pasar")
monopoly_margin = st.sidebar.slider(
    "Margin Monopoli di atas BPP (%)", 10.0, 100.0, 40.0, step=5.0
)
oligopoly_discount = st.sidebar.slider(
    "Diskon Oligopoli dari Monopoli (%)", 5.0, 50.0, 20.0, step=5.0
)
# ───────────── Tambahkan Skenario ─────────────
st.sidebar.markdown("### 🎯 Pilih Skenario")
skenario = st.sidebar.selectbox(
    "Skenario Simulasi",
    ["Pesimis", "Moderat", "Optimis"]
)

# Set parameter sesuai skenario
if skenario == "Pesimis":
    demand_growth = 1.0          # % pertumbuhan permintaan
    tax_rate = 20.0              # % pajak/royalti
    monopoly_margin = 20.0       # % margin monopoli
    oligopoly_discount = 30.0
elif skenario == "Moderat":
    demand_growth = 3.0
    tax_rate = 13.5
    monopoly_margin = 40.0
    oligopoly_discount = 20.0
else:  # Optimis
    demand_growth = 5.0
    tax_rate = 10.0
    monopoly_margin = 60.0
    oligopoly_discount = 15.0

# ───────────── Tambahan Parameter Investasi ─────────────
st.sidebar.markdown("---")
st.sidebar.markdown("### ⚒️ Parameter Investasi Tambahan")
share_investor = st.sidebar.slider("Share Investor (%)", 0, 100, 10)
biaya_operasional = st.sidebar.slider("Biaya Operasional (%)", 0, 100, 30)
hari_operasional = st.sidebar.number_input("Hari Operasional", value=365)

st.sidebar.markdown("---")
st.sidebar.caption("Simulator ini bersifat edukatif dan tidak merupakan saran investasi.")
st.sidebar.markdown("### 📊 Parameter Hotelling")
interest_rate = st.sidebar.slider(
    "Tingkat Bunga Tahunan (%)", 0.0, 15.0, 5.0, step=0.5
)
st.sidebar.markdown("### 🌱 Parameter Green Paradox")
green_paradox_rate = st.sidebar.slider(
    "Kenaikan Harga Tahunan (%)", 0.0, 20.0, 5.0, step=0.5
)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown('<p class="main-header">⛏️ Simulator Ekonomi Batu Bara Indonesia</p>', unsafe_allow_html=True)
st.markdown("**Analisis struktur pasar & proyeksi harga berbasis data historis 2014–2024**")
st.divider()

# ─────────────────────────────────────────────
# 1. DASHBOARD DATA HISTORIS
# ─────────────────────────────────────────────
st.markdown('<p class="section-title">📊 Dashboard Data Historis</p>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Rata-rata Produksi (Juta Ton)", f"{df['Q'].mean():.2f}")
with col2:
    st.metric("Harga Tertinggi (Rp/Ton)", f"{df['P'].max():,.0f}")
with col3:
    avg_bpp = df["BPP_per_ton"].mean()
    st.metric("Rata-rata BPP/Ton", f"Rp {avg_bpp:,.0f}")
with col4:
    avg_mc = df["MC_per_ton"].mean()
    st.metric("Rata-rata MC/Ton", f"Rp {avg_mc:,.0f}")

# ───────────── Hasil Simulasi Investasi Tambahan ─────────────
# Asumsi sederhana: revenue = harga rata-rata * hari_operasional * share_investor (%)
harga_rata2 = df["P"].mean()
revenue = harga_rata2 * hari_operasional * (share_investor / 100)
cashflow_bulanan = (revenue - (revenue * biaya_operasional / 100)) / 12
investasi = harga_rata2 * (share_investor / 100)
break_even = investasi / (revenue - (revenue * biaya_operasional / 100)) * 12 if (revenue - (revenue * biaya_operasional / 100)) > 0 else 0
roi = ((revenue - (revenue * biaya_operasional / 100)) / investasi) * 100 if investasi > 0 else 0

st.markdown("<p class='section-title'>💡 Simulasi Investasi Sederhana</p>", unsafe_allow_html=True)
colA, colB, colC = st.columns(3)
with colA:
    st.metric("Cashflow Bulanan", f"Rp {cashflow_bulanan:,.0f}")
with colB:
    st.metric("Break Even (thn)", f"{break_even:.1f}")
with colC:
    st.metric("ROI (%)", f"{roi:.2f}")

with st.expander("📋 Lihat Tabel Data Historis Lengkap"):
    display_df = df[["Tahun","Q","P","BPP_per_ton","MC_per_ton","Cadangan"]].copy()
    display_df.columns = ["Tahun","Produksi (Juta Ton)","Harga (Rp/Ton)","BPP/Ton (Rp)","MC/Ton (Rp)","Cadangan (Bt)"]
    st.dataframe(display_df.set_index("Tahun").style.format({
        "Produksi (Juta Ton)": "{:.2f}",
        "Harga (Rp/Ton)": "{:,.0f}",
        "BPP/Ton (Rp)": "{:,.0f}",
        "MC/Ton (Rp)": "{:,.0f}",
        "Cadangan (Bt)": "{:.4f}",
    }), use_container_width=True)
# ───────────── Skenario ─────────────
st.markdown(f"### 📝 Narasi Skenario: {skenario}")
if skenario == "Pesimis":
    st.info("""
    - Permintaan rendah, pajak tinggi, margin monopoli kecil → harga cenderung stagnan.
    - ROI dan cashflow lebih rendah, break-even lebih lama.
    - Cadangan habis lebih lambat, potensi profit kecil.
    """)
elif skenario == "Moderat":
    st.success("""
    - Permintaan sedang, pajak dan margin normal.
    - ROI dan cashflow stabil, cadangan habis sesuai proyeksi.
    - Kondisi paling realistis untuk perencanaan.
    """)
else:  # Optimis
    st.warning("""
    - Permintaan tinggi, pajak rendah, margin monopoli besar.
    - ROI dan cashflow tinggi, break-even cepat.
    - Risiko eksploitasi cadangan meningkat → mitigasi keberlanjutan diperlukan.
    """)

last = df.iloc[-1]
base_year = int(last["Tahun"])
base_q = last["Q"]
base_bpp = last["BPP_per_ton"]
base_mc = last["MC_per_ton"]
base_cad = last["Cadangan"]

# Sidebar slider untuk tahun proyeksi (baru setelah base_year ada)
tahun_proyeksi = st.sidebar.slider("Tahun Proyeksi ke Depan", 1, 10, 5)

# Buat daftar tahun proyeksi
proj_years = list(range(base_year + 1, base_year + tahun_proyeksi + 1))
# ─────────────────────────────────────────────
# 2. LOGIKA SIMULASI
# ─────────────────────────────────────────────
def simulate(years, base_bpp, base_mc, base_q, base_cad,
             demand_growth_pct, tax_pct, mono_margin_pct, oligo_discount_pct,
             interest_rate):
    rows = []
    bpp = base_bpp
    mc  = base_mc
    q   = base_q
    cad = base_cad
    for i, yr in enumerate(years):
        cad *= 0.99
        scarcity_factor = 1 + (0.01 / max(cad, 0.001))
        mc *= 1.02 * scarcity_factor
        bpp *= 1.025
        q_demand = q * ((1 + demand_growth_pct / 100) ** (i + 1))
        p_competition = mc
        p_monopoly = bpp * (1 + mono_margin_pct / 100)
        p_oligopoly = p_monopoly * (1 - oligo_discount_pct / 100)
        tax = tax_pct / 100
        rows.append({
            "Tahun": yr,
            "Q_Demand (Juta Ton)": round(q_demand, 2),
            "MC/Ton (Rp)": mc,
            "BPP/Ton (Rp)": bpp,
            "Cadangan (Bt)": round(cad,4),
            "Harga Persaingan (Rp/Ton)": p_competition * (1+tax),
            "Harga Monopoli (Rp/Ton)": p_monopoly * (1+tax),
            "Harga Oligopoli (Rp/Ton)": p_oligopoly * (1+tax),
            "Harga Hotelling (Rp/Ton)": bpp * ((1 + interest_rate/100) ** (i+1))
        })
    return pd.DataFrame(rows)

proj_df = simulate(proj_years, base_bpp, base_mc, base_q, base_cad,
                   demand_growth, tax_rate, monopoly_margin, oligopoly_discount,
                   interest_rate)
def simulate_hotelling(years, base_bpp, interest_rate):
    rows = []
    for i, yr in enumerate(years):
        p_hotelling = base_bpp * ((1 + interest_rate / 100) ** (i + 1))
        rows.append({"Tahun": yr, "Harga Hotelling (Rp/Ton)": p_hotelling})
    return pd.DataFrame(rows)
def simulate_green_paradox(years, base_q, base_bpp, interest_rate, green_rate):
    rows = []
    for i, yr in enumerate(years):
        q_future = base_q * ((1 + green_rate / 100) ** (i + 1))
        p_gp = base_bpp * ((1 + interest_rate / 100) ** (i + 1))
        rows.append({"Tahun": yr, "Produksi (Juta Ton)": round(q_future,2),
                     "Harga GP (Rp/Ton)": round(p_gp,0)})
    return pd.DataFrame(rows)

hotelling_df = simulate_hotelling(proj_years, base_bpp, interest_rate)
gp_df = simulate_green_paradox(proj_years, base_q, base_bpp, interest_rate, green_paradox_rate)
fig_hot, ax_hot = plt.subplots(figsize=(12,5))
ax_hot.plot(hotelling_df["Tahun"], hotelling_df["Harga Hotelling (Rp/Ton)"],
            color="#9c27b0", marker="X", label="Hotelling")
ax_hot.set_xlabel("Tahun")
ax_hot.set_ylabel("Harga (Rp/Ton)")
ax_hot.set_title("Tren Harga Hotelling Batu Bara")
ax_hot.grid(alpha=0.3)
st.pyplot(fig_hot)
fig_gp, ax_gp = plt.subplots(figsize=(12,5))
ax2 = ax_gp.twinx()
ax_gp.plot(gp_df["Tahun"], gp_df["Produksi (Juta Ton)"], color="#43a047", marker="o", label="Produksi GP")
ax_gp.set_ylabel("Produksi (Juta Ton)", color="#43a047")
ax2.plot(gp_df["Tahun"], gp_df["Harga GP (Rp/Ton)"], color="#e53935", marker="^", label="Harga GP")
ax2.set_ylabel("Harga GP (Rp/Ton)", color="#e53935")
lines, labels = ax_gp.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax_gp.legend(lines+lines2, labels+labels2)
st.pyplot(fig_gp)
# ─────────────────────────────────────────────
# 3. VISUALISASI
# ─────────────────────────────────────────────
st.divider()
st.markdown('<p class="section-title">📈 Perbandingan Harga Historis vs Proyeksi</p>', unsafe_allow_html=True)

# ── Grafik Tren Harga ─────────────────────────
fig1, ax1 = plt.subplots(figsize=(12, 5))
ax1.plot(df["Tahun"], df["P"], color="#0f3460", linewidth=2.5,
         marker="o", markersize=5, label="Harga Historis (Aktual)")
ax1.plot(proj_df["Tahun"], proj_df["Harga Persaingan (Rp/Ton)"],
         color="#4caf50", linewidth=2, linestyle="--", marker="s", markersize=4,
         label="Proyeksi: Pasar Persaingan")
ax1.plot(proj_df["Tahun"], proj_df["Harga Monopoli (Rp/Ton)"],
         color="#e53935", linewidth=2, linestyle="--", marker="^", markersize=4,
         label="Proyeksi: Monopoli")
ax1.plot(proj_df["Tahun"], proj_df["Harga Oligopoli (Rp/Ton)"],
         color="#fb8c00", linewidth=2, linestyle="--", marker="D", markersize=4,
         label="Proyeksi: Oligopoli")
ax1.plot(proj_df["Tahun"], proj_df["Harga Hotelling (Rp/Ton)"],
         color="#9c27b0", linewidth=2, linestyle="--", marker="X", markersize=5,
         label="Proyeksi: Hotelling")

ax1.axvline(x=base_year, color="gray", linestyle=":", linewidth=1.2, alpha=0.7)
ax1.text(base_year + 0.1, ax1.get_ylim()[0], "→ Proyeksi", color="gray", fontsize=9)
ax1.set_xlabel("Tahun", fontsize=11)
ax1.set_ylabel("Harga (Rp/Ton)", fontsize=11)
ax1.set_title("Tren Harga Batu Bara: Historis & Proyeksi 3 Mekanisme Pasar", fontsize=13, fontweight="bold")
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"Rp {x:,.0f}"))
ax1.grid(alpha=0.3)
fig1.tight_layout()
st.pyplot(fig1)

# ── Grafik Batang Perbandingan ─────────────────
st.markdown('<p class="section-title">📊 Perbandingan Harga Akhir Proyeksi (Tahun Terakhir)</p>', unsafe_allow_html=True)
last_proj = proj_df.iloc[-1]
mekanisme = ["Persaingan", "Oligopoli", "Monopoli","Hotelling"]
harga_vals = [
    last_proj["Harga Persaingan (Rp/Ton)"],
    last_proj["Harga Oligopoli (Rp/Ton)"],
    last_proj["Harga Monopoli (Rp/Ton)"],
    last_proj["Harga Hotelling (Rp/Ton)"]  # ← tambahkan ini
]
colors_bar = ["#4caf50", "#fb8c00", "#e53935", "#9c27b0"]  # warna baru untuk Hotelling

fig2, ax2 = plt.subplots(figsize=(8, 5))
bars = ax2.bar(mekanisme, harga_vals, color=colors_bar, edgecolor="#4caf50", width=0.5)
for bar, val in zip(bars, harga_vals):
    ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() * 1.01,
             f"Rp {val:,.0f}", ha="center", va="bottom", fontsize=9, fontweight="bold")
ax2.set_ylabel("Harga (Rp/Ton)", fontsize=11)
ax2.set_title(f"Proyeksi Harga Batu Bara – Tahun {int(last_proj['Tahun'])}\n(setelah pajak/royalti {tax_rate:.1f}%)",
              fontsize=12, fontweight="bold")
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"Rp {x:,.0f}"))
ax2.grid(axis="y", alpha=0.3)
fig2.tight_layout()
st.pyplot(fig2)
st.divider()
st.markdown('<p class="section-title">📈 Proyeksi Harga Hotelling</p>', unsafe_allow_html=True)
st.markdown("Harga Hotelling menunjukkan kenaikan harga batu bara karena kelangkaan dan opportunity cost.")
fig_hot, ax_hot = plt.subplots(figsize=(12, 5))
ax_hot.plot(hotelling_df["Tahun"], hotelling_df["Harga Hotelling (Rp/Ton)"],
            color="#9c27b0", linewidth=2.5, marker="X", markersize=6,
            label="Proyeksi: Hotelling")
ax_hot.set_xlabel("Tahun", fontsize=11)
ax_hot.set_ylabel("Harga Hotelling (Rp/Ton)", fontsize=11)
ax_hot.set_title("Tren Harga Hotelling Batu Bara", fontsize=13, fontweight="bold")
ax_hot.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"Rp {x:,.0f}"))
ax_hot.grid(alpha=0.3)
ax_hot.legend()
fig_hot.tight_layout()
st.pyplot(fig_hot)
st.markdown("### 📋 Tabel Proyeksi Hotelling")
st.dataframe(
    hotelling_df.set_index("Tahun").style.format({
        "Harga Hotelling (Rp/Ton)": "{:,.0f}"
    }),
    use_container_width=True
)
st.markdown("### 💡 Narasi Hotelling Price")
st.info("""
- Hotelling menunjukkan kenaikan harga batu bara karena kelangkaan dan opportunity cost.
- Harga ini meningkat setiap tahun sesuai tingkat bunga (`interest_rate`) yang dipilih.
- Berguna untuk memahami efek green paradox: eksploitasi cadangan bisa dipercepat saat harga Hotelling tinggi.
""")
# Sub-bab Green Paradox
st.divider()
st.markdown('<p class="section-title">📈 Simulasi Green Paradox</p>', unsafe_allow_html=True)
st.markdown("Green Paradox menunjukkan percepatan produksi akibat ekspektasi harga masa depan yang naik.")

# Line Chart
fig_gp, ax_gp = plt.subplots(figsize=(12,5))
ax2 = ax_gp.twinx()

# Plot produksi di ax_gp
ax_gp.plot(gp_df["Tahun"], gp_df["Produksi (Juta Ton)"], color="#43a047", marker="o", label="Produksi GP (Juta Ton)")
ax_gp.set_ylabel("Produksi (Juta Ton)", color="#43a047")
ax_gp.tick_params(axis='y', labelcolor="#43a047")

# Plot harga di ax2
ax2.plot(gp_df["Tahun"], gp_df["Harga GP (Rp/Ton)"], color="#e53935", marker="^", label="Harga GP (Rp/Ton)")
ax2.set_ylabel("Harga GP (Rp/Ton)", color="#e53935")
ax2.tick_params(axis='y', labelcolor="#e53935")

# Title & grid
ax_gp.set_title("Tren Produksi & Harga Green Paradox")
ax_gp.grid(alpha=0.3)

# Legend gabungan
lines, labels = ax_gp.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax_gp.legend(lines + lines2, labels + labels2, loc="upper left")

fig_gp.tight_layout()
st.pyplot(fig_gp)

# Narasi GP
st.markdown("### 💡 Narasi Green Paradox")
st.info("""
- Green Paradox menunjukkan percepatan produksi batu bara karena ekspektasi harga masa depan meningkat.
- Produksi meningkat tiap tahun sesuai `green_paradox_rate`.
- Berguna untuk memahami tekanan cadangan dan efek kebijakan energi hijau.
""")

# ─────────────────────────────────────────────
# 4. TABEL PROYEKSI
# ─────────────────────────────────────────────
st.markdown('<p class="section-title">🗓️ Tabel Proyeksi Detail</p>', unsafe_allow_html=True)
st.dataframe(
    proj_df.set_index("Tahun").style.format({
        "Q_Demand (Juta Ton)": "{:.2f}",
        "MC/Ton (Rp)": "{:,.0f}",
        "BPP/Ton (Rp)": "{:,.0f}",
        "Cadangan (Bt)": "{:.4f}",
        "Harga Persaingan (Rp/Ton)": "{:,.0f}",
        "Harga Monopoli (Rp/Ton)": "{:,.0f}",
        "Harga Oligopoli (Rp/Ton)": "{:,.0f}",
        "Harga Hotelling (Rp/Ton)": "{:,.0f}",  # ← tambahkan ini
    }),
    use_container_width=True
)

# ─────────────────────────────────────────────
# 5. DOWNLOAD
# ─────────────────────────────────────────────
st.divider()
st.markdown('<p class="section-title">⬇️ Export Hasil Proyeksi</p>', unsafe_allow_html=True)
buf = io.BytesIO()
with pd.ExcelWriter(buf, engine="openpyxl") as writer:
    df[["Tahun","Q","P","BPP_per_ton","MC_per_ton","Cadangan"]].to_excel(
        writer, sheet_name="Data Historis", index=False)
    proj_df.to_excel(writer, sheet_name="Proyeksi Simulasi", index=False)
buf.seek(0)
st.download_button(
    label="📥 Download Excel (Historis + Proyeksi)",
    data=buf,
    file_name="simulasi_batu_bara.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

# ─────────────────────────────────────────────
# PENJELASAN METODOLOGI
# ─────────────────────────────────────────────
with st.expander("ℹ️ Metodologi & Penjelasan Model"):
    st.markdown("""
**Sumber Data:** Data historis produksi batu bara Indonesia 2014–2024 (BPP & MC dihitung per ton dari data agregat).

**Tiga Mekanisme Pasar:**
| Mekanisme | Formula Harga Dasar | Karakteristik |
|---|---|---|
| **Persaingan** | ≈ MC/ton | Efisiensi maksimal, keuntungan normal |
| **Monopoli** | BPP × (1 + margin%) | Satu pemain dominan, profit maksimum |
| **Oligopoli** | Monopoli × (1 − diskon%) | Kinked demand: pemain besar saling mengikuti |

**Faktor Penyesuaian:**
- **Kelangkaan Cadangan:** MC naik seiring turunnya cadangan (asumsi -1%/tahun).
- **Pajak/Royalti:** Ditambahkan ke harga akhir semua mekanisme.
- **Pertumbuhan Permintaan:** Mempengaruhi volume Q proyeksi (tidak langsung mengubah harga dalam model ini).

> ⚠️ Model ini disederhanakan untuk keperluan edukasi. Harga aktual dipengaruhi banyak faktor eksternal lain (kurs, kebijakan pemerintah, harga energi global, dll.)
""")