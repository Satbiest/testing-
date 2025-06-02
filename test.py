import streamlit as st
import pandas as pd
import altair as alt
import time

# Data awal
df = pd.DataFrame({
    'UNIQUE ID': ['7b6d04c9', '1dbecdbe', '46fd6e1c', 'cdb6bf28'],
    'Role': ['Data Analyst', 'Data Scientist', 'Data Analyst', 'AI Engineer'],
    'Mathematics.Linear Algebra': [2, 4, 2, 5],
    'Mathematics.Differential Equations': [2, 3, 2, 5],
    'Mathematics.Optimization Technique': [3, 3, 1, 5]
})

st.title("🔄 Infinite Real-Time Streaming: Stacked Bar of Mathematics Score")

# Placeholder chart
chart_placeholder = st.empty()

# Data yang akan bertambah terus
streamed_data = pd.DataFrame()

# Infinite loop
i = 0
while True:
    # Ambil baris berdasarkan urutan berulang
    new_row = df.iloc[[i % len(df)]]
    
    # Tambahkan ke data stream
    streamed_data = pd.concat([streamed_data, new_row], ignore_index=True)

    # Ubah ke long format untuk Altair
    long_df = pd.melt(
        streamed_data,
        id_vars=['UNIQUE ID'],
        value_vars=[
            'Mathematics.Linear Algebra',
            'Mathematics.Differential Equations',
            'Mathematics.Optimization Technique'
        ],
        var_name='Mathematics Category',
        value_name='Score'
    )

    # Hitung rata-rata skor per kategori per user
    avg_df = long_df.groupby(['Mathematics Category', 'UNIQUE ID'])['Score'].mean().reset_index()

    # Buat stacked bar chart
    chart = alt.Chart(avg_df).mark_bar().encode(
        x=alt.X('Mathematics Category:N', title='Mathematics Category'),
        y=alt.Y('mean(Score):Q', title='Average Score'),
        color=alt.Color('UNIQUE ID:N', title='User'),
        tooltip=['UNIQUE ID', 'Score']
    ).properties(
        width=700,
        height=400
    )

    # Tampilkan chart
    chart_placeholder.altair_chart(chart, use_container_width=True)

    # Jeda 1 detik
    time.sleep(1)
    
    # Lanjut ke iterasi berikutnya
    i += 1
