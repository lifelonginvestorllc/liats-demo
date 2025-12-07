from AlgorithmImports import *
from core.LIConfiguration import *


class LICandlestick:
    def __init__(self, bar: IBaseDataBar, configs: dict):
        self.bar = bar
        self.configs = configs

        # Updated by rolling window dynamically if not specified
        self.avgBodySize = configs.get(LIConfigKey.candlestickAvgBodySize, (self.bar.close + self.bar.open) / 2)
        # Updated by rolling window dynamically if not specified
        self.avgWickSize = configs.get(LIConfigKey.candlestickAvgWickSize, (self.bar.high - self.bar.low) / 3)
        self.bodyTolerance = configs.get(LIConfigKey.candlestickBodyTolerance, LIDefault.candlestickBodyTolerance)
        self.dojiBodyMaxRatio = configs.get(LIConfigKey.candlestickDojiBodyMaxRatio, LIDefault.candlestickDojiBodyMaxRatio)
        self.spinningTopBodyMaxRatio = configs.get(LIConfigKey.candlestickSpinningTopBodyMaxRatio, LIDefault.candlestickSpinningTopBodyMaxRatio)

    def configs(self):
        return self.configs

    def isUp(self):
        return self.body() > 0 and self.bodySize() > self.bodyTolerance

    def isFlat(self):
        return self.body() == 0

    def isDown(self):
        return self.body() < 0 and self.bodySize() > self.bodyTolerance

    def body(self) -> float:
        return round(self.bar.close - self.bar.open, LIGlobal.percentPrecision)

    def bodySize(self) -> float:
        return abs(self.body())

    def bodyRatio(self) -> float:
        ratio = (self.bodySize() / self.avgBodySize) if self.avgBodySize else self.bodySize()
        if self.isDown():
            ratio *= -1
        return ratio

    def wickSize(self) -> float:
        return self.wickUpperSize() + self.wickLowerSize()

    def wickUpperSize(self) -> float:
        return self.bar.high - max(self.bar.open, self.bar.close)

    def wickUpperRatio(self) -> float:
        return (self.wickUpperSize() / self.avgWickSize) if self.avgWickSize else self.wickUpperSize()

    def wickLowerSize(self) -> float:
        return min(self.bar.open, self.bar.close) - self.bar.low

    def wickLowerRatio(self) -> float:
        return (self.wickLowerSize() / self.avgWickSize) if self.avgWickSize else self.wickLowerSize()

    def wickBodyRatio(self) -> float:
        ratio = (self.wickSize() / self.bodySize()) if self.bodySize() else self.wickSize()
        if self.isDown():
            ratio *= -1
        return ratio

    def wickTopDownRatio(self) -> float:
        """The bigger wick divides the smaller wick, positive for (upper > lower) and negative for (upper < lower)"""
        if self.wickUpperSize() >= self.wickLowerSize():
            ratio = math.inf if self.wickLowerSize() == 0 else self.wickUpperSize() / self.wickLowerSize()
        else:
            ratio = -(math.inf if self.wickUpperSize() == 0 else self.wickLowerSize() / self.wickUpperSize())
        return ratio

    def dojiScore(self) -> float:
        """
        https://www.investopedia.com/terms/d/doji.asp

        Doji tend to look like a cross or plus sign and have small or nonexistent bodies.
        From an auction theory perspective, doji represent indecision on the side of both buyers and sellers.
        Everyone is equally matched, so the price goes nowhere; buyers and sellers are in a standoff.

        Spinning tops are quite similar to doji, but their bodies are larger, where the open and close are relatively close.
        A candle's body generally can represent up to 5% of the size of the entire candle's range to be classified as a doji.
        Any more than that, and it becomes a spinning top.
        """
        score = 0
        if abs(self.bodyRatio()) <= self.dojiBodyMaxRatio:
            score = 2  # 2 for Doji
            if self.isDown():
                score *= -1
            score += 1 if self.wickTopDownRatio() >= 0 else -1
        return score

    def spinningTopScore(self) -> float:
        """
        https://www.investopedia.com/terms/s/spinning-top.asp

        A spinning top candlestick has a short real body that's vertically centered between long upper and lower wicks.
        The bulls sent the price sharply higher and the bears sent the price sharply lower, but in the end, the price closed near where it opened.
        This indecision can signal more sideways movement, especially if the spinning top occurs within an established range.
        It can also signal a possible price reversal if it occurs following a price advance or decline.

        Sometimes spinning tops may signal a significant trend change. A spinning top that occurs at the top of an uptrend could be a sign
        that bulls are losing their control and the trend may reverse. Similarly, a spinning top at the bottom of a downtrend could signal
        that bears are losing control and bulls may take the reins.
        """
        score = 0
        if abs(self.bodyRatio()) <= self.spinningTopBodyMaxRatio and not self.dojiScore():
            score = 1
            if self.isDown():
                score *= -1
            score += 0.5 if self.wickTopDownRatio() > 0 else -0.5
        return score

    def __str__(self) -> str:
        result = "candlestick={"
        result += f"time={self.bar.end_time.strftime('%H:%M')},"
        result += f"open={self.bar.open:.2f},"
        result += f"high={self.bar.high:.2f},"
        result += f"low={self.bar.low:.2f},"
        result += f"close={self.bar.close:.2f},"
        result += f"volume={self.bar.volume:.0f},"
        result += f"bodyRatio={self.bodyRatio():.2f},"
        result += f"wickBodyRatio={self.wickBodyRatio():.2f},"
        result += f"wickUpDownRatio={self.wickTopDownRatio():.2f},"
        if self.dojiScore():
            result += f"dojiScore={self.dojiScore():.2f},"
        if self.spinningTopScore():
            result += f"spinningTopScore={self.spinningTopScore():.2f},"
        result = result.rstrip(',') + "}"
        return result
