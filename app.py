import streamlit as st
import pandas as pd
import plotly.express as px

# ១. ការកំណត់ទម្រង់ទំព័រ (Page Configuration)
st.set_page_config(page_title="SEG Grading System", page_icon="🏫", layout="wide")

# ២. បន្ថែមស្ទាយ Custom CSS ឱ្យមើលទៅមានវិជ្ជាជីវៈ
st.markdown("""
    <style>
    .main { background-color: #f4f7f9; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #003057; color: white; font-weight: bold; }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); border-left: 5px solid #003057; }
    footer {visibility: hidden;}
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

# ៤. បង្កើត Header និង Session State (Database)
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

# --- ៥. SIDEBAR: ការបញ្ចូលទិន្នន័យ ---
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
        else:
            st.sidebar.error("រកមិនឃើញក្បាលតារាង 'Student Name' ទេ។")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

st.sidebar.divider()

# ផ្នែកបញ្ចូលពិន្ទុ (Edit Score)
st.sidebar.subheader("✍️ Step 2: Edit Score")
levels_list = ["K1", "K2", "K3", "K4", "Level 1", "Level 2", "Level 3", "Level 4", "Level 5", "Level 6", "Level 7", "Level 8", "Level 9", "Level 10", "Level 11", "Level 12"]

if not st.session_state.db.empty:
    # Sticky Level
    current_level = st.sidebar.selectbox("📚 Select Level", levels_list, index=levels_list.index(st.session_state.selected_level))
    st.session_state.selected_level = current_level

    # បង្ហាញសញ្ញា 🔴 (មិនទាន់វាយ) និង ✅ (វាយរួច) ក្នុងបញ្ជីឈ្មោះ
    display_to_real = {f"{'✅ ' if r['Average (%)'] > 0 else '🔴 '}{r['Student Name']}": r['Student Name'] for _, r in st.session_state.db.iterrows()}
    
    with st.sidebar.form(key=f"score_form_{st.session_state.form_key}"):
        selected_display = st.selectbox("🎯 ជ្រើសរើសសិស្ស", list(display_to_real.keys()))
        selected_name = display_to_real[selected_display]
        
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
            idx = st.session_state.db[st.session_state.db['Student Name'] == selected_name].index
            st.session_state.db.loc[idx, ['Level', 'Grammar', 'Vocabulary', 'Speaking', 'Reading', 'Listening', 'Daily Homework', 'Monthly Score', 'Mid-term', 'Final', 'Average (%)', 'Result Grade']] = [current_level, gram, vocab, speak, read, listn, hw, monthly, midterm, final, round(avg, 2), grade]
            reset_scores()
            st.rerun()

# --- ៦. MAIN PAGE: DASHBOARD ---
st.title("🏫 SEG Student Management Dashboard")

if not st.session_state.db.empty:
    # --- ផ្នែកវិភាគ (Pie Chart) ---
    st.subheader("📊 Grade Distribution")
    active_db = st.session_state.db[st.session_state.db['Average (%)'] > 0]
    if not active_db.empty:
        grade_counts = active_db['Result Grade'].value_counts().reset_index()
        grade_counts.columns = ['Grade', 'Count']
        fig = px.pie(grade_counts, values='Count', names='Grade', hole=0.4,
                     color_discrete_sequence=px.colors.qualitative.Safe)
        st.plotly_chart(fig, use_container_width=True)

    # --- ផ្នែក FILTER ---
    st.subheader("🔍 Filter & Leaderboard")
    f1, f2 = st.columns(2)
    with f1:
        all_grades = ["All Grades"] + sorted(st.session_state.db['Result Grade'].unique().tolist())
        selected_grade = st.selectbox("Filter by Grade", all_grades)
    with f2:
        sort_order = st.radio("Sort Score:", ["High to Low", "Low to High"], horizontal=True)

    # Filter និង Sort ទិន្នន័យ
    display_df = st.session_state.db.copy()
    if selected_grade != "All Grades":
        display_df = display_df[display_df['Result Grade'] == selected_grade]
    
    ascending = (sort_order == "Low to High")
    display_df = display_df.sort_values(by='Average (%)', ascending=ascending)

    # បង្ហាញតារាង
    def color_grade(val):
        color = 'red' if val == 'F' else '#2e7d32' if 'A' in str(val) else '#ef6c00' if 'C' in str(val) else '#1565c0'
        return f'color: {color}; font-weight: bold'

    st.write(f"Showing **{len(display_df)}** students")
    st.dataframe(display_df.style.map(color_grade, subset=['Result Grade']), use_container_width=True)

    # ប៊ូតុង Download និង Clear
    st.divider()
    c_dl, c_cl = st.columns([4, 1])
    with c_dl:
        csv = display_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Download Excel Report", csv, "seg_report.csv", "text/csv")
    with c_cl:
        if st.button("🗑️ Clear Data"):
            st.session_state.db = pd.DataFrame(columns=columns)
            st.rerun()
else:
    st.info("💡 Please upload student names from Excel to start.")

# --- ៧. FOOTER CREDITS ---
st.divider()
st.markdown("""
    <div style='text-align: center; color: gray; padding: 10px;'>
        <p>Developed by <b>CHAN Sokhoeurn, C2/DBA</b></p>
        <p>© 2026 SEG Management System | Prek Leap Branch</p>
    </div>
    """, unsafe_allow_html=True)
