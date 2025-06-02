import streamlit as st
import pandas as pd
import altair as alt
import time

# Simulasi data
df = pd.DataFrame({
    'UNIQUE ID': ['7b6d04c9', '1dbecdbe', '46fd6e1c', 'cdb6bf28'],
    'Role': ['Data Analyst', 'Data Scientist', 'Data Analyst', 'AI Engineer'],
    'Mathematics.Linear Algebra': [2, 4, 2, 5],
    'Mathematics.Differential Equations': [2, 3, 2, 5],
    'Mathematics.Optimization Technique': [3, 3, 1, 5]
})

st.title("📊 Real-Time Dashboard: Average Score per Mathematics Category")

# Placeholder chart
chart_placeholder = st.empty()

# Data akumulasi
streamed_data = pd.DataFrame()

# Loop streaming per baris
for i in range(len(df)):
    # Tambahkan satu baris baru ke data
    streamed_data = pd.concat([streamed_data, df.iloc[[i]]], ignore_index=True)

    # Transformasi ke long format
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

    # Hitung rata-rata skor per kategori
    avg_df = long_df.groupby(['Mathematics Category', 'UNIQUE ID'])['Score'].mean().reset_index()

    # Buat stacked bar chart: X = Kategori, Y = Rata-rata, Color = UNIQUE ID
    chart = alt.Chart(avg_df).mark_bar().encode(
        x=alt.X('Mathematics Category:N', title='Mathematics Category'),
        y=alt.Y('mean(Score):Q', title='Average Score'),
        color=alt.Color('UNIQUE ID:N', title='User'),
        tooltip=['UNIQUE ID', 'Score']
    ).properties(
        width=700,
        height=400
    )

    # Update chart
    chart_placeholder.altair_chart(chart, use_container_width=True)

    # Delay 1 detik
    time.sleep(1)
