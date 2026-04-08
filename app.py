import streamlit as st
import pandas as pd

# ... (កូដផ្នែកខាងលើរក្សាទុកដដែល) ...

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df_upload = pd.read_csv(uploaded_file)
        else:
            df_upload = pd.read_excel(uploaded_file, engine='openpyxl')
        
        # កែសម្រួល៖ ឱ្យវាស្គាល់ទាំងអក្សរធំ និងអក្សរតូច (student name, STUDENT NAME, Student Name)
        df_upload.columns = [str(x).strip().title() for x in df_upload.columns]
        
        if "Student Name" in df_upload.columns:
            if st.sidebar.button("បញ្ចូលឈ្មោះសិស្សទាំងអស់"):
                names_to_add = df_upload["Student Name"].dropna().unique()
                for name in names_to_add:
                    if name not in st.session_state.db['Student Name'].values:
                        new_entry = pd.DataFrame([[name, "N/A", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "F"]], columns=columns)
                        st.session_state.db = pd.concat([st.session_state.db, new_entry], ignore_index=True)
                st.sidebar.success(f"បានបញ្ចូលសិស្ស {len(names_to_add)} នាក់!")
                st.rerun()
        else:
            st.sidebar.error("⚠️ សូមពិនិត្យក្បាលតារាងក្នុង Excel ត្រូវតែមានឈ្មោះថា 'Student Name'")
            st.sidebar.info("ឧទាហរណ៍៖ ក្រឡា A1 ត្រូវសរសេរថា Student Name")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

# ... (កូដផ្នែកខាងក្រោមរក្សាទុកដដែល) ...
