import streamlit as st
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# Load dataset (pastikan file 'data_umkm.csv' ada di folder yang sama)
@st.cache_data
def load_data():
    df = pd.read_csv('data_umkm.csv')
    # Pastikan kolom tenaga kerja dalam bentuk integer
    df['tenaga_kerja_perempuan'] = df['tenaga_kerja_perempuan'].fillna(0).astype(int)
    df['tenaga_kerja_laki_laki'] = df['tenaga_kerja_laki_laki'].fillna(0).astype(int)
    return df

df = load_data()

st.title("Recommender System UMKM (Content-Based Filtering)")

# User input - Nama Usaha dengan search box
nama_usaha_input = st.text_input("Masukkan Nama Usaha (search engine)")

# Input aset dan kapasitas produksi
aset_input = st.number_input("Masukkan Nilai Aset (Rp)", min_value=0, value=1000000, step=100000)
kapasitas_input = st.number_input("Masukkan Kapasitas Produksi", min_value=0, value=100, step=1)

if st.button("Rekomendasi"):
    # Cari usaha berdasarkan nama usaha (case-insensitive substring match)
    df_filtered = df[df['nama_usaha'].str.contains(nama_usaha_input, case=False, na=False)]
    
    if df_filtered.empty:
        st.warning("Usaha dengan nama tersebut tidak ditemukan.")
    else:
        # Ambil usaha pertama yang cocok sebagai usaha user
        usaha_user = df_filtered.iloc[0].copy()
        
        # Update nilai aset dan kapasitas produksi dari input user
        usaha_user['aset'] = aset_input
        usaha_user['kapasitas_produksi'] = kapasitas_input
        
        # Pastikan tenaga kerja dalam bentuk integer
        usaha_user['tenaga_kerja_perempuan'] = int(usaha_user['tenaga_kerja_perempuan'])
        usaha_user['tenaga_kerja_laki_laki'] = int(usaha_user['tenaga_kerja_laki_laki'])
        
        # Pilih fitur numerik untuk similarity
        fitur = ['aset', 'kapasitas_produksi', 'tenaga_kerja_perempuan', 'tenaga_kerja_laki_laki', 'laba', 'omset']
        
        # Handle NaN dengan mengisi nol agar similarity berjalan lancar
        df[fitur] = df[fitur].fillna(0)
        
        # Buat matriks fitur
        fitur_matrix = df[fitur].values
        
        # Vektor usaha user
        user_vector = usaha_user[fitur].values.reshape(1, -1)
        
        # Hitung cosine similarity
        similarity = cosine_similarity(user_vector, fitur_matrix)[0]
        
        # Tambahkan similarity ke dataframe
        df['similarity'] = similarity
        
        # Ambil top 5 usaha mirip (kecuali usaha user sendiri)
        df_similar = df[df['id_umkm'] != usaha_user['id_umkm']].sort_values(by='similarity', ascending=False).head(5)
        
        # Rata-rata untuk fitur yang diinginkan dari usaha mirip
        rata_rata_omset = df_similar['omset'].mean()
        rata_rata_laba = df_similar['laba'].mean()
        rata_rata_tenaga_perempuan = int(round(df_similar['tenaga_kerja_perempuan'].mean()))
        rata_rata_tenaga_laki = int(round(df_similar['tenaga_kerja_laki_laki'].mean()))
        rata_rata_jumlah_pelanggan = df_similar['jumlah_pelanggan'].mean()
        
        # Output hasil
        st.header("Informasi Usaha")
        st.write(f"**Nama Usaha:** {usaha_user['nama_usaha']}")
        st.write(f"**Jenis Usaha:** {usaha_user['jenis_usaha']}")
        st.write(f"**Tahun Berdiri:** {usaha_user['tahun_berdiri']}")
        st.write(f"**Status Legalitas:** {usaha_user['status_legalitas']}")
        st.write(f"**Marketplace Saat Ini:** {usaha_user['marketplace']}")
        
        st.markdown("---")
        st.subheader("💰 Rekomendasi Optimalisasi Omset & Laba")
        st.write(f"Omset Saat Ini: Rp {usaha_user['omset']:,}")
        st.write(f"Laba Saat Ini: Rp {usaha_user['laba']:,}")
        st.write(f"Potensi Omset Optimal (rata-rata usaha sejenis): Rp {int(rata_rata_omset):,}")
        st.write(f"Potensi Laba Optimal (rata-rata usaha sejenis): Rp {int(rata_rata_laba):,}")
        
        st.markdown("---")
        st.subheader("👥 Rekomendasi Efisiensi SDM & Biaya")
        st.write(f"Tenaga Kerja Perempuan Saat Ini: {usaha_user['tenaga_kerja_perempuan']}")
        st.write(f"Tenaga Kerja Laki-laki Saat Ini: {usaha_user['tenaga_kerja_laki_laki']}")
        st.write(f"Rata-rata Tenaga Kerja Perempuan usaha mirip: {rata_rata_tenaga_perempuan}")
        st.write(f"Rata-rata Tenaga Kerja Laki-laki usaha mirip: {rata_rata_tenaga_laki}")
        
        st.markdown("---")
        st.subheader("📊 Analisis Kompetitor Sejenis")
        st.write(f"Jumlah usaha sejenis: {len(df_similar)}")
        st.write(f"Rata-rata aset: Rp {int(df_similar['aset'].mean()):,}")
        st.write(f"Rata-rata laba: Rp {int(df_similar['laba'].mean()):,}")
        st.write(f"Rata-rata pelanggan: {int(df_similar['jumlah_pelanggan'].mean()):,}")
        
        # Contoh insight sederhana
        usaha_terdaftar = df_similar[df_similar['status_legalitas'].str.lower() == 'terdaftar']
        if not usaha_terdaftar.empty:
            rata_laba_terdaftar = usaha_terdaftar['laba'].mean()
            rata_laba_non_terdaftar = df_similar[~df_similar.index.isin(usaha_terdaftar.index)]['laba'].mean()
            if rata_laba_terdaftar > rata_laba_non_terdaftar:
                st.write("✅ Usaha dengan status legalitas terdaftar cenderung memiliki laba lebih tinggi.")
