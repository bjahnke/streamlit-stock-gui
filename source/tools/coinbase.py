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


        




products = products_viewer(config_pkl_path='cb_column_config.pkl', load_data=load_products, key='cb_products', use_container_width=True)




from source.code.sidebar import coinbase_scan_form
from source.code.settings import source_settings


def regime_scanner(data, symbol):
    floor_ceiling = sci.FloorCeiling()
    if data.empty:
        print(f'No data for {symbol}')
        return
    try:
        floor_ceiling.update(data)
    except Exception as e:
        print(f'Could Not Process {symbol}: {e}')
        return

    return floor_ceiling.tables


def scan(symbols, interval, bar_count, **_):
    trading_range = sci.TradingRangePeak(peak_window=3)
    regimes = []
    range_values = pd.DataFrame(columns=['symbol', 'tr_signal'])
    largest_table = pd.DataFrame()
    coinbase_settings = source_settings.get('coinbase')
    for i, symbol in enumerate(symbols):
        data = coinbase_settings.get_price_history(symbol, bar_count, interval)
        largest_table = data if len(data) > len(largest_table) else largest_table
        tables = regime_scanner(data, symbol)
        if tables is not None:
            regimes.append(tables.regime_table)
            tables.regime_table['symbol'] = symbol
        
            res = trading_range.update(data, tables.peak_table)
            range_values.loc[len(range_values)] = {'symbol': symbol, 'tr_signal': res['tr_signal'].iloc[-2]}

    regime_table = pd.concat(regimes).reset_index(drop=True)

    # express the start and end columns in datetime for readability
    regime_table.start = largest_table.loc[regime_table.start, 'Datetime'].values
    regime_table.end = largest_table.loc[regime_table.end, 'Datetime'].values

    return regime_table, range_values

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

    regimes = []
    ranges = []
    while not output.empty():
        regime_table, range_values = output.get()
        regimes.append(regime_table)
        ranges.append(range_values)

    combined_results = pd.concat(regimes).reset_index(drop=True)
    combined_ranges = pd.concat(ranges).reset_index(drop=True)

    max_date = combined_results['end'].max()
    current_regimes = combined_results[combined_results['end'] == max_date]
    combined_ranges = combined_ranges.merge(current_regimes[['symbol', 'rg']], on='symbol', how='left').dropna()

    print('done')
    
    return combined_results, combined_ranges

fetch_args, cols = coinbase_scan_form()

with cols[0]:
    run_button = st.button('Run Scanner')



if run_button:
    symbols = products.loc[products.quote_currency_id == 'USD', 'product_id'].to_list()
    _rg_table, _range_table = parallel_scan(symbols, **fetch_args)
    _rg_table.to_pickle('cb_scan.pkl')
    _range_table.to_pickle('cb_scan_range.pkl')

    products_viewer('cb_scan_config.pkl', lambda: _rg_table, key='cb_scan', use_container_width=True)
    products_viewer('cb_scan_range_config.pkl', lambda: _range_table, key='cb_scan_range')
else:
    try:
        products_viewer('cb_scan_config.pkl', lambda: pd.read_pickle('cb_scan.pkl'), key='cb_scan', use_container_width=True)
        products_viewer('cb_scan_range_config.pkl', lambda: pd.read_pickle('cb_scan_range.pkl'), key='cb_scan_range')
    except FileNotFoundError:
        pass
