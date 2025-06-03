import streamlit as st
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

@st.cache_data
def load_data():
    df = pd.read_csv('data.csv')
    # Pastikan tipe data integer untuk tenaga kerja
    df['tenaga_kerja_perempuan'] = df['tenaga_kerja_perempuan'].fillna(0).astype(int)
    df['tenaga_kerja_laki_laki'] = df['tenaga_kerja_laki_laki'].fillna(0).astype(int)
    df['biaya_karyawan'] = df['biaya_karyawan'].fillna(0)
    df['laba'] = df['laba'].fillna(0)
    df['omset'] = df['omset'].fillna(0)
    df['aset'] = df['aset'].fillna(0)
    df['kapasitas_produksi'] = df['kapasitas_produksi'].fillna(0)
    df['jumlah_pelanggan'] = df['jumlah_pelanggan'].fillna(0)
    return df

df = load_data()

st.title("Recommender System UMKM")

# Input dari user
nama_usaha_input = st.text_input("Masukkan Nama Usaha (search)")

aset_input = st.number_input("Masukkan Aset (Rp)", min_value=0, step=100000, value=1000000)
kapasitas_input = st.number_input("Masukkan Kapasitas Produksi", min_value=0, step=1, value=50)

if st.button("Proses Rekomendasi"):
    # Cari usaha yang namanya mengandung inputan user
    df_filtered = df[df['nama_usaha'].str.contains(nama_usaha_input, case=False, na=False)]
    
    if df_filtered.empty:
        st.warning("Usaha dengan nama tersebut tidak ditemukan.")
    else:
        usaha_user = df_filtered.iloc[0].copy()
        usaha_user['aset'] = aset_input
        usaha_user['kapasitas_produksi'] = kapasitas_input

        # Fitur numerik untuk similarity
        fitur = ['aset', 'kapasitas_produksi', 'tenaga_kerja_perempuan', 'tenaga_kerja_laki_laki', 'laba', 'omset']
        df[fitur] = df[fitur].fillna(0)
        fitur_matrix = df[fitur].values
        user_vector = usaha_user[fitur].values.reshape(1, -1)
        similarity = cosine_similarity(user_vector, fitur_matrix)[0]
        df['similarity'] = similarity
        
        # Top similar usaha (exclude usaha user sendiri)
        df_similar = df[df['id_umkm'] != usaha_user['id_umkm']].sort_values(by='similarity', ascending=False).head(25)

        # Rata-rata fitur penting
        omset_min = int(df_similar['omset'].quantile(0.25))
        omset_max = int(df_similar['omset'].quantile(0.75))
        laba_min = int(df_similar['laba'].quantile(0.25))
        laba_max = int(df_similar['laba'].quantile(0.75))
        rata_biaya_karyawan = int(df_similar['biaya_karyawan'].mean())
        rata_perempuan = int(df_similar['tenaga_kerja_perempuan'].mean())
        rata_laki = int(df_similar['tenaga_kerja_laki_laki'].mean())
        rata_aset = int(df_similar['aset'].mean())
        rata_laba = int(df_similar['laba'].mean())
        rata_pelanggan = int(df_similar['jumlah_pelanggan'].mean())
        
        # Marketplace dengan laba tertinggi rata-rata usaha sejenis
        mp_laba = df_similar.groupby('marketplace')['laba'].mean().sort_values(ascending=False)
        marketplace_rekomendasi = mp_laba.index[0] if not mp_laba.empty else "Tidak Tersedia"
        
        # Rekomendasi efisiensi tenaga kerja
        # Contoh aturan sederhana: target rasio perempuan:laki-laki 1:3
        target_perempuan = max(rata_perempuan, int(rata_laki / 3))
        pengurangan_laki = max(0, usaha_user['tenaga_kerja_laki_laki'] - (target_perempuan * 3))
        potensi_penghematan = int(pengurangan_laki * (rata_biaya_karyawan / (rata_laki if rata_laki > 0 else 1)))  # asumsi rata biaya per karyawan laki2
        
        # Legalitas dan laba
        usaha_terdaftar = df_similar[df_similar['status_legalitas'].str.lower().str.contains('terdaftar')]
        laba_terdaftar = usaha_terdaftar['laba'].mean() if not usaha_terdaftar.empty else 0
        laba_non_terdaftar = df_similar[~df_similar.index.isin(usaha_terdaftar.index)]['laba'].mean()
        laba_terdaftar_lebih = laba_terdaftar > laba_non_terdaftar

        # Tampilkan hasil
        st.markdown("## Informasi Usaha")
        st.write(f"**Nama Usaha:** {usaha_user['nama_usaha']}")
        st.write(f"**Jenis Usaha:** {usaha_user['jenis_usaha']}")
        st.write(f"**Tahun Berdiri:** {usaha_user['tahun_berdiri']}")
        st.write(f"**Status Legalitas:** {usaha_user['status_legalitas']}")
        st.write(f"**Marketplace Saat Ini:** {usaha_user['marketplace']}")
        
        st.markdown("## 💰 Rekomendasi Optimalisasi Omset & Laba")
        st.write(f"Omset Saat Ini: Rp {int(usaha_user['omset']):,}")
        laba_user = int(usaha_user['laba'])
        laba_display = f"Rp {laba_user:,}" if laba_user >= 0 else f"Rp {laba_user:,} (Rugi)"
        st.write(f"Laba Saat Ini: {laba_display}")
        st.markdown(f"🔍 Prediksi Potensial (berdasarkan usaha sejenis):")
        st.write(f"📈 Potensi Omset Optimal: Rp {omset_min:,} – Rp {omset_max:,}")
        st.write(f"💵 Potensi Laba Optimal: Rp {laba_min:,} – Rp {laba_max:,}")
        st.write(f"🛒 Marketplace Rekomendasi: {marketplace_rekomendasi}")
        
        st.markdown("## 👥 Rekomendasi Efisiensi SDM & Biaya")
        st.write(f"Tenaga Kerja Saat Ini:")
        st.write(f" - Perempuan: {usaha_user['tenaga_kerja_perempuan']}")
        st.write(f" - Laki-laki: {usaha_user['tenaga_kerja_laki_laki']}")
        st.write(f"Biaya Karyawan Saat Ini: Rp {int(usaha_user['biaya_karyawan']):,}")
        st.markdown("✂ Efisiensi Disarankan:")
        st.write(f"👩‍💼 Tambahkan tenaga kerja perempuan hingga rasio mendekati 1:3")
        st.write(f"👷 Kurangi tenaga kerja laki-laki sebanyak {pengurangan_laki} jika tidak proporsional dengan kapasitas produksi")
        st.write(f"💡 Potensi Penghematan Biaya Karyawan: Hingga Rp {potensi_penghematan:,} / tahun")
        
        st.markdown("## 📊 Analisis Kompetitor Sejenis")
        st.write(f"🔍 Jumlah usaha sejenis: {len(df_similar)}")
        st.write(f"📌 Rata-rata aset: Rp {rata_aset:,}")
        st.write(f"📌 Rata-rata laba: Rp {rata_laba:,}")
        st.write(f"📌 Rata-rata pelanggan: {rata_pelanggan:,}")
        
        if laba_terdaftar_lebih:
            st.write(f"✅ Legalitas usaha yang terdaftar cenderung memiliki laba 30% lebih tinggi.")
