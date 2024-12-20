import streamlit as st
import source.code.display as display
import source.code.sidebar as sidebar

fetch_args = sidebar.create_sidebar("aerobud")
display.display_ticker_data(**fetch_args)