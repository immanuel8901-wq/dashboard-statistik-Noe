"""Dashboard Statistik Deskriptif - Streamlit.
Jalankan:  streamlit run streamlit_app.py
"""
import pandas as pd
import streamlit as st
from app import compute, insights  # pakai ulang logika dari versi Flask

st.set_page_config(page_title="Statistik Deskriptif", layout="wide")
st.title("Dashboard Statistik Deskriptif")
st.caption("Data nilai 10 kelompok × 10 orang")


@st.cache_data
def get_rows():
    return compute()


rows = get_rows()
info = insights(rows)
k = info["kpi"]

# --- KPI ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("Jumlah Kelompok", k["jumlah_kelompok"])
c2.metric("Rata-rata Keseluruhan", f"{k['mean_total']:.2f}", f"SD {k['sd_total']:.2f}", delta_color="off")
c3.metric("SD Terbesar", f"{k['sd_terbesar']['nilai']:.2f}", k["sd_terbesar"]["kelompok"], delta_color="off")
c4.metric("SD Terkecil", f"{k['sd_terkecil']['nilai']:.2f}", k["sd_terkecil"]["kelompok"], delta_color="off")

# --- Tabel ---
df = pd.DataFrame(rows).drop(columns=["values"]).set_index("kelompok")
st.subheader("Tabel Statistik Deskriptif")
st.dataframe(df.style.format({"mean": "{:.1f}", "median": "{:.1f}", "q1": "{:.2f}", "q3": "{:.2f}",
                              "sd": "{:.2f}", "varians": "{:.2f}", "cv": "{:.1f}"}),
             width="stretch")

# --- Grafik ---
left, right = st.columns(2)
with left:
    st.subheader("Rata-rata per Kelompok")
    st.bar_chart(df["mean"])
with right:
    st.subheader("Standar Deviasi per Kelompok")
    st.bar_chart(df["sd"])

# --- Distribusi per kelompok ---
st.subheader("Distribusi Nilai per Kelompok")
nama = st.selectbox("Pilih kelompok", df.index)
r = next(x for x in rows if x["kelompok"] == nama)
m1, m2, m3, m4 = st.columns(4)
m1.metric("Mean", f"{r['mean']:.1f}")
m2.metric("Median", f"{r['median']:.1f}")
m3.metric("Modus", r["modus"])
m4.metric("SD", f"{r['sd']:.2f}")
counts = pd.Series(r["values"]).value_counts().reindex(range(1, 11), fill_value=0)
st.bar_chart(counts)

# --- Insight ---
a, b = st.columns(2)
with a:
    st.subheader("Temuan")
    for t in info["temuan"]:
        st.markdown(f"- {t}")
with b:
    st.subheader("Keputusan yang Bisa Diambil")
    for t in info["keputusan"]:
        st.markdown(f"- {t}")
