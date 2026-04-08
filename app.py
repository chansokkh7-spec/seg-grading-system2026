import streamlit as st
import pandas as pd
import plotly.express as px

# កំណត់ទម្រង់ទំព័រ
st.set_page_config(page_title="SEG Grading System - Excel Upload", page_icon="🏫", layout="wide")

# បន្ថែមស្ទាយ
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
st.sidebar.title("SEG Data Manager")

# ១. មុខងារ Upload Excel
st.sidebar.subheader("📂 Step 1: Bulk Upload")
uploaded_file = st.sidebar.file_uploader("Upload Excel/CSV ឈ្មោះសិស្ស", type=['xlsx', 'csv'])

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df_upload = pd.read_csv(uploaded_file)
        else:
            df_upload = pd.read_excel(uploaded_file)
        
        if "Student Name" in df_upload.columns:
            if st.sidebar.button("បញ្ចូលឈ្មោះសិស្សទាំងអស់"):
                for name in df_upload["Student Name"]:
                    # បង្កើតជួរដេកថ្មីដែលមានតែឈ្មោះសិស្ស ហើយពិន្ទុដាក់ ០ សិន
                    new_entry = pd.DataFrame([[name, "N/A", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "F"]], columns=columns)
                    st.session_state.db = pd.concat([st.session_state.db, new_entry], ignore_index=True)
                st.sidebar.success(f"បានបញ្ចូលសិស្ស {len(df_upload)} នាក់រួចរាល់!")
        else:
            st.sidebar.error("ក្នុង Excel ត្រូវមាន Column ឈ្មោះ 'Student Name'")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

st.sidebar.divider()

# ២. មុខងារបញ្ចូលពិន្ទុម្នាក់ៗ
st.sidebar.subheader("✍️ Step 2: Edit Score")
levels_list = ["K1", "K2", "K3", "K4", "Level 1", "Level 2", "Level 3", "Level 4", "Level 5", "Level 6", "Level 7", "Level 8", "Level 9", "Level 10", "Level 11", "Level 12"]

with st.sidebar.form("edit_form"):
    if not st.session_state.db.empty:
        selected_student = st.selectbox("ជ្រើសរើសសិស្សដើម្បីដាក់ពិន្ទុ", st.session_state.db['Student Name'].tolist())
        level = st.selectbox("📚 Select Level", levels_list)
        st.write("---")
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
        
        midterm = st.number_input("Mid-term Exam", 0, 100)
        final = st.number_input("Final Exam", 0, 100)
        
        if st.form_submit_button("Update Score"):
            avg = (gram + vocab + speak + read + listn + hw + monthly + midterm + final) / 9
            grade = calculate_grade(avg)
            
            # Update ទិន្នន័យក្នុងជួរដែលបានជ្រើសរើស
            idx = st.session_state.db[st.session_state.db['Student Name'] == selected_student].index
            st.session_state.db.loc[idx, ['Level', 'Grammar', 'Vocabulary', 'Speaking', 'Reading', 'Listening', 'Daily Homework', 'Monthly Score', 'Mid-term', 'Final', 'Average (%)', 'Result Grade']] = [level, gram, vocab, speak, read, listn, hw, monthly, midterm, final, round(avg, 2), grade]
            st.sidebar.success(f"Updated {selected_student}!")
            st.rerun()
    else:
        st.write("សូម Upload Excel ជាមុនសិន")
        st.form_submit_button("Save", disabled=True)

# --- MAIN PAGE: DASHBOARD ---
st.title("🏫 SEG Student Management Dashboard")
st.write(f"Prek Leap Branch | សម្រាប់សិស្សច្រើននាក់")

# Metrics
m1, m2, m3 = st.columns(3)
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

st.divider()

# តារាងពិន្ទុ
st.subheader("📊 Class Results Sheet")

def color_grade(val):
    color = 'red' if val == 'F' else '#2e7d32' if 'A' in str(val) else '#ef6c00' if 'C' in str(val) else '#1565c0'
    return f'color: {color}; font-weight: bold'

if not st.session_state.db.empty:
    styled_df = st.session_state.db.style.map(color_grade, subset=['Result Grade'])
    st.dataframe(styled_df, use_container_width=True)
else:
    st.info("💡 គន្លឹះ៖ រៀបចំ File Excel ដែលមាន Column ឈ្មោះ 'Student Name' រួច Upload តាម Sidebar ខាងឆ្វេង។")

# Footer Buttons
st.divider()
c1, c2 = st.columns([4, 1])
with c1:
    if not st.session_state.db.empty:
        csv = st.session_state.db.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Download Official Report (Excel)", csv, "seg_official_report.csv", "text/csv")
with c2:
    if st.button("🗑️ Clear All"):
        st.session_state.db = pd.DataFrame(columns=columns)
        st.rerun()
