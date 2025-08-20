# TODO integrate this with models code


# class DatabaseClient:
#     def __init__(self, session: Session):
#         self.session = session

#     def push_price_history(self, data: pd.DataFrame, stock_id: int):
#         """
#         Pushes price history data to the `stock_data` and `timestamp_data` tables.

#         :param data: A pandas DataFrame containing price history. Must include:
#                      'timestamp', 'open', 'close', 'high', 'low', 'volume'.
#         :param stock_id: The ID of the stock associated with the data.
#         :raises: ValueError if required columns are missing or transaction fails.
#         """
#         required_columns = {'timestamp', 'open', 'close', 'high', 'low', 'volume'}
#         if not required_columns.issubset(data.columns):
#             raise ValueError(f"DataFrame must include columns: {required_columns}")

#         try:
#             # Prepare data for `timestamp_data`
#             timestamp_rows = [
#                 TimestampDatum(
#                     interval="1d",  # Example, adjust as needed
#                     timestamp=row['timestamp'],
#                     data_source="api_example"  # Example, adjust as needed
#                 )
#                 for _, row in data.iterrows()
#             ]
#             self.session.add_all(timestamp_rows)
#             self.session.flush()  # Get primary keys for timestamp_data

#             # Prepare data for `stock_data`
#             stock_data_rows = [
#                 StockDatum(
#                     bar_number=index + 1,  # Example bar_number, adjust as needed
#                     stock_id=stock_id,
#                     close=row['close'],
#                     open=row['open'],
#                     high=row['high'],
#                     low=row['low'],
#                     volume=row['volume'],
#                     bar_number=timestamp_row.bar_number  # Map timestamp PK
#                 )
#                 for index, (timestamp_row, (_, row)) in enumerate(zip(timestamp_rows, data.iterrows()))
#             ]
#             self.session.add_all(stock_data_rows)

#             # Commit transaction
#             self.session.commit()
#         except Exception as e:
#             self.session.rollback()
#             raise ValueError(f"Failed to push price history: {e}")




from __future__ import annotations
from backend.models.models import Stock, StockData
from sqlalchemy import text
import pandas as pd


def delete_table(session, table):
    session.execute(f"DELETE FROM {table}")
    session.commit()

def add_stock_data(stock: Stock, data, session):
    # Reformat the data to fit db model
    stock = stock.get_or_create(session)

    data = data.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'})
    data = data.reset_index().rename(columns={'Date': 'timestamp'})
    data['interval'] = stock.interval
    data['data_source'] = stock.data_source
    data['stock_id'] = stock.id
    data.to_sql('stock_data', session.bind, if_exists='append', index=False)

    return stock.id


from sqlalchemy import and_

