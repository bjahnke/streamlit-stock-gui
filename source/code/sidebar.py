import streamlit as st
import source.code.display as display
import source.code.yfinance_fetch as yfinance_fetch
from source.code.settings import source_options, source_settings
from source.code.indicators import IndicatorManager
import pandas as pd

def load_saved_args(page_name):
    if 'ticker_args' not in st.session_state:
        st.session_state.ticker_args = pd.read_pickle('ticker_args.pkl')
    if page_name not in st.session_state.ticker_args:
        st.session_state.ticker_args[page_name] = {
            "symbol": page_name,
            "interval": "1 day",
            "chart_type": "Candlestick",
            "indicators": ['Trading Range', 'Floor/Ceiling'],
            "bar_count": 300,
            "source": "yfinance"
        }
    return st.session_state.ticker_args[page_name]


def create_sidebar(new_page_name: str):
    saved_fetch_args = load_saved_args(new_page_name)
    track_change = hof_track_change(saved_fetch_args)
    return new_search_form(st.sidebar, saved_fetch_args=saved_fetch_args, track_change=track_change)


def hof_track_change(fetch_args):
    def track_change(fetch_key, input_field):
        result = input_field(fetch_args[fetch_key], f'{fetch_key}.{fetch_key}')
        if fetch_key == 'indicators':
            print(fetch_args[fetch_key])
        if result != fetch_args[fetch_key]:
            fetch_args[fetch_key] = result
            st.rerun()
    return track_change


def new_search_form(st_obj, saved_fetch_args, track_change):

    fetch_args = saved_fetch_args 

    source = fetch_args.get('source', 'yfinance')

    interval_options = source_settings.get_setting(source).options
    chart_type_options = ['Candlestick', 'Line']
    indicators_options = IndicatorManager.options()

    st_obj.header('Settings')
    track_change(
        input_field=lambda x, y: st_obj.selectbox('Select Data Source', source_options, index=source_options.index(x), key=y), 
        fetch_key='source')
    track_change(
        input_field=lambda x, y: st_obj.text_input('Enter Ticker', x, key=y), 
        fetch_key='symbol')
    track_change(
        input_field=lambda x, y: st_obj.slider('Enter Bar Count', min_value=100, max_value=5000, value=x, key=y), 
        fetch_key='bar_count')
    track_change(
        input_field=lambda x, y: st_obj.selectbox('Select Interval', interval_options, index=interval_options.index(x), key=y), 
        fetch_key='interval')
    track_change(
        input_field=lambda x, y: st_obj.selectbox('Select Chart Type', chart_type_options, index=chart_type_options.index(x), key=y), 
        fetch_key='chart_type')
    track_change(
        input_field=lambda x, y: st_obj.multiselect('Select Indicators', indicators_options, default=x, key=y), 
        fetch_key='indicators')
    
    if st_obj.button('Refresh'):
        display.display_ticker_data(**fetch_args)

    return fetch_args


def coinbase_scan_form():
    fetch_args = load_saved_args('coinbase')
    track_change = hof_track_change(fetch_args)
    interval_options = source_settings.get_setting('coinbase').options
    
    st.markdown('### Coinbase Scan')

    form = [
        ('bar_count', lambda x, y: st.slider('Enter Bar Count', min_value=100, max_value=5000, value=x, key=y)),
        ('interval', lambda x, y: st.selectbox('Select Interval', interval_options, index=interval_options.index(x), key=y)),
    ]
    cols = st.columns([1, 1, 1])

    with cols[0]:
        [track_change(fetch_key, input_field) for fetch_key, input_field in form]
    return fetch_args, cols