import streamlit as st
import os
import json
from pathlib import Path

def load_api_file(file_path):
    """
    Loads an API key from a specified file, sets it as an environment variable,
    and saves the file path to a JSON configuration file.
    Args:
        file_path (str): The path to the file containing the API key.
    Raises:
        Exception: If there is an error reading the file or writing to the JSON configuration file.
    Side Effects:
        - Sets the 'COINBASE_API_KEY' environment variable.
        - Writes the API key file path to a JSON configuration file.
        - Displays success or error messages using Streamlit.
    Streamlit Messages:
        - st.success: If the API key is successfully loaded and saved.
        - st.error: If there is an error during the process.
    """
    try:
        with open(file_path, 'r') as file:
            os.environ['COINBASE_API_KEY'] = file_path
            config_path = Path('.') / 'api_path.json'
            with open(config_path, 'w') as path_file:
                json.dump({"api_path": file_path}, path_file)
            st.success("API key path saved to JSON file.")
    except Exception as e:
        st.error(f"Error loading API file: {e}")

st.title("Coinbase API Configuration")

file_path = st.text_input("Enter the path to your local Coinbase API file:")


if st.button("Load API Key"):
    load_api_file(file_path)