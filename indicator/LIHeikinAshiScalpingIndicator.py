# region imports

from QuantConnect.Indicators.CandlestickPatterns import *

from indicator.LICandlestickRollingWindow import *
from indicator.LIInsightIndicator import *


# endregion


class LIHeikinAshiScalpingIndicator(LIInsightIndicator):
    """
    Heikin-Ashi: A Better Candlestick -> https://www.investopedia.com/trading/heikin-ashi-better-candlestick/

    Bull Uptrend:
        Trend starts: rising up/green candles
        Trend becomes stronger: up candles become longer with less (lower/upper) wicks
        Trend becomes weaker: up candles become shorter with more (upper/lower) wicks
        Trend reverses: spinning tops or doji, plus upper wicks starts downtrend
    Bear Downtrend:
        Trend starts: falling down/red candles
        Trend becomes stronger: down candles become longer with less (upper/lower) wicks
        Trend becomes weaker: down candles become shorter with more (lower/upper) wicks
        Trend reverses: spinning tops or doji, plus lower wicks starts uptrend
    """

    def __init__(self, securityMonitor, positionManager, mainChart, configs):
        super().__init__(securityMonitor, positionManager, mainChart, configs)

        self.candlesticksWindowSize = 20  # How many history candlesticks to track
        self.candlestickConsolidator = None
        self.plotHeikinAshiChart = False

        # Below auxiliary/light-weight indicators to be updated in onHeikinAshiUpdated
        # Value range {0: Not, 1: Yes}, use our customized Doji instead of this one (too lax!)
        self.doji = Doji(f"{self.securityMonitor.getSymbolStr()}-doji")
        self.doji.Updated += self.onDojiUpdated
        # Value range {-1:Down, 0: Not, 1:Up}, use our customized Spinning Top instead of this one (too lax!)
        self.spinningTop = SpinningTop(f"{self.securityMonitor.getSymbolStr()}-spinningTop")
        self.spinningTop.Updated += self.onSpinningTopUpdated

        # Add to rolling window when it is updated, 0 is the most recent one
        self.heikinAshi = HeikinAshi(self.securityMonitor.getSymbolStr())
        self.candlestickRollingWindow = LICandlestickRollingWindow(self.candlesticksWindowSize, configs)
        self.heikinAshi.Updated += self.onHeikinAshiUpdated  # Callback to emit trade insights/signals

        if self.plotHeikinAshiChart:
            self.mainChart.AddSeries(getCandlestickSeries("Heikin", unit="$", z_index=-1))

        # To be called in onSecurityChanged()
        # self.resetIndicators()

        # In favor of logging future rolling windows
        self.futureTimestamps: [datetime] = list()
        self.magnitudes: [float] = list()

    def resetIndicators(self):
        self.doji.Reset()
        self.spinningTop.Reset()
        self.heikinAshi.Reset()
        self.candlestickRollingWindow.reset()

        # Recreate a new candlestick consolidator
        if self.candlestickConsolidator is not None:
            self.candlestickConsolidator.DataConsolidated -= self.onDataConsolidated
        self.candlestickConsolidator = self.securityMonitor.getConsolidator(self.indicatorPeriod)
        self.candlestickConsolidator.DataConsolidated += self.onDataConsolidated

        totalPeriods = (self.candlesticksWindowSize + 1) * self.indicatorPeriod
        bars = self.getHistoryBars(self.getSymbol(), totalPeriods, self.securityMonitor.getResolution())
        barsCount = 0
        for bar in bars:
            self.candlestickConsolidator.Update(bar)
            barsCount += 1
        log(f"{self.getSymbol().Value}: Reset HeikinAshi scalping indicator with totalPeriods={totalPeriods}, updated with {barsCount} history trade bars.")

    def onMonitorBarUpdated(self, bar):
        if self.getSymbol() == bar.Symbol:
            self.candlestickConsolidator.Update(bar)

    def onDataConsolidated(self, sender: Object, bar):
        self.heikinAshi.Update(bar)

    def onDojiUpdated(self, sender: Object, updated: IndicatorDataPoint):
        if not self.doji.IsReady or not self.candlestickRollingWindow.isReady():
            return
        # if updated.Value:
        #     log(f"Doji: value={updated.Value}, {self.candlestickRollingWindow}")

    def onSpinningTopUpdated(self, sender: Object, updated: IndicatorDataPoint):
        if not self.spinningTop.IsReady or not self.candlestickRollingWindow.isReady():
            return
        # if updated.Value:
        #     log(f"Spinning Top: value={updated.Value}, {self.candlestickRollingWindow}")

    def onHeikinAshiUpdated(self, sender: Object, updated: IndicatorDataPoint):
        if not self.heikinAshi.IsReady:
            return

        self.updateRollingWindow()

        tradeBar = TradeBar(self.heikinAshi.Current.EndTime,
                            self.heikinAshi.Current.Symbol,
                            self.heikinAshi.Open.Current.Value,
                            self.heikinAshi.High.Current.Value,
                            self.heikinAshi.Low.Current.Value,
                            self.heikinAshi.Close.Current.Value,
                            self.heikinAshi.Volume.Current.Value,
                            timedelta(minutes=self.indicatorPeriod))
        self.doji.Update(tradeBar)
        self.spinningTop.Update(tradeBar)
        self.plotIndicatorCharts(tradeBar)

        if not self.candlestickRollingWindow.isReady():
            return

        while self.futureTimestamps and self.futureTimestamps[0] <= self.candlestickRollingWindow.candlesticks[0].time:
            timestamp = self.futureTimestamps.pop(0) + timedelta(minutes=-self.candlesticksWindowSize)
            log(f"Pairs with {timestamp.strftime('%H:%M')}: {self.candlestickRollingWindow}")

        tradeInsight = self.predictTradeInsight(tradeBar.Time)
        if tradeInsight is not None:
            for listener in self.tradeInsightListeners:
                listener.onEmitTradeInsight(tradeInsight)

    def updateRollingWindow(self):
        candlestick = LICandlestick(self.heikinAshi.Current.EndTime,
                                    self.heikinAshi.Open.Current.Value,
                                    self.heikinAshi.High.Current.Value,
                                    self.heikinAshi.Low.Current.Value,
                                    self.heikinAshi.Close.Current.Value,
                                    self.heikinAshi.Volume.Current.Value,
                                    self.configs)
        self.candlestickRollingWindow.append(candlestick)

    def plotIndicatorCharts(self, bar: Bar):
        if self.plotHeikinAshiChart:
            plot(self.mainChart.name, "Heikin", bar)

    def predictTradeInsight(self, timestamp=None, updated=None) -> LITradeInsight:
        window = self.candlestickRollingWindow

        tradeInsight = self.isDowntrendReversing2Long(timestamp)
        if tradeInsight is not None:
            # self.futureTimestamps.append(window.candlesticks[0].time + timedelta(minutes=self.candlesticksWindowSize))
            # log(f"Reverse to Long: {window}")
            self.tradeInsight = tradeInsight
            return tradeInsight

        tradeInsight = self.isUptrendReversing2Short(timestamp)
        if tradeInsight is not None:
            # self.futureTimestamps.append(window.candlesticks[0].time + timedelta(minutes=self.candlesticksWindowSize))
            # log(f"Reverse to Short: {window}")
            self.tradeInsight = tradeInsight
            return tradeInsight

        # tradeInsight = self.isUptrendStarting2Long(timestamp)
        # if tradeInsight is not None:
        #     self.futureTimestamps.append(window.candlesticks[0].time + timedelta(minutes=self.candlesticksWindowSize))
        #     log(f"Start to Long: {window}")
        #     self.tradeInsight = tradeInsight
        #     return tradeInsight
        #
        # tradeInsight = self.isDowntrendStarting2Short(timestamp)
        # if tradeInsight is not None:
        #     self.futureTimestamps.append(window.candlesticks[0].time + timedelta(minutes=self.candlesticksWindowSize))
        #     log(f"Start to Short: {window}")
        #     self.tradeInsight = tradeInsight
        #     return tradeInsight

    # Detect a bear downtrend reversing to open long
    def isDowntrendReversing2Long(self, timestamp) -> LITradeInsight:
        window = self.candlestickRollingWindow
        (openLong, magnitude) = (True, 0)

        trendReverseScore = window.trendReverseScore()
        openLong = openLong and trendReverseScore > 1.5
        magnitude += abs(trendReverseScore)

        trendEndingScore = window.trendEndingScore()
        openLong = openLong and trendEndingScore[0] < -3
        openLong = openLong and trendEndingScore[1] <= 0
        magnitude += abs(trendEndingScore[0])
        magnitude += abs(trendEndingScore[1])

        lowerWickTrendScore = window.lowerWickTrendScore()
        openLong = openLong and lowerWickTrendScore >= 0
        magnitude += abs(lowerWickTrendScore)

        if openLong:
            self.magnitudes.append(magnitude)
            return LITradeInsight(serialId=self.tradeInsight.serialId + 1,
                                  symbolStr=self.getSymbol().Value,
                                  signalType=LISignalType.LONG,
                                  magnitude=magnitude,
                                  trendScore=trendEndingScore[0],
                                  trendStrength=trendEndingScore[1],
                                  trendReverseScore=trendReverseScore,
                                  timestamp=timestamp)
        return None

    # Detect a bull uptrend reversing to open short
    def isUptrendReversing2Short(self, timestamp) -> LITradeInsight:
        window = self.candlestickRollingWindow
        (openShort, magnitude) = (True, 0)

        trendReverseScore = window.trendReverseScore()
        openShort = openShort and trendReverseScore < -1.5
        magnitude += abs(trendReverseScore)

        trendEndingScore = window.trendEndingScore()
        openShort = openShort and trendEndingScore[0] > 3
        openShort = openShort and trendEndingScore[1] <= 0
        magnitude += abs(trendEndingScore[0])
        magnitude += abs(trendEndingScore[1])

        upperWickTrendScore = window.upperWickTrendScore()
        openShort = openShort and upperWickTrendScore <= 0
        magnitude += abs(upperWickTrendScore)

        if openShort:
            self.magnitudes.append(magnitude)
            return LITradeInsight(serialId=self.tradeInsight.serialId + 1,
                                  symbolStr=self.getSymbol().Value,
                                  signalType=LISignalType.SHORT,
                                  magnitude=magnitude,
                                  trendScore=trendEndingScore[0],
                                  trendStrength=trendEndingScore[1],
                                  trendReverseScore=trendReverseScore,
                                  timestamp=timestamp)

        return None

    # Detect uptrend starting to open long
    def isUptrendStarting2Long(self, timestamp) -> LITradeInsight:
        window = self.candlestickRollingWindow
        (openLong, magnitude) = (True, 0)

        trendReverseScore = window.trendReverseScore()
        openLong = openLong and trendReverseScore > 0
        magnitude += abs(trendReverseScore)

        trendStartingScore = window.trendStartingScore()
        openLong = openLong and trendStartingScore[0] > 3
        openLong = openLong and trendStartingScore[1] >= 0
        magnitude += abs(trendStartingScore[0])
        magnitude += abs(trendStartingScore[1])

        lowerWickTrendScore = window.lowerWickTrendScore()
        openLong = openLong and lowerWickTrendScore >= 0
        magnitude += abs(lowerWickTrendScore)

        upperWickTrendScore = window.upperWickTrendScore()
        openLong = openLong and upperWickTrendScore >= 0
        magnitude += abs(upperWickTrendScore)

        if openLong:
            self.magnitudes.append(magnitude)
            return LITradeInsight(serialId=self.tradeInsight.serialId + 1,
                                  symbolStr=self.getSymbol().Value,
                                  signalType=LISignalType.LONG,
                                  magnitude=magnitude,
                                  trendScore=trendStartingScore[0],
                                  trendStrength=trendStartingScore[1],
                                  trendReverseScore=trendReverseScore,
                                  timestamp=timestamp)
        return None

    # Detect downtrend starting to open short
    def isDowntrendStarting2Short(self, timestamp) -> LITradeInsight:
        window = self.candlestickRollingWindow
        (openShort, magnitude) = (True, 0)

        trendReverseScore = window.trendReverseScore()
        openShort = openShort and trendReverseScore < 0
        magnitude += abs(trendReverseScore)

        trendStartingScore = window.trendStartingScore()
        openShort = openShort and trendStartingScore[0] < -3
        openShort = openShort and trendStartingScore[1] >= 0
        magnitude += abs(trendStartingScore[0])
        magnitude += abs(trendStartingScore[1])

        upperWickTrendScore = window.upperWickTrendScore()
        openShort = openShort and upperWickTrendScore <= 0
        magnitude += abs(upperWickTrendScore)

        lowerWickTrendScore = window.lowerWickTrendScore()
        openShort = openShort and lowerWickTrendScore <= 0
        magnitude += abs(lowerWickTrendScore)

        if openShort:
            self.magnitudes.append(magnitude)
            return LITradeInsight(serialId=self.tradeInsight.serialId + 1,
                                  symbolStr=self.getSymbol().Value,
                                  signalType=LISignalType.SHORT,
                                  magnitude=magnitude,
                                  trendScore=trendStartingScore[0],
                                  trendStrength=trendStartingScore[1],
                                  trendReverseScore=trendReverseScore,
                                  timestamp=timestamp)

        return None

    def onSecurityChanged(self, removedSecurity: Security):
        if removedSecurity is None:
            self.resetIndicators()

    def onDayOpenGapUpOrDownEvent(self):
        self.resetIndicators()
