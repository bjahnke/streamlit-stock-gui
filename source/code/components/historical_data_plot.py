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
from time import sleep
from requests.exceptions import HTTPError
import uuid

def plot_historical_data(fig, data, chart_type, indicators):
    """
    @param data: The historical data to plot.
    @param chart_type: The type of chart to plot. Either 'Candlestick' or 'Line'.
    """
    # Plot the stock price chart
    x  = data['Datetime']
    if chart_type == 'Candlestick':
        fig.add_trace(go.Candlestick(x=x,
                                     open=data['open'],
                                     high=data['high'],
                                     low=data['low'],
                                     close=data['close']))
    else:
        fig = px.line(data, x='Datetime', y='close')

    indicator_data = sci.IndicatorManager.plot(fig, x, data, indicators)

    fig.update_layout(title=f'Price Chart',
                      xaxis_title='Time',
                      yaxis_title='Price (USD)',
                      autosize=True,
                      height=800)
    
    return fig, indicator_data