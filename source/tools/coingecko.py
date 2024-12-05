from pycoingecko import CoinGeckoAPI
import streamlit as st
import pandas as pd
from source.tools.utils import products_viewer

cg = CoinGeckoAPI(demo_api_key='CG-na5pJBr1tPEmg9d5i1m94Jwi')
pd.options.display.float_format = '{:,.2f}'.format

@st.cache_data
def get_products(**kwargs):
    products = pd.DataFrame.from_records(cg.get_coins_markets(vs_currency='usd', **kwargs))
    products['url'] = products['id'].apply(lambda x: f'https://www.coingecko.com/en/coins/{x}')
    products = products.fillna('0')
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
        'roi': 'object',
    })

    # def make_clickable(val):
    #     return f'<a href="{val}" target="_blank">{val.split("/")[-1]}</a>'

    # products['url'] = products['url'].apply(make_clickable)
    # products = products.style.format({'url': make_clickable})

    return products

col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 10])
search_args = {}
with col1:
    page = st.number_input('Page', min_value=1, value=1)
    search_args['page'] = page
with col2:
    per_page = st.number_input('Per Page', min_value=1, max_value=250, value=250)
    search_args['per_page'] = per_page
with col3:
    category = st.text_input('Category')
    if category:
        search_args['category'] = category
with col4:
    submit = st.button('Submit', use_container_width=True)

st.markdown('# Coin Markets')
products_viewer(config_pkl_path='cg_column_config.pkl', load_data=lambda: get_products(**search_args), key='cg_markets')

@st.cache_data
def get_coins_categories():
    return pd.DataFrame.from_records(cg.get_coins_categories())

st.markdown('# Coin Categories')
products_viewer(config_pkl_path='cg_category_column_config.pkl', load_data=get_coins_categories, key='cg_category')

