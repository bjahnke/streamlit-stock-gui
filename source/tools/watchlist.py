import streamlit as st
import pandas as pd
import uuid
import typing as t

# Initialize session state for watchlist if not already done
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = [{'id': str(uuid.uuid4()), 'symbol': '', 'data_source': ''}]
else:
    # Ensure all items have an 'id' key
    for item in st.session_state.watchlist:
        if 'id' not in item:
            item['id'] = str(uuid.uuid4())

# Function to add an item to the watchlist
def add_to_watchlist(symbol, data_source):
    data = {'id': str(uuid.uuid4()), 'symbol': symbol, 'data_source': data_source}
    st.session_state.watchlist.append(data)
    return data

# Function to delete an item from the watchlist
def delete_from_watchlist(index):
    st.session_state.watchlist.pop(index)

# Streamlit interface
st.title("Asset Watchlist")

class Watchlist:
    def __init__(self):
        self.watchlist = dict()



    def add(self, symbol, source, interval):
        self.watchlist[(symbol, source, interval)] = {
            'symbol': symbol,
            'source': source,
        } 

class WatchlistRow:
    def __init__(self, symbol, source):
        self.symbol = symbol
        self.source = source

def show_watchlist(watchlist):
    for i, item in enumerate(watchlist):
        pass

def display_watchlist(watchlist: dict):
    watchlist_df = pd.DataFrame.from_records(watchlist)
    cols_len = len(watchlist_df.columns)
    cols = st.columns(cols_len)
    for i, item in enumerate(watchlist):
        pass

"""

"""

# Add new asset and set focus to the new symbol field
def on_click():
    add_to_watchlist('', '')

class WatchlistManager:
    def __init__(self, columns):
        self.columns = columns + [WatchlistColumn(name='')]

    def render(self, watchlist):
        with st.expander("Watchlist", expanded=True):
            cols_len = len(self.columns)
            display_cols = st.columns(cols_len)
            for column in self.columns:
                with display_cols[self.columns.index(column)]:
                    st.write(column.name)
            
            for i, item in enumerate(watchlist):
                out_row = dict()
                display_cols = st.columns(cols_len)
                for col_idx, col in enumerate(self.columns):
                    with display_cols[col_idx]:
                        if col_idx == len(self.columns) - 1:
                            col.render_button(item, i)
                        else:
                            if col.name not in item:
                                item[col.name] = ''
                            out_row[col.name] = col.render(item, i)
                st.session_state.watchlist[i] = out_row
                st.session_state.watchlist[i]['id'] = item['id']
            st.button("Add New Asset", on_click=on_click)

class WatchlistColumn:
    def __init__(self, name, options: t.Optional[t.List]=None):
        self.name = name
        self.options = options if options is not None else []
        self.type = type

        if self.options:
            self.render = self.render_select
        else:
            self.render = self.render_text
       
    def render_button(self, item, idx):
        if st.button("Delete", key=f"delete_{item['id']}"):
            delete_from_watchlist(idx)
            st.rerun()
    
    def render_text(self, item, _=None):
        print('item:', item)
        return st.text_input(self.name , value=item[self.name], key=f"symbol_{item['id']}", label_visibility='hidden')
    
    def render_select(self, item, _=None):
        return st.selectbox(
            self.name, 
            self.options, 
            index=self.options.index(item[self.name]) if item[self.name] in self.options else 0, 
            key=f"{self.name}_{item['id']}",
            label_visibility='hidden'
        )


wm = WatchlistManager(
    columns=[
        WatchlistColumn(name='symbol'),
        WatchlistColumn(name='interval', options=['1m', '5m', '15m', '30m', '1h', '1d']),
        WatchlistColumn(name='data_source', options=['yfinance', 'coinbase', 'coingecko']),
        # WatchlistColumn(name='delete', type='button'),
    ]
)

# Display the watchlist using Streamlit columns with borders and input fields
st.subheader("Current Watchlist")
wm.render(st.session_state.watchlist)






# Set focus to the last field of the watchlist table when the page loads
if st.session_state.watchlist:
    last_item = st.session_state.watchlist[-1]


    # Display the watchlist in a dataframe
    st.subheader("Watchlist DataFrame")
    df = pd.DataFrame(st.session_state.watchlist)
    st.dataframe(df, use_container_width=True)
