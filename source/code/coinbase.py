import pandas as pd
from datetime import datetime, timedelta
import source.code.settings_model as settings_model
from coinbase.rest import RESTClient
from dotenv import load_dotenv
import os
from source.code.settings_model import FetchConfig
import requests
import json
load_dotenv()

key_file = os.getenv('COINBASE_API_KEY')
if key_file is None:
    # Load API key path from JSON file
    config_path = os.path.join(os.path.dirname(__file__), '../../config.json')
    try:
        with open('api_path.json') as key_file_address_path:
            key_file = json.load(key_file_address_path)['api_path']

            print(key_file)
    except FileNotFoundError:
        raise FileNotFoundError(f"API key file not found at {config_path}")

    # raise ValueError("Coinbase API not saved, please specify the path to the API key file in config")

client = RESTClient(key_file=key_file)


def get_price_history(product_id: str, bars: int, fetch_config: FetchConfig, end_date=None):
    all_data = []
    remaining_bars = bars
    current_end_date = end_date

    while remaining_bars > 0:
        fetch_bars = min(remaining_bars, 350)
        data = _get_price_history(product_id, fetch_bars, fetch_config, current_end_date)
        all_data.append(data)
        remaining_bars -= fetch_bars
        current_end_date = data['start'].min() - timedelta(seconds=1)

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


def _get_price_history(product_id: str, bars: int, fetch_config: FetchConfig, end_date=None):
    """
    Fetches historical price data (OHLC candles) from Coinbase for a given product.
    
    :param product_id: The trading pair (e.g., 'BTC-USD').
    :param start_date: Start date for the price history (datetime object, only date part is used).
    :param end_date: End date for the price history (datetime object, only date part is used).
    :param granularity: The time period for each candle (in seconds), e.g., 3600 for 1-hour candles.
    :return: A list of OHLC data (time, low, high, open, close, volume).
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
    price_data['start'] = pd.to_datetime(price_data['start'], unit='s', origin='unix')
    return price_data