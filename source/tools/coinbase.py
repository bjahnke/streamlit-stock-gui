"""
Resources:
https://stackoverflow.com/questions/76344856/retaining-changes-for-streamlit-data-editor-when-hiding-or-switching-between-wid
"""

import source.code.coinbase as cb
import streamlit as st
import pandas as pd
from time import sleep, time
from streamlit.components.v1 import html
from source.tools.utils import products_viewer
from source.code.sidebar import new_search_form
import source.code.indicators as sci
import multiprocessing
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
# Warning-causing lines of code here

@st.cache_data
def load_products():
    products = pd.DataFrame.from_records(cb.client.get_products().to_dict()['products'])
    products = products.fillna('0')
    products = products.replace('','0')
    products = products.astype({
        'product_id': 'str',
        'price_percentage_change_24h': 'float',
        'volume_24h': 'float',
        'volume_percentage_change_24h': 'float',
        # 'base_currency': 'str',
        # 'quote_currency': 'str',
        'base_increment': 'float',
        'base_min_size': 'float',
        'base_max_size': 'float',
        'quote_increment': 'float',
        'display_name': 'str',
        # 'min_market_funds': 'float',
        # 'max_market_funds': 'float',
        # 'margin_enabled': 'bool',
        # 'fx_stablecoin': 'bool',
        # 'max_slippage_percentage': 'float',
        'post_only': 'bool',
        'limit_only': 'bool',
        'cancel_only': 'bool',
        'trading_disabled': 'bool',
        'status': 'str',
        # 'status_message': 'str',
        'auction_mode': 'bool'
    })
    return products


        




products = products_viewer(config_pkl_path='cb_column_config.pkl', load_data=load_products, key='cb_products')




from source.code.sidebar import coinbase_scan_form
from source.code.settings import source_settings


def regime_scanner(symbol, largest_table, bar_count, interval):
    floor_ceiling = sci.FloorCeiling()
    coinbase_settings = source_settings.get('coinbase')
    data = coinbase_settings.get_price_history(symbol, bar_count, interval)
    largest_table = data if len(data) > len(largest_table) else largest_table
    if data.empty:
        print(f'No data for {symbol}')
        return
    try:
        floor_ceiling.update(data)
    except Exception as e:
        print(f'Could Not Process {symbol}: {e}')
        return
    floor_ceiling.tables.regime_table['symbol'] = symbol
    return floor_ceiling.tables.regime_table, largest_table

def trading_range_scanner(symbol, largest_table, bar_count, interval):
    trading_range = sci.TradingRange()
    coinbase_settings = source_settings.get('coinbase')
    data = coinbase_settings.get_price_history(symbol, bar_count, interval)
    largest_table = data if len(data) > len(largest_table) else largest_table
    if data.empty:
        print(f'No data for {symbol}')
        return
    try:
        trading_range.update(data)
    except Exception as e:
        print(f'Could Not Process {symbol}: {e}')
        return
    trading_range.tables.regime_table['symbol'] = symbol
    return trading_range.tables.regime_table, largest_table

def scan(symbols, interval, bar_count, **_):
    
    regimes = []
    largest_table = pd.DataFrame()
    for i, symbol in enumerate(symbols):
        res = regime_scanner(symbol, largest_table, bar_count, interval)
        if res is not None:
            regime_table, largest_table = res
            regimes.append(regime_table)

    regime_table = pd.concat(regimes).reset_index(drop=True)

    # express the start and end columns in datetime for readability
    regime_table.start = largest_table.loc[regime_table.start, 'Datetime'].values
    regime_table.end = largest_table.loc[regime_table.end, 'Datetime'].values

    return regime_table

def parallel_scan(symbols, interval, bar_count, num_processes=4, **kwargs):
    def worker(symbols_chunk, output):
        result = scan(symbols_chunk, interval, bar_count, **kwargs)
        output.put(result)

    chunk_size = len(symbols) // num_processes
    processes = []
    output = multiprocessing.Queue()
    for i in range(num_processes):
        chunk = symbols[i * chunk_size:(i + 1) * chunk_size]
        p = multiprocessing.Process(target=worker, args=(chunk, output))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    results = []
    while not output.empty():
        results.append(output.get())

    combined_results = pd.concat(results).reset_index(drop=True)

    print('done')
    
    return combined_results

fetch_args, cols = coinbase_scan_form()

with cols[0]:
    run_button = st.button('Run Scanner')



if run_button:
    symbols = products.loc[products.quote_currency_id == 'USD', 'product_id'].to_list()
    rg_table = parallel_scan(symbols, **fetch_args)
    rg_table.to_pickle('cb_scan.pkl')

    products_viewer('cb_scan_config.pkl', lambda: parallel_scan(symbols, **fetch_args), key='cb_scan')
else:
    try:
        products_viewer('cb_scan_config.pkl', lambda: pd.read_pickle('cb_scan.pkl'), key='cb_scan')
    except FileNotFoundError:
        pass
