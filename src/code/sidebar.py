import streamlit as st
import src.code.display as display
import src.code.yfinance_fetch as yfinance_fetch
from src.code.settings import source_options, source_settings

def create_sidebar(new_page_name: str):

    page_name = new_page_name

    fetch_args = st.session_state.ticker_args[page_name]

    with open("new_page_template.py", "r") as file:
        file_template = file.read()

    source = fetch_args.get('source', 'yfinance')

    source = st.sidebar.selectbox('Select Data Source', source_options, index=source_options.index(fetch_args['source']), key=f'{source}.source')
    interval_options = source_settings.get_setting(source).options
    chart_type_options = ['Candlestick', 'Line']
    indicators_options = ['SMA 20', 'EMA 20', 'Trading Range']

    symbol = fetch_args.get('symbol', '')

    st.sidebar.header('Settings')
    symbol = st.sidebar.text_input('Enter Ticker', fetch_args['symbol'], key=f'{symbol}.symbol')
    bar_count = st.sidebar.slider('Enter Bar Count', min_value=100, max_value=5000, value=fetch_args['bar_count'], key=f'{symbol}.bar_count')
    interval = st.sidebar.selectbox('Select Interval', interval_options, index=interval_options.index(fetch_args['interval']), key=f'{symbol}.interval')
    chart_type = st.sidebar.selectbox('Select Chart Type', chart_type_options, index=chart_type_options.index(fetch_args['chart_type']), key=f'{symbol}.chart_type')
    indicators = st.sidebar.multiselect('Select Indicators', indicators_options, default=fetch_args['indicators'], key=f'{symbol}.indicators')
    fetch_args["symbol"] = symbol
    fetch_args["interval"] = interval
    fetch_args["chart_type"] = chart_type
    fetch_args["indicators"] = indicators
    fetch_args["bar_count"] = bar_count
    fetch_args["source"] = source

    display.display_ticker_data(**fetch_args)

    if st.sidebar.button('Refresh'):
        display.display_ticker_data(**fetch_args)
