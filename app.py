import streamlit as st
import pandas as pd
import plotly.express as px

# ១. ការកំណត់ទម្រង់ទំព័រ
st.set_page_config(
    page_title="SEG Grading System | Developed by CHAN Sokhoeurn", 
    page_icon="🏫", 
    layout="wide"
)

# ២. កន្លែងកំណត់ Logo SEG (អ្នកគ្រូអាចយក Link មកដាក់ជំនួស ឬប្រើ File ក្នុងម៉ាស៊ីន)
LOGO_URL = "https://img.icons8.com/fluency/150/school.png" 

# ៣. CSS សម្រាប់ដេគ័រកម្មវិធីឱ្យស្អាត
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { 
        width: 100%; border-radius: 8px; height: 3em; 
        background-color: #003057; color: white; font-weight: bold; 
    }
    .footer-text { 
        text-align: center; color: #666; padding: 20px; 
        font-size: 0.9em; border-top: 1px solid #eee; margin-top: 50px; 
    }
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ៤. មុខងារគណនា Grade
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

# ៥. Session State
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=[
        'Student Name', 'Level', 'Grammar', 'Vocabulary', 'Speaking', 
        'Reading', 'Listening', 'Daily Homework', 'Monthly Score', 
        'Mid-term', 'Final', 'Average (%)', 'Result Grade'
    ])

if 'form_key' not in st.session_state: st.session_state.form_key = 0
if 'selected_level' not in st.session_state: st.session_state.selected_level = "Level 1"

# --- ៦. SIDEBAR ---
st.sidebar.image(LOGO_URL, width=120)
st.sidebar.title("SEG Data Manager")
st.sidebar.divider()

# Upload
uploaded_file = st.sidebar.file_uploader("Upload Excel/CSV ឈ្មោះសិស្ស", type=['xlsx', 'csv'])
if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
        df.columns = [str(x).strip().title() for x in df.columns]
        if "Student Name" in df.columns:
            if st.sidebar.button("បញ្ចូលឈ្មោះសិស្សទាំងអស់"):
                for name in df["Student Name"].dropna().unique():
                    if name not in st.session_state.db['Student Name'].values:
                        new_row = pd.DataFrame([[name, "N/A", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "F"]], columns=st.session_state.db.columns)
                        st.session_state.db = pd.concat([st.session_state.db, new_row], ignore_index=True)
                st.rerun()
    except Exception as e: st.sidebar.error(f"Error: {e}")

# បញ្ចូលពិន្ទុ
if not st.session_state.db.empty:
    levels = ["K1", "K2", "K3", "K4"] + [f"Level {i}" for i in range(1, 13)]
    st.session_state.selected_level = st.sidebar.selectbox("📚 Select Level", levels, index=levels.index(st.session_state.selected_level))
    
    student_status = {f"{'✅ ' if r['Average (%)'] > 0 else '🔴 '}{r['Student Name']}": r['Student Name'] for _, r in st.session_state.db.iterrows()}
    
    with st.sidebar.form(key=f"form_{st.session_state.form_key}"):
        sel_display = st.selectbox("🎯 ជ្រើសរើសសិស្ស", list(student_status.keys()))
        sel_name = student_status[sel_display]
        
        c1, c2 = st.columns(2)
        with c1:
            g, r, l, h = [st.number_input(x, 0, 100, 0) for x in ["Grammar", "Reading", "Listening", "Homework"]]
        with c2:
            v, s, m = [st.number_input(x, 0, 100, 0) for x in ["Vocabulary", "Speaking", "Monthly"]]
        
        mid, fin = [st.number_input(x, 0, 100, 0) for x in ["Mid-term", "Final"]]
        
        if st.form_submit_button("Save & Update"):
            avg = (g+v+s+r+l+h+m+mid+fin)/9
            idx = st.session_state.db[st.session_state.db['Student Name'] == sel_name].index
            st.session_state.db.loc[idx, ['Level','Grammar','Vocabulary','Speaking','Reading','Listening','Daily Homework','Monthly Score','Mid-term','Final','Average (%)','Result Grade']] = [st.session_state.selected_level, g, v, s, r, l, h, m, mid, fin, round(avg, 2), calculate_grade(avg)]
            st.session_state.form_key += 1
            st.rerun()

# --- ៧. MAIN PAGE ---
col_logo, col_title = st.columns([1, 6])
with col_logo:
    st.image(LOGO_URL, width=100)
with col_title:
    st.title("SEG Student Management Dashboard")
    st.write("Academic Year: 2026 | Branch: **Prek Leap**")

if not st.session_state.db.empty:
    # Analysis
    st.divider()
    active_db = st.session_state.db[st.session_state.db['Average (%)'] > 0]
    if not active_db.empty:
        st.subheader("📊 Class Performance")
        grade_counts = active_db['Result Grade'].value_counts().reset_index()
        grade_counts.columns = ['Grade', 'Count']
        fig = px.pie(grade_counts, values='Count', names='Grade', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)

    # Filter & Sort
    st.subheader("🔍 Filter & Leaderboard")
    f1, f2 = st.columns(2)
    with f1:
        sel_grade = st.selectbox("Filter Grade", ["All Grades"] + sorted(st.session_state.db['Result Grade'].unique().tolist()))
    with f2:
        order = st.radio("Sort Score", ["High to Low", "Low to High"], horizontal=True)

    disp = st.session_state.db.copy()
    if sel_grade != "All Grades": disp = disp[disp['Result Grade'] == sel_grade]
    disp = disp.sort_values(by='Average (%)', ascending=(order == "Low to High"))

    def style_grade(val):
        color = 'red' if val == 'F' else '#2e7d32' if 'A' in str(val) else '#ef6c00' if 'C' in str(val) else '#1565c0'
        return f'color: {color}; font-weight: bold'

    st.write(f"Showing **{len(disp)}** students")
    st.dataframe(disp.style.map(style_grade, subset=['Result Grade']), use_container_width=True)

    # Export
    csv = disp.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 Download Report (CSV)", csv, "seg_report.csv", "text/csv")
    if st.button("🗑️ Clear All Data"):
        st.session_state.db = pd.DataFrame(columns=st.session_state.db.columns)
        st.rerun()
else:
    st.info("💡 សូមបញ្ចូលឈ្មោះសិស្សពី Excel ដើម្បីចាប់ផ្តើម។")

# --- ៨. FOOTER ---
st.markdown(f"""
    <div class="footer-text">
        <p>Developed with ❤️ by <b>CHAN Sokhoeurn, C2/DBA</b></p>
        <p>© 2026 SEG School Management System | Prek Leap Branch</p>
    </div>
    """, unsafe_allow_html=True)
