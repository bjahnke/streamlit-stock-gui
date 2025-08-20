"""
This module provides functionality for creating and managing the sidebar in a Streamlit application.

Functions:
- load_saved_args(page_name): Loads or initializes saved arguments for a specific page.
- create_sidebar(new_page_name): Creates a sidebar for a new page with user-configurable options.
- hof_track_change(fetch_args): Higher-order function to track changes in user inputs.
- new_search_form(st_obj, saved_fetch_args, track_change): Renders a form for configuring search parameters in the sidebar.
- coinbase_scan_form(): Renders a form specific to Coinbase scan settings.

Usage:
- Use `create_sidebar` to dynamically generate a sidebar for a new page.
- Use `coinbase_scan_form` for Coinbase-specific configurations.
"""

import streamlit as st
import source.code.display as display
import source.code.yfinance_fetch as yfinance_fetch
from source.code.settings import source_options, source_settings
from source.code.indicators import IndicatorManager
import pandas as pd
from source.code.settings_model import FetchArgs
from source.tools.utils import save_ticker_args

def load_saved_args(page_name):
    """
    Loads or initializes saved arguments for a specific page.

    Parameters:
    - page_name (str): The name of the page for which to load or initialize arguments.

    Returns:
    - FetchArgs: The arguments for the specified page.
    """
    if 'ticker_args' not in st.session_state:
        st.session_state.ticker_args = pd.read_pickle('ticker_args.pkl')
    if page_name not in st.session_state.ticker_args:
        st.session_state.ticker_args[page_name] = {**FetchArgs(**{
            "symbol": page_name,
            "interval": "1 day",
            "chart_type": "Candlestick",
            "indicators": ['Trading Range', 'Floor/Ceiling'],
            "bar_count": 300,
            "source": "yfinance",
            'live_data': False
        })}
    elif isinstance(st.session_state.ticker_args[page_name], dict):
        st.session_state.ticker_args[page_name] = {**FetchArgs(**st.session_state.ticker_args[page_name])}
    else:
        st.session_state.ticker_args[page_name] = {**FetchArgs.migrate(st.session_state.ticker_args[page_name])}

    st.session_state.ticker_args[page_name] = {**FetchArgs.migrate(st.session_state.ticker_args[page_name])}
    print(st.session_state.ticker_args[page_name])
    return FetchArgs(**st.session_state.ticker_args[page_name])


def create_sidebar(new_page_name: str):
    """
    Creates a sidebar for a new page with user-configurable options.

    Parameters:
    - new_page_name (str): The name of the new page.

    Returns:
    - dict: The updated fetch arguments for the page.
    """
    saved_fetch_args = load_saved_args(new_page_name)
    track_change = hof_track_change(st.session_state.ticker_args[new_page_name])
    fetch_args = new_search_form(st.sidebar, saved_fetch_args=saved_fetch_args, track_change=track_change)
    save_ticker_args()
    return fetch_args


def hof_track_change(fetch_args):
    """
    Higher-order function to track changes in user inputs.

    Parameters:
    - fetch_args (dict): The current fetch arguments.

    Returns:
    - function: A function to track changes for a specific input field.
    """
    def track_change(key, input_field):
        result = input_field(fetch_args[key], f'{key}')
        if key == 'indicators':
            print(fetch_args[key])
        if result != fetch_args[key]:
            fetch_args[key] = result
            st.rerun()
    return track_change


def new_search_form(st_obj, saved_fetch_args, track_change):
    """
    Renders a form for configuring search parameters in the sidebar.

    Parameters:
    - st_obj (Streamlit object): The Streamlit object to render the form.
    - saved_fetch_args (dict): The saved fetch arguments.
    - track_change (function): A function to track changes in input fields.

    Returns:
    - dict: The updated fetch arguments.
    """
    fetch_args = saved_fetch_args 
    source = fetch_args.get('source', 'yfinance')
    interval_settings = source_settings.get_setting(source)
    bar_settings = interval_settings._bar_settings
    chart_type_options = ['Candlestick', 'Line']
    indicators_options = IndicatorManager.options()
    st_obj.header('Settings')

    print(fetch_args)

    track_change(
        input_field=lambda x, y: st_obj.selectbox('Select Data Source', source_options, index=source_options.index(x), key=y), 
        key='source')
    track_change(
        input_field=lambda x, y: st_obj.text_input('Enter Ticker', x, key=y), 
        key='symbol')
    track_change(
        input_field=lambda x, y: st_obj.slider('Enter Bar Count', min_value=bar_settings.min_bars, max_value=bar_settings.max_bars, value=x, key=y), 
        key='bar_count')
    track_change(
        input_field=lambda x, y: st_obj.selectbox('Select Interval', interval_settings.options, index=interval_settings.get_index(x), key=y), 
        key='interval')
    track_change(
        input_field=lambda x, y: st_obj.selectbox('Select Chart Type', chart_type_options, index=chart_type_options.index(x), key=y), 
        key='chart_type')
    track_change(
        input_field=lambda x, y: st_obj.multiselect('Select Indicators', indicators_options, default=x, key=y), 
        key='indicators')
    track_change(
        input_field=lambda x, y: st_obj.checkbox('Live Data', value=x, key=y), 
        key='live_data')
    
    if st_obj.button('Refresh'):
        display.display_ticker_data(**fetch_args)

    return fetch_args


def coinbase_scan_form():
    """
    Renders a form specific to Coinbase scan settings.

    Returns:
    - tuple: The fetch arguments and the layout columns for the form.
    """
    fetch_args = load_saved_args('coinbase')
    track_change = hof_track_change(st.session_state.ticker_args['coinbase'])
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