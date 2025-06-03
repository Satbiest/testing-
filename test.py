import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity

# --- Load data ---
@st.cache_data
def load_data():
    df = pd.read_csv('data.csv')
    # Pastikan kolom tahun_berdiri berupa int
    df['tahun_berdiri'] = pd.to_numeric(df['tahun_berdiri'], errors='coerce').fillna(0).astype(int)
    return df

df = load_data()

# --- Input User ---
st.title("UMKM Optimasi & Rekomendasi")

nama_usaha_list = df['nama_usaha'].dropna().unique()
nama_usaha_input = st.selectbox("Cari Nama Usaha", nama_usaha_list)

aset_input = st.number_input("Masukkan Nilai Aset (Rp)", min_value=0, step=1000000)
kapasitas_input = st.number_input("Masukkan Kapasitas Produksi", min_value=0, step=1)

# --- Proses content-based filtering ---
if st.button("Proses Rekomendasi"):
    if nama_usaha_input not in df['nama_usaha'].values:
        st.error("Nama usaha tidak ditemukan di database.")
    else:
        usaha_user = df[df['nama_usaha'] == nama_usaha_input].iloc[0]

        fitur_categorical = ['jenis_usaha', 'marketplace', 'status_legalitas']
        fitur_numerical = ['aset', 'kapasitas_produksi', 'tahun_berdiri']

        # Encoding categorical
        encoder = OneHotEncoder(handle_unknown='ignore')
        fitur_cat_encoded = encoder.fit_transform(df[fitur_categorical])

        # Normalisasi numerical
        scaler = MinMaxScaler()
        fitur_num_scaled = scaler.fit_transform(df[fitur_numerical])

        # Gabungkan fitur
        fitur_all = np.hstack([fitur_cat_encoded.toarray(), fitur_num_scaled])

        # Vektor input user
        input_cat = encoder.transform([usaha_user[fitur_categorical]])
        input_num = scaler.transform([[aset_input, kapasitas_input, usaha_user['tahun_berdiri']]])
        input_vec = np.hstack([input_cat.toarray(), input_num])

        # Hitung similarity
        similarities = cosine_similarity(input_vec, fitur_all).flatten()

        # Ambil top 5 usaha mirip (kecuali usaha user sendiri)
        top_indices = similarities.argsort()[-6:][::-1]  # 6 karena satu adalah usaha user
        top_indices = top_indices[top_indices != usaha_user.name][:5]  # exclude self

        top_usaha = df.iloc[top_indices]

        # Rata-rata usaha mirip
        rata_rata_omset = top_usaha['omset'].mean()
        rata_rata_laba = top_usaha['laba'].mean()
        rata_rata_tenaga_perempuan = top_usaha['tenaga_kerja_perempuan'].mean()
        rata_rata_tenaga_laki = top_usaha['tenaga_kerja_laki_laki'].mean()
        rata_rata_biaya_karyawan = top_usaha['biaya_karyawan'].mean()
        rata_rata_pelanggan = top_usaha['jumlah_pelanggan'].mean()

        # Output detail usaha user
        st.subheader("Informasi Usaha Anda")
        st.write(f"**Nama Usaha:** {usaha_user['nama_usaha']}")
        st.write(f"**Jenis Usaha:** {usaha_user['jenis_usaha']}")
        st.write(f"**Tahun Berdiri:** {usaha_user['tahun_berdiri']}")
        st.write(f"**Status Legalitas:** {usaha_user['status_legalitas']}")
        st.write(f"**Marketplace Saat Ini:** {usaha_user['marketplace']}")
        st.write(f"**Omset Saat Ini:** Rp {usaha_user['omset']:,.0f}")
        st.write(f"**Laba Saat Ini:** Rp {usaha_user['laba']:,.0f}")
        st.write(f"**Tenaga Kerja Perempuan:** {usaha_user['tenaga_kerja_perempuan']}")
        st.write(f"**Tenaga Kerja Laki-laki:** {usaha_user['tenaga_kerja_laki_laki']}")
        st.write(f"**Biaya Karyawan Saat Ini:** Rp {usaha_user['biaya_karyawan']:,.0f}")

        # Rekomendasi optimasi berdasarkan usaha mirip
        st.subheader("💰 Rekomendasi Optimalisasi Omset & Laba")
        st.write(f"Potensi Omset Optimal: Rp {rata_rata_omset:,.0f}")
        st.write(f"Potensi Laba Optimal: Rp {rata_rata_laba:,.0f}")

        # Efisiensi tenaga kerja
        st.subheader("👥 Rekomendasi Efisiensi SDM & Biaya")
        st.write(f"Rata-rata Tenaga Kerja Perempuan pada usaha mirip: {rata_rata_tenaga_perempuan:.1f}")
        st.write(f"Rata-rata Tenaga Kerja Laki-laki pada usaha mirip: {rata_rata_tenaga_laki:.1f}")
        st.write(f"Rata-rata Biaya Karyawan pada usaha mirip: Rp {rata_rata_biaya_karyawan:,.0f}")

        # Estimasi penghematan biaya jika disesuaikan dengan rata-rata
        biaya_karyawan_sekarang = usaha_user['biaya_karyawan']
        penghematan = biaya_karyawan_sekarang - rata_rata_biaya_karyawan
        if penghematan > 0:
            st.write(f"💡 Potensi Penghematan Biaya Karyawan: Rp {penghematan:,.0f}")
        else:
            st.write("💡 Biaya karyawan Anda sudah efisien dibanding usaha sejenis.")

        # Estimasi pelanggan untuk optimasi omset
        st.write(f"Estimasi Target Pelanggan: {rata_rata_pelanggan:.0f}")

        # Analisis kompetitor sejenis
        st.subheader("📊 Analisis Kompetitor Sejenis")
        usaha_sejenis = df[df['jenis_usaha'] == usaha_user['jenis_usaha']]
        st.write(f"Jumlah usaha sejenis: {len(usaha_sejenis)}")
        st.write(f"Rata-rata aset: Rp {usaha_sejenis['aset'].mean():,.0f}")
        st.write(f"Rata-rata laba: Rp {usaha_sejenis['laba'].mean():,.0f}")
        st.write(f"Rata-rata pelanggan: {usaha_sejenis['jumlah_pelanggan'].mean():,.0f}")

        legalitas_terdaftar = usaha_sejenis[usaha_sejenis['status_legalitas'] != 'Belum Terdaftar']
        if len(legalitas_terdaftar) > 0:
            laba_terdaftar = legalitas_terdaftar['laba'].mean()
            laba_belum = usaha_sejenis[usaha_sejenis['status_legalitas'] == 'Belum Terdaftar']['laba'].mean()
            peningkatan_persen = ((laba_terdaftar - laba_belum) / abs(laba_belum)) * 100 if laba_belum != 0 else 0
            st.write(f"Usaha terdaftar cenderung memiliki laba {peningkatan_persen:.1f}% lebih tinggi.")

        # Tampilkan usaha mirip sebagai referensi
        st.subheader("Usaha Mirip (Referensi)")
        st.dataframe(top_usaha[['nama_usaha', 'jenis_usaha', 'aset', 'kapasitas_produksi', 'omset', 'laba']])

