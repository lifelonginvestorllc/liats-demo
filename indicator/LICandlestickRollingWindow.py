# region imports

from indicator.LICandlestick import *


# endregion


class LICandlestickRollingWindow:
    """
    Keep the consistency with Lean's RollingWindow behavior, the first one is the most recent one!
    """

    def __init__(self, windowSize: int, configs: dict):
        self.candlesticks: list[LICandlestick] = []
        self.windowSize = windowSize
        self.configs = configs

        self.backtraceHalf = windowSize / 2  # Look back half of the window
        self.backtraceQuarter = windowSize / 4  # Look back quarter of the window
        self.tolerateNoise = 2  # Tolerate break points (noise)

        # In favor of calculating average body size
        self.totalCount = 0  # Track all candlesticks count
        self.totalVolume = 0  # Sum up all candlestick's volume
        self.totalBodySize = 0  # Sum up all candlestick's body size
        self.totalWickSize = 0  # Sum up all candlestick's wick size

        self.defaultAvgBodySize = configs.get(LIConfigKey.candlestickAvgBodySize)
        self.defaultAvgWickSize = configs.get(LIConfigKey.candlestickAvgWickSize)

    def size(self) -> int:
        return self.windowSize

    def count(self) -> int:
        return len(self.candlesticks)

    def isReady(self) -> bool:
        return self.count() == self.size()

    def reset(self):
        self.totalCount = 0
        self.totalBodySize = 0
        self.totalWickSize = 0
        self.candlesticks.clear()

    def weight(self, index):
        """
        :param index: starts with 0
        :return: e.g. backtrace=10, return 1, 0.9, 0.8, ..., 0.1, and 0.1 for all rest
        """
        return round(1 - min(index, self.backtraceHalf - 1) / self.backtraceHalf, 1)

    def weight2(self, index):
        """
        :param index: starts with 0
        :return: e.g. backtrace=10, return 1, 0.9, 0.8, ..., 0.1, and 0.1 for all rest
        """
        return round(1 - min(index, self.backtraceQuarter - 1) / self.backtraceQuarter, 1)

    def append(self, candlestick: LICandlestick):
        self.totalCount += 1
        self.totalVolume += candlestick.volume
        self.totalBodySize += candlestick.bodySize()
        self.totalWickSize += candlestick.wickUpperSize() + candlestick.wickLowerSize()
        if self.defaultAvgBodySize is None:
            self.configs[LIConfigKey.candlestickAvgBodySize] = self.avgBodySize()
        if self.defaultAvgWickSize is None:
            self.configs[LIConfigKey.candlestickAvgWickSize] = self.avgWickSize()
        # Add the most recent one to first position
        self.candlesticks.insert(0, candlestick)
        # Remove last/staled/tailing candlesticks!
        while self.count() > self.windowSize:
            self.candlesticks.pop()

    def avgVolume(self) -> float:
        return round(self.totalVolume / max(self.totalCount, 1), LIGlobal.percentPrecision)

    def avgBodySize(self) -> float:
        return round(self.totalBodySize / max(self.totalCount, 1), LIGlobal.percentPrecision)

    def avgWickSize(self) -> float:
        # Each candlestick has upper&lower 2 wicks
        return round(self.totalWickSize / max(self.totalCount, 1) / 2, LIGlobal.percentPrecision)

    def trendReverseScore(self) -> float:
        score, crack = 0, 0
        for index, candlestick in enumerate(self.candlesticks):
            reverse = candlestick.dojiScore() + candlestick.spinningTopScore()
            score += reverse * self.weight(index)
            if reverse == 0:
                crack += 1
            if crack == self.tolerateNoise or index == self.backtraceHalf - 1:
                break
        return score

    def trendEndingScore(self):
        uptrendEndingScore = self.uptrendEndingScore()
        downtrendEndingScore = self.downtrendEndingScore()
        return uptrendEndingScore if abs(uptrendEndingScore[0]) >= abs(downtrendEndingScore[0]) else downtrendEndingScore

    def uptrendEndingScore(self) -> (float, float):
        """Return positive uptrend score"""
        score, crack = 0, 0
        strength, previous = 0, None
        bodySize, wickSize = 0, 0
        for index, current in enumerate(self.candlesticks):
            bodySize += current.bodySize() * self.weight(index)
            wickSize += current.wickSize() * self.weight(index)
            # Rising up/green candles
            if current.isUp() or current.isFlat():
                score += current.bodyRatio() * self.weight(index)
                if previous is not None:
                    # Up candles become longer/shorter
                    temp = previous.bodyRatio() - current.bodyRatio()
                    # Longer with lower wicks or shorter with upper wicks
                    temp += previous.wickLowerRatio() if temp > 0 else -previous.wickUpperRatio()
                    strength += temp * self.weight(index - 1)
                previous = current
            elif current.bodyRatio() < -0.5:
                break  # Abort if met large down candlestick
            else:
                score += current.bodyRatio() * self.weight(index)  # Decrease score a bit
                crack += 1
            if crack == self.tolerateNoise:
                break
        strength *= wickSize / bodySize if wickSize and bodySize else 1
        return score, strength

    def downtrendEndingScore(self) -> (float, float):
        """Return negative downtrend score"""
        score, crack = 0, 0
        strength, previous = 0, None
        bodySize, wickSize = 0, 0
        for index, current in enumerate(self.candlesticks):
            bodySize += current.bodySize() * self.weight(index)
            wickSize += current.wickSize() * self.weight(index)
            # Falling down/red candles
            if current.isDown() or current.isFlat():
                score += current.bodyRatio() * self.weight(index)
                if previous is not None:
                    # Down candles become longer/shorter
                    temp = previous.bodyRatio() - current.bodyRatio()
                    # Longer with upper wicks or shorter with lower wicks
                    temp += previous.wickUpperRatio() if temp > 0 else -previous.wickLowerRatio()
                    strength += temp * self.weight(index - 1)
                previous = current
            elif current.bodyRatio() > 0.5:
                break  # Abort for large up candle
            else:
                score += current.bodyRatio() * self.weight(index)  # Increase score a bit
                crack += 1
            if crack == self.tolerateNoise:
                break
        strength *= wickSize / bodySize if wickSize and bodySize else 1
        return score, strength

    def trendStartingScore(self):
        uptrendStartingScore = self.uptrendStartingScore()
        downtrendStartingScore = self.downtrendStartingScore()
        return uptrendStartingScore if abs(uptrendStartingScore[0]) >= abs(downtrendStartingScore[0]) else downtrendStartingScore

    def uptrendStartingScore(self) -> (float, float):
        """Return positive uptrend score"""
        score, crack = 0, 0
        strength, previous = 0, None
        bodySize, wickSize = 0, 0
        for index, current in enumerate(self.candlesticks):
            bodySize += current.bodySize() * self.weight(index)
            wickSize += current.wickSize() * self.weight(index)
            # Rising up/green candles
            if current.isUp() or current.isFlat():
                score += current.bodyRatio() * self.weight(index)
                if previous is not None:
                    # Up candles become longer/shorter
                    temp = previous.bodyRatio() - current.bodyRatio()
                    # Longer with lower wicks or shorter with upper wicks
                    temp += previous.wickLowerRatio() if temp > 0 else -previous.wickUpperRatio()
                    strength += temp * self.weight(index - 1)
                previous = current
            else:
                break
        strength *= wickSize / bodySize if wickSize and bodySize else 1
        return score, strength

    # Detect downtrend starting score in a narrow window
    def downtrendStartingScore(self) -> (float, float):
        """Return negative downtrend score"""
        score, crack = 0, 0
        strength, previous = 0, None
        bodySize, wickSize = 0, 0
        for index, current in enumerate(self.candlesticks):
            bodySize += current.bodySize() * self.weight(index)
            wickSize += current.wickSize() * self.weight(index)
            # Falling down/red candles
            if current.isDown() or current.isFlat():
                score += current.bodyRatio() * self.weight2(index)
                if previous is not None:
                    # Down candles become longer/shorter
                    temp = previous.bodyRatio() - current.bodyRatio()
                    # Longer with upper wicks or shorter with upper wicks
                    temp += previous.wickUpperRatio() if temp > 0 else -previous.wickLowerRatio()
                    strength += temp * self.weight2(index - 1)
                previous = current
            else:
                break  # Abort due to an unexpected up candlestick
        strength *= wickSize / bodySize if wickSize and bodySize else 1
        return score, strength

    def upperWickTrendScore(self):
        score = self.upperWickUptrendScore()
        return self.upperWickDowntrendScore() if score == 0 else score

    def upperWickUptrendScore(self) -> float:
        """
        :return: 4 for [4, 3, 1, 2, 2, 1, 2, 1]
        """
        score, crack = 0, 0
        previous = self.candlesticks[0]
        for current in self.candlesticks[1:]:
            if current.high <= previous.high:
                score += 1
                previous = current
            else:
                crack += 1
            if crack == self.tolerateNoise:
                break
        return score

    def upperWickDowntrendScore(self) -> float:
        """
        :return: -4 for [1, 2, 2, 1, 3, 4, 1, 2]
        """
        score, crack = 0, 0
        previous = self.candlesticks[0]
        for current in self.candlesticks[1:]:
            if current.high >= previous.high:
                score -= 1
                previous = current
            else:
                crack += 1
            if crack == self.tolerateNoise:
                break
        return score

    def lowerWickTrendScore(self) -> float:
        score = self.lowerWickUptrendScore()
        return self.lowerWickDowntrendScore() if score == 0 else score

    def lowerWickUptrendScore(self) -> float:
        """
        :return: 4 for [4, 3, 1, 2, 2, 1, 2, 1]
        """
        score, crack = 0, 0
        previous = self.candlesticks[0]
        for current in self.candlesticks[1:]:
            if current.low <= previous.low:
                score += 1
                previous = current
            else:
                crack += 1
            if crack == self.tolerateNoise:
                break
        return score

    def lowerWickDowntrendScore(self) -> float:
        """
        :return: -4 for [1, 2, 2, 1, 3, 4, 1, 2]
        """
        score, crack = 0, 0
        previous = self.candlesticks[0]
        for current in self.candlesticks[1:]:
            if current.low >= previous.low:
                score -= 1
                previous = current
            else:
                crack += 1
            if crack == self.tolerateNoise:
                break
        return score

    def volumeTrendScore(self):
        score = self.volumeUptrendScore()
        return self.volumeDowntrendScore() if score == 0 else score

    def volumeUptrendScore(self) -> float:
        """
        :return: 4 for [4, 3, 1, 2, 2, 1, 2, 1]
        """
        score, crack = 0, 0
        previous = self.candlesticks[0]
        for current in self.candlesticks[1:]:
            if current.volume <= previous.volume:
                score += 1
                previous = current
            else:
                crack += 1
            if crack == self.tolerateNoise:
                break
        return score

    def volumeDowntrendScore(self) -> float:
        """
        :return: -4 for [1, 2, 2, 1, 3, 4, 1, 2]
        """
        score, crack = 0, 0
        previous = self.candlesticks[0]
        for current in self.candlesticks[1:]:
            if current.volume >= previous.volume:
                score -= 1
                previous = current
            else:
                crack += 1
            if crack == self.tolerateNoise:
                break
        return score

    def __str__(self) -> str:
        result = ""
        if self.defaultAvgBodySize is None:
            result += f"avgBodySize={self.avgBodySize():.5f},"
        if self.defaultAvgWickSize is None:
            result += f"avgWickSize={self.avgWickSize():.5f},"
        if abs(self.trendEndingScore()[0]) > 0:
            result += f"trendEndingScore=({self.trendEndingScore()[0]:.2f},{self.trendEndingScore()[1]:.2f}),"
        if abs(self.trendReverseScore()) > 0:
            result += f"trendReverseScore={self.trendReverseScore():.2f},"
        if abs(self.trendStartingScore()[0]) > 0:
            result += f"trendStartingScore=({self.trendStartingScore()[0]:.2f},{self.trendStartingScore()[1]:.2f}),"
        if abs(self.upperWickTrendScore()) > 0:
            result += f"upperWickTrendScore={self.upperWickTrendScore():.2f},"
        if abs(self.lowerWickTrendScore()) > 0:
            result += f"lowerWickTrendScore={self.lowerWickTrendScore():.2f},"
        if abs(self.volumeTrendScore()) > 0:
            result += f"volumeTrendScore={self.volumeTrendScore():.2f},"
        result += f"latest {self.count()} candlesticks: "
        for candlestick in self.candlesticks:
            result += f"\n{candlestick}"
        return result
