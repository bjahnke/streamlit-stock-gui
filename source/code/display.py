import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import pytz
import ta
import typing as t
from source.tools.utils import save_ticker_args
import source.code.yfinance_fetch as yfinance_fetch
from source.code.settings import source_settings, Settings, SourceOptions
import src.floor_ceiling_regime
import source.code.indicators as sci


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
    return last_close, change, pct_change, high, low, volume


from requests.exceptions import HTTPError
def display_ticker_data(source: SourceOptions, symbol, interval, chart_type, indicators, bar_count):

    source_setting = source_settings.get_setting(source)

    try:
        data = source_setting.get_price_history(symbol, bar_count, interval)
    except HTTPError as e:
        st.error(f"Error fetching data: {e}")
        return

    save_ticker_args()
    
    last_close, change, pct_change, high, low, volume = calculate_metrics(data)
    
    col1, col2, col3 = st.columns(3)
    start_date = data['Datetime'].min()
    end_date = data['Datetime'].max()
    col1.metric(label=f"{symbol} Last Price", value=f"{last_close} USD", delta=f"{change} ({pct_change}%)")
    col2.metric(label="Start Date", value=start_date.strftime('%Y-%m-%d %H:%M'))
    col3.metric(label="End Date", value=end_date.strftime('%Y-%m-%d %H:%M'))
    col1, col2, col3 = st.columns(3)
    col1.metric("High", f"{high} USD")
    col2.metric("Low", f"{low} USD")
    col3.metric("Volume", f"{volume}")
    
    # Plot the stock price chart
    fig = go.Figure()
    x  = data['Datetime']
    if chart_type == 'Candlestick':
        fig.add_trace(go.Candlestick(x=x,
                                     open=data['open'],
                                     high=data['high'],
                                     low=data['low'],
                                     close=data['close']))
    else:
        fig = px.line(data, x='Datetime', y='close')

    sci.IndicatorManager.plot(fig, x, data, indicators)

    fig.update_layout(title=f'{symbol} {interval.upper()} Chart',
                      xaxis_title='Time',
                      yaxis_title='Price (USD)',
                      autosize=True,
                      height=800)
    st.plotly_chart(fig, use_container_width=True)

    fetched_data_cols = ['Datetime', 'open', 'high', 'low', 'close', 'volume']
    
    st.subheader('Historical Data')

    st.dataframe(data[fetched_data_cols])
    
    st.subheader('Technical Indicators')
    query = st.text_input("Enter query to filter data:")
    if query:
        try:
            filtered_data = data.query(query)
        except Exception as e:
            st.error(f"Query failed: {e}")
            filtered_data = data
    else:
        filtered_data = data

    columns_to_display = [col for col in filtered_data.columns if col not in fetched_data_cols]
    st.dataframe(filtered_data[columns_to_display])
    


