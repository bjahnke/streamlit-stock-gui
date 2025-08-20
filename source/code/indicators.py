"""
This module provides various technical indicators for financial data analysis and visualization.

Classes:
- Indicator: Base class for all indicators.
- TradingRange: Calculates trading range bands and signals.
- FloorCeiling: Identifies floor and ceiling levels in price data.
- SMA: Calculates the Simple Moving Average (SMA).
- EMA: Calculates the Exponential Moving Average (EMA).
- TradingRangePeak: Extends TradingRange with peak-based calculations.
- IndicatorManager: Manages and applies multiple indicators.

Functions:
- trading_range: Computes trading range bands for a given window.
- addBand: Adds rolling max/min and trading range bands to price data.
- addBandExpanding: Expands rolling max/min and trading range bands over time.
- addBandAggregatePeakConcat: Aggregates and concatenates trading range bands based on peaks.

Usage:
- Use the IndicatorManager to apply multiple indicators to financial data.
- Individual indicators can be used for specific calculations and visualizations.
"""

import pandas as pd
import plotly.graph_objects as go
import src.floor_ceiling_regime
import plotly.express as px

class Indicator:
    """
    Base class for all indicators. Provides methods for updating and plotting data.

    Methods:
    - update(data: pd.DataFrame) -> pd.DataFrame: Updates the data with indicator-specific calculations.
    - plot(fig, x, data): Plots the indicator on a given figure.
    - update_and_plot(data: pd.DataFrame, fig, x): Updates the data and plots the indicator.
    """
    def __init__(self) -> None:
        self.data = None

    def update(self, data: pd.DataFrame) -> pd.DataFrame:
        return data
    
    def plot(self, fig, x, data):
        pass

    def update_and_plot(self, data: pd.DataFrame, fig, x):
        data = self.update(data)
        self.plot(fig, x, data)

import numpy as np
class TradingRange(Indicator):
    """
    Calculates trading range bands and signals for financial data.

    Attributes:
    - window (int): The rolling window size for calculations.

    Methods:
    - update(data: pd.DataFrame) -> pd.DataFrame: Updates the data with trading range bands and signals.
    - plot(fig, x, data): Plots the trading range bands on a given figure.
    """
    def __init__(self, window=200) -> None:
        super().__init__()
        self.window = window

    def update(self, data: pd.DataFrame) -> pd.DataFrame:
        tr = trading_range(data, self.window)
        tr['tr_signal'] = np.nan
        tr.loc[(tr['close'] <= tr['trading_range_23']), 'tr_signal'] = 0
        tr.loc[(tr['close'] > tr['trading_range_23']) & (tr['close'] <= tr['trading_range_hi_band']), 'tr_signal'] = 1
        tr.loc[(tr['close'] > tr['trading_range_hi_band']) & (tr['close'] <= tr['trading_range_lo_band']), 'tr_signal'] = 2
        tr.loc[(tr['close'] > tr['trading_range_lo_band']) & (tr['close'] <= tr['trading_range_76']), 'tr_signal'] = 3
        tr.loc[(tr['close'] > tr['trading_range_76']) & (tr['close'] <= tr['High_Rolling']), 'tr_signal'] = 4
        return trading_range(data, 200)
    
    def plot(self, fig, x, data):
        fig.add_trace(go.Scatter(x=x, y=data['High_Rolling'], name='High Rolling'))
        fig.add_trace(go.Scatter(x=x, y=data['Low_Rolling'], name='Low Rolling'))
        fig.add_trace(go.Scatter(x=x, y=data['trading_range_lo_band'], name='TR Low Band'))
        fig.add_trace(go.Scatter(x=x, y=data['trading_range_hi_band'], name='TR High Band'))
        fig.add_trace(go.Scatter(x=x, y=data['trading_range_23'], name='TR 23%'))
        fig.add_trace(go.Scatter(x=x, y=data['trading_range_76'], name='TR 76%'))