class MyStock(Stock):
    def __init__(
            self, 
            symbol, 
            interval, 
            is_relative, 
            data_source, 
            market_index, 
            sec_type
        ):
        super().__init__(symbol=symbol, interval=interval, is_relative=is_relative, data_source=data_source, market_index=market_index, sec_type=sec_type)
    
    @classmethod
    def get_by_id(cls, session, stock_id) -> Stock:
        return session.query(cls).filter(cls.id == stock_id).first()
    
    def get_or_create(self, session) -> Stock:
        """returns data from the db if it exists, otherwise creates it"""
        if self.id:
            return self
        
        stock = session.query(Stock).filter(
            Stock.symbol == self.symbol,
            Stock.interval == self.interval,
            Stock.data_source == self.data_source,
            Stock.market_index == self.market_index,
            Stock.sec_type == self.sec_type
        ).first()
        if stock:
            self.id = stock.id
            return stock
        
        session.add(self)
        session.commit()
        return self
    
    @classmethod
    def get_column_names(cls):
        return [c.name for c in cls.__table__.columns]

    def add_stock_data(self, data: pd.DataFrame, session):
        """
        Appends new stock data to the database for the current stock instance, avoiding duplicates.

        This method takes a pandas DataFrame containing stock price data and attempts to insert it into the
        stock_data table in the database. It uses a stored procedure (insert_unique_timestamp_data) to ensure
        that only rows with unique (timestamp, stock_id) pairs are inserted—any rows where the combination of
        timestamp and stock_id already exists in the database are ignored.

        Args:
            data (pd.DataFrame): DataFrame containing stock data. Must include columns for at least 'timestamp',
                'open', 'close', 'high', 'low', 'volume', and 'stock_id'.
            session (Session): SQLAlchemy session for database operations.

        Returns:
            int: The stock ID associated with the inserted data.

        Example:
            >>> stock = MyStock(...)
            >>> stock.add_stock_data(df, session)
        """
        # Reformat the data to fit db model
        stock = self.get_or_create(session)

        # data = data.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'})
        
        # data = data.reset_index().rename(columns={'Date': 'timestamp'})
        # data['interval'] = stock.interval
        # data['data_source'] = stock.data_source
        cols = MyStockData.get_column_names()

        data = data[MyStockData.get_column_names()].copy()

        data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms', utc=True).dt.tz_localize(None)
        print(data['timestamp'])
        data['timestamp'] = normalize_timestamp(data['timestamp'], str(self.interval)).astype(str)
        print(data['timestamp'])
        data['stock_id'] = stock.id
        json_data = data.to_json(orient='records')
        session.execute(
            text("CALL insert_unique_timestamp_data(:data)"),
            {'data': json_data}
        )
        session.commit()
        return stock.id
    
    def get_stock_data(self, session, limit=1000):
        """
        Retrieves stock data for the current stock instance from the database.

        Args:
            session (Session): SQLAlchemy session for database operations.
            limit (int): Maximum number of rows to retrieve. Defaults to 1000.

        Returns:
            pd.DataFrame: DataFrame containing the stock data.
        """
        self.get_or_create(session)
        return MyStockData.get_price_history(session, self.id, limit)
    
    def create_up_sample(self, session, new_interval: str = '1 day', limit=1000) -> MyStock:
        """
        Resamples the stock data to a new interval and updates the database.

        Args:
            session (Session): SQLAlchemy session for database operations.
            new_interval (str): The new interval to resample the data to. 
                                Must be a valid interval and larger than the current interval.
            limit (int): Maximum number of rows to retrieve for resampling.

        Returns:
            MyStock: instance of MyStock with the upsampled data.
        """


        # 1. Get historical data
        historical_data = self.get_stock_data(session, limit)
        print(historical_data.head())

        # 2. Set timestamp as index and ensure it's datetime
        historical_data['timestamp'] = pd.to_datetime(historical_data['timestamp'])
        historical_data = historical_data.set_index('timestamp').sort_index()
        # 3. Resample to new interval (e.g., '1D' for daily)
        # You may want to adjust the aggregation logic as needed
        agg_dict = {
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum',
            'stock_id': 'first'
        }

        # So far, we only support '1 day' as the new interval
        resample_interval = '1D'
        if new_interval != '1 day':
            raise ValueError(f"Unsupported new interval: {new_interval}. Must be '1 day'.")
        
        upsampled = historical_data.resample(resample_interval).agg(agg_dict).dropna(subset=['open', 'close'])
        print(len(upsampled))

        # 4. Reset index to get timestamp back as a column
        upsampled = upsampled.reset_index()

        print(upsampled.head())

        # 5. Create/get new stock entry for the upsampled interval
        upsampled_stock = MyStock(
            symbol=self.symbol,
            interval=new_interval,
            is_relative=self.is_relative,
            data_source='internal',
            market_index=self.market_index,
            sec_type=self.sec_type
        )


        # 6. Store upsampled data in the database
        upsampled_stock.add_stock_data(upsampled, session)

        return upsampled_stock
        

import uuid
    

class MyStockData(StockData):

    @classmethod
    def get_column_names(cls):
        return [c.name for c in cls.__table__.columns if c.name != 'id' and c.name != 'stock_id']

    @classmethod
    def get_price_history(cls, session, id, limit=1000):
        """
        Retrieves price history for a specific stock ID.

        Args:
            session (Session): SQLAlchemy session for database operations.
            id (int): The stock ID to retrieve data for.
            limit (int): Maximum number of rows to retrieve. Defaults to 1000.

        Returns:
            pd.DataFrame: DataFrame containing the price history.
        """
        query = text("""
            SELECT * FROM stock_data
            WHERE stock_id = :stock_id
            ORDER BY timestamp DESC
            LIMIT :limit
        """)
        result = session.execute(query, {'stock_id': id, 'limit': limit})
        return pd.DataFrame(result.fetchall(), columns=result.keys())
    
from source.code.settings import Interval
def normalize_timestamp(ts: pd.Series, interval: str) -> pd.Series:
    if interval in {Interval.ONE_MINUTE, Interval.FIVE_MINUTE, Interval.FIFTEEN_MINUTE,
                    Interval.THIRTY_MINUTE, Interval.ONE_HOUR}:
        return ts.dt.floor('min')
    elif interval in {Interval.SIX_HOUR}:
        return ts.dt.floor('6H')
    elif interval == Interval.ONE_DAY:
        return ts.dt.floor('D')
    elif interval == Interval.FIVE_DAY:
        return ts.dt.floor('5D')
    elif interval == Interval.MAX:
        return ts  # leave as is
    else:
        raise ValueError(f"Unknown interval: {interval}")