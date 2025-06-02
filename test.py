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

st.title("📊 Real-Time Streaming (Loop from Beginning)")

# Inisialisasi state
if "i" not in st.session_state:
    st.session_state.i = 0
if "streamed_data" not in st.session_state:
    st.session_state.streamed_data = pd.DataFrame(columns=df.columns)

# Ambil data berdasarkan index saat ini
current_index = st.session_state.i % len(df)
new_row = df.iloc[[current_index]]

# Tambahkan baris ke streamed_data
st.session_state.streamed_data = pd.concat(
    [st.session_state.streamed_data, new_row],
    ignore_index=True
)

# Ubah ke format long
long_df = pd.melt(
    st.session_state.streamed_data,
    id_vars=['UNIQUE ID'],
    value_vars=[
        'Mathematics.Linear Algebra',
        'Mathematics.Differential Equations',
        'Mathematics.Optimization Technique'
    ],
    var_name='Mathematics Category',
    value_name='Score'
)

# Hitung rata-rata
avg_df = long_df.groupby(['Mathematics Category', 'UNIQUE ID'])['Score'].mean().reset_index()

# Buat stacked bar chart
chart = alt.Chart(avg_df).mark_bar().encode(
    x=alt.X('Mathematics Category:N'),
    y=alt.Y('Score:Q', title='Average Score'),
    color='UNIQUE ID:N',
    tooltip=['UNIQUE ID', 'Score']
).properties(
    width=700,
    height=400
)

# Tampilkan chart
st.altair_chart(chart, use_container_width=True)

# Tambah iterasi dan delay, lalu rerun
st.session_state.i += 1
time.sleep(1)
st.experimental_rerun()
