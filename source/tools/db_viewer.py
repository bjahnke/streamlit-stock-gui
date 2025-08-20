import streamlit as st
import source.code.display as display
import source.code.sidebar as sidebar
import pandas as pd
from sqlalchemy.orm import sessionmaker
from backend.db_setup import engine
from backend.models.models import Stock



# Create a session factory
Session = sessionmaker(bind=engine)

# Streamlit app to display Stock table
st.title("Stock Table Viewer")

# Fetch data from the Stock table
with Session() as session:
    query = session.query(Stock).all()
    data = [
        {
            "id": stock.id,
            "symbol": stock.symbol,
            "interval": stock.interval,
            "is_relative": stock.is_relative,
            "data_source": stock.data_source,
            "market_index": stock.market_index,
            "sec_type": stock.sec_type,
        }
        for stock in query
    ]

# Convert to DataFrame
stock_df = pd.DataFrame(data)

from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode

# Display the DataFrame with AgGrid
if not stock_df.empty:
    st.write("Select a Stock to View Data:")

    # Configure AgGrid options
    gb = GridOptionsBuilder.from_dataframe(stock_df)
    gb.configure_selection('single', use_checkbox=True)  # Enable row selection
    grid_options = gb.build()

    # Display the table
    grid_response = AgGrid(
        stock_df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        height=400,
        theme='streamlit',  # Use Streamlit theme
    )

    # Get the selected row
    selected_row = grid_response['selected_rows']
    if selected_row is not None:  # Ensure selected_row is not empty
        row = selected_row.iloc[0]  # Get the first selected row
        fetch_args = {
            "source": 'internal',
            "symbol": row["symbol"],
            "interval": row["interval"],
            "chart_type": "line",  # Example chart type, adjust as needed
            "indicators": [],  # Example indicators, adjust as needed
            "bar_count": 100,  # Example bar count, adjust as needed
        }

        # Display the ticker data using the display module
        fetch_args = sidebar.create_sidebar(fetch_args['symbol'])
        display.display_ticker_data(**fetch_args)