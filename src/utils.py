import pickle
import streamlit as st
from pathlib import Path

def save_ticker_args():
    with open("ticker_args.pkl", "wb") as f:
        pickle.dump(st.session_state.ticker_args, f)

def load_ticker_args():
    if Path("ticker_args.pkl").exists():
        with open("ticker_args.pkl", "rb") as f:
            st.session_state.ticker_args = pickle.load(f)
    else:
        st.session_state.ticker_args = dict()