import streamlit as st
import pandas as pd

st.set_page_config(page_title="SEG Grading System", page_icon="🏫")

st.title("🏫 ប្រព័ន្ធគ្រប់គ្រងពិន្ទុសិស្ស - SEG")

# បង្កើត Session State សម្រាប់រក្សាទិន្នន័យ
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=['ID', 'Student Name', 'Level', 'Reading', 'Writing', 'Total'])

# ផ្នែកបញ្ចូលទិន្នន័យ
with st.expander("➕ បញ្ចូលពិន្ទុសិស្សថ្មី", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("ឈ្មោះសិស្ស")
        level = st.selectbox("កម្រិតសិក្សា", ["GEP 7", "GEP 8", "GEP 9", "GEP 10", "GEP 11", "GEP 12"])
    with col2:
        r_score = st.number_input("Reading Score", 0, 100)
        w_score = st.number_input("Writing Score", 0, 100)
    
    if st.button("រក្សាទុកទិន្នន័យ"):
        if name:
            new_id = len(st.session_state.df) + 1
            new_row = {'ID': new_id, 'Student Name': name, 'Level': level, 'Reading': r_score, 'Writing': w_score, 'Total': r_score + w_score}
            st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
            st.success(f"បានបញ្ចូលពិន្ទុឱ្យសិស្ស {name} រួចរាល់!")
        else:
            st.error("សូមបំពេញឈ្មោះសិស្ស!")

# បង្ហាញតារាង
st.subheader("📊 បញ្ជីពិន្ទុសិស្ស")
st.dataframe(st.session_state.df, use_container_width=True)

# ប៊ូតុងបញ្ជា
col_dl, col_clr = st.columns([1, 1])
with col_dl:
    if not st.session_state.df.empty:
        csv = st.session_state.df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 ទាញយកជា Excel (CSV)", csv, "student_scores.csv", "text/csv")

with col_clr:
    if st.button("🗑️ លុបទិន្នន័យទាំងអស់"):
        st.session_state.df = pd.DataFrame(columns=['ID', 'Student Name', 'Level', 'Reading', 'Writing', 'Total'])
        st.rerun()
