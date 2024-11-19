import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import pytz
import ta
import typing as t
from src.utils import save_ticker_args

##########################################################################################
## PART 1: Define Functions for Pulling, Processing, and Creating Techincial Indicators ##
##########################################################################################

# Fetch stock data based on the ticker, period, and interval
def fetch_stock_data(ticker, period, interval):
    end_date = datetime.now()
    if period == '1wk':
        start_date = end_date - timedelta(days=7)
        data = yf.download(ticker, start=start_date, end=end_date, interval=interval)
    else:
        data = yf.download(ticker, period=period, interval=interval)
    return round(data, 2)


def yf_download_data(tickers, bars, interval) -> pd.DataFrame:
    """
    batch download of stock history download, normalize columns
    :param tickers: list of tickers to download data
    :param bars: number of bars to download
    :param interval: interval of bars
    """
    # calculate start date by multiplying bars by interval 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk
    interval_to_timedelta = {
        '1m': timedelta(minutes=1),
        '2m': timedelta(minutes=2),
        '5m': timedelta(minutes=5),
        '10m': timedelta(minutes=10),
        '15m': timedelta(minutes=15),
        '30m': timedelta(minutes=30),
        '60m': timedelta(hours=1),
        '1h': timedelta(hours=1),
        '1d': timedelta(days=1),
        '5d': timedelta(days=5)
    }
    if interval in interval_to_timedelta:
        interval_timedelta = interval_to_timedelta[interval]
    else:
        raise ValueError("Invalid interval")

    end = datetime.now()
    start = end - (bars * interval_timedelta)

    data = yf.download(
        tickers,
        start=start,
        end=end,
        interval=interval,
    )
    return data

# Process data to ensure it is timezone-aware and has the correct format
def process_data(data):
    if data.index.tzinfo is None:
        data.index = data.index.tz_localize('UTC')
    data.index = data.index.tz_convert('US/Eastern')
    data.reset_index(inplace=True)
    data.rename(columns={'Date': 'Datetime'}, inplace=True)
    return data

# Calculate basic metrics from the stock data
def calculate_metrics(data):
    last_close = data['Close'].iloc[-1]
    prev_close = data['Close'].iloc[0]
    change = last_close - prev_close
    pct_change = (change / prev_close) * 100
    high = data['High'].max()
    low = data['Low'].min()
    volume = data['Volume'].sum()
    return last_close, change, pct_change, high, low, volume

# Add simple moving average (SMA) and exponential moving average (EMA) indicators
def add_technical_indicators(data):
    data['SMA_20'] = data.Close.rolling(window=20).mean()
    data['EMA_20'] = data.Close.ewm(span=20, adjust=False).mean()
    return data

def trading_range(data, window):
    data['High_Rolling'] = data['Close'].rolling(window=window).max()
    data['Low_Rolling'] = data['Close'].rolling(window=window).min()
    data['trading_range'] = (data.High_Rolling - data.Low_Rolling)
    data['trading_range_lo_band'] = data.Low_Rolling + data.trading_range * .61
    data['trading_range_hi_band'] = data.Low_Rolling + data.trading_range * .40
    data['trading_range_23'] = data.Low_Rolling + data.trading_range * .23
    data['trading_range_76'] = data.Low_Rolling + data.trading_range * .76
    return data



def sidebar(symbol, period, chart_type, indicators):
    st.sidebar.header('Settings')
    symbol = st.sidebar.text_input('Enter Ticker', symbol)
    period = st.sidebar.selectbox('Select Time Period', ['1d', '1wk', '1mo', '1y', 'max'], index=0)
    chart_type = st.sidebar.selectbox('Select Chart Type', ['Candlestick', 'Line'], index=0)
    indicators = st.sidebar.multiselect('Select Indicators', ['SMA 20', 'EMA 20', 'Trading Range'])
    return symbol, period, chart_type, indicators


def display_ticker_data(symbol, period, chart_type, indicators):
    interval_mapping = {
        '1d': '1m',
        '1wk': '30m',
        '1mo': '1d',
        '1y': '1d',
        'max': '1d'
    }

    data = fetch_stock_data(symbol, period, interval_mapping[period])
    data.columns = data.columns.get_level_values(0)
    data = process_data(data)
    data = add_technical_indicators(data)

    save_ticker_args()
    
    last_close, change, pct_change, high, low, volume = calculate_metrics(data)
    
    st.metric(label=f"{symbol} Last Price", value=f"{last_close} USD", delta=f"{change} ({pct_change}%)")
    col1, col2, col3 = st.columns(3)
    col1.metric("High", f"{high} USD")
    col2.metric("Low", f"{low} USD")
    col3.metric("Volume", f"{volume}")
    
    # Plot the stock price chart
    fig = go.Figure()
    if chart_type == 'Candlestick':
        fig.add_trace(go.Candlestick(x=data['Datetime'],
                                     open=data['Open'],
                                     high=data['High'],
                                     low=data['Low'],
                                     close=data['Close']))
    else:
        fig = px.line(data, x='Datetime', y='Close')

    for indicator in indicators:
        if indicator == 'SMA 20':
            fig.add_trace(go.Scatter(x=data['Datetime'], y=data['SMA_20'], name='SMA 20'))
        elif indicator == 'EMA 20':
            fig.add_trace(go.Scatter(x=data['Datetime'], y=data['EMA_20'], name='EMA 20'))
        elif indicator == 'Trading Range':
            data = trading_range(data, 256)
            fig.add_trace(go.Scatter(x=data['Datetime'], y=data['High_Rolling'], name='High Rolling'))
            fig.add_trace(go.Scatter(x=data['Datetime'], y=data['Low_Rolling'], name='Low Rolling'))
            fig.add_trace(go.Scatter(x=data['Datetime'], y=data['trading_range_lo_band'], name='TR Low Band'))
            fig.add_trace(go.Scatter(x=data['Datetime'], y=data['trading_range_hi_band'], name='TR High Band'))
            fig.add_trace(go.Scatter(x=data['Datetime'], y=data['trading_range_23'], name='TR 23%'))
            fig.add_trace(go.Scatter(x=data['Datetime'], y=data['trading_range_76'], name='TR 76%'))

    fig.update_layout(title=f'{symbol} {period.upper()} Chart',
                      xaxis_title='Time',
                      yaxis_title='Price (USD)',
                      autosize=True,
                      height=800)
    st.plotly_chart(fig, use_container_width=True)

    fetched_data_cols = ['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']
    
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
    


