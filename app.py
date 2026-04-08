import streamlit as st
import pandas as pd
import plotly.express as px

# ១. ការកំណត់ទំព័រ
st.set_page_config(page_title="SEG Grading System", page_icon="🏫", layout="wide")

# ២. ឈ្មោះ File Logo
LOGO_FILE = "logo.png" 

# ៣. CSS
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 8px; background-color: #003057; color: white; }
    .footer-text { text-align: center; color: #666; padding: 20px; border-top: 1px solid #eee; margin-top: 50px; }
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

# ៥. Session State Setup
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=['Student Name', 'Level', 'Grammar', 'Vocabulary', 'Speaking', 'Reading', 'Listening', 'Daily Homework', 'Monthly Score', 'Mid-term', 'Final', 'Average (%)', 'Result Grade'])

if 'form_key' not in st.session_state: st.session_state.form_key = 0

# --- ៦. SIDEBAR ---
col_s1, col_s2, col_s3 = st.sidebar.columns([1, 2, 1])
with col_side2:
    try: st.image(LOGO_FILE, use_container_width=True)
    except: st.write("🏫")

st.sidebar.markdown("<h2 style='text-align: center;'>SEG Manager</h2>", unsafe_allow_html=True)
st.sidebar.divider()

# Upload
uploaded_file = st.sidebar.file_uploader("Upload Excel/CSV", type=['xlsx', 'csv'])
if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
        df.columns = [str(x).strip().title() for x in df.columns]
        if "Student Name" in df.columns:
            if st.sidebar.button("បញ្ចូលឈ្មោះសិស្ស"):
                for name in df["Student Name"].dropna().unique():
                    if name not in st.session_state.db['Student Name'].values:
                        new_row = pd.DataFrame([[name, "N/A", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "F"]], columns=st.session_state.db.columns)
                        st.session_state.db = pd.concat([st.session_state.db, new_row], ignore_index=True)
                st.rerun()
    except Exception as e: st.sidebar.error(f"Error: {e}")

# បញ្ចូលពិន្ទុ
if not st.session_state.db.empty:
    levels = ["K1", "K2", "K3", "K4"] + [f"Level {i}" for i in range(1, 13)]
    sel_level = st.sidebar.selectbox("📚 Select Level", levels)
    
    student_status = {f"{'✅ ' if r['Average (%)'] > 0 else '🔴 '}{r['Student Name']}": r['Student Name'] for _, r in st.session_state.db.iterrows()}
    
    with st.sidebar.form(key=f"f_{st.session_state.form_key}"):
        sel_name = student_status[st.selectbox("🎯 ជ្រើសរើសសិស្ស", list(student_status.keys()))]
        c1, c2 = st.columns(2)
        with c1:
            g, r, l, h = [st.number_input(x, 0, 100, 0) for x in ["Grammar", "Reading", "Listening", "Homework"]]
        with c2:
            v, s, m = [st.number_input(x, 0, 100, 0) for x in ["Vocabulary", "Speaking", "Monthly"]]
        mid, fin = [st.number_input(x, 0, 100, 0) for x in ["Mid-term", "Final"]]
        
        if st.form_submit_button("Save & Update"):
            avg = (g+v+s+r+l+h+m+mid+fin)/9
            idx = st.session_state.db[st.session_state.db['Student Name'] == sel_name].index
            st.session_state.db.loc[idx, ['Level','Grammar','Vocabulary','Speaking','Reading','Listening','Daily Homework','Monthly Score','Mid-term','Final','Average (%)','Result Grade']] = [sel_level, g, v, s, r, l, h, m, mid, fin, round(avg, 2), calculate_grade(avg)]
            st.session_state.form_key += 1
            st.rerun()

# --- ៧. MAIN PAGE ---
st.markdown("<h1 style='text-align: center;'>🏫 SEG Grading Dashboard</h1>", unsafe_allow_html=True)

if not st.session_state.db.empty:
    # --- ផ្នែក PIE CHART ---
    st.write("---")
    active_data = st.session_state.db[st.session_state.db['Average (%)'] > 0]
    
    if not active_data.empty:
        st.subheader("📊 Grade Distribution Analysis")
        grade_counts = active_data['Result Grade'].value_counts().reset_index()
        grade_counts.columns = ['Grade', 'Count']
        
        fig = px.pie(grade_counts, values='Count', names='Grade', hole=0.4, 
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ មិនទាន់ឃើញមាន Pie Chart ទេ ព្រោះមិនទាន់មានសិស្សណាត្រូវបានបញ្ចូលពិន្ទុ។ សូមបញ្ចូលពិន្ទុសិស្សយ៉ាងតិចម្នាក់សិន។")

    # តារាងទិន្នន័យ
    st.subheader("🔍 Student List")
    disp = st.session_state.db.copy()
    st.dataframe(disp, use_container_width=True)

    # Export
    csv = disp.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 Download CSV", csv, "seg_report.csv", "text/csv")
else:
    st.info("💡 សូមបញ្ចូលឈ្មោះសិស្សដើម្បីចាប់ផ្តើម។")

# --- ៨. FOOTER ---
st.markdown(f'<div class="footer-text"><p>Developed by <b>CHAN Sokhoeurn, C2/DBA</b> | 2026</p></div>', unsafe_allow_html=True)
