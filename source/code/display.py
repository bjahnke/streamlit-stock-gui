import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import pytz
import ta
import typing as t
from source.utils import save_ticker_args
import source.code.yfinance_fetch as yfinance_fetch
from source.code.settings import source_settings, Settings, SourceOptions
import src.floor_ceiling_regime


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
    return round(data, 5)


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

# Add simple moving average (SMA) and exponential moving average (EMA) indicators
def add_technical_indicators(data):
    data['SMA_20'] = data.close.rolling(window=20).mean()
    data['EMA_20'] = data.close.ewm(span=20, adjust=False).mean()
    return data

def trading_range(data, window):
    data['High_Rolling'] = data['close'].rolling(window=window).max()
    data['Low_Rolling'] = data['close'].rolling(window=window).min()
    data['trading_range'] = (data.High_Rolling - data.Low_Rolling)
    data['trading_range_lo_band'] = data.Low_Rolling + data.trading_range * .61
    data['trading_range_hi_band'] = data.Low_Rolling + data.trading_range * .40
    data['trading_range_23'] = data.Low_Rolling + data.trading_range * .23
    data['trading_range_76'] = data.Low_Rolling + data.trading_range * .76
    return data

def sidebar(symbol, bar_count, period, chart_type, indicators):
    st.sidebar.header('Settings')
    symbol = st.sidebar.text_input('Enter Ticker', symbol)
    bar_count = st.sidebar.number_input('Enter Bar Count', min_value=100, max_value=5000, value=bar_count)
    period = st.sidebar.selectbox('Select Time Period', ['1d', '1wk', '1mo', '1y', 'max'], index=0)
    chart_type = st.sidebar.selectbox('Select Chart Type', ['Candlestick', 'Line'], index=0)
    indicators = st.sidebar.multiselect('Select Indicators', ['SMA 20', 'EMA 20', 'Trading Range'])
    return symbol, period, chart_type, indicators


def display_ticker_data(source: SourceOptions, symbol, interval, chart_type, indicators, bar_count):

    source_setting = source_settings.get_setting(source)
    data = source_setting.get_price_history(symbol, bar_count, source_setting.get_setting(interval))
    
    data = add_technical_indicators(data)

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

    for indicator in indicators:
        if indicator == 'SMA 20':
            fig.add_trace(go.Scatter(x=data['Datetime'], y=data['SMA_20'], name='SMA 20'))
        elif indicator == 'EMA 20':
            fig.add_trace(go.Scatter(x=data['Datetime'], y=data['EMA_20'], name='EMA 20'))
        elif indicator == 'Trading Range':
            data = trading_range(data, 200)
            fig.add_trace(go.Scatter(x=x, y=data['High_Rolling'], name='High Rolling'))
            fig.add_trace(go.Scatter(x=x, y=data['Low_Rolling'], name='Low Rolling'))
            fig.add_trace(go.Scatter(x=x, y=data['trading_range_lo_band'], name='TR Low Band'))
            fig.add_trace(go.Scatter(x=x, y=data['trading_range_hi_band'], name='TR High Band'))
            fig.add_trace(go.Scatter(x=x, y=data['trading_range_23'], name='TR 23%'))
            fig.add_trace(go.Scatter(x=x, y=data['trading_range_76'], name='TR 76%'))
        elif indicator == 'Floor/Ceiling':
            
            fig.add_trace(go.Scatter(x=x, y=data['Floor'], name='Floor'))
            fig.add_trace(go.Scatter(x=x, y=data['Ceiling'], name='Ceiling'))
        elif indicator == 'Peaks':
            pass
        
        d = data.copy()
        d = d.reset_index().rename(columns={'index': 'bar_number'})
        tables = src.floor_ceiling_regime.fc_scale_strategy_live(d)
        # breakpoint()
        fig.add_trace(go.Scatter(x=x, y=tables.enhanced_price_data['rg'], name='RG', yaxis='y2', line=dict(color='white')))

        fig.update_layout(
        title=f'{symbol} {interval.upper()} Chart',
        xaxis_title='Time',
        yaxis_title='Price (USD)',
        yaxis2=dict(
            title='RG',
            overlaying='y',
            side='right'
        ),
        autosize=True,
        height=800
        )
        

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
    


