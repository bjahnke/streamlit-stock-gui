"""
Resources:
https://stackoverflow.com/questions/76344856/retaining-changes-for-streamlit-data-editor-when-hiding-or-switching-between-wid
"""

import source.code.coinbase as cb
import streamlit as st
import pandas as pd
import pickle
import os
from time import sleep, time
from streamlit.components.v1 import html

@st.cache_data
def load_products():
    products = pd.DataFrame.from_records(cb.client.get_products().to_dict()['products'])
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



@st.cache_data
def load_config():
    return pd.read_pickle('column_config.pkl')

def main():
    table_height = 800
    products = load_products()
    
    if 'products_columns_config' not in st.session_state:
        print('***Reloading Config From Pickle***')
        st.session_state.products_columns_config = load_config()

    edited_columns_config = st.session_state.products_columns_config
    if edited_columns_config is None or edited_columns_config.empty:
        edited_columns_config = pd.DataFrame(columns=products.columns)
        edited_columns_config.loc['Show'] = True

    st.markdown(
        '[Learn more about DataFrame query](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.query.html)',
        unsafe_allow_html=True
    )
    query = st.text_input("Query")

    def save_config():
        edited_columns_config.to_pickle('column_config.pkl')

    # before = edited_columns_config.copy()
    # # edited_columns_config = st.data_editor(edited_columns_config, key='pcg')
    # after = edited_columns_config.copy()

    # save = st.button('Save Config')
    # if save:
    #     if not before.equals(after):
    #         st.session_state.products_columns_config = edited_columns_config
    #         st.session_state.products_columns_config.to_pickle('column_config.pkl')
    #         st.rerun()

    #     st.session_state.products_columns_config = edited_columns_config
    #     st.session_state.products_columns_config.to_pickle('column_config.pkl')

    col1, col2 = st.columns([1, 7])

    vals = []
    changed = False
    with col1:
        with st.container(height=table_height):
            for column in edited_columns_config.columns:
                val = edited_columns_config.loc['Show', column]
                after = edited_columns_config.loc['Show', column] = st.checkbox(
                    label=f'{column}', 
                    value=val, 
                    key=f'pcg_checkbox_{column}'
                )
                vals.append(after)
                if val != after:
                    changed = True
            if changed: 
                st.session_state.products_columns_config = pd.DataFrame(index=['Show'], columns=edited_columns_config.columns)
                st.session_state.products_columns_config.loc['Show'] = vals
                st.session_state.products_columns_config.to_pickle('column_config.pkl')
                st.rerun()
    

    with col2:
        if query:
            try: 
                filtered_products = products.query(query)
            except Exception as e:
                st.error(f"Query failed: {e}")
                filtered_products = products
        else:
            filtered_products = products

        visible_columns = edited_columns_config.columns[edited_columns_config.loc['Show']].tolist()
        filtered_products = filtered_products[visible_columns]

        st.dataframe(filtered_products, height=table_height, key='products', use_container_width=True)

    if query:
        try: 
            filtered_products = products.query(query)
        except Exception as e:
            st.error(f"Query failed: {e}")
            filtered_products = products
    else:
        filtered_products = products

    visible_columns = edited_columns_config.columns[edited_columns_config.loc['Show']].tolist()
    filtered_products = filtered_products[visible_columns]

    # st.dataframe(filtered_products, height=800, key='products')


def get_column_config_path():
    return os.path.join(os.path.dirname(__file__), 'column_config.pkl')

def load_column_config():
    path = get_column_config_path()
    if os.path.exists(path):
        with open(path, 'rb') as f:
            return pickle.load(f)

def save_column_config(df):
    path = get_column_config_path()
    with open(path, 'wb') as f:
        pickle.dump(df, f)
        f.flush()
        os.fsync(f.fileno())

main()