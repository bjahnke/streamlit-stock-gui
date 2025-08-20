from strategy.indicators import *
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
        'Floor/Ceiling': Regime,
        'SMA 20': MoveAvg,
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
                    fc = Regime()
                    fc.update_and_plot(data, fig, x)
                    peak_table = fc.value.peak_table
                else:
                    cls.lookup[indicator]().update_and_plot(data, fig, x)

        if 'Trading Range Peak' in indicators:
            if peak_table is None:
                fc = Regime()
                fc.update(data)
                peak_table = fc.value.peak_table

            trp = TradingRangePeak(peak_table, peak_window=3)
            trp_data = trp.update(data)
            trp.plot(trp_data, fig, x) 
        return data

    @classmethod
    def options(cls):
        return list(cls.lookup.keys())
    
    