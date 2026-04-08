import streamlit as st
import pandas as pd
import plotly.express as px

# ១. ការកំណត់ទម្រង់ទំព័រ
st.set_page_config(page_title="SEG Grading System", page_icon="🏫", layout="wide")

# ២. មុខងារគណនា Grade
def calculate_grade(score):
    if score >= 97: return "A+"
    elif score >= 93: returimport streamlit as st
import pandas as pd
import plotly.express as px

# ១. ការកំណត់ទម្រង់ទំព័រ
st.set_page_config(page_title="SEG Grading System", page_icon="🏫", layout="wide")

# ២. មុខងារគណនា Grade
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

# ៣. បង្កើត Header និង Session State
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

# --- ៤. SIDEBAR: DATA INPUT ---
st.sidebar.title("SEG Data Manager")
uploaded_file = st.sidebar.file_uploader("Upload Excel/CSV", type=['xlsx', 'csv'])

if uploaded_file:
    try:
        df_upload = pd.read_excel(uploaded_file, engine='openpyxl') if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
        df_upload.columns = [str(x).strip().title() for x in df_upload.columns]
        if "Student Name" in df_upload.columns:
            if st.sidebar.button("បញ្ចូលឈ្មោះសិស្សទាំងអស់"):
                for name in df_upload["Student Name"].dropna().unique():
                    if name not in st.session_state.db['Student Name'].values:
                        new_row = pd.DataFrame([[name, "N/A", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "F"]], columns=columns)
                        st.session_state.db = pd.concat([st.session_state.db, new_row], ignore_index=True)
                st.rerun()
    except Exception as e: st.sidebar.error(f"Error: {e}")

st.sidebar.divider()
levels_list = ["K1", "K2", "K3", "K4", "Level 1", "Level 2", "Level 3", "Level 4", "Level 5", "Level 6", "Level 7", "Level 8", "Level 9", "Level 10", "Level 11", "Level 12"]

if not st.session_state.db.empty:
    current_level = st.sidebar.selectbox("📚 Select Level", levels_list, index=levels_list.index(st.session_state.selected_level))
    st.session_state.selected_level = current_level

    display_to_real = {f"{'✅ ' if r['Average (%)'] > 0 else '🔴 '}{r['Student Name']}": r['Student Name'] for _, r in st.session_state.db.iterrows()}
    
    with st.sidebar.form(key=f"score_form_{st.session_state.form_key}"):
        selected_display = st.selectbox("🎯 ជ្រើសរើសសិស្ស", list(display_to_real.keys()))
        selected_name = display_to_real[selected_display]
        
        st.write("---")
        c1, c2 = st.columns(2)
        with c1:
            gram, read, listn, hw = [st.number_input(l, 0, 100, 0) for l in ["Grammar", "Reading", "Listening", "Homework"]]
        with c2:
            vocab, speak, monthly = [st.number_input(l, 0, 100, 0) for l in ["Vocabulary", "Speaking", "Monthly"]]
        
        midterm, final = [st.number_input(l, 0, 100, 0) for l in ["Mid-term Exam", "Final Exam"]]
        
        if st.form_submit_button("Update & Save"):
            avg = (gram + vocab + speak + read + listn + hw + monthly + midterm + final) / 9
            grade = calculate_grade(avg)
            idx = st.session_state.db[st.session_state.db['Student Name'] == selected_name].index
            st.session_state.db.loc[idx, ['Level', 'Grammar', 'Vocabulary', 'Speaking', 'Reading', 'Listening', 'Daily Homework', 'Monthly Score', 'Mid-term', 'Final', 'Average (%)', 'Result Grade']] = [current_level, gram, vocab, speak, read, listn, hw, monthly, midterm, final, round(avg, 2), grade]
            reset_scores()
            st.rerun()

# --- ៥. MAIN PAGE: DASHBOARD ---
st.title("🏫 SEG Student Management Dashboard")

if not st.session_state.db.empty:
    # --- ផ្នែកវិភាគនិទ្ទេស (Pie Chart) ---
    st.subheader("📊 Grade Analysis")
    grade_counts = st.session_state.db[st.session_state.db['Average (%)'] > 0]['Result Grade'].value_counts().reset_index()
    grade_counts.columns = ['Grade', 'Count']
    
    fig = px.pie(grade_counts, values='Count', names='Grade', title='Class Grade Distribution',
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig, use_container_width=True)

    # --- ផ្នែក FILTER ---
    st.subheader("🔍 Filter & Leaderboard")
    f1, f2 = st.columns(2)
    
    with f1:
        all_grades = ["All Grades"] + sorted(st.session_state.db['Result Grade'].unique().tolist())
        selected_grade = st.selectbox("បង្ហាញតាមនិទ្ទេស (Grade)", all_grades)
    
    with f2:
        sort_order = st.radio("តម្រៀបពិន្ទុ (Sort by Score):", ["ខ្ពស់ទៅទាប (High to Low)", "ទាបទៅខ្ពស់ (Low to High)"], horizontal=True)

    display_df = st.session_state.db.copy()
    if selected_grade != "All Grades":
        display_df = display_df[display_df['Result Grade'] == selected_grade]
    
    ascending = (sort_order == "ទាបទៅខ្ពស់ (Low to High)")
    display_df = display_df.sort_values(by='Average (%)', ascending=ascending)

    st.write(f"បង្ហាញសិស្សចំនួន: **{len(display_df)}** នាក់")
    
    def color_grade(val):
        color = 'red' if val == 'F' else '#2e7d32' if 'A' in str(val) else '#ef6c00' if 'C' in str(val) else '#1565c0'
        return f'color: {color}; font-weight: bold'

    st.dataframe(display_df.style.map(color_grade, subset=['Result Grade']), use_container_width=True)

    # Download
    csv = display_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 Download This List", csv, "seg_filtered_report.csv", "text/csv")
