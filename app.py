import streamlit as st
import pandas as pd
import plotly.express as px

# ១. ការកំណត់ទម្រង់ទំព័រ
st.set_page_config(page_title="SEG Professional Grading System", page_icon="🏫", layout="wide")

# ២. បន្ថែមស្ទាយ Custom CSS
st.markdown("""
    <style>
    .main { background-color: #f4f7f9; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #003057; color: white; font-weight: bold; }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); border-left: 5px solid #003057; }
    </style>
    """, unsafe_allow_html=True)

# ៣. មុខងារគណនា Grade
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

# ៤. បង្កើត Header និង Session State
columns = [
    'Student Name', 'Level', 'Grammar', 'Vocabulary', 'Speaking', 
    'Reading', 'Listening', 'Daily Homework', 'Monthly Score', 
    'Mid-term', 'Final', 'Average (%)', 'Result Grade'
]

if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=columns)

# ចងចាំ Level ដែលបានជ្រើសរើស (Sticky Level)
if 'selected_level' not in st.session_state:
    st.session_state.selected_level = "Level 1"

# State សម្រាប់សម្អាតពិន្ទុ (Reset Score Only)
if 'form_key' not in st.session_state:
    st.session_state.form_key = 0

def reset_scores():
    st.session_state.form_key += 1

# --- ៥. SIDEBAR: ការគ្រប់គ្រងទិន្នន័យ ---
st.sidebar.image("https://img.icons8.com/fluency/96/school.png", width=80)
st.sidebar.title("SEG Data Manager")

# ផ្នែក Upload Excel
st.sidebar.subheader("📂 Step 1: Bulk Upload")
uploaded_file = st.sidebar.file_uploader("Upload Excel/CSV ឈ្មោះសិស្ស", type=['xlsx', 'csv'])

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df_upload = pd.read_csv(uploaded_file)
        else:
            df_upload = pd.read_excel(uploaded_file, engine='openpyxl')
        
        df_upload.columns = [str(x).strip().title() for x in df_upload.columns]
        
        if "Student Name" in df_upload.columns:
            if st.sidebar.button("បញ្ចូលឈ្មោះសិស្សទាំងអស់"):
                names_to_add = df_upload["Student Name"].dropna().unique()
                for name in names_to_add:
                    if name not in st.session_state.db['Student Name'].values:
                        new_row = pd.DataFrame([[name, "N/A", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "F"]], columns=columns)
                        st.session_state.db = pd.concat([st.session_state.db, new_row], ignore_index=True)
                st.sidebar.success(f"បានបញ្ចូលសិស្ស {len(names_to_add)} នាក់!")
                st.rerun()
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

st.sidebar.divider()

# ផ្នែកបញ្ចូលពិន្ទុ (Edit Score)
st.sidebar.subheader("✍️ Step 2: Edit Score")
levels_list = ["K1", "K2", "K3", "K4", "Level 1", "Level 2", "Level 3", "Level 4", "Level 5", "Level 6", "Level 7", "Level 8", "Level 9", "Level 10", "Level 11", "Level 12"]

if not st.session_state.db.empty:
    # កន្លែងកំណត់ឱ្យ Level នៅជាប់ (Sticky Level)
    current_level = st.sidebar.selectbox(
        "📚 Select Level (នឹងនៅជាប់រហូត)", 
        levels_list, 
        index=levels_list.index(st.session_state.selected_level)
    )
    st.session_state.selected_level = current_level

    # Form សម្រាប់ពិន្ទុ (នឹង Reset ទៅ 0 តែពិន្ទុទេ)
    with st.sidebar.form(key=f"score_form_{st.session_state.form_key}"):
        selected_student = st.selectbox("ជ្រើសរើសសិស្ស", st.session_state.db['Student Name'].tolist())
        
        st.write("---")
        c1, c2 = st.columns(2)
        with c1:
            gram = st.number_input("Grammar", 0, 100, value=0)
            read = st.number_input("Reading", 0, 100, value=0)
            listn = st.number_input("Listening", 0, 100, value=0)
            hw = st.number_input("Homework", 0, 100, value=0)
        with c2:
            vocab = st.number_input("Vocabulary", 0, 100, value=0)
            speak = st.number_input("Speaking", 0, 100, value=0)
            monthly = st.number_input("Monthly", 0, 100, value=0)
        
        midterm = st.number_input("Mid-term Exam", 0, 100, value=0)
        final = st.number_input("Final Exam", 0, 100, value=0)
        
        if st.form_submit_button("Update & Save"):
            avg = (gram + vocab + speak + read + listn + hw + monthly + midterm + final) / 9
            grade = calculate_grade(avg)
            
            idx = st.session_state.db[st.session_state.db['Student Name'] == selected_student].index
            st.session_state.db.loc[idx, ['Level', 'Grammar', 'Vocabulary', 'Speaking', 'Reading', 'Listening', 'Daily Homework', 'Monthly Score', 'Mid-term', 'Final', 'Average (%)', 'Result Grade']] = [st.session_state.selected_level, gram, vocab, speak, read, listn, hw, monthly, midterm, final, round(avg, 2), grade]
            
            st.sidebar.success(f"Saved: {selected_student}")
            reset_scores() # លុបតែពិន្ទុចេញដើម្បីវាយសិស្សថ្មី
            st.rerun()
else:
    st.sidebar.info("សូម Upload Excel ដើម្បីចាប់ផ្តើម")

# --- ៦. MAIN PAGE ---
st.title("🏫 SEG Student Management Dashboard")

if not st.session_state.db.empty:
    st.subheader("📊 Class Results Sheet")
    def color_grade(val):
        color = 'red' if val == 'F' else '#2e7d32' if 'A' in str(val) else '#ef6c00' if 'C' in str(val) else '#1565c0'
        return f'color: {color}; font-weight: bold'

    styled_df = st.session_state.db.style.map(color_grade, subset=['Result Grade'])
    st.dataframe(styled_df, use_container_width=True)

    # ប៊ូតុងទាញយក
    csv = st.session_state.db.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 Download Report (Excel)", csv, "seg_report.csv", "text/csv")
    
    if st.button("🗑️ Clear All Data"):
        st.session_state.db = pd.DataFrame(columns=columns)
        st.rerun()
