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
from dataclasses import dataclass
import source.code.settings_model as settings_model
from source.code.settings_model import FetchConfig


def granularity_to_datetime(granularity: str, bar_count: int):
    """translate coinbase ENUM granularity to a datetime timedelta"""
    if granularity == 'ONE_MINUTE':
        return timedelta(minutes=bar_count)
    elif granularity == 'FIVE_MINUTE':
        return timedelta(minutes=5*bar_count)
    elif granularity == 'FIFTEEN_MINUTE':
        return timedelta(minutes=15*bar_count)
    elif granularity == 'ONE_HOUR':
        return timedelta(hours=bar_count)
    elif granularity == 'SIX_HOUR':
        return timedelta(hours=6*bar_count)
    elif granularity == 'ONE_DAY':
        return timedelta(days=1*bar_count)
    else:
        raise ValueError('Granularity not supported')
    


# Process data to ensure it is timezone-aware and has the correct format
def process_data(data):
    if data.index.tzinfo is None:
        data.index = data.index.tz_localize('UTC')
    data.index = data.index.tz_convert('US/Eastern')
    data.reset_index(inplace=True)
    data.rename(columns={'Date': 'Datetime'}, inplace=True)
    return data


def get_price_history(tickers, bars, fetch_config: FetchConfig, end_date=None) -> pd.DataFrame:
    """
    batch download of stock history download, normalize columns
    :param tickers: list of tickers to download data
    :param bars: number of bars to download
    :param interval: interval of bars
    """
    # calculate start date by multiplying bars by interval 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk
    end = datetime.now()
    start = end - (bars * fetch_config.timedelta)

    data = yf.download(
        tickers,
        start=start,
        end=end,
        interval=fetch_config.interval,
    )
    if data is None:
        raise ValueError('Yfinance download attempt has returned None')
    
    data = data.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'})
    data = process_data(round(data, 5))
    data.columns = data.columns.get_level_values(0)
    return data