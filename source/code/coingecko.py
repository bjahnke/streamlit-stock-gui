from pycoingecko import CoinGeckoAPI
import pandas as pd
import json

with open('api_path.json', 'r') as file:
    api_keys = json.load(file)
    coingecko_key = api_keys.get('coingecko_key')

cg = CoinGeckoAPI(demo_api_key=coingecko_key)


def get_price_history(symbol, bars=None, *__, **_):
    data = cg.get_coin_market_chart_by_id(id=symbol, vs_currency='usd', days=str(bars))
    data = pd.DataFrame.from_records(data['prices'], columns=['Datetime', 'close'])
    data['open'] = data['close']
    data['high'] = data['close']
    data['low'] = data['close']
    data['volume'] = 0
    data['Datetime'] = pd.to_datetime(data['Datetime'], unit='ms')
    return data 
