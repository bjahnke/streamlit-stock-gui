import streamlit as st
import src.code.display as display

page_name = "{new_page_name}"

fetch_args = st.session_state.ticker_args[page_name]

with open("new_page_template.py", "r") as file:
    file_template = file.read()

period_options = ['1d', '1wk', '1mo', '1y', 'max']
chart_type_options = ['Candlestick', 'Line']
indicators_options = ['SMA 20', 'EMA 20', 'Trading Range']

symbol = fetch_args.get('symbol', '')

st.sidebar.header('Settings')
symbol = st.sidebar.text_input('Enter Ticker', fetch_args['symbol'], key=f'{symbol}.symbol')
period = st.sidebar.selectbox('Select Time Period', period_options, index=period_options.index(fetch_args['period']), key=f'{symbol}.period')
chart_type = st.sidebar.selectbox('Select Chart Type', chart_type_options, index=chart_type_options.index(fetch_args['chart_type']), key=f'{symbol}.chart_type')
indicators = st.sidebar.multiselect('Select Indicators', indicators_options, default=fetch_args['indicators'], key=f'{symbol}.indicators')
fetch_args["symbol"] = symbol
fetch_args["period"] = period
fetch_args["chart_type"] = chart_type
fetch_args["indicators"] = indicators

display.display_ticker_data(**fetch_args)

if st.sidebar.button('Refresh'):
    display.display_ticker_data(**fetch_args)
