import streamlit as st
import pandas as pd
import plotly.express as px

# កំណត់ទម្រង់ទំព័រឱ្យស្អាត និងធំទូលាយ
st.set_page_config(page_title="SEG Advanced Grading System", page_icon="🏫", layout="wide")

# បន្ថែមស្ទាយបន្តិចបន្តួចសម្រាប់ពណ៌ និងប៊ូតុង
st.markdown("""
    <style>
    .main { background-color: #f4f7f9; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #003057; color: white; font-weight: bold; }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# បង្កើត Header សម្រាប់រក្សាទុកទិន្នន័យ
columns = [
    'Student Name', 'Level', 'Grammar', 'Vocabulary', 'Speaking', 
    'Reading', 'Listening', 'Daily Homework', 'Monthly Score', 
    'Mid-term', 'Final', 'Total Score'
]

if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=columns)

# --- SIDEBAR: បញ្ចូលទិន្នន័យយ៉ាងលម្អិត ---
st.sidebar.image("https://img.icons8.com/fluency/96/school.png", width=80)
st.sidebar.title("Student Grading Editor")

levels_list = [
    "K1", "K2", "K3", "K4", 
    "Level 1", "Level 2", "Level 3", "Level 4", 
    "Level 5", "Level 6", "Level 7", "Level 8", 
    "Level 9", "Level 10", "Level 11", "Level 12"
]

with st.sidebar.form("grading_form", clear_on_submit=True):
    st.subheader("Personal Info")
    name = st.text_input("👤 Student Full Name")
    level = st.selectbox("📚 Select Level", levels_list)
    
    st.divider()
    st.subheader("Skill Scores (0-100)")
    c1, c2 = st.columns(2)
    with c1:
        gram = st.number_input("✍️ Grammar", 0, 100)
        read = st.number_input("📖 Reading", 0, 100)
        listn = st.number_input("🎧 Listening", 0, 100)
    with c2:
        vocab = st.number_input("📝 Vocabulary", 0, 100)
        speak = st.number_input("🗣️ Speaking", 0, 100)
        hw = st.number_input("🏠 Daily Homework", 0, 100)
    
    st.divider()
    st.subheader("Examination Scores")
    monthly = st.number_input("📅 Monthly Score", 0, 100)
    midterm = st.number_input("🕒 Mid-term Exam", 0, 100)
    final = st.number_input("🏆 Final Exam", 0, 100)
    
    submitted = st.form_submit_button("Save All Scores")

if submitted:
    if name:
        # គណនាពិន្ទុសរុប (អ្នកគ្រូអាចកែសម្រួលមធ្យមភាគតាមក្រោយបាន)
        total = (gram + vocab + speak + read + listn + hw + monthly + midterm + final)
        
        new_entry = pd.DataFrame({
            'Student Name': [name],
            'Level': [level],
            'Grammar': [gram],
            'Vocabulary': [vocab],
            'Speaking': [speak],
            'Reading': [read],
            'Listening': [listn],
            'Daily Homework': [hw],
            'Monthly Score': [monthly],
            'Mid-term': [midterm],
            'Final': [final],
            'Total Score': [total]
        })
        st.session_state.db = pd.concat([st.session_state.db, new_entry], ignore_index=True)
        st.sidebar.success(f"Successfully saved {name}!")
    else:
        st.sidebar.error("Please enter student name!")

# --- MAIN PAGE: DASHBOARD ---
st.title("🏫 SEG Advanced Student Management")
st.write(f"Branch: **Prek Leap** | Data Management System")

# KPIs Section
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Total Students", len(st.session_state.db))
with m2:
    avg = st.session_state.db['Total Score'].mean() if not st.session_state.db.empty else 0
    st.metric("Avg Class Score", f"{avg:.1f}")
with m3:
    if not st.session_state.db.empty:
        top = st.session_state.db.loc[st.session_state.db['Total Score'].idxmax()]['Student Name']
        st.metric("Top Achiever", top)
    else:
        st.metric("Top Achiever", "N/A")
with m4:
    st.metric("Active Levels", st.session_state.db['Level'].nunique() if not st.session_state.db.empty else 0)

st.divider()

# តារាងទិន្នន័យពេញលេញ
st.subheader("📊 Comprehensive Grade Sheet")
st.dataframe(st.session_state.db, use_container_width=True)

# ក្រាហ្វិកវិភាគពិន្ទុតាមជំនាញ
if not st.session_state.db.empty:
    st.subheader("📈 Performance Breakdown")
    # បង្ហាញក្រាហ្វិកប្រៀបធៀប Final Score និង Mid-term
    fig = px.scatter(st.session_state.db, x='Mid-term', y='Final', size='Total Score', 
                     color='Level', hover_name='Student Name', title="Mid-term vs Final Comparison")
    st.plotly_chart(fig, use_container_width=True)

# ប៊ូតុងបញ្ជា
st.divider()
c1, c2, c3 = st.columns([2, 2, 1])
with c1:
    if not st.session_state.db.empty:
        csv = st.session_state.db.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Download Excel Report (Full)", csv, "seg_full_report.csv", "text/csv")
with c3:
    if st.button("🗑️ Reset All"):
        st.session_state.db = pd.DataFrame(columns=columns)
        st.rerun()
