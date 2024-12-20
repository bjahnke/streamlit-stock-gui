import streamlit as st
import plotly.graph_objects as go
import typing as t
from source.code.settings import source_settings, SourceOptions
from time import sleep
from requests.exceptions import HTTPError
import uuid
from source.code.components.historical_data_plot import plot_historical_data

##########################################################################################
## PART 1: Define Functions for Pulling, Processing, and Creating Techincial Indicators ##
##########################################################################################



# Calculate basic metrics from the stock data
def calculate_metrics(data):
    last_close = data['close'].iloc[-1]
    prev_close = data['close'].iloc[0]
    change = last_close - prev_close
    pct_change = (change / prev_close) * 100
    high = data['high'].max()
    low = data['low'].min()
    volume = data['volume'].sum()
    return format_float(last_close), format_float(change), format_float(pct_change), format_float(high), format_float(low), volume


def display_ticker_data(source: SourceOptions, symbol, interval, chart_type, indicators, bar_count, **kwargs):
    """
    Temporary wrapper for displaying ticker data which makes the get_price_history call. The get price history call 
    will probably moved higher up the stack in the future.
    """
    source_setting = source_settings.get_setting(source)
    try:
        data = source_setting.get_price_history(symbol, bar_count, interval)
    except HTTPError as e:
        st.error(f"Error fetching data: {e}")
        return
    
    unique_id = str(uuid.uuid4())
    key=f"{symbol}_{interval}_{unique_id}"
    
    _display_ticker_data(data, symbol, chart_type, indicators, key, **kwargs)


def _display_ticker_data(data, symbol, chart_type, indicators, key, **kwargs):

    last_close, change, pct_change, high, low, volume = calculate_metrics(data)
    
    st.markdown(f'# {symbol}')
    col1, col2, col3 = st.columns(3)
    start_date = data['Datetime'].min()
    end_date = data['Datetime'].max()
    
    col1.metric(label=f"{symbol} Last Price", value=f"{last_close} USD", delta=f"{change} ({pct_change}%)")
    col2.metric(label="Start Date", value=start_date.strftime('%Y-%m-%d %H:%M'))
    col3.metric(label="End Date", value=end_date.strftime('%Y-%m-%d %H:%M'))
    col1, col2, col3 = st.columns(3)

    fig = go.Figure()
    
    fig, indicator_data = plot_historical_data(fig, data, chart_type, indicators)

    st.plotly_chart(fig, use_container_width=True, key=key)

    fetched_data_cols = ['Datetime', 'open', 'high', 'low', 'close', 'volume']

    st.subheader('Notes')
    notes = st.text_area("Notes:", key=f"notes_{key}")
    if notes:
        st.write("Your notes:")
        st.write(notes)
    
    st.subheader('Historical Data')

    st.dataframe(data[fetched_data_cols])
    
    st.subheader('Technical Indicators')

    st.dataframe(indicator_data)

    if kwargs.get('live_data', False):
        sleep(30)
        st.rerun()


def format_float(value: float) -> str:
    """
    Format a float to:
    - Always show 2 decimal places for values >= 1.
    - Show 4 most significant decimals for values < 1.

    :param value: The float value to format.
    :return: A string representation of the formatted value.
    """
    if value >= 1:
        # Fixed format with 2 decimal places
        return f"{value:.2f}"
    else:
        # Format with 4 significant digits
        return f"{value:.4g}"
    

def dataframe_query(data, query):
    # query = st.text_input("Enter query to filter data:", key=f"{symbol}_{interval}{unique_id}")
    # if query:
    #     try:
    #         filtered_data = data.query(query)
    #     except Exception as e:
    #         st.error(f"Query failed: {e}")
    #         filtered_data = data
    # else:
    #     filtered_data = data

    # columns_to_display = [col for col in filtered_data.columns if col not in fetched_data_cols]
    pass