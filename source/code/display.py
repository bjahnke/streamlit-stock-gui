from source.code.settings import SourceOptions
from source.code.components.ticker_display import display_ticker_data as display_ticker_data_new
import streamlit as st
import typing as t
from source.code.settings import source_settings, SourceOptions
from time import sleep
from requests.exceptions import HTTPError
import uuid
from source.code.components.historical_data_plot import plot_historical_data
from source.code.settings_model import FetchSettings
from backend.models.custom import MyStock
from backend.db_setup import SessionLocal
import pandas as pd
from source.code.settings import Interval

def display_ticker_data(source: SourceOptions, symbol, interval, chart_type, indicators, bar_count, **kwargs):
    source_setting: FetchSettings = source_settings.get_setting(source)
    try:
        data = source_setting.get_price_history(symbol, bar_count, interval)
    except HTTPError as e:
        st.error(f"Error fetching data: {e}")
        return

    # Add stock data to the database using MyStock.add_stock_data
    with SessionLocal() as session:
        # Create a MyStock instance (you may want to adjust attributes as needed)
        limit = bar_count
        stock = MyStock(
            symbol=symbol,
            interval=interval,
            is_relative=False,  # Set appropriate value
            data_source=str(source),  # Set appropriate value or convert as needed
            market_index="TEMP",  # Set appropriate value
            sec_type="TEMP"  # Set appropriate value
        )
        # Ensure 'data' is a DataFrame
        if not isinstance(data, pd.DataFrame):
            data = pd.DataFrame(data)


        save_data = data.rename(columns={'Datetime': 'timestamp', 'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'})
                # Ensure the column is numeric and convert from ms to datetime

        if source == SourceOptions.COINGECKO:
            save_data = save_data[:-1]  # do not save the last row, as it is not complete

        stock.add_stock_data(save_data, session)
        new_data = stock.get_stock_data(session, limit)
        new_data = new_data.rename(columns={'timestamp': 'Datetime'})
        new_data = new_data.sort_values(by="Datetime", ascending=True)
        
    unique_id = str(uuid.uuid4())
    key=f"{symbol}_{interval}_{unique_id}"
    new_data = pd.concat([new_data, data.iloc[[-1]]], ignore_index=True)
    if source == SourceOptions.CMC: 
        new_data['Datetime'] = pd.to_datetime(new_data['Datetime'], utc=True).dt.tz_localize(None)


    display_ticker_data_new(new_data, symbol, chart_type, indicators, key, **kwargs)

