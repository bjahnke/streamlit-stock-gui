from pycoingecko import CoinGeckoAPI
import streamlit as st
import pandas as pd
from source.tools.utils import products_viewer
from source.code.coingecko import get_products, get_all_products, category_product_relation_generator, build_category_table, cg_public
from time import sleep
import typing as tp
import source.tools.coingecko.db

cg = CoinGeckoAPI(demo_api_key='CG-na5pJBr1tPEmg9d5i1m94Jwi')
pd.options.display.float_format = '{:,.2f}'.format

@st.cache_data
def get_products_cached(**kwargs):
    print('***Fetching Coin Markets***')
    return get_products(**kwargs)

SupportedDownloadFormatsType = tp.Literal['csv', 'db', 'pkl']
def hof_download_products_process(how: SupportedDownloadFormatsType):
    """
    Higher order function to download products
    Supports downloading products in csv, pkl and db formats
    """
    if how in ['csv', 'pkl']:
        def save_products(products: pd.DataFrame):
            products.to_csv(f'products.{how}', index=False)

    elif how == 'db':
        def save_products(products: pd.DataFrame):
            products.to_sql('coin_gecko_products', con=st.session_state.db_con, if_exists='replace', index=False)
    def download_products_process():
        with st.spinner('Downloading products...'):
            products = get_all_products()
                
        with st.spinner('Saving products...'):
            save_products(products)

        st.success('Products downloaded and saved successfully')

    return download_products_process


st.markdown('# Download Products')
st.write('Download all products from CoinGecko to your connected DataBase')
SUPPORTED_FORMATS = ['db', 'csv', 'pkl']
col1, col3 = st.columns([1, 10])
with col1:
    download_format = st.selectbox('Download Format', SUPPORTED_FORMATS)
with col3:
    st.write('')
    download_all_products_button = st.button(
        label='Download All Products', 
        help='Download all product data from CoinGecko to you desired destination/format',
        on_click=hof_download_products_process(download_format)
    )

st.markdown('# Build Category Table')
if st.button('Build Category Table', help='Build a table mapping product IDs to categories using CoinGecko API'):
    with st.spinner('Building category table...'):
        # Fetch product IDs from the database
        product_ids = pd.read_sql('SELECT id FROM coin_gecko_products', con=st.session_state.db_con)['id'].tolist()
        
        category_table = build_category_table(product_ids)
        # Save the category table to the database
        category_table.to_sql('coin_gecko_product_category', con=st.session_state.db_con, if_exists='replace', index=False)
    st.success('Category table built successfully')


st.markdown('# Coin Markets')
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
    st.markdown("")
    submit = st.button('Submit', use_container_width=True, help='Click to submit')
with col5:
    col5_col1, col5_col2 = st.columns([5, 1])
    with col5_col2:
        st.markdown("")


products_viewer(config_pkl_path='cg_column_config.pkl', load_data=lambda: get_products_cached(**search_args), key='cg_markets', name='Markets')

@st.cache_data
def get_coins_categories():
    return pd.DataFrame.from_records(cg_public.get_coins_categories())

st.markdown('# Coin Categories')
if st.button('Download all Categories'):
    with st.spinner('Downloading categories...'):
        categories = get_coins_categories()
    with st.spinner('Saving categories...'):
        categories.to_sql('coin_gecko_categories', con=st.session_state.db_con, if_exists='replace', index=False)
    st.success('Categories downloaded and saved successfully')

products_viewer(config_pkl_path='cg_category_column_config.pkl', load_data=get_coins_categories, key='cg_category', name='Categories')

st.markdown('# Build Category Product Relation')
if st.button('Build Category Product Relation', help='Build a relation between categories and products for all products listed on coingecko. Store in your connected database'):
    
    with st.spinner('Building category product relation...'):
        # TODO update generator to search on specific categories or skip categeories
        for relation in category_product_relation_generator():
            relation.to_sql('coin_gecko_category_product_relation', con=st.session_state.db_con, if_exists='append', index=False)
    st.success('Category product relation built successfully')


st.markdown('# Coin Search by ID')
coin_id = st.text_input('Enter Coin ID')
if st.button('Search Coin'):
    with st.spinner('Searching for coin...'):
        coin_data = cg.get_coin_by_id(coin_id)
    st.write(coin_data['categories'])

