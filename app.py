import streamlit as st
import pandas as pd

# ១. ការកំណត់ទម្រង់ទំព័រ
st.set_page_config(page_title="SEG Grading System", page_icon="🏫", layout="wide")

# ២. បង្កើត Header និង Session State
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

# --- ៣. SIDEBAR: ការគ្រប់គ្រងទិន្នន័យ ---
st.sidebar.title("SEG Data Manager")

# ផ្នែក Upload Excel
uploaded_file = st.sidebar.file_uploader("Upload Excel/CSV", type=['xlsx', 'csv'])

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
                st.sidebar.success(f"បញ្ចូលសិស្ស {len(names_to_add)} នាក់រួចរាល់!")
                st.rerun()
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

st.sidebar.divider()

# ផ្នែកបញ្ចូលពិន្ទុ
st.sidebar.subheader("✍️ Step 2: Edit Score")
levels_list = ["K1", "K2", "K3", "K4", "Level 1", "Level 2", "Level 3", "Level 4", "Level 5", "Level 6", "Level 7", "Level 8", "Level 9", "Level 10", "Level 11", "Level 12"]

if not st.session_state.db.empty:
    # Sticky Level
    current_level = st.sidebar.selectbox(
        "📚 Select Level", 
        levels_list, 
        index=levels_list.index(st.session_state.selected_level)
    )
    st.session_state.selected_level = current_level

    # --- ការបង្កើត Highlight ក្នុងបញ្ជីជ្រើសរើសឈ្មោះសិស្ស ---
    # បង្កើត Dictionary ដើម្បីងាយស្រួលរកឈ្មោះដើម
    display_to_real_name = {}
    student_display_list = []

    for _, row in st.session_state.db.iterrows():
        # បើ Average > 0 មានន័យថាវាយរួចហើយ
        is_done = row['Average (%)'] > 0
        status_icon = "✅ " if is_done else "🔴 "
        display_label = f"{status_icon}{row['Student Name']}"
        
        student_display_list.append(display_label)
        display_to_real_name[display_label] = row['Student Name']

    with st.sidebar.form(key=f"score_form_{st.session_state.form_key}"):
        # បង្ហាញឈ្មោះសិស្សដែលមាន Highlight ជា Emoji 🔴 និង ✅
        selected_display = st.selectbox("🎯 ជ្រើសរើសសិស្ស (🔴=នៅសល់, ✅=រួចរាល់)", student_display_list)
        selected_name = display_to_real_name[selected_display]
        
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
            
            # កំណត់ Grade
            if avg >= 97: grade = "A+"
            elif avg >= 93: grade = "A"
            elif avg >= 90: grade = "A-"
            elif avg >= 87: grade = "B+"
            elif avg >= 83: grade = "B"
            elif avg >= 80: grade = "B-"
            elif avg >= 77: grade = "C+"
            elif avg >= 73: grade = "C"
            elif avg >= 70: grade = "C-"
            elif avg >= 67: grade = "D+"
            elif avg >= 63: grade = "D"
            elif avg >= 60: grade = "D-"
            else: grade = "F"
            
            idx = st.session_state.db[st.session_state.db['Student Name'] == selected_name].index
            st.session_state.db.loc[idx, ['Level', 'Grammar', 'Vocabulary', 'Speaking', 'Reading', 'Listening', 'Daily Homework', 'Monthly Score', 'Mid-term', 'Final', 'Average (%)', 'Result Grade']] = [st.session_state.selected_level, gram, vocab, speak, read, listn, hw, monthly, midterm, final, round(avg, 2), grade]
            
            st.sidebar.success(f"Saved: {selected_name}")
            reset_scores()
            st.rerun()

# --- ៤. MAIN PAGE ---
st.title("🏫 SEG Student Management Dashboard")

if not st.session_state.db.empty:
    st.subheader("📊 Class Results Sheet")
    st.dataframe(st.session_state.db, use_container_width=True)
    
    csv = st.session_state.db.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 Download Excel Report", csv, "seg_report.csv", "text/csv")
    
    if st.button("🗑️ Clear All Data"):
        st.session_state.db = pd.DataFrame(columns=columns)
        st.rerun()
