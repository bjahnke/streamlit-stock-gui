import os
import dotenv
dotenv.load_dotenv()
cmc_api_key = os.getenv('CMC_API_KEY')
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

class CoinMarketCapClient:
    def __init__(self, api_key, base_url='https://pro-api.coinmarketcap.com'):
        self.api_key = api_key
        self.base_url = base_url
        self.session = Session()
        self.session.headers.update({
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': self.api_key,
        })

    def get_listings(self, start=1, limit=100, convert='USD'):
        url = f"{self.base_url}/v1/cryptocurrency/listings/latest"
        params = {
            'start': str(start),
            'limit': str(limit),
            'convert': convert
        }
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print(e)
            return None

    def get_info(self, symbol=None, id=None):
        """
        Get static metadata for one or more cryptocurrencies.
        You can specify either symbol (e.g., 'BTC') or id (e.g., 1).
        """
        url = f"{self.base_url}/v1/cryptocurrency/info"
        params = {}
        if symbol:
            params['symbol'] = symbol
        if id:
            params['id'] = str(id)
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print(e)
            return None

    def get_quote(self, symbol=None, id=None, convert='USD'):
        """
        Get the latest price and market data for one or more cryptocurrencies.
        You can specify either symbol (e.g., 'BTC') or id (e.g., 1).
        """
        url = f"{self.base_url}/v1/cryptocurrency/quotes/latest"
        params = {'convert': convert}
        if symbol:
            params['symbol'] = symbol
        if id:
            params['id'] = str(id)
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print(e)
            return None
        
    def get_quotes_historical(
            self, 
            symbol=None, 
            id=None, 
            convert='USD', 
            time_start=None, 
            time_end=None,
            interval='daily'  # Default interval is 1 day
    
    ):
        """
        Get historical data for one or more cryptocurrencies.
        You can specify either symbol (e.g., 'BTC') or id (e.g., 1).

        Parameters:
        - symbol: The symbol of the cryptocurrency (e.g., 'BTC').
        - id: The ID of the cryptocurrency (e.g., 1).
        - convert: The currency to convert to (default is 'USD').
        - time_start: The start time for the historical data (optional).
        - time_end: The end time for the historical data (optional).
        - interval: 'daily', 'hourly', 'weekly', 'monthly', 'yearly'
        """
        url = f"{self.base_url}/v2/cryptocurrency/quotes/historical"
        params = {'convert': convert}
        if symbol:
            params['symbol'] = symbol
        if id:
            params['id'] = str(id)
        if time_start:
            params['time_start'] = time_start
        if time_end:
            params['time_end'] = time_end
        if interval:
            params['interval'] = interval
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print(e)
            return {}


client = CoinMarketCapClient(cmc_api_key)

from source.code.settings_model import FetchConfig
import pandas as pd

def get_price_history(symbol: str, bars: int, fetch_config: FetchConfig) -> pd.DataFrame:
    if fetch_config.interval == 'daily':
        bars = min(bars, 365)  # API limits hobbyist to 365 days
    
    start_date, end_data = fetch_config.get_data_range(bars)
    interval = fetch_config.interval

    client = CoinMarketCapClient(api_key=cmc_api_key)
    json_quotes = client.get_quotes_historical(
        symbol=symbol,
        interval=interval,
        time_start=start_date,
        time_end=end_data
    )['data'][symbol][0]['quotes']
    records = []
    for q in json_quotes:
        usd = q.get('quote', {}).get('USD', {})
        # Optionally add timestamp or other top-level fields
        if 'timestamp' in q:
            usd['timestamp'] = q['timestamp']
        records.append(usd)

    df = pd.DataFrame.from_records(records)

    # Convert timestamp to datetime if present
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.rename(columns={'timestamp': 'Datetime'})

    if 'price' in df.columns:
        df = df.rename(columns={'price': 'close'})
        df['open'] = df['close']
        df['high'] = df['close']
        df['low'] = df['close']
        df['volume'] = 0


    return df

if __name__ == "__main__":
    # Example usage:
    cmc_client = CoinMarketCapClient(cmc_api_key)
    listings = cmc_client.get_listings(limit=10)

    info = cmc_client.get_info(symbol='BTC')
    quote = cmc_client.get_quote(symbol='BTC')
    # print(json.dumps(listings, indent=2))
    # print(info)
    print(json.dumps(quote, indent=2))