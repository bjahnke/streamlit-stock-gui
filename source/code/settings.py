from source.code.settings_model import FetchConfig, FetchSettings
from datetime import timedelta
from source.code.settings_model import Settings, SourceSettings
import source.code.coinbase as cb_fetch
import source.code.yfinance_fetch as yfinance_fetch
import source.code.coingecko as cg_fetch

class Interval:
    """Enum for time interval keys for consistency and avoiding typos"""
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
    COINBASE = 'coinbase'
    YFINANCE = 'yfinance'
    COINGECKO = 'coingecko'

source_options = [value for name, value in vars(SourceOptions).items() if not name.startswith('__')]


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
        }, 
        get_price_history=cg_fetch.get_price_history,
        min_bars=1,
        max_bars=300
    )
})