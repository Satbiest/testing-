import streamlit as st
import pandas as pd
import time
import altair as alt

# Data simulasi
df = pd.DataFrame({
    'UNIQUE ID': ['7b6d04c9', '1dbecdbe', '46fd6e1c', 'cdb6bf28'],
    'Role': ['Data Analyst', 'Data Scientist', 'Data Analyst', 'AI Engineer'],
    'Mathematics.Linear Algebra': [2, 4, 2, 5],
    'Mathematics.Differential Equations': [2, 3, 2, 5],
    'Mathematics.Optimization Technique': [3, 3, 1, 5]
})

st.title("Simulasi Real-time Stacked Bar Chart: Assessment Score")

# Placeholder untuk grafik
chart_placeholder = st.empty()

# Data akumulasi (buat DataFrame kosong untuk ditambahkan tiap iterasi)
streamed_data = pd.DataFrame()

# Simulasi stream data masuk
for i in range(len(df)):
    # Tambahkan baris baru ke data akumulasi
    streamed_data = pd.concat([streamed_data, df.iloc[[i]]], ignore_index=True)

    # Ubah ke format long-form untuk stacked bar
    long_df = pd.melt(
        streamed_data,
        id_vars=['UNIQUE ID', 'Role'],
        value_vars=[
            'Mathematics.Linear Algebra',
            'Mathematics.Differential Equations',
            'Mathematics.Optimization Technique'
        ],
        var_name='Category',
        value_name='Score'
    )

    # Bikin stacked bar chart dengan Altair
    chart = alt.Chart(long_df).mark_bar().encode(
        x=alt.X('UNIQUE ID:N', title="User"),
        y=alt.Y('sum(Score):Q', title='Total Score'),
        color=alt.Color('Category:N', title='Category'),
        tooltip=['Role', 'Category', 'Score']
    ).properties(
        width=700,
        height=400
    )

    # Tampilkan chart
    chart_placeholder.altair_chart(chart, use_container_width=True)

    # Delay 1 detik
    time.sleep(1)


