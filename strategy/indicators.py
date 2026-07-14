from typing import Literal
from .logic.indicator import Indicator
import src.floor_ceiling_regime as fcr
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np


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


class MoveAvg(Indicator):
    _window: int

    def __init__(self, window: int = 120):
        assert window > 0
        super().__init__()
        self._window = window

    def __get__(self):
        return self._value
    
    def _update(self, value):
        self._value = value.close.rolling(self._window).mean()
        return self._value
    
    @property
    def window(self):
        return self._window
    
    def plot(self, fig, x, data):
        fig.add_trace(go.Scatter(x=x, y=data, name='SMA 120'))


class MoveAvgCross(Indicator):
    _fast: MoveAvg
    _slow: MoveAvg

    def __init__(self, fast: int, slow: int):
        assert fast < slow
        super().__init__()
        self._slow = self._indicators.add(MoveAvg(slow))
        self._fast = self._indicators.add(MoveAvg(fast))

    def _update(self, value):
        self._value = self._fast.update(value) - self._slow.update(value)
        return self._value
    
    @property
    def fast(self):
        return self._fast
    
    @property
    def slow(self):
        return self._slow
    

class BollingerBand(Indicator):
    _window: int
    _std: int
    _middle: MoveAvg

    def __init__(self, window: int = 20, std: int = 2):
        assert window > 0
        assert std > 0
        super().__init__()
        self._window = window
        self._std = std
        self._middle = self._indicators.add(MoveAvg(window))

    def _update(self, value):
        std = value.rolling(self._window).std() * self._std
        self._value = pd.DataFrame({
            'upper': self._middle.value + std, 
            'lower': self._middle.value - std
        })
        return self._value
    
    @property
    def window(self):
        return self._window
    
    @property
    def std(self):
        return self._std
    
    @property
    def middle(self):
        return self._middle.value
    
    @property
    def upper(self):
        return self._value['upper']
    
    @property
    def lower(self):
        return self._value['lower']
    

class TradingRange(Indicator):
    def __init__(self, high_band_pct=.40, low_band_pct=.61, window=200):
        assert 0 < high_band_pct < 1, 'High band must be between 0 and 1'
        assert 0 < low_band_pct < 1, 'Low band must be between 0 and 1'
        assert high_band_pct < low_band_pct, f'High band must be greater than low band, but {high_band_pct} < {low_band_pct}'
        super().__init__()
        self._high_band_pct = high_band_pct
        self._low_band_pct = low_band_pct
        self._window = window

    def _update(self, value):
        rolling_max = value.close.rolling(self._window).max()
        rolling_min = value.close.rolling(self._window).min()
        trading_range = (rolling_max - rolling_min)  
        value = pd.DataFrame({
            'upper': rolling_min + trading_range * self._high_band_pct,
            'lower': rolling_min + trading_range * self._low_band_pct,
            'band_24': rolling_min + trading_range * .24,
            'band_76': rolling_min + trading_range * .76,
            'min': rolling_min,
            'max': rolling_max
        })
        return value
    
    @property
    def upper(self):
        return self._value['upper']
    
    @property
    def lower(self):
        return self._value['lower']
    
    @property
    def high_band_pct(self):
        return self._high_band_pct
    
    @property
    def low_band_pct(self):
        return self._low_band_pct
    
    @property
    def window(self):
        return self._window
    
    def plot(self, fig, x, data):
        fig.add_trace(go.Scatter(x=x, y=data['max'], name='High Rolling'))
        fig.add_trace(go.Scatter(x=x, y=data['min'], name='Low Rolling'))
        fig.add_trace(go.Scatter(x=x, y=data['lower'], name='TR Low Band'))
        fig.add_trace(go.Scatter(x=x, y=data['upper'], name='TR High Band'))
        fig.add_trace(go.Scatter(x=x, y=data['band_24'], name='TR 23%'))
        fig.add_trace(go.Scatter(x=x, y=data['band_76'], name='TR 76%'))
    

import src.regime.utils as sru

