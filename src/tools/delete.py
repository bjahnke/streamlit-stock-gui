import streamlit as st
import os

# Directory containing the pages
views_dir = 'src/views'

# Function to delete a file
def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        st.success(f"Deleted {file_path}")
    else:
        st.error(f"File {file_path} not found")

# List all files in the views directory
files = os.listdir(views_dir)

st.title("Delete Pages")

if files:
    for file in files:
        if file not in ['__init__.py', '_config.py']:
            file_path = os.path.join(views_dir, file)
            if st.button(f"Delete {file}", key=file):
                delete_file(file_path)
                st.rerun()
else:
    st.write("No files found in the views directory.")