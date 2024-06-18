import backtrader as bt

from ai_trader.trader import AITrader
from ai_trader.strategy.base import BaseStrategy


class MacdStrategy(BaseStrategy):
    """
    MACD consists of three lines.
    DIF: the difference between two moving averages (fast moving average (typically 12 days) and
    the slow moving average (typically 26 days).
    DEA: a nine-day exponential moving average of the DIF
    MACD histogram: The MACD histogram is the difference between the DIF line and the DEA line, used to show the
    divergence between the DIF line and the DEA line.

    The buy signal in the MACD strategy occurs when a golden cross appears.
    When the DIF line crosses above the DEA line and the MACD histogram shifts from negative to positive,
    traders can consider buying to participate in the upward trend.

    The sell signal in the MACD strategy occurs when a death cross appears.
    When the DIF line crosses below the DEA line and the MACD histogram shifts from positive to negative,
    traders can consider selling to avoid a downward trend.
    """

    params = (
        ("fastperiod", 10),
        ("slowperiod", 22),
        ("signalperiod", 8),
    )

    def __init__(self):

        kwargs = {
            "fastperiod": self.p.fastperiod,
            "fastmatype": bt.talib.MA_Type.EMA,
            "slowperiod": self.p.slowperiod,
            "slowmatype": bt.talib.MA_Type.EMA,
            "signalperiod": self.p.signalperiod,
            "signalmatype": bt.talib.MA_Type.EMA,
        }

        self.macd = bt.talib.MACDEXT(self.data0.close, **kwargs)
        self.crossover = bt.indicators.CrossOver(
            self.macd.macd, self.macd.macdsignal, plot=False
        )
        self.above = bt.And(self.macd.macd > 0.0, self.macd.macdsignal > 0.0)
        self.buy_signal = bt.And(self.above, self.crossover == 1)
        self.sell_signal = self.crossover == -1

        self.order = None

    def next(self):
        if self.order:
            return

        if not self.position:
            if self.buy_signal[0]:
                self.buy()
        else:
            if self.sell_signal[0]:
                self.sell()


if __name__ == "__main__":
    engine = AITrader()
    engine.add_strategy(MacdStrategy)
    engine.run()
    engine.plot()
