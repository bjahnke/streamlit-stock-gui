from datetime import datetime, timedelta
import typing as t
from dataclasses import dataclass
from abc import ABC

@dataclass 
class FetchArgs(dict):
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
    

    # def __getitem__(self, key):
    #     return getattr(self, key)
    
    # def get(self, key, default=None):
    #     return vars(self).get(key, default)

    # def __iter__(self):
    #     for key in self.__annotations__.keys():
    #         yield (key, getattr(self, key))

    # def __call__(self):
    #     return dict(self)
    
    def track_change(self, key, input_field):
        result = input_field(self.get(key), f'{key}.{key}')
        if result != self.get(key):
            self.kwargs[key] = result
            return True
        return False


@dataclass
class FetchConfig:
    interval: str
    timedelta: timedelta

    def get_start_time(self, bars: int):
        return datetime.now() - (bars * self.timedelta)


class Settings(ABC):
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
    min_bars: int
    max_bars: int


class FetchSettings(Settings):
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
    _settings: t.Dict[str, FetchSettings]