import pandas as pd
import plotly.graph_objects as go
import src.floor_ceiling_regime

class Indicator:
    def __init__(self) -> None:
        self.data = None

    def update(self, data: pd.DataFrame) -> pd.DataFrame:
        return data
    
    def plot(self, fig, x, data):
        pass

    def update_and_plot(self, data: pd.DataFrame, fig, x):
        data = self.update(data)
        self.plot(fig, x, data)


class TradingRange(Indicator):

    def update(self, data: pd.DataFrame) -> pd.DataFrame:
        return trading_range(data, 200)
    
    def plot(self, fig, x, data):
        fig.add_trace(go.Scatter(x=x, y=data['High_Rolling'], name='High Rolling'))
        fig.add_trace(go.Scatter(x=x, y=data['Low_Rolling'], name='Low Rolling'))
        fig.add_trace(go.Scatter(x=x, y=data['trading_range_lo_band'], name='TR Low Band'))
        fig.add_trace(go.Scatter(x=x, y=data['trading_range_hi_band'], name='TR High Band'))
        fig.add_trace(go.Scatter(x=x, y=data['trading_range_23'], name='TR 23%'))
        fig.add_trace(go.Scatter(x=x, y=data['trading_range_76'], name='TR 76%'))


class FloorCeiling(Indicator):
    def __init__(self) -> None:
        self.tables = None

    def update(self, data: pd.DataFrame):
        data = data.copy().reset_index().rename(columns={'index': 'bar_number'})
        tables = src.floor_ceiling_regime.fc_scale_strategy_live(data)
        self.tables = tables
        return tables.enhanced_price_data
    
    def plot(self, fig, x, data):
        """Assumes data is enhanced_price_data type dataframe"""

        fig.add_trace(go.Scatter(x=x, y=data['rg'], name='RG', yaxis='y2', line=dict(color='white')))

        fig.update_layout(
            yaxis2=dict(
                title='RG',
                overlaying='y',
                side='right'
            ),
        )

class SMA(Indicator):
    def update(self, data: pd.DataFrame) -> pd.DataFrame:
        data['SMA_20'] = data.close.rolling(window=20).mean()
        return data
    
    def plot(self, fig, x, data):
        fig.add_trace(go.Scatter(x=x, y=data['SMA_20'], name='SMA 20'))

class EMA(Indicator):
    def update(self, data: pd.DataFrame) -> pd.DataFrame:
        data['EMA_20'] = data.close.ewm(span=20, adjust=False).mean()
        return data
    
    def plot(self, fig, x, data):
        fig.add_trace(go.Scatter(x=x, y=data['EMA_20'], name='EMA 20'))


class IndicatorManager:
    lookup = {
        'Trading Range': TradingRange,
        'Floor/Ceiling': FloorCeiling,
        'SMA 20': SMA,
        'EMA 20': EMA
    }

    @classmethod
    def plot(cls, fig, x, data, indicators):
        for indicator in indicators:
            if indicator in cls.lookup:
                cls.lookup[indicator]().update_and_plot(data, fig, x)


    @classmethod
    def options(cls):
        return list(cls.lookup.keys())


def trading_range(data, window):
    data['High_Rolling'] = data['close'].rolling(window=window).max()
    data['Low_Rolling'] = data['close'].rolling(window=window).min()
    data['trading_range'] = (data.High_Rolling - data.Low_Rolling)
    data['trading_range_lo_band'] = data.Low_Rolling + data.trading_range * .61
    data['trading_range_hi_band'] = data.Low_Rolling + data.trading_range * .40
    data['trading_range_23'] = data.Low_Rolling + data.trading_range * .23
    data['trading_range_76'] = data.Low_Rolling + data.trading_range * .76
    return data