class Peak(Indicator):
    def __init__(self):
        super().__init__()
        self._value = None
        self._px_with_swing = None

    def _update(self, value):
        table, px_with_swing = fcr.init_peak_table(value, distance_pct=0.05, retrace_pct=0.05, swing_window=63, sw_lvl=3)
        self._value = table
        self._px_with_swing = px_with_swing
        return self._value


class Regime(Indicator):
    _threshold: float
    _direction: Literal[-1, 1]

    def _update(self, value) -> fcr.FcStrategyTables:
        value = value.reset_index(drop=True).reset_index().rename(columns={'index': 'bar_number'})
        self._value = fcr.fc_scale_strategy_live(value, find_retest_swing=False)
        print(self._value.peak_table.columns)
        return self._value
    
    @property
    def threshold(self):
        return self._threshold
    
    def plot(self, data, fig=None, x=None):
        if fig is None:
            fig = px.line(data, y='close', line_shape='linear', color_discrete_sequence=['white'])
        if x is None:
            x = data.index
        """Assumes data is enhanced_price_data type dataframe"""
        
        fig.add_trace(go.Scatter(x=x, y=data['rg'], name='rg', yaxis='y2', line=dict(color='white')))
        fig.add_trace(go.Scatter(x=x, y=data['lo2'], name='lo2', mode='markers', marker=dict(color='lightgreen')))
        fig.add_trace(go.Scatter(x=x, y=data['hi2'], name='hi2', mode='markers', marker=dict(color='orange')))
        fig.add_trace(go.Scatter(x=x, y=data['hi3'], name='hi3', mode='markers', marker=dict(symbol='triangle-down', color='red', size=10)))
        fig.add_trace(go.Scatter(x=x, y=data['lo3'], name='lo3', mode='markers', marker=dict(symbol='triangle-up', color='green', size=10)))
        fig.update_layout(
            yaxis2=dict(
                title='rg',
                overlaying='y',
                side='right'
            ),
        )
        print(self.analyze_peaks())
        return fig
    
    def update_and_plot(self, data: pd.DataFrame, fig, x):
        data = self.update(data)
        self.plot(self._value.enhanced_price_data, fig, x)

    def analyze_peaks(self):
        """
        peak columns ['start', 'end', 'type', 'lvl', 'st_px', 'en_px']

        analyze l2 swing performance
         - for each swing (process -1 and 1 type swings separately):
         - record the length of time between peak.end and price cross (first bar after peak.end where swing low)
         - record the percent change between entry and max price (if processing swing low), or min price if swing high
        """
        peaks = self._value.peak_table.loc[self._value.peak_table.lvl == 2].copy()
        price_data = self._value.enhanced_price_data
        
        results = []
        for sw_type in [1, -1]:
            swings = peaks.loc[(peaks.type == sw_type)]
            
            for _, swing in swings.iterrows():
                swing_end = int(swing['end'])
                swing_price = swing['en_px']
                
                # Get price data after swing end
                future_prices = price_data.iloc[swing_end + 1:]
                
                if len(future_prices) == 0:
                    continue
                
                # Find first cross based on swing type
                if sw_type == 1:  # Swing low - look for price crossing above
                    cross_idx = future_prices[future_prices['close'] > swing_price].index
                    if len(cross_idx) > 0:
                        bars_to_cross = cross_idx[0] - swing_end
                        max_price = future_prices.loc[:cross_idx[0], 'close'].max()
                        pct_change = ((max_price - swing_price) / swing_price) * 100
                        active = False
                    else:
                        bars_to_cross = len(future_prices)
                        max_price = future_prices['close'].max()
                        pct_change = ((max_price - swing_price) / swing_price) * 100
                        active = True
                else:  # Swing high - look for price crossing below
                    cross_idx = future_prices[future_prices['close'] < swing_price].index
                    if len(cross_idx) > 0:
                        bars_to_cross = cross_idx[0] - swing_end
                        min_price = future_prices.loc[:cross_idx[0], 'close'].min()
                        pct_change = ((swing_price - min_price) / swing_price) * 100
                        active = False
                    else:
                        bars_to_cross = len(future_prices)
                        min_price = future_prices['close'].min()
                        pct_change = ((swing_price - min_price) / swing_price) * 100
                        active = True
                
                results.append({
                    'swing_type': sw_type,
                    'swing_end': swing_end,
                    'swing_price': swing_price,
                    'bars_to_cross': bars_to_cross,
                    'pct_change': pct_change,
                    'active': active
                })
        return pd.DataFrame(results)
    
    def plot_peak_best_case(self, peaks_df=None, top_n=None, target_fig: go.Figure = None):
        """
        Visualize "best-case" performance for longs vs shorts based on the output
        of `analyze_peaks()`.

        Approach:
        - Use the `pct_change` column (percentage) computed by `analyze_peaks()` as
          the per-trade return (positive for both longs and shorts in that output).
        - For best-case cumulative growth: sort returns descending (best trades first),
          then compute cumulative product of (1 + return_decimal) to simulate
          sequentially capturing the best trades.
        - Also produce a box/violin plot (and points) to compare the full
          distribution of returns between longs and shorts.

        Parameters:
        - peaks_df: optional DataFrame produced by `analyze_peaks()`; if None,
                    the method will call `self.analyze_peaks()`.
        - top_n: optional int, limit to top N best trades for the cumulative growth
                 curve. If None, use all trades.

        Returns:
        - dict with Plotly figures: {'growth': fig_growth, 'box': fig_box}
        """
        # Acquire peaks data
        df = peaks_df if peaks_df is not None else self.analyze_peaks()
        if df is None or df.empty:
            print("No peak data available to plot.")
            return None

        # Normalize/clean data
        df = df.copy()
        # Ensure numeric
        df['pct_change'] = pd.to_numeric(df['pct_change'], errors='coerce')
        df = df.dropna(subset=['pct_change'])
        if df.empty:
            print("No valid pct_change values to plot.")
            return None

        figs = {}

        # Growth figure (best-trades-first cumulative compounding)
        fig_growth = go.Figure()
        print(df)
        for sw_type, label in [(1, 'Longs (swing lows)'), (-1, 'Shorts (swing highs)')]:
            arr = df.loc[df.swing_type == sw_type, 'pct_change'].astype(float) / 100.0
            if arr.empty:
                continue
            arr_sorted = arr

            if top_n is not None:
                arr_sorted = arr_sorted[:top_n]
            # cumulative product to simulate sequentially taking best trades
            cum = np.cumprod(1.0 + arr_sorted)
            fig_growth.add_trace(go.Scatter(
                x=np.arange(1, len(cum) + 1),
                y=cum,
                mode='lines+markers',
                name=label
            ))

        fig_growth.update_layout(
            title='Best-case cumulative growth (best trades first)',
            xaxis_title='Number of trades (best-first)',
            yaxis_title='Growth (starting capital = 1)'
        )
        figs['growth'] = fig_growth

        # If a target_fig is provided, copy the growth traces into it so callers
        # can render the growth lines on an existing price figure.
        if target_fig is not None:
            try:
                for trace in fig_growth.data:
                    target_fig.add_trace(trace)
                figs['combined'] = target_fig
            except Exception:
                # if combining fails, ignore and return the separate figures
                pass

        # Distribution comparison (box + points)
        try:
            fig_box = px.box(df, x='swing_type', y='pct_change', points='all',
                             labels={'swing_type': 'swing_type (-1=short, 1=long)', 'pct_change': 'pct_change (%)'},
                             title='Distribution of pct_change by swing type')
        except Exception:
            # Fallback to go.Box if px fails for any reason
            fig_box = go.Figure()
            for sw_type, label in [(-1, 'Longs'), (1, 'Shorts')]:
                vals = df.loc[df.swing_type == sw_type, 'pct_change']
                if vals.empty:
                    continue
                fig_box.add_trace(go.Box(y=vals, name=label, boxpoints='all', jitter=0.5))

        figs['box'] = fig_box

        return figs
            
    

