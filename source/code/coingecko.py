from pycoingecko import CoinGeckoAPI
import pandas as pd
import json

with open('api_path.json', 'r') as file:
    api_keys = json.load(file)
    coingecko_key = api_keys.get('coingecko_key')

cg = CoinGeckoAPI(demo_api_key=coingecko_key)


def get_price_history(symbol, bars=None, *__, **_):
    """
    Get price history for a given symbol
    """
    data = cg.get_coin_market_chart_by_id(id=symbol, vs_currency='usd', days=str(bars))
    data = pd.DataFrame.from_records(data['prices'], columns=['Datetime', 'close'])
    data['open'] = data['close']
    data['high'] = data['close']
    data['low'] = data['close']
    data['volume'] = 0
    data['Datetime'] = pd.to_datetime(data['Datetime'], unit='ms')
    return data 


def get_products(**kwargs):
    products = pd.DataFrame.from_records(cg.get_coins_markets(vs_currency='usd', **kwargs))
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
    get all products listed on coingecko
    Use generator to avoid memory issues
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

from time import sleep
from requests.exceptions import HTTPError as HTTPClientError
def get_all_products(**kwargs) -> pd.DataFrame:
    """
    get all products listed on coingecko
    """
    per_page = min([kwargs.get('per_page', 250), 250])  # 250 is Maximum per_page value as of 12/2024
    page = kwargs.get('page', 1)

    page = 1
    per_page = 250 
    products = [] 
    while True:
        product_page = retry_get_products(2, page, per_page, **kwargs)
        if product_page.empty:
            break
        products.append(product_page)
        page += 1
    return pd.concat(products)


def retry_get_products(retry_time, page, per_page, **kwargs):
    """
    Retry get_products until it returns a non-empty DataFrame,
    Sometimes we'll hit a rate limit (30 per minute with Demo API key),
    Retry for up to a minute before giving up (at that point there is likely a different issue)
    """
    max_retries = int(60/retry_time)
    retries = 0
    product_page = pd.DataFrame()
    while retries < max_retries:
        try:
            product_page = get_products(**{'per_page': per_page, 'page': page, **kwargs})
        except HTTPClientError:
            sleep(retry_time)
            retries += 1
            print(f'\rRetry Products Fetch {retries}/{max_retries}', end='')
            continue
        break

    return product_page


def build_category_product_relation():
    """
    Build a relation between categories and products for all products listed on coingecko
    """
    categories = cg.get_coins_categories_list()
    product_relations = []
    for category in categories:
        products = get_all_products(**{'category': category['category_id']})
        p_relation = products[['id']].rename(columns={'id': 'product_id'})
        p_relation['category_id'] = category['category_id']
        product_relations.append(p_relation)

    return pd.concat(product_relations)
