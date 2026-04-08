import streamlit as st
import pandas as pd
import plotly.express as px

# ១. ការកំណត់ទម្រង់ទំព័រ (Page Configuration)
st.set_page_config(
    page_title="SEG Grading System | Developed by CHAN Sokhoeurn", 
    page_icon="🏫", 
    layout="wide"
)

# ២. កន្លែងកំណត់ Logo (អ្នកគ្រូអាចប្តូរ URL នេះទៅជា Link Logo របស់សាលាអ្នកគ្រូបាន)
LOGO_URL = "https://img.icons8.com/fluency/150/school.png" 

# ៣. បន្ថែមស្ទាយ Custom CSS ឱ្យមើលទៅមានវិជ្ជាជីវៈ និងស្អាត
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { 
        width: 100%; 
        border-radius: 8px; 
        height: 3em; 
        background-color: #003057; 
        color: white; 
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover {
        background-color: #004a87;
        color: white;
    }
    .footer-text { 
        text-align: center; 
        color: #666; 
        padding: 20px; 
        font-size: 0.9em; 
        border-top: 1px solid #eee; 
        margin-top: 50px; 
    }
    /* ហាមបង្ហាញ Footer របស់ Streamlit */
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ៤. មុខងារគណនា Grade (តាមស្តង់ដារ)
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

# ៥. រៀបចំ Session State (ទុកទិន្នន័យបណ្តោះអាសន្ន)
columns = [
    'Student Name', 'Level', 'Grammar', 'Vocabulary', 'Speaking', 
    'Reading', 'Listening', 'Daily Homework', 'Monthly Score', 
    'Mid-term', 'Final', 'Average (%)', 'Result Grade'
]

if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=columns)

if 'selected_level' not in st.session_state:
    st.session_state.selected_level = "Level 1"

if 'form_key' not in st.session_state:
    st.session_state.form_key = 0

def reset_scores():
    st.session_state.form_key += 1

# --- ៦. SIDEBAR: ការគ្រប់គ្រងទិន្នន័យ និង LOGO ---
st.sidebar.image(LOGO_URL, width=120)
st.sidebar.title("SEG Data Manager")
st.sidebar.write("---")

# ផ្នែក Upload ឈ្មោះសិស្ស
st.sidebar.subheader("📂 Step 1: Bulk Upload")
uploaded_file = st.sidebar.file_uploader("Upload Excel/CSV", type=['xlsx', 'csv'])

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df_upload = pd.read_csv(uploaded_file)
        else:
            df_upload = pd.read_excel(uploaded_file, engine='openpyxl')
        
        # សម្អាតឈ្មោះ Column
        df_upload.columns = [str(x).strip().title() for x in df_upload.columns]
        
        if "Student Name" in df_upload.columns:
            if st.sidebar.button("បញ្ចូលឈ្មោះសិស្សទាំងអស់"):
                names = df_upload["Student Name"].dropna().unique()
                for name in names:
                    if name not in st.session_state.db['Student Name'].values:
                        new_row = pd.DataFrame([[name, "N/A", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "F"]], columns=columns)
                        st.session_state.db = pd.concat([st.session_state.db, new_row], ignore_index=True)
                st.sidebar.success(f"បានបញ្ចូលសិស្ស {len(names)} នាក់!")
                st.rerun()
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

st.sidebar.write("---")

# ផ្នែកបញ្ចូលពិន្ទុ (Edit Score)
st.sidebar.subheader("✍️ Step 2: Edit Score")
levels_list = ["K1", "K2", "K3", "K4"] + [f"Level {i}" for i in range(1, 13)]