class TradingRangePeak(Indicator):
    """
    Extends TradingRange with peak-based calculations.

    Attributes:
    - peak_window (int): The window size for peak calculations.

    Methods:
    - update(data: pd.DataFrame, peak_table): Updates the data with peak-based trading range bands.
    - plot(fig, x, data): Plots the peak-based trading range bands on a given figure.
    """
    def __init__(self, peak_table, peak_window=200) -> None:
        # TODO temporary code, peak should be an indicator that can be update with new data
        super().__init__()
        self._peak_table = peak_table
        self.peak_window = peak_window

    def _update(self, data: pd.DataFrame) -> pd.DataFrame:
        tr = addBandAggregatePeakConcat(data, self.peak_window, self._peak_table)[0]
        tr['tr_signal'] = 0
        tr.loc[(tr['close'] <= tr['band_24']), 'tr_signal'] = 0
        tr.loc[(tr['close'] > tr['band_24']) & (tr['close'] <= tr['trading_range_hi_band']), 'tr_signal'] = 1
        tr.loc[(tr['close'] > tr['trading_range_hi_band']) & (tr['close'] <= tr['trading_range_lo_band']), 'tr_signal'] = 2
        tr.loc[(tr['close'] > tr['trading_range_lo_band']) & (tr['close'] <= tr['band_76']), 'tr_signal'] = 3
        tr.loc[(tr['close'] > tr['band_76']) & (tr['close'] <= tr['rolling_max']), 'tr_signal'] = 4
        return tr
    
    def plot(self, data, fig, x = None, ):
        if x is None:
            x = data.index
        fig.add_trace(go.Scatter(x=x, y=data['rolling_max'], name='High Rolling'))
        fig.add_trace(go.Scatter(x=x, y=data['rolling_min'], name='Low Rolling'))
        fig.add_trace(go.Scatter(x=x, y=data['trading_range_lo_band'], name='TR Low Band'))
        fig.add_trace(go.Scatter(x=x, y=data['trading_range_hi_band'], name='TR High Band'))
        fig.add_trace(go.Scatter(x=x, y=data['band_24'], name='TR 24%'))
        fig.add_trace(go.Scatter(x=x, y=data['band_76'], name='TR 76%'))



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
    def __init__(
            self, atr_period=50, vol_period=50, 
            atr_threshold=1.0, vol_threshold=1.0,
            atr_short_period=14, vol_short_period=14
            ):
        super().__init__()
        self.atr_period = atr_period
        self.vol_period = vol_period
        self.atr_threshold = atr_threshold
        self.vol_threshold = vol_threshold
        self.atr_short_period = atr_short_period
        self.vol_short_period = vol_short_period
    
    def _compute_atr(self, df):
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift(1))
        low_close = np.abs(df['low'] - df['close'].shift(1))
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(window=self.atr_short_period).mean()
        return atr

    def _update(self, df: pd.DataFrame) -> pd.DataFrame:
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

        # fig.add_trace(go.Scatter(x=x, y=data['atr'], name='ATR'))
        # fig.add_trace(go.Scatter(x=x, y=data['atr_mean'], name='ATR Mean'))
        # fig.add_trace(go.Scatter(x=x, y=data['volume'], name='Volume', yaxis='y2'))
        # fig.add_trace(go.Scatter(x=x, y=data['vol_mean'], name='Volume Mean', yaxis='y2'))


        sig_up = data.copy()
        sig_up.loc[(sig_up.breakout_signal == -1) | (sig_up.breakout_signal == 0), 'breakout_signal'] = np.nan
        sig_up['breakout_signal'] = sig_up.loc[sig_up.breakout_signal == 1, 'close']
        sig_dn = data.copy()
        sig_dn.loc[(sig_dn.breakout_signal == 1) | (sig_dn.breakout_signal == 0), 'breakout_signal'] = np.nan
        sig_dn['breakout_signal'] = sig_dn.loc[sig_dn.breakout_signal == -1, 'close']


        fig.add_trace(go.Scatter(
            x=x, y=sig_up['breakout_signal'],
            mode='markers', marker=dict(symbol='triangle-up', size=10, color='green'),
            name='Bullish Breakout'
        ))
        fig.add_trace(go.Scatter(
            x=x, y=sig_dn['breakout_signal'],
            mode='markers', marker=dict(symbol='triangle-down', size=10, color='red'),
            name='Bearish Breakout'
        ))