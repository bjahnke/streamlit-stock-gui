from source.code.settings import SourceOptions
from source.code.components.ticker_display import display_ticker_data as display_ticker_data_new

def display_ticker_data(source: SourceOptions, symbol, interval, chart_type, indicators, bar_count, **kwargs):
    display_ticker_data_new(source, symbol, interval, chart_type, indicators, bar_count, **kwargs)