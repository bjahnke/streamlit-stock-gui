"""
This module provides functionality to interact with the CoinGecko API to fetch cryptocurrency data, including price history, product listings, and category relations.

Modules and Libraries Used:
- pycoingecko: For interacting with the CoinGecko API.
- pandas: For data manipulation and analysis.
- json: To parse JSON data.
- time: To introduce delays between API requests.
- requests.exceptions: To handle HTTP errors.

Classes and Functions:
- get_price_history(symbol, bars=None, *__, **_):
    Fetches historical price data for a given cryptocurrency symbol.

- get_products(cg_client=cg_public, **kwargs):
    Fetches a list of cryptocurrency products from CoinGecko.

- get_all_products_generator(**kwargs):
    A generator to fetch all cryptocurrency products from CoinGecko in batches.

- get_all_products(cg_client=cg_public, **kwargs):
    Fetches all cryptocurrency products from CoinGecko and returns them as a DataFrame.

- hof_retry(func, default):
    A higher-order function to retry a function until it succeeds or the maximum retries are reached.

- retry_get_products(cg_client, page, per_page, **kwargs):
    Retries fetching products from CoinGecko until successful or the maximum retries are reached.

- retry_get_product_by_id(product_id):
    Retries fetching a product by its ID from CoinGecko until successful or the maximum retries are reached.

- build_category_product_relation():
    Builds a relation between categories and products for all products listed on CoinGecko.

- category_product_relation_generator(existing_relations=None):
    A generator to yield category-product relations.

- build_category_table(product_ids):
    Builds a table mapping product IDs to categories using the CoinGecko API.

Usage:
- Ensure the CoinGecko API key is stored in 'cg_api_key.json'.
- Use the provided functions to fetch cryptocurrency data and build relations.
"""

from pycoingecko import CoinGeckoAPI
import pandas as pd
import json
from time import sleep
from requests.exceptions import HTTPError as HTTPClientError
from source.code.settings_model import FetchConfig
from datetime import datetime, timedelta


with open('cg_api_key.json', 'r') as file:
    api_keys = json.load(file)
    coingecko_key = api_keys.get('cg_key', None)

if coingecko_key is None:
    raise ValueError('CoinGecko API key not found in cg_api_key.json')

cg = CoinGeckoAPI(api_key=coingecko_key)
cg_public = CoinGeckoAPI()


# def get_price_history(symbol, bars=None, *__, **_):
#     """
#     Fetch historical price data for a given cryptocurrency symbol.

#     Parameters:
#     - symbol (str): The cryptocurrency symbol (e.g., 'bitcoin').
#     - bars (int, optional): Number of days of historical data to fetch. Defaults to None.

#     Returns:
#     - pd.DataFrame: A DataFrame containing historical price data with columns ['Datetime', 'close', 'open', 'high', 'low', 'volume'].
#     """

#     data = cg.get_coin_market_chart_by_id(id=symbol, vs_currency='usd', days=str(bars))
#     data = pd.DataFrame.from_records(data['prices'], columns=['Datetime', 'close'])
#     data['open'] = data['close']
#     data['high'] = data['close']
#     data['low'] = data['close']
#     data['volume'] = 0
#     data['Datetime'] = pd.to_datetime(data['Datetime'], unit='ms')
#     return data 

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


def _get_price_history(product_id, bar_count, fetch_config, end_date):
    start_date, end_date = get_data_range(fetch_config=fetch_config, bars=bar_count, end_date=end_date)
    data = cg.get_coin_market_chart_range_by_id(id=product_id, vs_currency='usd', from_timestamp=start_date, to_timestamp=end_date)
    # Convert each key to a DataFrame
    prices_df = pd.DataFrame(data["prices"], columns=["Datetime", "close"])
    market_caps_df = pd.DataFrame(data["market_caps"], columns=["Datetime", "mcap"])
    total_volumes_df = pd.DataFrame(data["total_volumes"], columns=["Datetime", "volume"])

    # Merge all DataFrames on the "Datetime" column
    data = prices_df.merge(market_caps_df, on="Datetime").merge(total_volumes_df, on="Datetime")

    # Convert the "Datetime" column from milliseconds to a readable datetime format
    data['open'] = data['close']
    data['high'] = data['close']
    data['low'] = data['close']
    data['Datetime'] = pd.to_datetime(data['Datetime'], unit='ms')
    return data 