class FloorCeiling(Indicator):
    """
    Identifies floor and ceiling levels in price data.

    Methods:
    - update(data: pd.DataFrame): Updates the data with floor and ceiling levels.
    - plot(fig, x, data): Plots the floor and ceiling levels on a given figure.
    """
    def __init__(self) -> None:
        self.tables = None

    def update(self, data: pd.DataFrame):
        data = data.copy().reset_index().rename(columns={'index': 'bar_number'})
        tables = src.floor_ceiling_regime.fc_scale_strategy_live(data, find_retest_swing=False)
        self.tables = tables
        return tables.enhanced_price_data
    
    def plot(self, data, fig=None, x=None):
        """Assumes data is enhanced_price_data type dataframe"""
        if fig is None:
            fig = px.line(data, x='bar_number', y='close')
        if x is None:
            x = data['bar_number']

        print(data.columns)
        fig.add_trace(go.Scatter(x=x, y=data['rg'], name='RG', yaxis='y2', line=dict(color='white')))
        fig.add_trace(go.Scatter(x=x, y=data['lo2'], name='lo2', mode='markers', marker=dict(color='lightgreen')))
        fig.add_trace(go.Scatter(x=x, y=data['hi2'], name='hi2', mode='markers', marker=dict(color='orange')))
        fig.add_trace(go.Scatter(x=x, y=data['hi3'], name='hi3', mode='markers', marker=dict(symbol='triangle-down', color='red', size=10)))
        fig.add_trace(go.Scatter(x=x, y=data['lo3'], name='lo3', mode='markers', marker=dict(symbol='triangle-up', color='green', size=10)))
        fig.update_layout(
            yaxis2=dict(
                title='RG',
                overlaying='y',
                side='right'
            ),
        )


class SMA(Indicator):
    """
    Calculates the Simple Moving Average (SMA) for financial data.

    Methods:
    - update(data: pd.DataFrame) -> pd.DataFrame: Updates the data with SMA values.
    - plot(fig, x, data): Plots the SMA on a given figure.
    """
    def update(self, data: pd.DataFrame) -> pd.DataFrame:
        data['SMA_120'] = data.close.rolling(window=120).mean()
        return data
    
    def plot(self, fig, x, data):
        fig.add_trace(go.Scatter(x=x, y=data['SMA_120'], name='SMA 120'))


class EMA(Indicator):
    """
    Calculates the Exponential Moving Average (EMA) for financial data.

    Methods:
    - update(data: pd.DataFrame) -> pd.DataFrame: Updates the data with EMA values.
    - plot(fig, x, data): Plots the EMA on a given figure.
    """
    def update(self, data: pd.DataFrame) -> pd.DataFrame:
        data['EMA_20'] = data.close.ewm(span=20, adjust=False).mean()
        return data
    
    def plot(self, fig, x, data):
        fig.add_trace(go.Scatter(x=x, y=data['EMA_20'], name='EMA 20'))


def trading_range(data, window):
    """
    Computes trading range bands for a given rolling window.

    Parameters:
    - data (pd.DataFrame): The input financial data.
    - window (int): The rolling window size.

    Returns:
    - pd.DataFrame: The data with added trading range bands.
    """
    data['High_Rolling'] = data['close'].rolling(window=window).max()
    data['Low_Rolling'] = data['close'].rolling(window=window).min()
    data['trading_range'] = (data.High_Rolling - data.Low_Rolling)
    data['trading_range_lo_band'] = data.Low_Rolling + data.trading_range * .61
    data['trading_range_hi_band'] = data.Low_Rolling + data.trading_range * .40
    data['trading_range_23'] = data.Low_Rolling + data.trading_range * .23
    data['trading_range_76'] = data.Low_Rolling + data.trading_range * .76
    return data


def addBand(price, window):
    """
    Adds rolling max/min and trading range bands to price data.

    Parameters:
    - price (pd.DataFrame): The input price data.
    - window (int): The rolling window size.

    Returns:
    - tuple: The updated price data and the window size.
    """
    price['rolling_max'] = price.close.rolling(window=window).max()
    price['rolling_min'] = price.close.rolling(window=window).min()
    price['trading_range'] = (price.rolling_max - price.rolling_min)
    price['trading_range_lo_band'] = price.rolling_min + price.trading_range * .61
    price['trading_range_hi_band'] = price.rolling_min + price.trading_range * .40
    price['band_24'] = price.rolling_min + price.trading_range * .24
    price['band_76'] = price.rolling_min + price.trading_range * .76
    return price, window


def addBandExpanding(price, window):
    """
    Expands rolling max/min and trading range bands over time.

    Parameters:
    - price (pd.DataFrame): The input price data.
    - window (int): The initial window size.

    Returns:
    - tuple: The updated price data and the window size.
    """
    price['rolling_max'] = 0
    rm = price.close
    price['rolling_max'] = price.close.expanding(window).max()
    price['rolling_min'] = price.close.expanding(window).min()
    price['trading_range'] = (price.rolling_max - price.rolling_min)
    price['trading_range_lo_band'] = price.rolling_min + price.trading_range * .61
    price['trading_range_hi_band'] = price.rolling_min + price.trading_range * .40
    price['band_24'] = price.rolling_min + price.trading_range * .24
    price['band_76'] = price.rolling_min + price.trading_range * .76
    return price, window