else:
    st.info("💡 សូម Upload Excel ដើម្បីចាប់ផ្តើម")

# --- ៦. FOOTER: CREDITS ---
st.divider()
st.markdown("""
    <div style='text-align: center; color: gray; padding: 10px;'>
        <p>Developed by <b>CHAN Sokhoeurn, C2/DBA</b></p>
        <p>© 2026 SEG Management System | Prek Leap Branch</p>
    </div>
    """, unsafe_allow_html=True)n "A"
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

# ៣. បង្កើត Header និង Session State
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

# --- ៤. SIDEBAR: DATA INPUT ---
st.sidebar.title("SEG Data Manager")
uploaded_file = st.sidebar.file_uploader("Upload Excel/CSV", type=['xlsx', 'csv'])

if uploaded_file:
    try:
        df_upload = pd.read_excel(uploaded_file, engine='openpyxl') if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
        df_upload.columns = [str(x).strip().title() for x in df_upload.columns]
        if "Student Name" in df_upload.columns:
            if st.sidebar.button("បញ្ចូលឈ្មោះសិស្សទាំងអស់"):
                for name in df_upload["Student Name"].dropna().unique():
                    if name not in st.session_state.db['Student Name'].values:
                        new_row = pd.DataFrame([[name, "N/A", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "F"]], columns=columns)
                        st.session_state.db = pd.concat([st.session_state.db, new_row], ignore_index=True)
                st.rerun()
    except Exception as e: st.sidebar.error(f"Error: {e}")

st.sidebar.divider()
levels_list = ["K1", "K2", "K3", "K4", "Level 1", "Level 2", "Level 3", "Level 4", "Level 5", "Level 6", "Level 7", "Level 8", "Level 9", "Level 10", "Level 11", "Level 12"]

if not st.session_state.db.empty:
    current_level = st.sidebar.selectbox("📚 Select Level", levels_list, index=levels_list.index(st.session_state.selected_level))
    st.session_state.selected_level = current_level

    display_to_real = {f"{'✅ ' if r['Average (%)'] > 0 else '🔴 '}{r['Student Name']}": r['Student Name'] for _, r in st.session_state.db.iterrows()}
    
    with st.sidebar.form(key=f"score_form_{st.session_state.form_key}"):
        selected_display = st.selectbox("🎯 ជ្រើសរើសសិស្ស", list(display_to_real.keys()))
        selected_name = display_to_real[selected_display]
        
        st.write("---")
        c1, c2 = st.columns(2)
        with c1:
            gram, read, listn, hw = [st.number_input(l, 0, 100, 0) for l in ["Grammar", "Reading", "Listening", "Homework"]]
        with c2:
            vocab, speak, monthly = [st.number_input(l, 0, 100, 0) for l in ["Vocabulary", "Speaking", "Monthly"]]
        
        midterm, final = [st.number_input(l, 0, 100, 0) for l in ["Mid-term Exam", "Final Exam"]]
        
        if st.form_submit_button("Update & Save"):
            avg = (gram + vocab + speak + read + listn + hw + monthly + midterm + final) / 9
            grade = calculate_grade(avg)
            idx = st.session_state.db[st.session_state.db['Student Name'] == selected_name].index
            st.session_state.db.loc[idx, ['Level', 'Grammar', 'Vocabulary', 'Speaking', 'Reading', 'Listening', 'Daily Homework', 'Monthly Score', 'Mid-term', 'Final', 'Average (%)', 'Result Grade']] = [current_level, gram, vocab, speak, read, listn, hw, monthly, midterm, final, round(avg, 2), grade]
            reset_scores()
            st.rerun()

# --- ៥. MAIN PAGE: DASHBOARD WITH FILTER ---
st.title("🏫 SEG Student Management Dashboard")

if not st.session_state.db.empty:
    # --- ផ្នែក FILTER ថ្មី ---
    st.subheader("🔍 Filter & Leaderboard")
    f1, f2 = st.columns(2)
    
    with f1:
        # Filter តាម Grade
        all_grades = ["All Grades"] + sorted(st.session_state.db['Result Grade'].unique().tolist())
        selected_grade = st.selectbox("បង្ហាញតាមនិទ្ទេស (Grade)", all_grades)
    
    with f2:
        # តម្រៀបតាមពិន្ទុ
        sort_order = st.radio("តម្រៀបពិន្ទុ (Sort by Score):", ["ខ្ពស់ទៅទាប (High to Low)", "ទាបទៅខ្ពស់ (Low to High)"], horizontal=True)

    # បង្កើត DataFrame សម្រាប់បង្ហាញ (Filtered & Sorted)
    display_df = st.session_state.db.copy()
    
    if selected_grade != "All Grades":
        display_df = display_df[display_df['Result Grade'] == selected_grade]
    
    if sort_order == "ខ្ពស់ទៅទាប (High to Low)":
        display_df = display_df.sort_values(by='Average (%)', ascending=False)
    else:
        display_df = display_df.sort_values(by='Average (%)', ascending=True)

    # បង្ហាញតារាង
    st.write(f"បង្ហាញសិស្សចំនួន: **{len(display_df)}** នាក់")
    
    def color_grade(val):
        color = 'red' if val == 'F' else '#2e7d32' if 'A' in str(val) else '#ef6c00' if 'C' in str(val) else '#1565c0'
        return f'color: {color}; font-weight: bold'

    st.dataframe(display_df.style.map(color_grade, subset=['Result Grade']), use_container_width=True)

    # Download
    csv = display_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 Download This List", csv, "seg_filtered_report.csv", "text/csv")
else:
    st.info("💡 សូម Upload Excel ដើម្បីចាប់ផ្តើម")