def get_price_history(product_id, bars, fetch_config: FetchConfig, end_date=None):
    all_data = []
    remaining_bars = bars
    current_end_date = end_date

    bar_limit = 1000

    if fetch_config.interval == '1 hour':
        bar_limit = 2160 # this many hours in 90 days 

    while remaining_bars > 0:
        fetch_bars = min(remaining_bars, bar_limit)
        data = _get_price_history(product_id, fetch_bars, fetch_config, current_end_date)
        if data.empty:
            break
        all_data.append(data)
        remaining_bars -= fetch_bars
        current_end_date = data['Datetime'].min() - timedelta(seconds=1)
        sleep(0.1)  # Ensure we do not exceed 10 requests per second

    if not all_data:
        return pd.DataFrame(columns=['Datetime', 'low', 'high', 'open', 'close', 'volume'])
    
    res = pd.concat(all_data).sort_values(by='Datetime').reset_index(drop=True)
    res = res.astype({
        'low': 'float',
        'high': 'float',
        'open': 'float',
        'close': 'float',
        'volume': 'float',
    })
    return res

def get_products(cg_client=cg_public, **kwargs):
    """
    Fetch a list of cryptocurrency products from CoinGecko.

    Parameters:
    - cg_client (CoinGeckoAPI, optional): The CoinGecko API client. Defaults to the public client.
    - **kwargs: Additional parameters for the API request.

    Returns:
    - pd.DataFrame: A DataFrame containing product data with various attributes such as 'id', 'symbol', 'name', 'current_price', etc.
    """
    products = pd.DataFrame.from_records(cg_client.get_coins_markets(vs_currency='usd', **kwargs))
    if products.empty:
        return products
    products['url'] = products['id'].apply(lambda x: f'https://www.coingecko.com/en/coins/{x}')
    products.roi = products.roi.apply(json.dumps)
    # products = products.fillna('0')
    products.market_cap_rank = products.market_cap_rank.fillna(-1)
    products = products.astype({
        'id': 'string',
        'symbol': 'string',
        'name': 'string',
        'current_price': 'float',
        'market_cap': 'float',
        'market_cap_rank': 'int',
        'fully_diluted_valuation': 'float',
        'total_volume': 'float',
        'high_24h': 'float',
        'low_24h': 'float',
        'price_change_24h': 'float',
        'price_change_percentage_24h': 'float',
        'market_cap_change_24h': 'float',
        'market_cap_change_percentage_24h': 'float',
        'circulating_supply': 'float',
        'total_supply': 'float',
        'max_supply': 'float',
        'ath': 'float',
        'ath_change_percentage': 'float',
        'atl': 'float',
        'atl_change_percentage': 'float',
    })
    return products


def get_all_products_generator(**kwargs):
    """
    Fetch all cryptocurrency products from CoinGecko using a generator to avoid memory issues.

    Parameters:
    - **kwargs: Additional parameters for the API request.

    Yields:
    - pd.DataFrame: A DataFrame containing product data for each batch.
    """
    per_page = min([kwargs.get('per_page', 250), 250])  # 250 is Maximum per_page value as of 12/2024
    page = kwargs.get('page', 1)

    page = 1
    per_page = 250  
    while True:
        products = get_products(**{'per_page': per_page, 'page': page, **kwargs})
        if products.empty:
            break
        yield products
        page += 1


def get_all_products(cg_client=cg_public, **kwargs) -> pd.DataFrame:
    """
    Fetch all cryptocurrency products from CoinGecko and return them as a DataFrame.

    Parameters:
    - cg_client (CoinGeckoAPI, optional): The CoinGecko API client. Defaults to the public client.
    - **kwargs: Additional parameters for the API request.

    Returns:
    - pd.DataFrame: A DataFrame containing all product data.
    """
    per_page = min([kwargs.get('per_page', 250), 250])  # 250 is Maximum per_page value as of 12/2024
    page = kwargs.get('page', 1)

    page = 1
    per_page = 250 
    products = [] 
    while True:
        print(f'\rFetching page {page}', end='')
        product_page = retry_get_products(page=page, per_page=per_page, cg_client=cg_client, **kwargs)
        if product_page.empty:
            break
        products.append(product_page)
        page += 1
    return pd.concat(products)


