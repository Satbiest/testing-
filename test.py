import streamlit as st
import pandas as pd
import altair as alt
import time

# Data awal (static source)
df = pd.DataFrame({
    'UNIQUE ID': ['7b6d04c9', '1dbecdbe', '46fd6e1c', 'cdb6bf28'],
    'Role': ['Data Analyst', 'Data Scientist', 'Data Analyst', 'AI Engineer'],
    'Mathematics.Linear Algebra': [2, 4, 2, 5],
    'Mathematics.Differential Equations': [2, 3, 2, 5],
    'Mathematics.Optimization Technique': [3, 3, 1, 5]
})

st.title("📡 Real-Time Streaming Stacked Bar (No Clicks)")

# Inisialisasi session state
if "i" not in st.session_state:
    st.session_state.i = 0
if "streamed_data" not in st.session_state:
    st.session_state.streamed_data = pd.DataFrame()

# Ambil baris berikutnya berdasarkan index modulo
i = st.session_state.i
new_row = df.iloc[[i % len(df)]]
st.session_state.streamed_data = pd.concat(
    [st.session_state.streamed_data, new_row], ignore_index=True
)
st.session_state.i += 1

# Transformasi untuk chart
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

avg_df = long_df.groupby(['Mathematics Category', 'UNIQUE ID'])['Score'].mean().reset_index()

# Stacked bar chart
chart = alt.Chart(avg_df).mark_bar().encode(
    x=alt.X('Mathematics Category:N', title='Mathematics Category'),
    y=alt.Y('mean(Score):Q', title='Average Score'),
    color=alt.Color('UNIQUE ID:N', title='User'),
    tooltip=['UNIQUE ID', 'Score']
).properties(
    width=700,
    height=400
)

st.altair_chart(chart, use_container_width=True)

# Delay singkat agar bisa terlihat
time.sleep(1)

# Auto rerun (kunci ilusi streaming!)
st.experimental_rerun()