def addBandAggregatePeakConcat(price, peak_window, peaks, fast_band=False):
    """
    Aggregates and concatenates trading range bands based on peaks.

    Parameters:
    - price (pd.DataFrame): The input price data.
    - peak_window (int): The window size for peak aggregation.
    - peaks (pd.DataFrame): The peak data.
    - fast_band (bool, optional): Whether to use fast band calculation. Defaults to False.

    Returns:
    - tuple: The updated price data and the band window size.
    """
    assert peak_window > 0, 'peak_window must be greater than 0'

    peaks.start = peaks.start.astype(int)
    peaks.end = peaks.end.astype(int)
    major_peaks = peaks[peaks.lvl == 3].sort_values('end').reset_index(drop=True)
    if len(major_peaks) < peak_window:
        return addBand(price, len(price))

    band_periods = []

    peak_window = peak_window - 1
    for index in range(peak_window, len(major_peaks)):
        window_start = int(major_peaks.iloc[index - peak_window:index].start.min())
        window_end = int(price.index[-1]) if index == len(major_peaks) - 1 else int(major_peaks.iloc[index + 1].end - 1)
        price_slice = price[window_start: window_end]
        band_window = int(major_peaks.iloc[index].end - window_start)
        price_slice, band_window = addBandExpanding(price_slice.copy(), band_window)
        if index != peak_window:
            price_slice: pd.DataFrame = price_slice.dropna(subset=['rolling_max'])

        band_periods.append(price_slice)

    result = pd.concat(band_periods)
    result = result[~result.index.duplicated(keep='first')]

    price = price.copy()
    price['rolling_max'] = result['rolling_max']
    price['rolling_min'] = result['rolling_min']
    price['trading_range'] = result['trading_range']
    price['trading_range_lo_band'] = result['trading_range_lo_band']
    price['trading_range_hi_band'] = result['trading_range_hi_band']
    price['band_24'] = result['band_24']
    price['band_76'] = result['band_76']
    
    return price, band_window


class TradingRangePeak(Indicator):
    """
    Extends TradingRange with peak-based calculations.

    Attributes:
    - peak_window (int): The window size for peak calculations.

    Methods:
    - update(data: pd.DataFrame, peak_table): Updates the data with peak-based trading range bands.
    - plot(fig, x, data): Plots the peak-based trading range bands on a given figure.
    """
    def __init__(self, peak_window=200) -> None:
        self.peak_window = peak_window

    def update(self, data: pd.DataFrame, peak_table) -> pd.DataFrame:
        tr = addBandAggregatePeakConcat(data, self.peak_window, peak_table)[0]
        tr['tr_signal'] = 0
        tr.loc[(tr['close'] <= tr['band_24']), 'tr_signal'] = 0
        tr.loc[(tr['close'] > tr['band_24']) & (tr['close'] <= tr['trading_range_hi_band']), 'tr_signal'] = 1
        tr.loc[(tr['close'] > tr['trading_range_hi_band']) & (tr['close'] <= tr['trading_range_lo_band']), 'tr_signal'] = 2
        tr.loc[(tr['close'] > tr['trading_range_lo_band']) & (tr['close'] <= tr['band_76']), 'tr_signal'] = 3
        tr.loc[(tr['close'] > tr['band_76']) & (tr['close'] <= tr['rolling_max']), 'tr_signal'] = 4
        return tr
    
    def plot(self, fig, x, data):
        fig.add_trace(go.Scatter(x=x, y=data['rolling_max'], name='High Rolling'))
        fig.add_trace(go.Scatter(x=x, y=data['rolling_min'], name='Low Rolling'))
        fig.add_trace(go.Scatter(x=x, y=data['trading_range_lo_band'], name='TR Low Band'))
        fig.add_trace(go.Scatter(x=x, y=data['trading_range_hi_band'], name='TR High Band'))
        fig.add_trace(go.Scatter(x=x, y=data['band_24'], name='TR 24%'))
        fig.add_trace(go.Scatter(x=x, y=data['band_76'], name='TR 76%'))


import numpy as np
import pandas as pd
from copy import copy

