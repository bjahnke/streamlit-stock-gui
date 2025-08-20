import streamlit as st
import plotly.graph_objects as go
import typing as t
from source.code.settings import source_settings, SourceOptions
from time import sleep
from requests.exceptions import HTTPError
import uuid
from source.code.components.historical_data_plot import plot_historical_data
from source.code.settings_model import FetchSettings
from plotly.subplots import make_subplots


##########################################################################################
## PART 1: Define Functions for Pulling, Processing, and Creating Techincial Indicators ##
##########################################################################################



# Calculate basic metrics from the stock data
def calculate_metrics(data):
    last_close = data['close'].iloc[-1]
    prev_close = data['close'].iloc[0]
    change = last_close - prev_close
    pct_change = (change / prev_close) * 100
    high = data['high'].max()
    low = data['low'].min()
    volume = data['volume'].sum()
    return format_float(last_close), format_float(change), format_float(pct_change), format_float(high), format_float(low), volume

def plot_volume(data, key):
        volume_fig = go.Figure()
        volume_fig.add_trace(go.Bar(x=data['Datetime'], y=data['volume'], name='Volume'))
        volume_fig.update_layout(xaxis_title='Datetime', yaxis_title='Volume', template='plotly_dark')
        st.plotly_chart(volume_fig, use_container_width=True, key=f"volume_{key}")


def display_ticker_data(data, symbol, chart_type, indicators, key, **kwargs):

    last_close, change, pct_change, high, low, volume = calculate_metrics(data)
    
    st.markdown(f'# {symbol}')
    col1, col2, col3 = st.columns(3)
    start_date = data['Datetime'].min()
    end_date = data['Datetime'].max()
    
    col1.metric(label=f"{symbol} Last Price", value=f"{last_close} USD", delta=f"{change} ({pct_change}%)")
    col2.metric(label="Start Date", value=start_date.strftime('%Y-%m-%d %H:%M'))
    col3.metric(label="End Date", value=end_date.strftime('%Y-%m-%d %H:%M'))
    col1, col2, col3 = st.columns(3)

    # fig = go.Figure()
    
    #fig, indicator_data = plot_historical_data(fig, data, chart_type, indicators)

    # st.plotly_chart(fig, use_container_width=True, key=key)

    # Combine price and volume charts into a single figure
    if None and 'volume' in data.columns and any(data.volume > 0):
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, row_heights=[0.8, 0.1, 0.1], vertical_spacing=0.05)

        # Add price chart to the first row
        fig1, indicator_data = plot_historical_data(go.Figure(), data, chart_type, indicators)
        for trace in fig1.data:
            fig.add_trace(trace, row=1, col=1)

        # Add volume chart to the second row
        fig.add_trace(
            go.Bar(x=data['Datetime'], y=data['volume'], name='Volume'),
            row=2, col=1
        )



        # Update layout for combined figure
        fig.update_layout(
            title=f"{symbol} Price and Volume",
            xaxis_title="Datetime",
            yaxis_title="Price",
            xaxis2_title="Datetime",
            yaxis2_title="Volume",
            template="plotly_dark",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=800  # Increase the height of the chart
        )

        # Generate a unique key for the chart
        unique_key = f"{key}_{uuid.uuid4()}"

        # Use the unique key for the combined chart
        # st.plotly_chart(fig, use_container_width=True, key=unique_key)
    else:
        # Display only the price chart if volume is not available
        fig, indicator_data = plot_historical_data(go.Figure(), data, chart_type, indicators)
    
    
    

    # # Calculate rolling standard deviation
    # data['std_dev1'] = data['close'].rolling(window=2).std()
    # data['std_dev2'] = data['close'].rolling(window=20).std()
    # data['std_dev3'] = data['close'].rolling(window=40).std()
    # data['std_dev4'] = data['close'].rolling(window=70).std()

    # # Add standard deviation chart to the third row
    # for i in range(1, 5):
    #     fig.add_trace(
    #         go.Scatter(
    #             x=data['Datetime'],
    #             y=data[f'std_dev{i}'],
    #             mode='lines',
    #             name='Standard Deviation',
    #         ),
    #         row=3, col=1
    #     )



    st.plotly_chart(fig, use_container_width=True, key=key)
    # Check if 'volume' column exists and plot it
    # if 'volume' in data.columns and any(data.volume > 0):
    #     plot_volume(data, key)

    fetched_data_cols = ['Datetime', 'open', 'high', 'low', 'close', 'volume']

    st.subheader('Notes')
    notes = st.text_area("Notes:", key=f"notes_{key}")
    if notes:
        st.write("Your notes:")
        st.write(notes)
    
    st.subheader('Historical Data')

    st.dataframe(data[fetched_data_cols])
    
    st.subheader('Technical Indicators')

    st.dataframe(indicator_data)

    if kwargs.get('live_data', False):
        sleep(30)
        st.rerun()


def format_float(value: float) -> str:
    """
    Format a float to:
    - Always show 2 decimal places for values >= 1.
    - Show 4 most significant decimals for values < 1.

    :param value: The float value to format.
    :return: A string representation of the formatted value.
    """
    if value >= 1:
        # Fixed format with 2 decimal places
        return f"{value:.2f}"
    else:
        # Format with 4 significant digits
        return f"{value:.4g}"
    

def dataframe_query(data, query):
    # query = st.text_input("Enter query to filter data:", key=f"{symbol}_{interval}{unique_id}")
    # if query:
    #     try:
    #         filtered_data = data.query(query)
    #     except Exception as e:
    #         st.error(f"Query failed: {e}")
    #         filtered_data = data
    # else:
    #     filtered_data = data

    # columns_to_display = [col for col in filtered_data.columns if col not in fetched_data_cols]
    pass