if not st.session_state.db.empty:
    # Sticky Level
    current_level = st.sidebar.selectbox("📚 Select Level", levels_list, index=levels_list.index(st.session_state.selected_level))
    st.session_state.selected_level = current_level

    # បង្ហាញសញ្ញា 🔴 (នៅសល់) និង ✅ (រួចរាល់)
    student_status = {f"{'✅ ' if r['Average (%)'] > 0 else '🔴 '}{r['Student Name']}": r['Student Name'] for _, r in st.session_state.db.iterrows()}
    
    with st.sidebar.form(key=f"score_form_{st.session_state.form_key}"):
        selected_display = st.selectbox("🎯 ជ្រើសរើសសិស្ស", list(student_status.keys()))
        selected_name = student_status[selected_display]
        
        st.write("---")
        c1, c2 = st.columns(2)
        with c1:
            gram = st.number_input("Grammar", 0, 100, 0)
            read = st.number_input("Reading", 0, 100, 0)
            listn = st.number_input("Listening", 0, 100, 0)
            hw = st.number_input("Homework", 0, 100, 0)
        with c2:
            vocab = st.number_input("Vocabulary", 0, 100, 0)
            speak = st.number_input("Speaking", 0, 100, 0)
            monthly = st.number_input("Monthly", 0, 100, 0)
        
        midterm = st.number_input("Mid-term", 0, 100, 0)
        final = st.number_input("Final Exam", 0, 100, 0)
        
        if st.form_submit_button("Save & Update"):
            avg = (gram + vocab + speak + read + listn + hw + monthly + midterm + final) / 9
            grade = calculate_grade(avg)
            
            idx = st.session_state.db[st.session_state.db['Student Name'] == selected_name].index
            st.session_state.db.loc[idx, ['Level', 'Grammar', 'Vocabulary', 'Speaking', 'Reading', 'Listening', 'Daily Homework', 'Monthly Score', 'Mid-term', 'Final', 'Average (%)', 'Result Grade']] = [current_level, gram, vocab, speak, read, listn, hw, monthly, midterm, final, round(avg, 2), grade]
            
            st.sidebar.success(f"បានរក្សាទុក៖ {selected_name}")
            reset_scores()
            st.rerun()

# --- ៧. MAIN PAGE: DASHBOARD ---
col_l, col_r = st.columns([1, 6])
with col_l:
    st.image(LOGO_URL, width=100)
with col_r:
    st.title("SEG Student Management Dashboard")
    st.write("Academic Year: 2026 | Branch: **Prek Leap**")

if not st.session_state.db.empty:
    # ក្រាហ្វិកវិភាគនិទ្ទេស (Pie Chart)
    st.divider()
    active_data = st.session_state.db[st.session_state.db['Average (%)'] > 0]
    if not active_data.empty:
        st.subheader("📊 Grade Analysis (Pie Chart)")
        grade_counts = active_data['Result Grade'].value_counts().reset_index()
        grade_counts.columns = ['Grade', 'Count']
        fig = px.pie(grade_counts, values='Count', names='Grade', hole=0.4,
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)

    # ផ្នែក Filter និងការតម្រៀប
    st.subheader("🔍 Filter & Leaderboard")
    f1, f2 = st.columns(2)
    with f1:
        all_grades = ["All Grades"] + sorted(st.session_state.db['Result Grade'].unique().tolist())
        sel_grade = st.selectbox("Filter by Grade (A+, A...)", all_grades)
    with f2:
        sort_ord = st.radio("Sorting Score:", ["High to Low", "Low to High"], horizontal=True)

    # ការរៀបចំទិន្នន័យសម្រាប់បង្ហាញ
    disp_df = st.session_state.db.copy()
    if sel_grade != "All Grades":
        disp_df = disp_df[disp_df['Result Grade'] == sel_grade]
    
    disp_df = disp_df.sort_values(by='Average (%)', ascending=(sort_ord == "Low to High"))

    # មុខងារប្តូរពណ៌តាម Grade
    def color_grade(val):
        color = 'red' if val == 'F' else '#2e7d32' if 'A' in str(val) else '#ef6c00' if 'C' in str(val) else '#1565c0'
        return f'color: {color}; font-weight: bold'

    st.write(f"Showing **{len(disp_df)}** students")
    st.dataframe(disp_df.style.map(color_grade, subset=['Result Grade']), use_container_width=True)

    # ប៊ូតុងទាញយក និងសម្អាត
    st.write("---")
    c_dl, c_cl = st.columns([4, 1])
    with c_dl:
        csv = disp_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Download Official Report", csv, "seg_report_2026.csv", "text/csv")
    with c_cl:
        if st.button("🗑️ Clear All"):
            st.session_state.db = pd.DataFrame(columns=columns)
            st.rerun()
else:
    st.info("💡 Please upload student names from Excel to start grading.")

# --- ៨. FOOTER (CREDITS) ---
st.markdown(f"""
    <div class="footer-text">
        <p>Developed with ❤️ by <b>CHAN Sokhoeurn, C2/DBA</b></p>
        <p>© 2026 SEG School Management System | Prek Leap Branch</p>
    </div>
    """, unsafe_allow_html=True)
