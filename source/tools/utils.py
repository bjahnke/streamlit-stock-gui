import pickle
import streamlit as st
from pathlib import Path
import pandas as pd
import os

def save_ticker_args():
    with open("ticker_args.pkl", "wb") as f:
        pickle.dump(st.session_state.ticker_args, f)

def load_ticker_args():
    if Path("ticker_args.pkl").exists():
        with open("ticker_args.pkl", "rb") as f:
            st.session_state.ticker_args = pickle.load(f)
    else:
        st.session_state.ticker_args = dict()

def load_config(path):
    return pd.read_pickle(path)

class DataFrameQueryField:
    def __init__(self, id):
        self.query = st.text_input("Query", key=id)

    def __call__(self, df):
        if self.query:
            try:
                return df.query(self.query)
            except Exception as e:
                st.error(f"Query failed: {e}")
                return df
        return df
    
def query_call(df, query):
    if query:
        try:
            return df.query(query)
        except Exception as e:
            st.error(f"Query failed: {e}")
            return df
    return df
    
def column_filter_config(col_config, config_pkl_path, key, table_height=800):
    changed = False
    vals = []
    with st.container(height=table_height):
        for column in col_config.columns:
            val = col_config.loc['Show', column]
            after = col_config.loc['Show', column] = st.checkbox(
                label=f'{column}', 
                value=val, 
                key=f'pcg_checkbox_{column}_{key}'
            )
            vals.append(after)
            if val != after:
                changed = True
        if changed: 
            edited_columns_config = pd.DataFrame(index=['Show'], columns=col_config.columns)
            edited_columns_config.loc['Show'] = vals
            edited_columns_config.to_pickle(config_pkl_path)
            st.rerun()
    return col_config


def products_viewer(config_pkl_path, load_data, key, use_container_width=False, name=''):
    table_height = 800
    products = load_data()

    
    config_pkl_path = Path(config_pkl_path)
    key = config_pkl_path.stem
    if config_pkl_path.stem not in st.session_state:
        print('***Reloading Config From Pickle***')
        try:
            st.session_state[config_pkl_path.stem] = load_config(config_pkl_path)
        except FileNotFoundError:
            st.session_state[config_pkl_path.stem] = pd.DataFrame(columns=products.columns)
            st.session_state[config_pkl_path.stem].loc['Show'] = True

    edited_columns_config = st.session_state[config_pkl_path.stem]
    if edited_columns_config.empty:
        edited_columns_config = pd.DataFrame(columns=products.columns)
        edited_columns_config.loc['Show'] = True

    # Add any columns in products not in edited_columns_config, give them the value of True at ['Show']
    for column in products.columns:
        if column not in edited_columns_config.columns:
            edited_columns_config[column] = True
    with st.expander(name, expanded=True):
        st.markdown(
            '[Learn more about DataFrame query](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.query.html)',
            unsafe_allow_html=True
        )
        query = st.text_input("Query", key=f'{key}_query')


        col1, col2 = st.columns([1, 7])


        
        with col1:
            edited_columns_config = column_filter_config(
                edited_columns_config, 
                config_pkl_path=config_pkl_path, 
                key=key, table_height=table_height)

        
        with col2:
            filtered_products = query_call(products, query)
            visible_columns = edited_columns_config.columns[edited_columns_config.loc['Show']].tolist()

            filtered_products = filtered_products[visible_columns]

            # Apply gradient styling to float columns
            float_columns = filtered_products.select_dtypes(include=['float']).columns
            styled_df = filtered_products.style.background_gradient(subset=float_columns, cmap='viridis')

            # format floats to show commas
            styled_df = styled_df.format(precision=4, thousands=",")

            kwargs = dict()
            if 'url' in filtered_products.columns:
                kwargs['column_config'] = {
                    'url': st.column_config.LinkColumn(display_text='Link', width='small')
                }
                kwargs['column_order'] = ['url'] + [col for col in filtered_products.columns if col != 'url']
                
            st.dataframe(
                styled_df, 
                height=table_height, 
                key=key, 
                use_container_width=use_container_width,
                **kwargs
            )

    return products
        

def color_gradient(value):
    """Generate a blue to yellow color gradient based on the value."""
    if value < 0:
        blue = 255
        yellow = int(255 * (1 + value))
    else:
        yellow = 255
        blue = int(255 * (1 - value))
    return f'rgb({blue},{blue},{yellow})'

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
