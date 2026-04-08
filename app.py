import streamlit as st
import pandas as pd
import plotly.express as px

# កំណត់ទម្រង់ទំព័រឱ្យស្អាត
st.set_page_config(page_title="SEG Grading System", page_icon="🏫", layout="wide")

# បន្ថែមស្ទាយបន្តិចបន្តួច
st.markdown("""
    <style>
    .main { background-color: #f4f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #003057; color: white; }
    .stDataFrame { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# បង្កើតកន្លែងរក្សាទុកទិន្នន័យក្នុង Session
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=['Student Name', 'Level', 'Grammar', 'Speaking', 'Total'])

# --- SIDEBAR: បញ្ចូលទិន្នន័យ ---
st.sidebar.image("https://img.icons8.com/fluency/96/school.png", width=80)
st.sidebar.title("Grading Panel")
with st.sidebar.form("grading_form", clear_on_submit=True):
    name = st.text_input("👤 Student Full Name")
    level = st.selectbox("📚 Level", ["GEP 7", "GEP 8", "GEP 9", "GEP 10", "GEP 11", "GEP 12"])
    gram_score = st.number_input("✍️ Grammar Score", 0, 100)
    speak_score = st.number_input("🗣️ Speaking Score", 0, 100)
    
    submitted = st.form_submit_button("Save Score")

if submitted:
    if name:
        new_entry = pd.DataFrame({
            'Student Name': [name],
            'Level': [level],
            'Grammar': [gram_score],
            'Speaking': [speak_score],
            'Total': [gram_score + speak_score]
        })
        st.session_state.db = pd.concat([st.session_state.db, new_entry], ignore_index=True)
        st.sidebar.success(f"Saved: {name}")
    else:
        st.sidebar.error("Please enter name!")

# --- MAIN PAGE: បង្ហាញលទ្ធផល ---
st.title("🏫 SEG Student Management Dashboard")

# បង្ហាញជា Stats ខ្លីៗ
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Students", len(st.session_state.db))
with col2:
    avg_score = st.session_state.db['Total'].mean() if not st.session_state.db.empty else 0
    st.metric("Average Total Score", f"{avg_score:.2f}")
with col3:
    st.metric("School Branch", "Prek Leap")

# តារាងទិន្នន័យ
st.subheader("📊 Class Grade Sheet")
st.dataframe(st.session_state.db, use_container_width=True)

# ក្រាហ្វិកវិភាគ (Analytics)
if not st.session_state.db.empty:
    st.subheader("📈 Performance Analysis")
    fig = px.bar(st.session_state.db, x='Student Name', y='Total', color='Level', 
                 title="Student Total Scores Comparison", barmode='group')
    st.plotly_chart(fig, use_container_width=True)

# ប៊ូតុងទាញយក និង លុប
st.markdown("---")
c1, c2 = st.columns(2)
with c1:
    if not st.session_state.db.empty:
        csv = st.session_state.db.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Export to Excel (CSV)", csv, "seg_grades.csv", "text/csv")
with c2:
    if st.button("🗑️ Reset All Records"):
        st.session_state.db = pd.DataFrame(columns=['Student Name', 'Level', 'Grammar', 'Speaking', 'Total'])
        st.rerun()