class ATRVolumeBreakout(Indicator):
    """
    ATR + Volume-based breakout signal indicator.

    Detects breakouts using simultaneous spikes in volatility (ATR) and volume,
    and marks direction based on the price change.

    Parameters
    ----------
    atr_period : int
        Rolling window for ATR calculation.
    vol_period : int
        Rolling window for volume average calculation.
    atr_threshold : float
        Multiplier for ATR above its mean to trigger a signal.
    vol_threshold : float
        Multiplier for volume above its mean to trigger a signal.

    Output
    ------
    DataFrame with added columns:
    - 'atr': raw ATR values
    - 'atr_mean': mean ATR over `atr_period`
    - 'vol_mean': mean volume over `vol_period`
    - 'breakout_signal': 1 (bull), -1 (bear), 0 (none)
    """
    def __init__(self, atr_period=14, vol_period=20, atr_threshold=1.2, vol_threshold=1.2):
        super().__init__()
        self.atr_period = atr_period
        self.vol_period = vol_period
        self.atr_threshold = atr_threshold
        self.vol_threshold = vol_threshold
    
    def _compute_atr(self, df):
        tr = df['close'].diff().abs()
        atr = tr.rolling(window=self.atr_period).mean()
        return atr

    def update(self, df: pd.DataFrame) -> pd.DataFrame:
        assert 'volume' in df.columns, "Input DataFrame must contain a 'volume' column"
        df = df.copy()
        df['atr'] = self._compute_atr(df)
        df['atr_mean'] = df['atr'].rolling(self.atr_period).mean()
        df['vol_mean'] = df['volume'].rolling(self.vol_period).mean()

        atr_spike = df['atr'] > (df['atr_mean'] * self.atr_threshold)
        vol_spike = df['volume'] > (df['vol_mean'] * self.vol_threshold)
        direction = np.sign(df['close'].diff())
        df['breakout_signal'] = np.where(
            atr_spike & vol_spike, direction, 0
        ).astype(int)

        self._value = df
        return df

    def plot(self, fig, x, data):
        print(data.head())
        fig.add_trace(go.Scatter(x=x, y=data['atr'], name='ATR'))
        fig.add_trace(go.Scatter(x=x, y=data['atr_mean'], name='ATR Mean'))
        fig.add_trace(go.Scatter(x=x, y=data['volume'], name='Volume', yaxis='y2'))
        fig.add_trace(go.Scatter(x=x, y=data['vol_mean'], name='Volume Mean', yaxis='y2'))

        sig_up = data[data['breakout_signal'] == 1]
        sig_dn = data[data['breakout_signal'] == -1]

        fig.add_trace(go.Scatter(
            x=sig_up.index, y=sig_up['close'],
            mode='markers', marker=dict(symbol='triangle-up', size=10),
            name='Bullish Breakout'
        ))
        fig.add_trace(go.Scatter(
            x=sig_dn.index, y=sig_dn['close'],
            mode='markers', marker=dict(symbol='triangle-down', size=10),
            name='Bearish Breakout'
        ))

    



class IndicatorManager:
    """
    Manages and applies multiple indicators to financial data.

    Attributes:
    - lookup (dict): A dictionary mapping indicator names to their classes.

    Methods:
    - plot(fig, x, data, indicators): Applies and plots multiple indicators on a given figure.
    - options(): Returns a list of available indicators.
    """
    lookup = {
        'Trading Range': TradingRange,
        'Trading Range Peak': TradingRangePeak,
        'Floor/Ceiling': FloorCeiling,
        'SMA 20': SMA,
        'EMA 20': EMA,
        'ATR Volume Breakout': ATRVolumeBreakout,
    }

    @classmethod
    def plot(cls, fig, x, data, indicators):
        peak_table = None
        for indicator in indicators:
            if indicator in cls.lookup:
                if indicator == 'Trading Range Peak':
                    continue
                if indicator == 'Floor/Ceiling':
                    fc = FloorCeiling()
                    fc.update_and_plot(data, fig, x)
                    peak_table = fc.tables.peak_table
                else:
                    cls.lookup[indicator]().update_and_plot(data, fig, x)

        if 'Trading Range Peak' in indicators:
            if peak_table is None:
                fc = FloorCeiling()
                fc.update(data)
                peak_table = fc.tables.peak_table

            trp = TradingRangePeak(peak_window=3)
            trp_data = trp.update(data, peak_table)
            trp.plot(fig, x, trp_data)

        return data

    @classmethod
    def options(cls):
        return list(cls.lookup.keys())