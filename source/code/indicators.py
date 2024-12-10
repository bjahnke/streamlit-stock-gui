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
    def __init__(self, window=200) -> None:
        super().__init__()
        self.window = window


    def update(self, data: pd.DataFrame) -> pd.DataFrame:
        tr = trading_range(data, self.window)
        # data['High_Rolling'] = data['close'].rolling(window=window).max()
        # data['Low_Rolling'] = data['close'].rolling(window=window).min()
        # data['trading_range'] = (data.High_Rolling - data.Low_Rolling)
        # data['trading_range_lo_band'] = data.Low_Rolling + data.trading_range * .61
        # data['trading_range_hi_band'] = data.Low_Rolling + data.trading_range * .40
        # data['trading_range_23'] = data.Low_Rolling + data.trading_range * .23
        # data['trading_range_76'] = data.Low_Rolling + data.trading_range * .76
        tr['tr_signal'] = 0
        tr.loc[(tr['close'] > tr['Low_Rolling']) & (tr['close'] <= tr['trading_range_23']), 'tr_signal'] = 0
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
    def __init__(self) -> None:
        self.tables = None

    def update(self, data: pd.DataFrame):
        data = data.copy().reset_index().rename(columns={'index': 'bar_number'})
        tables = src.floor_ceiling_regime.fc_scale_strategy_live(data, find_retest_swing=False)
        self.tables = tables
        return tables.enhanced_price_data
    
    def plot(self, fig, x, data):
        """Assumes data is enhanced_price_data type dataframe"""
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





def trading_range(data, window):
    data['High_Rolling'] = data['close'].rolling(window=window).max()
    data['Low_Rolling'] = data['close'].rolling(window=window).min()
    data['trading_range'] = (data.High_Rolling - data.Low_Rolling)
    data['trading_range_lo_band'] = data.Low_Rolling + data.trading_range * .61
    data['trading_range_hi_band'] = data.Low_Rolling + data.trading_range * .40
    data['trading_range_23'] = data.Low_Rolling + data.trading_range * .23
    data['trading_range_76'] = data.Low_Rolling + data.trading_range * .76
    return data


def addBand(price, window):
    price['rolling_max'] = price.close.rolling(window=window).max()
    price['rolling_min'] = price.close.rolling(window=window).min()
    price['trading_range'] = (price.rolling_max - price.rolling_min)
    price['trading_range_lo_band'] = price.rolling_min + price.trading_range * .61
    price['trading_range_hi_band'] = price.rolling_min + price.trading_range * .40
    price['band_24'] = price.rolling_min + price.trading_range * .24
    price['band_76'] = price.rolling_min + price.trading_range * .76
    return price, window

def addBandExpanding(price, window):
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
    assert peak_window > 0, 'peak_window must be greater than 0'

    peaks.start = peaks.start.astype(int)
    peaks.end = peaks.end.astype(int)
    major_peaks = peaks[peaks.lvl == 3].sort_values('end').reset_index(drop=True)
    if len(major_peaks) < peak_window:
        return addBand(price, len(price))

    # major_peaks_forward_look = major_peaks
    # major_peaks_backward_look = major_peaks.sort_values('start').reset_index(drop=True)
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

    # Concatenate all band periods
    result = pd.concat(band_periods)
    
    # Ensure no duplicate indexes
    result = result[~result.index.duplicated(keep='first')]

    # Set trading range columns onto price df
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
    def __init__(self, peak_window=200) -> None:
        self.peak_window = peak_window

    def update(self, data: pd.DataFrame, peak_table) -> pd.DataFrame:
        tr = addBandAggregatePeakConcat(data, self.peak_window, peak_table)[0]
        tr['tr_signal'] = 0
        tr.loc[(tr['close'] > tr['rolling_min']) & (tr['close'] <= tr['band_24']), 'tr_signal'] = 0
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



class IndicatorManager:
    lookup = {
        'Trading Range': TradingRange,
        'Trading Range Peak': TradingRangePeak,
        'Floor/Ceiling': FloorCeiling,
        'SMA 20': SMA,
        'EMA 20': EMA
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