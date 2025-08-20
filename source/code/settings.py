"""
This module defines settings and configurations for fetching financial data from various sources.

Classes:
- Interval: Enum for time interval keys to ensure consistency and avoid typos.
- SourceOptions: Enum for supported data sources (e.g., Coinbase, Yahoo Finance, CoinGecko).
- Watchlist: Manages a collection of financial symbols to track.

Global Variables:
- source_options: A list of available data sources.
- source_settings: A dictionary mapping data sources to their respective FetchSettings.

Usage:
- Use `source_settings` to configure and fetch data from supported sources.
- Use `Watchlist` to manage and render a list of tracked financial symbols.
"""

from source.code.settings_model import FetchConfig, FetchSettings
from datetime import timedelta
from source.code.settings_model import Settings, SourceSettings
import source.code.coinbase as cb_fetch
import source.code.yfinance_fetch as yfinance_fetch
import source.code.coingecko as cg_fetch
import pycoinmarketcap
from datetime import datetime, timedelta

class Interval:
    """
    Enum for time interval keys for consistency and avoiding typos.

    Attributes:
    - ONE_MINUTE (str): Represents a 1-minute interval.
    - FIVE_MINUTE (str): Represents a 5-minute interval.
    - FIFTEEN_MINUTE (str): Represents a 15-minute interval.
    - THIRTY_MINUTE (str): Represents a 30-minute interval.
    - ONE_HOUR (str): Represents a 1-hour interval.
    - SIX_HOUR (str): Represents a 6-hour interval.
    - ONE_DAY (str): Represents a 1-day interval.
    - FIVE_DAY (str): Represents a 5-day interval.
    - MAX (str): Represents the maximum available interval.
    """
    ONE_MINUTE = '1 minute'
    FIVE_MINUTE = '5 minute'
    FIFTEEN_MINUTE = '15 minute'
    THIRTY_MINUTE = '30 minute'
    ONE_HOUR = '1 hour'
    SIX_HOUR = '6 hour'
    ONE_DAY = '1 day'
    FIVE_DAY = '5 day'
    MAX = 'max'

i = Interval

class SourceOptions:
    """
    Enum for supported data sources.

    Attributes:
    - COINBASE (str): Represents the Coinbase data source.
    - YFINANCE (str): Represents the Yahoo Finance data source.
    - COINGECKO (str): Represents the CoinGecko data source.
    """
    COINBASE = 'coinbase'
    YFINANCE = 'yfinance'
    COINGECKO = 'coingecko'
    CMC = 'coinmarketcap'

# Global Variables
source_options = [value for name, value in vars(SourceOptions).items() if not name.startswith('__')]
"""
List of available data sources.
"""


"""
Dictionary mapping data sources to their respective FetchSettings.

Keys:
- SourceOptions.COINBASE: FetchSettings for Coinbase.
- SourceOptions.YFINANCE: FetchSettings for Yahoo Finance.
- SourceOptions.COINGECKO: FetchSettings for CoinGecko.
"""
source_settings = SourceSettings({
    SourceOptions.COINBASE: FetchSettings(
        {
            i.ONE_MINUTE: FetchConfig('ONE_MINUTE', timedelta(minutes=1)),
            i.FIVE_MINUTE: FetchConfig('FIVE_MINUTE', timedelta(minutes=5)),
            i.FIFTEEN_MINUTE: FetchConfig('FIFTEEN_MINUTE', timedelta(minutes=15)),
            i.ONE_HOUR: FetchConfig('ONE_HOUR', timedelta(hours=1)),
            i.SIX_HOUR: FetchConfig('SIX_HOUR', timedelta(hours=6)),
            i.ONE_DAY: FetchConfig('ONE_DAY', timedelta(days=1)),
        }, 
        get_price_history=cb_fetch.get_price_history
    ),
    SourceOptions.YFINANCE: FetchSettings(
        {
            i.ONE_MINUTE: FetchConfig('1m', timedelta(minutes=1)),
            # '2m': timedelta(minutes=2),
            i.FIVE_MINUTE: FetchConfig('5m', timedelta(minutes=5)),
            # '10m': timedelta(minutes=10),
            i.FIFTEEN_MINUTE: FetchConfig('15m', timedelta(minutes=15)),
            i.THIRTY_MINUTE: FetchConfig('30m', timedelta(minutes=30)),
            # '60m': timedelta(hours=1),
            i.ONE_HOUR: FetchConfig('1h', timedelta(hours=1)),
            i.ONE_DAY: FetchConfig('1d', timedelta(days=1)),
            i.FIVE_DAY: FetchConfig('5d', timedelta(days=5))
        },
        get_price_history=yfinance_fetch.get_price_history
    ),
    SourceOptions.COINGECKO: FetchSettings(
        {
            i.ONE_DAY: FetchConfig('ONE_MINUTE', timedelta(minutes=1)),
            i.ONE_HOUR: FetchConfig('ONE_HOUR', timedelta(hours=1))
        }, 
        get_price_history=cg_fetch.get_price_history,
        min_bars=1,
        max_bars=10000
    ),
    SourceOptions.CMC: FetchSettings(
        {
            i.ONE_HOUR: FetchConfig('hourly', timedelta(hours=1)),
            i.ONE_DAY: FetchConfig('daily', timedelta(days=1)),
        },
        get_price_history=pycoinmarketcap.get_price_history,
    )
})

class Watchlist:
    """
    Manages a collection of financial symbols to track.

    Attributes:
    - watchlist (dict): A dictionary storing tracked symbols, their sources, and intervals.

    Methods:
    - add(symbol, source, interval): Adds a new symbol to the watchlist.
    - render(): Renders the watchlist (implementation pending).
    """
    def __init__(self):
        self.watchlist = dict()

    def add(self, symbol, source, interval):
        """
        Adds a new symbol to the watchlist.

        Parameters:
        - symbol (str): The financial symbol to track (e.g., 'AAPL').
        - source (str): The data source (e.g., 'coinbase').
        - interval (str): The time interval for data (e.g., '1 day').
        """
        self.watchlist[(symbol, source, interval)] = {
            'symbol': symbol,
            'source': source,
        }

    def render(self):
        """
        Renders the watchlist.

        Note: Implementation is pending.
        """
        pass