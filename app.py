import streamlit as st
import pandas as pd
import plotly.express as px

# កំណត់ទម្រង់ទំព័រឱ្យស្អាត
st.set_page_config(page_title="SEG Grading System", page_icon="🏫", layout="wide")

# បន្ថែមស្ទាយបន្តិចបន្តួចសម្រាប់ពណ៌ និងប៊ូតុង
st.markdown("""
    <style>
    .main { background-color: #f4f7f9; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #003057; color: white; font-weight: bold; }
    .stDataFrame { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# បង្កើតកន្លែងរក្សាទុកទិន្នន័យក្នុង Session (វានឹងមិនបាត់ទេពេល Refresh ក្នុង Page តែមួយ)
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=['Student Name', 'Level', 'Grammar', 'Speaking', 'Total'])

# --- SIDEBAR: បញ្ចូលទិន្នន័យ ---
st.sidebar.image("https://img.icons8.com/fluency/96/school.png", width=80)
st.sidebar.title("Grading Panel")

# បញ្ជីកម្រិតសិក្សាដែលបានកែសម្រួលតាមអ្នកគ្រូកម្ម៉ង់
levels_list = [
    "K1", "K2", "K3", "K4", 
    "Level 1", "Level 2", "Level 3", "Level 4", 
    "Level 5", "Level 6", "Level 7", "Level 8", 
    "Level 9", "Level 10", "Level 11", "Level 12"
]

with st.sidebar.form("grading_form", clear_on_submit=True):
    name = st.text_input("👤 Student Full Name")
    level = st.selectbox("📚 Select Level", levels_list)
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
        st.sidebar.success(f"Saved: {name} ({level})")
    else:
        st.sidebar.error("Please enter student name!")

# --- MAIN PAGE: បង្ហាញលទ្ធផល ---
st.title("🏫 SEG Student Management Dashboard")
st.write(f"Branch: **Prek Leap** | Date: {pd.Timestamp.now().strftime('%Y-%m-%d')}")

# បង្ហាញជា Stats ខ្លីៗ (KPIs)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Students", len(st.session_state.db))
with col2:
    avg_score = st.session_state.db['Total'].mean() if not st.session_state.db.empty else 0
    st.metric("Average Score", f"{avg_score:.2f}")
with col3:
    if not st.session_state.db.empty:
        best_student = st.session_state.db.loc[st.session_state.db['Total'].idxmax()]['Student Name']
        st.metric("Top Student", best_student)
    else:
        st.metric("Top Student", "N/A")

st.markdown("---")

# តារាងទិន្នន័យ
st.subheader("📊 Class Grade Sheet")
st.dataframe(st.session_state.db, use_container_width=True)

# ក្រាហ្វិកវិភាគ (Analytics)
if not st.session_state.db.empty:
    st.subheader("📈 Performance Analysis")
    fig = px.bar(st.session_state.db, x='Student Name', y='Total', color='Level', 
                 title="Student Performance Comparison", 
                 color_discrete_sequence=px.colors.qualitative.Pastel)
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
