import streamlit as st
import source.code.display as display
import source.code.sidebar as sidebar

fetch_args = sidebar.create_sidebar("IO-USD")
display.display_ticker_data(**fetch_args)