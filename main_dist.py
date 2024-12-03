import os
import sys

if getattr(sys, 'frozen', False):  # Check if running as a PyInstaller executable
    script_path = os.path.join(os.path.dirname(sys.executable), "main.py")
else:  # Running as a regular Python script
    script_path = __file__

# Run Streamlit
os.system(f"streamlit run {script_path}")