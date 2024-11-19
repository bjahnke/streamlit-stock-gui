# Source: @DeepCharts Youtube Channel (https://www.youtube.com/@DeepCharts)

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import pytz
import ta
import typing as t




###############################################
## PART 2: Creating the Dashboard App layout ##
###############################################
from src.code.display import *
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# Assuming other necessary imports and functions are already defined

class TickerDataCollection:
    def __init__(self):
        self.tickers = {
            '\+ Add': AddTickerData(self.add_ticker)
        }
        self.tab_order = list(self.tickers.keys())
        self._selected_ticker = '\+ Add'

    def remove_ticker(self, symbol):
        if symbol in self.tickers and symbol != '\+ Add':
            del self.tickers[symbol]
            self.tab_order.remove(symbol)
            st.rerun()  # Re-render the sidebar

    def render(self):
        tabs = st.tabs(self.tab_order)
        active_tab = self.tickers[self.selected_ticker]
        with tabs[self.active_tab.position]:
            active_tab.render_sidebar()
            active_tab.render_data_display()

    @property
    def selected_ticker(self):
        return self._selected_ticker
    
    @selected_ticker.setter
    def selected_ticker(self, symbol):
        self._selected_ticker = symbol

    def add_ticker(self, symbol, period, chart_type, indicators):
        if symbol in self.tickers:
            return
        position = len(self.tickers) - 1
        data = TickerData(symbol, period, chart_type, indicators, position)
        self.tickers[data.symbol] = data
        self.tab_order.insert(position, data.symbol)
        self.selected_ticker = data.symbol
        st.rerun()  # Re-render the sidebar

    def update_ticker(self, data, old_symbol=None):
        ticker_data = self.tickers.get(data.symbol)
        if ticker_data:
            if old_symbol:
                del self.tickers[old_symbol]
                self.tab_order.remove(old_symbol)
            self.tickers[data.symbol] = data
            self.selected_ticker = data.symbol
            st.rerun()  # Re-render the sidebar

    def delete_ticker(self, data):
        ticker_data = self.tickers.get(data.symbol)
        if ticker_data:
            del self.tickers[data.symbol]
            self.tab_order.remove(data.symbol)
            st.experimental_rerun()  # Re-render the sidebar

class TickerData:
    def __init__(self, symbol, period, chart_type, indicators, position):
        self.symbol = symbol
        self.period = period
        self.chart_type = chart_type
        self.indicators = indicators
        self.position = position

    def render_sidebar(self):
        # Sidebar for user input parameters
        st.sidebar.header('Chart Parameters')
        period_options = ['1d', '1wk', '1mo', '1y', 'max']
        chart_type_options = ['Candlestick', 'Line']
        indicator_options = ['SMA 20', 'EMA 20', 'Trading Range']

        self.period = st.sidebar.selectbox(
            'Time Period', 
            period_options, 
            index=period_options.index(self.period), 
            key=f'{self.symbol}.time_period'
        )
        self.chart_type = st.sidebar.selectbox(
            'Chart Type', 
            chart_type_options, 
            index=chart_type_options.index(self.chart_type),
            key=f'{self.symbol}.chart_type'
        )
        self.indicators = st.sidebar.multiselect(
            'Technical Indicators', 
            indicator_options, 
            default=self.indicators, 
            key=f'{self.symbol}.indicators'
        )

    def render_data_display(self):
        st.header(f'{self.symbol} Data')
        # Placeholder for actual data display logic
        st.write(f"Displaying data for {self.symbol}")

class AddTickerData:
    def __init__(self, add_ticker_callback):
        self.add_ticker_callback = add_ticker_callback

    def render_sidebar(self):
        st.sidebar.header('Add New Ticker')
        new_symbol = st.sidebar.text_input('Ticker Symbol')
        period = st.sidebar.selectbox('Time Period', ['1d', '1wk', '1mo', '1y', 'max'])
        chart_type = st.sidebar.selectbox('Chart Type', ['Candlestick', 'Line'])
        indicators = st.sidebar.multiselect('Technical Indicators', ['SMA 20', 'EMA 20', 'Trading Range'])
        if st.sidebar.button('Add Ticker'):
            if new_symbol:
                self.add_ticker_callback(new_symbol, period, chart_type, indicators)

    def render_data_display(self):
        st.write("Add a new ticker to display its data")

def run():
    # Set up Streamlit page layout
    st.set_page_config(layout="wide")
    st.title('Real Time Stock Dashboard')
    if 'data_collection' not in st.session_state:
        st.session_state.data_collection = TickerDataCollection()

    data_collection = st.session_state.data_collection

    data_collection.render()
    

    # Sidebar for user input parameters

    # Mapping of time periods to data intervals
    # if not st.session_state.ticker_data:
    #     ticker_data = TickerData('', '1d', 'Candlestick', [])
    #     ticker_data.render_sidebar()

    # else:
    #     # Button to add a new ticker
    #     if st.sidebar.button('Update'):
    #         display_ticker_data(new_ticker, time_period, chart_type, indicators, interval_mapping)
    #         if new_ticker and new_ticker not in st.session_state.tickers:
    #             st.session_state.tickers.append(new_ticker)

    #     # Create tabs for each ticker
    #     if st.session_state.tickers:
            
    #         for i, ticker in enumerate(st.session_state.tickers):
    #             with tabs[i]:
    #                 st.header(f'{ticker} Data')
    #                 display_ticker_data(ticker, time_period, chart_type, indicators, interval_mapping)

        # new_ticker = st.text_input('new')
        # display_ticker_data(tabs[-1], time_period, chart_type, indicators, interval_mapping)
        # if st.button('Add'):
        #     if new_ticker and new_ticker not in st.session_state.tickers:
        #         st.session_state.tickers.append(new_ticker)


if __name__ == '__main__':
    run()