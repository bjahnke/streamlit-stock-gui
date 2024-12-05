from datetime import datetime, timedelta
import typing as t
from dataclasses import dataclass
from abc import ABC


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
    
    def get_setting(self, key):
        res = self._settings.get(key)
        if res is None:
            raise ValueError(f"Invalid key: {key}")
        return res
    
    def get(self, key):
        return self.get_setting(key)


class FetchSettings(Settings):
    _settings: t.Dict[str, FetchConfig]

    def __init__(self, settings: t.Dict[str, FetchConfig], get_price_history: t.Callable):
        super().__init__(settings)
        self._get_price_history = get_price_history

    def get_start_date(self, bars: int, interval: str):
        return self._settings[interval].get_start_time(bars)
    
    def get_price_history(self, symbol, bar_count, interval):
        return self._get_price_history(symbol, bar_count, self.get_setting(interval))




class SourceSettings(Settings):
    _settings: t.Dict[str, FetchSettings]