def hof_retry(func, default):
    """
    A higher-order function to retry a function until it succeeds or the maximum retries are reached.

    Parameters:
    - func (callable): The function to retry.
    - default: The default value to return if retries are exhausted.

    Returns:
    - callable: A wrapped function that retries the original function.
    """
    def _retry(retry_time, *args, **kwargs):
        max_retries = int(60/retry_time)
        retries = 0
        res = default
        while retries < max_retries:
            try:
                res = func(*args, **kwargs)
            except HTTPClientError:
                sleep(retry_time)
                retries += 1
                print(f'\rRetry {retries}/{max_retries}', end='')
                continue
            break
        return res
    
    return _retry

_retry_get_products = hof_retry(get_products, pd.DataFrame())

def retry_get_products(cg_client, page, per_page, **kwargs):
    """
    Retry fetching products from CoinGecko until successful or the maximum retries are reached.

    Parameters:
    - cg_client (CoinGeckoAPI): The CoinGecko API client.
    - page (int): The page number to fetch.
    - per_page (int): The number of products per page.
    - **kwargs: Additional parameters for the API request.

    Returns:
    - pd.DataFrame: A DataFrame containing product data for the specified page.
    """
    return _retry_get_products(cg_client=cg_client, retry_time=2, page=page, per_page=per_page, **kwargs)


_retry_get_product_by_id = hof_retry(cg.get_coin_by_id, {})

def retry_get_product_by_id(product_id):
    """
    Retry fetching a product by its ID from CoinGecko until successful or the maximum retries are reached.

    Parameters:
    - product_id (str): The ID of the product to fetch.

    Returns:
    - dict: A dictionary containing product data.
    """
    return _retry_get_product_by_id(retry_time=2, id=product_id)


def build_category_product_relation():
    """
    Build a relation between categories and products for all products listed on CoinGecko.

    Returns:
    - pd.DataFrame: A DataFrame containing category-product relations.
    """
    categories = cg.get_coins_categories()
    categories = pd.DataFrame(categories)
    categories = categories.dropna(subset=['market_cap'])
    categories = categories[categories['market_cap'] > 0]
    product_relations = []
    for category in categories.id:
        products = get_all_products(**{'category': category['category_id']})
        p_relation = products[['id']].rename(columns={'id': 'product_id'})
        p_relation['category_id'] = category['category_id']
        product_relations.append(p_relation)

    return pd.concat(product_relations)


def category_product_relation_generator(existing_relations=None):
    """
    Generate category-product relations.

    Parameters:
    - existing_relations (pd.DataFrame, optional): Existing relations to avoid duplication. Defaults to None.

    Yields:
    - pd.DataFrame: A DataFrame containing category-product relations for each category.
    """
    categories = cg.get_coins_categories()
    categories = pd.DataFrame(categories)
    categories = categories.dropna(subset=['market_cap'])
    categories = categories[categories['market_cap'] > 0]

    for i, cid in enumerate(categories.id):
        print(f'Processing category {cid} Number: {i}/{len(categories.id)}', end='')
        products = get_all_products(cg_client=cg, **{'category': cid})
        p_relation = products[['id']].rename(columns={'id': 'product_id'})
        p_relation['category_id'] = cid
        yield p_relation


def build_category_table(product_ids):
    """
    Build a table mapping product IDs to categories using the CoinGecko API.

    Parameters:
    - product_ids (list): A list of product IDs to map to categories.

    Returns:
    - pd.DataFrame: A DataFrame containing the product-to-category mappings.
    """
    # Initialize an empty DataFrame to store the mappings
    category_list = []

    # Iterate over product IDs and fetch categories from CoinGecko API
    total_products = len(product_ids)
    for idx, product_id in enumerate(product_ids, start=1):
        print(f'\rProcessing {idx}/{total_products}', end='')
        coin_data = retry_get_product_by_id(product_id)
        categories = coin_data.get('categories', [])
        for category in categories:
            category_list.append({'product_id': product_id, 'category': category})
    print()  # Move to the next line after the loop completes

    category_table = pd.DataFrame.from_records(category_list)
    return category_table


if __name__ == "__main__":
    res = build_category_product_relation()
    print(res)