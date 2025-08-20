"""
This module defines data models and settings for fetching and managing financial data.

Classes:
- FetchArgs: Represents arguments for fetching financial data.
- FetchConfig: Configuration for fetching data, including interval and timedelta.
- Settings: Abstract base class for managing settings.
- BarSettings: Defines minimum and maximum bar settings.
- FetchSettings: Extends Settings to include fetching logic and bar settings.
- SourceSettings: Extends Settings to manage multiple data sources.

Usage:
- Use FetchArgs to define parameters for data fetching.
- Use FetchSettings and SourceSettings to manage configurations for different data sources.
"""

from datetime import datetime, timedelta
import typing as t
from dataclasses import dataclass
from abc import ABC

@dataclass 
class FetchArgs(dict):
    """
    Represents arguments for fetching financial data.

    Attributes:
    - symbol (str): The financial symbol (e.g., 'AAPL').
    - interval (str): The time interval for data (e.g., '1 day').
    - bar_count (int): Number of data points to fetch.
    - chart_type (str): Type of chart (e.g., 'Candlestick').
    - indicators (list[str], optional): List of indicators to apply.
    - source (str): Data source (e.g., 'yfinance').
    - live_data (bool): Whether to fetch live data.

    Methods:
    - migrate(cls, old_args): Migrates old arguments to the new format.
    - track_change(key, input_field): Tracks changes in input fields.
    """
    symbol: str = ''
    interval: str = '1 day'
    bar_count: int = 300
    chart_type: str = 'Candlestick'
    indicators: t.Optional[t.List[str]] = None
    source: str = 'yfinance'
    live_data: bool = False

    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs
        self.indicators = kwargs.get('indicators', ['Trading Range', 'Floor/Ceiling'])
        self.symbol = kwargs.get('symbol', '')
        self.interval = kwargs.get('interval', '1 day')
        self.bar_count = kwargs.get('bar_count', 300)
        self.chart_type = kwargs.get('chart_type', 'Candlestick')
        self.source = kwargs.get('source', 'yfinance')
        self.live_data = kwargs.get('live_data', False)
        super().__init__(**{
            'symbol': self.symbol,
            'interval': self.interval,
            'bar_count': self.bar_count,
            'chart_type': self.chart_type,
            'indicators': self.indicators,
            'source': self.source,
            'live_data': self.live_data
        })


    @classmethod
    def migrate(cls, old_args):
        return cls(**old_args)
    

    def track_change(self, key, input_field):
        result = input_field(self.get(key), f'{key}.{key}')
        if result != self.get(key):
            self.kwargs[key] = result
            return True
        return False


@dataclass
class FetchConfig:
    """
    Configuration for fetching data, including interval and timedelta.

    Attributes:
    - interval (str): The time interval for data (e.g., '1 day').
    - timedelta (timedelta): The time delta corresponding to the interval.

    Methods:
    - get_start_time(bars): Calculates the start time based on the number of bars.
    """
    interval: str
    timedelta: timedelta

    def get_start_time(self, bars: int):
        return datetime.now() - (bars * self.timedelta)
    
    def get_data_range(self, bars: int, end_date=None):
        """
        Calculate the start time based on the number of bars and the fetch configuration.

        Parameters:
        - fetch_config (FetchConfig): Configuration for fetching data, including interval and timedelta.
        - bars (int): Number of data points to fetch.

        Returns:
        - datetime: The calculated start time.
        """
        if end_date is None:
            end_date = datetime.now().replace(second=0, microsecond=0)
            # if "DAY" in fetch_config.interval:
            #     end_date = end_date.replace(hour=0, minute=0)
        start_date = end_date - self.timedelta * bars

        # Format start and end dates to ISO 8601 strings (YYYY-MM-DD format)
        start_date = str(int(start_date.timestamp()))
        end_date = str(int(end_date.timestamp()))
        # Fetch candles with ISO 8601 date strings
        return start_date, end_date


class Settings(ABC):
    """
    Abstract base class for managing settings.

    Attributes:
    - _settings (dict): Dictionary of settings.
    - _options (list): List of available options.

    Methods:
    - options: Returns the list of available options.
    - get_index(option): Gets the index of an option.
    - get_setting(key): Retrieves a setting by key.
    - get(key): Alias for get_setting.
    """
    def __init__(self, settings: t.Dict[str, t.Any]):
        self._settings = settings
        self._options = list(settings.keys())

    @property
    def options(self):
        return self._options
    
    def get_index(self, option):
        try: 
            option_index = self._options.index(option)
        except ValueError:
            option_index = 0
        return option_index
    
    def get_setting(self, key):
        res = self._settings.get(key)
        if res is None:
            raise ValueError(f"Invalid key: {key}")
        return res
    
    def get(self, key):
        return self.get_setting(key)
    

@dataclass
class BarSettings:
    """
    Defines minimum and maximum bar settings.

    Attributes:
    - min_bars (int): Minimum number of bars.
    - max_bars (int): Maximum number of bars.
    """
    min_bars: int
    max_bars: int


class FetchSettings(Settings):
    """
    Extends Settings to include fetching logic and bar settings.

    Attributes:
    - _settings (dict): Dictionary of FetchConfig objects.
    - _get_price_history (callable): Function to fetch price history.
    - _bar_settings (BarSettings): Bar settings for the data source.

    Methods:
    - get_start_date(bars, interval): Calculates the start date for fetching data.
    - get_price_history(symbol, bar_count, interval): Fetches price history for a symbol.
    """
    _settings: t.Dict[str, FetchConfig]

    def __init__(self, settings: t.Dict[str, FetchConfig], get_price_history: t.Callable, min_bars=100, max_bars=5000) -> None:
        super().__init__(settings)
        self._get_price_history = get_price_history
        self._bar_settings = BarSettings(min_bars, max_bars)

    def get_start_date(self, bars: int, interval: str):
        return self._settings[interval].get_start_time(bars)
    
    def get_price_history(self, symbol, bar_count, interval):
        return self._get_price_history(symbol, bar_count, self.get_setting(interval))


class SourceSettings(Settings):
    """
    Extends Settings to manage multiple data sources.

    Attributes:
    - _settings (dict): Dictionary of FetchSettings objects.
    """
    _settings: t.Dict[str, FetchSettings]