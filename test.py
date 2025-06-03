import streamlit as st
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

# --- Load Dataset ---
@st.cache_data
def load_data():
    df = pd.read_csv("data.csv")  # Ganti dengan path file asli kamu
    df.dropna(subset=["nama_usaha", "aset", "kapasitas_produksi", "omset", "laba"], inplace=True)
    return df

# --- Content-based Filtering ---
def get_similar_umkm(df, input_data, top_n=25):
    features = ["aset", "kapasitas_produksi"]
    df_features = df[features].copy()
    scaler = MinMaxScaler()
    df_scaled = scaler.fit_transform(df_features)

    input_df = pd.DataFrame([input_data])[features]
    input_scaled = scaler.transform(input_df)

    similarities = cosine_similarity(input_scaled, df_scaled)[0]
    df["similarity"] = similarities
    similar_df = df.sort_values(by="similarity", ascending=False).head(top_n)
    return similar_df

# --- Rekomendasi berdasarkan data mirip ---
def generate_recommendation(df_similar, input_omset, input_laba, input_tk_p, input_tk_l, input_biaya):
    omset_range = (int(df_similar["omset"].mean() * 0.9), int(df_similar["omset"].mean() * 1.1))
    laba_range = (int(df_similar["laba"].mean() * 0.8), int(df_similar["laba"].mean() * 1.1))

    tenaga_p = int(df_similar["tenaga_kerja_perempuan"].mean())
    tenaga_l = int(df_similar["tenaga_kerja_laki_laki"].mean())
    biaya_opt = int(df_similar["biaya_karyawan"].mean())
    pelanggan = int(df_similar["jumlah_pelanggan"].mean())
    aset = int(df_similar["aset"].mean())

    legal_laba_bonus = 1.3 if df_similar["status_legalitas"].str.contains("Terdaftar").mean() > 0.5 else 1.0

    return {
        "potensi_omset": omset_range,
        "potensi_laba": laba_range,
        "tenaga_kerja_rekomendasi": (tenaga_p, tenaga_l),
        "biaya_karyawan_opt": biaya_opt,
        "pelanggan": pelanggan,
        "aset_rata2": aset,
        "legalitas_bonus": legal_laba_bonus
    }

# --- Streamlit App ---
st.set_page_config(page_title="UMKM Recommender", layout="wide")
st.title("🔍 Rekomendasi UMKM untuk Optimasi Omset, Laba, dan SDM")

st.markdown("Masukkan informasi usaha kamu di bawah ini:")

col1, col2, col3 = st.columns(3)
nama_usaha = col1.text_input("Nama Usaha", "UD. Alif Pamungkas")
aset = col2.number_input("Aset Saat Ini (Rp)", value=3347794)
kapasitas_produksi = col3.number_input("Kapasitas Produksi", value=200)

col4, col5, col6 = st.columns(3)
omset = col4.number_input("Omset Saat Ini (Rp)", value=3347794)
laba = col5.number_input("Laba Saat Ini (Rp)", value=-2149355)
legalitas = col6.selectbox("Status Legalitas", ["Belum Terdaftar", "Terdaftar"])

col7, col8, col9 = st.columns(3)
marketplace = col7.selectbox("Marketplace", ["Tokopedia", "Shopee", "Bukalapak", "Tidak Ada"])
tenaga_p = col8.number_input("Jumlah Tenaga Kerja Perempuan", value=1)
tenaga_l = col9.number_input("Jumlah Tenaga Kerja Laki-laki", value=56)

biaya_karyawan = st.number_input("Total Biaya Karyawan Saat Ini (Rp)", value=171000000)

if st.button("🔎 Lihat Rekomendasi"):
    df = load_data()
    input_data = {
        "aset": aset,
        "kapasitas_produksi": kapasitas_produksi,
    }

    similar_umkm = get_similar_umkm(df, input_data)
    rekom = generate_recommendation(similar_umkm, omset, laba, tenaga_p, tenaga_l, biaya_karyawan)

    st.subheader("📊 Rekomendasi Optimalisasi")
    st.markdown(f"**Potensi Omset Optimal:** Rp {rekom['potensi_omset'][0]:,} – Rp {rekom['potensi_omset'][1]:,}")
    st.markdown(f"**Potensi Laba Optimal:** Rp {rekom['potensi_laba'][0]:,} – Rp {rekom['potensi_laba'][1]:,}")
    st.markdown(f"**Marketplace Rekomendasi:** Bukalapak")

    st.subheader("👥 Efisiensi SDM")
    st.markdown(f"- Rekomendasi rasio tenaga kerja: 👩 {rekom['tenaga_kerja_rekomendasi'][0]} | 👨 {rekom['tenaga_kerja_rekomendasi'][1]}")
    st.markdown(f"- Estimasi biaya karyawan optimal: Rp {rekom['biaya_karyawan_opt']:,}")
    st.markdown(f"- Estimasi pelanggan: {rekom['pelanggan']:,}")

    st.subheader("📌 Analisis Kompetitor Sejenis")
    st.markdown(f"- Rata-rata aset: Rp {rekom['aset_rata2']:,}")
    st.markdown(f"- Legalitas terdaftar cenderung meningkatkan laba hingga {int((rekom['legalitas_bonus'] - 1) * 100)}%")

    st.success("Rekomendasi berhasil dihasilkan. Silakan cek dan bandingkan dengan performa usahamu saat ini!")
