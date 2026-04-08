import streamlit as st
import pandas as pd
import plotly.express as px

# កំណត់ទម្រង់ទំព័រ
st.set_page_config(page_title="SEG Professional Grading System", page_icon="🏫", layout="wide")

# បន្ថែមស្ទាយបន្តិចបន្តួច
st.markdown("""
    <style>
    .main { background-color: #f4f7f9; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #003057; color: white; font-weight: bold; }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); border-left: 5px solid #003057; }
    </style>
    """, unsafe_allow_html=True)

# មុខងារគណនា Grade
def calculate_grade(score):
    if score >= 97: return "A+"
    elif score >= 93: return "A"
    elif score >= 90: return "A-"
    elif score >= 87: return "B+"
    elif score >= 83: return "B"
    elif score >= 80: return "B-"
    elif score >= 77: return "C+"
    elif score >= 73: return "C"
    elif score >= 70: return "C-"
    elif score >= 67: return "D+"
    elif score >= 63: return "D"
    elif score >= 60: return "D-"
    else: return "F"

# បង្កើត Header សម្រាប់រក្សាទុកទិន្នន័យ
columns = [
    'Student Name', 'Level', 'Grammar', 'Vocabulary', 'Speaking', 
    'Reading', 'Listening', 'Daily Homework', 'Monthly Score', 
    'Mid-term', 'Final', 'Average (%)', 'Result Grade'
]

if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=columns)

# --- SIDEBAR: បញ្ចូលទិន្នន័យ ---
st.sidebar.image("https://img.icons8.com/fluency/96/school.png", width=80)
st.sidebar.title("SEG Grading Editor")

levels_list = [
    "K1", "K2", "K3", "K4", "Level 1", "Level 2", "Level 3", "Level 4", 
    "Level 5", "Level 6", "Level 7", "Level 8", "Level 9", "Level 10", "Level 11", "Level 12"
]

with st.sidebar.form("grading_form", clear_on_submit=True):
    name = st.text_input("👤 Student Full Name")
    level = st.selectbox("📚 Select Level", levels_list)
    
    st.divider()
    st.write("📝 **Skill & Daily Scores**")
    c1, c2 = st.columns(2)
    with c1:
        gram = st.number_input("Grammar", 0, 100)
        read = st.number_input("Reading", 0, 100)
        listn = st.number_input("Listening", 0, 100)
        hw = st.number_input("Homework", 0, 100)
    with c2:
        vocab = st.number_input("Vocabulary", 0, 100)
        speak = st.number_input("Speaking", 0, 100)
        monthly = st.number_input("Monthly", 0, 100)
    
    st.write("🏆 **Major Exams**")
    midterm = st.number_input("Mid-term Exam", 0, 100)
    final = st.number_input("Final Exam", 0, 100)
    
    submitted = st.form_submit_button("Submit Scores")

if submitted:
    if name:
        # គណនាមធ្យមភាគ (សរុបមាន ៩ ប្រអប់ពិន្ទុ)
        avg = (gram + vocab + speak + read + listn + hw + monthly + midterm + final) / 9
        grade = calculate_grade(avg)
        
        new_entry = pd.DataFrame({
            'Student Name': [name], 'Level': [level], 'Grammar': [gram],
            'Vocabulary': [vocab], 'Speaking': [speak], 'Reading': [read],
            'Listening': [listn], 'Daily Homework': [hw], 'Monthly Score': [monthly],
            'Mid-term': [midterm], 'Final': [final], 'Average (%)': [round(avg, 2)],
            'Result Grade': [grade]
        })
        st.session_state.db = pd.concat([st.session_state.db, new_entry], ignore_index=True)
        st.sidebar.success(f"Graded: {name} -> {grade}")
    else:
        st.sidebar.error("Please enter student name!")

# --- MAIN PAGE: DASHBOARD ---
st.title("🏫 SEG Student Management Dashboard")
st.write(f"Prek Leap Branch | Academic Year: 2026")

# Metrics Section
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Total Students", len(st.session_state.db))
with m2:
    avg_total = st.session_state.db['Average (%)'].mean() if not st.session_state.db.empty else 0
    st.metric("Class Average", f"{avg_total:.1f}%")
with m3:
    if not st.session_state.db.empty:
        pass_rate = (len(st.session_state.db[st.session_state.db['Result Grade'] != 'F']) / len(st.session_state.db)) * 100
        st.metric("Pass Rate", f"{pass_rate:.1f}%")
    else:
        st.metric("Pass Rate", "0%")
with m4:
    if not st.session_state.db.empty:
        best = st.session_state.db.loc[st.session_state.db['Average (%)'].idxmax()]['Result Grade']
        st.metric("Top Grade", best)
    else:
        st.metric("Top Grade", "N/A")

st.divider()

# តារាងពិន្ទុ
st.subheader("📊 Class Results Sheet")

# មុខងារប្តូរពណ៌អក្សរតាម Grade (ប្រើពាក្យ map ជំនួស applymap)
def color_grade(val):
    color = 'red' if val == 'F' else '#2e7d32' if 'A' in str(val) else '#ef6c00' if 'C' in str(val) else '#1565c0'
    return f'color: {color}; font-weight: bold'

if not st.session_state.db.empty:
    # --- កន្លែងដែលបានកែ Error គឺត្រង់នេះ ---
    styled_df = st.session_state.db.style.map(color_grade, subset=['Result Grade'])
    st.dataframe(styled_df, use_container_width=True)
else:
    st.info("No data yet. Use the sidebar to add students.")

# Analytics
if not st.session_state.db.empty:
    st.subheader("📈 Grade Distribution")
    fig = px.pie(st.session_state.db, names='Result Grade', title='Student Achievement Overview', hole=0.4,
                 color_discrete_sequence=px.colors.qualitative.Set3)
    st.plotly_chart(fig, use_container_width=True)

# Footer Buttons
st.divider()
c1, c2 = st.columns([4, 1])
with c1:
    if not st.session_state.db.empty:
        csv = st.session_state.db.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Download Official Report (Excel)", csv, "seg_official_report.csv", "text/csv")
with c2:
    if st.button("🗑️ Clear Records"):
        st.session_state.db = pd.DataFrame(columns=columns)
        st.rerun()
