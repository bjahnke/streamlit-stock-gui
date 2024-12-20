import streamlit as st
from sqlalchemy.engine import URL, create_engine

st.session_state['db_con'] = create_engine(URL.create(
    drivername="postgresql+psycopg2",
    username="postgres",
    password="password",
    host='localhost',
    port=5432,
    database="asset_analysis"
))