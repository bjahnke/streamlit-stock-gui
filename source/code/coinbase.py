"""
This module provides functionality to interact with the Coinbase API to fetch historical price data (OHLC candles) for a given trading pair.

Modules and Libraries Used:
- pandas: For data manipulation and analysis.
- datetime: To handle date and time operations.
- os: To interact with the operating system for environment variables and file paths.
- dotenv: To load environment variables from a .env file.
- requests: To handle HTTP requests.
- json: To parse JSON data.
- time: To introduce delays between API requests.
- streamlit: For displaying error messages in a Streamlit app.

Classes and Functions:
- get_price_history(product_id: str, bars: int, fetch_config: FetchConfig, end_date=None):
    Fetches historical price data for a given trading pair and returns it as a pandas DataFrame.

- _get_price_history(product_id: str, bars: int, fetch_config: FetchConfig, end_date=None):
    Helper function to fetch a specific range of historical price data from Coinbase.

Global Variables:
- key_file: Stores the Coinbase API key loaded from an environment variable or a JSON file.
- client: An instance of RESTClient initialized with the API key.

Usage:
- Ensure the Coinbase API key is stored in an environment variable or a JSON file specified in 'api_path.json'.
- Use the `get_price_history` function to fetch historical price data for a specific trading pair.

"""

import pandas as pd
from datetime import datetime, timedelta
import source.code.settings_model as settings_model
from coinbase.rest import RESTClient
from dotenv import load_dotenv
import os
from source.code.settings_model import FetchConfig
import requests
import json
import time
import streamlit as st

load_dotenv()

key_file = os.getenv('COINBASE_API_KEY')
if key_file is None:
    # Load API key path from JSON file
    config_path = os.path.join(os.path.dirname(__file__), '../../config.json')
    try:
        with open('api_path.json') as key_file_address_path:
            key_file = json.load(key_file_address_path)['api_path']

            # print(key_file)
    except FileNotFoundError:
        st.error(f"API key file not found at {config_path}")

    # raise ValueError("Coinbase API not saved, please specify the path to the API key file in config")

if key_file is not None:
    client = RESTClient(key_file=key_file)


def get_price_history(product_id: str, bars: int, fetch_config: FetchConfig, end_date=None):
    """
    Fetch historical price data for a given trading pair from Coinbase.

    Parameters:
    - product_id (str): The trading pair (e.g., 'BTC-USD').
    - bars (int): Number of data points to fetch.
    - fetch_config (FetchConfig): Configuration for fetching data, including interval and timedelta.
    - end_date (datetime, optional): The end date for the data fetch. Defaults to None.

    Returns:
    - pd.DataFrame: A DataFrame containing historical price data with columns ['Datetime', 'low', 'high', 'open', 'close', 'volume'].
    """
    all_data = []
    remaining_bars = bars
    current_end_date = end_date

    while remaining_bars > 0:
        fetch_bars = min(remaining_bars, 350)
        data = _get_price_history(product_id, fetch_bars, fetch_config, current_end_date)
        if data.empty:
            break
        all_data.append(data)
        remaining_bars -= fetch_bars
        current_end_date = data['start'].min() - timedelta(seconds=1)
        time.sleep(0.1)  # Ensure we do not exceed 10 requests per second

    if not all_data:
        return pd.DataFrame(columns=['start', 'low', 'high', 'open', 'close', 'volume'])
    
    res = pd.concat(all_data).sort_values(by='start').reset_index(drop=True)
    res = res.astype({
        'low': 'float',
        'high': 'float',
        'open': 'float',
        'close': 'float',
        'volume': 'float',
    })
    res = res.rename(columns={'start': 'Datetime'})
    return res


def get_data_range(fetch_config: FetchConfig, bars: int, end_date=None):
    """
    Calculate the start time based on the number of bars and the fetch configuration.

    Parameters:
    - fetch_config (FetchConfig): Configuration for fetching data, including interval and timedelta.
    - bars (int): Number of data points to fetch.

    Returns:
    - datetime: The calculated start time.
    """
    if end_date is None:
        end_date = datetime.now().replace(second=0, microsecond=0)
        # if "DAY" in fetch_config.interval:
        #     end_date = end_date.replace(hour=0, minute=0)
    start_date = end_date - fetch_config.timedelta * bars

    # Format start and end dates to ISO 8601 strings (YYYY-MM-DD format)
    start_date = str(int(start_date.timestamp()))
    end_date = str(int(end_date.timestamp()))
    # Fetch candles with ISO 8601 date strings
    return start_date, end_date



def _get_price_history(product_id: str, bars: int, fetch_config: FetchConfig, end_date=None):
    """
    Fetches historical price data (OHLC candles) from Coinbase for a given product.
    
    :param product_id: The trading pair (e.g., 'BTC-USD').
    :param start_date: Start date for the price history (datetime object, only date part is used).
    :param end_date: End date for the price history (datetime object, only date part is used).
    :param granularity: The time period for each candle (in seconds), e.g., 3600 for 1-hour candles.
    :return: A list of OHLC data (time, low, high, open, close, volume).
    """
    start_date, end_date = fetch_config.get_data_range(bars, end_date)

    retry = 0
    while True:
        try:
            candles = client.get_candles(
                product_id=product_id,
                start=start_date,
                end=end_date,
                granularity=fetch_config.interval
            )
            break
        except requests.exceptions.ConnectionError as e:
            if retry >= 3:
                raise e
            print(e)
            print("Retrying...")
            retry += 1
            
    price_data = pd.DataFrame(candles.to_dict()['candles'])
    price_data = price_data.iloc[::-1].reset_index(drop=True)
    if price_data.empty:
        return pd.DataFrame(columns=['start', 'low', 'high', 'open', 'close', 'volume'])
    price_data['start'] = pd.to_datetime(price_data['start'].astype(int), unit='s', origin='unix')
    return price_data