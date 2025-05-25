# region imports

from indicator.LIInsightIndicator import *


# endregion

class LIMACDTrendFollowingIndicator(LIInsightIndicator):
    """
    The exponential moving average, or EMA, gives more weight to recent price data than the simple moving average, or SMA, enabling it to react
    and move more quickly than the SMA. The EMA is very popular in stock, futures and forex trading, and is often the basis of a trading strategy.
    A common trading strategy utilizing EMAs is to trade based on the position of a shorter-term (fast) EMA in relation to a longer-term (slow) EMA. For example,
    traders are bullish when the 20 EMA crosses above the 50 EMA or remains above the 50 EMA, and only turn bearish if the 20 EMA falls below the
    50 EMA.

    Momentum indicators, such as the average directional index, or ADX, or the moving average convergence divergence, or MACD, often indicate an
    upcoming change in market direction before the price moves far enough to cause a moving average crossover. Therefore, traders often use such
    momentum indicators as early warning signs that a market has either peaked or hit bottom. Combining both indicators can provide a robust
    trading system that alerts for both an entry (EMA crossover) and a take profit area (MACD/ADX).
    Trendlines are also often used in conjunction with moving averages, as they can provide confirmation a market is in a trend or indicate it has
    entered a ranging area. Various trendlines drawn on a chart produce chart patterns, such as channels, triangles, etc., that can be used as
    additional indicators of possible future market direction.

    MACD: A Primer -> https://www.investopedia.com/trading/macd
    MACD Indicator -> https://www.investopedia.com/terms/m/macd.asp

    This indicator will eventually combine MACD(fast&slow EMA), ADX, RSI and trendlines, with the flexibility to optimize for different securities.
    """

    def __init__(self, securityMonitor, positionManager, mainChart, configs):
        super().__init__(securityMonitor, positionManager, mainChart, configs)

        self.auxRSIPeriod = configs.get(LIConfigKey.auxRSIPeriod, LIDefault.auxRSIPeriod)
        self.signalPeriod = configs.get(LIConfigKey.signalPeriod, LIDefault.signalPeriod)
        self.fastEMAPeriod = configs.get(LIConfigKey.fastEMAPeriod, LIDefault.fastEMAPeriod)
        self.slowEMAPeriod = configs.get(LIConfigKey.slowEMAPeriod, LIDefault.slowEMAPeriod)
        self.longEMAPeriod = configs.get(LIConfigKey.longEMAPeriod, LIDefault.longEMAPeriod)
        self.heikinAshiPlies = configs.get(LIConfigKey.heikinAshiPlies, LIDefault.heikinAshiPlies)
        self.macdIndicatorTolerance = configs.get(LIConfigKey.macdIndicatorTolerance, LIDefault.macdIndicatorTolerance)

        self.dataConsolidator = None

        self.auxRSI = RelativeStrengthIndex(self.auxRSIPeriod) if self.auxRSIPeriod else None
        self.longEMA = ExponentialMovingAverage(self.longEMAPeriod) if self.longEMAPeriod else None
        if self.heikinAshiPlies:
            self.heikinAshi = HeikinAshi(self.securityMonitor.getSymbolStr())
            self.heikinAshi.Updated += self.onHeikinAshiUpdated  # Call back to update MACD indicator
        self.macdEMA = MovingAverageConvergenceDivergence(self.fastEMAPeriod, self.slowEMAPeriod, self.signalPeriod, MovingAverageType.Exponential)
        log(f"{self.getSymbol().Value}: Created MACD indicator with {LIConfigKey.fastEMAPeriod}={self.fastEMAPeriod}, {LIConfigKey.slowEMAPeriod}={self.slowEMAPeriod}, {LIConfigKey.signalPeriod}={self.signalPeriod}")
        self.macdEMA.Updated += self.onMacdIndicatorUpdated  # Callback to emit trade insights/signals

        self.mainChart.AddSeries(Series("Price", SeriesType.Line, "$", Color.Blue))
        if self.heikinAshiPlies:
            self.mainChart.AddSeries(Series("Heikin", SeriesType.Line, "$", Color.Orange))
        self.mainChart.AddSeries(Series("Fast", SeriesType.Line, "$", Color.Purple))
        self.mainChart.AddSeries(Series("Slow", SeriesType.Line, "$", Color.Red))
        if self.longEMAPeriod:
            self.mainChart.AddSeries(Series("EMA", SeriesType.Line, "$", Color.Green))
        self.mainChart.AddSeries(Series("Filled", SeriesType.Line, "$", Color.Red))
        self.macdChart = Chart(f"{self.securityMonitor.getSymbolStr()}-macd")
        getAlgo().AddChart(self.macdChart)
        self.macdChart.AddSeries(Series("Signal", SeriesType.Line, "", Color.Purple))
        self.macdChart.AddSeries(Series("Histogram", SeriesType.Bar, "", Color.Orange))
        self.macdChart.AddSeries(Series("Divergence", SeriesType.Line, "", Color.Red))
        if self.auxRSIPeriod:
            self.auxChart.AddSeries(Series("RSI", SeriesType.Line, "", Color.Blue))
            self.auxChart.AddSeries(Series("Trade", SeriesType.Line, "", Color.Orange))

        # To be called in onSecurityChanged()
        # self.resetIndicators(None, None)

    def resetIndicators(self, dailyHistoryCount=None, minsHistoryCount=None):
        if self.auxRSIPeriod:
            self.auxRSI.Reset()
        if self.longEMAPeriod:
            self.longEMA.Reset()
        if self.heikinAshiPlies:
            self.heikinAshi.Reset()
        self.macdEMA.Reset()

        # Recreate a new consolidator
        if self.dataConsolidator is not None:
            self.dataConsolidator.DataConsolidated -= self.onDataConsolidated
        self.dataConsolidator = self.securityMonitor.getConsolidator(self.indicatorPeriod)
        self.dataConsolidator.DataConsolidated += self.onDataConsolidated

        # Warm up with history data
        period = self.longEMAPeriod if self.longEMAPeriod else self.slowEMAPeriod
        totalPeriods = (period + 1) * self.indicatorPeriod
        bars = self.getHistoryBars(self.getSymbol(), totalPeriods, self.securityMonitor.getResolution())
        barsCount = 0
        for bar in bars:
            self.dataConsolidator.Update(bar)
            barsCount += 1
        log(f"{self.getSymbol().Value}: Reset indicators with totalPeriods={totalPeriods}, updated with {barsCount} history trade bars.")

    def onDataConsolidated(self, sender: Object, bar: Bar):
        if bar is None:
            return  # Just in case

        if self.heikinAshiPlies:
            self.heikinAshi.Update(bar)
        else:
            if self.auxRSIPeriod:
                self.auxRSI.Update(bar.EndTime, bar.Close)
            if self.longEMAPeriod:
                self.longEMA.Update(bar.EndTime, bar.Close)
            self.macdEMA.Update(bar.EndTime, bar.Close)

    def onHeikinAshiUpdated(self, sender: Object, updated: IndicatorDataPoint):
        if not self.heikinAshi.IsReady:
            return
        if self.auxRSIPeriod:
            self.auxRSI.Update(updated.EndTime, updated.Value)
        if self.longEMAPeriod:
            self.longEMA.Update(updated.EndTime, updated.Value)
        self.macdEMA.Update(updated.EndTime, updated.Value)

    def onMacdIndicatorUpdated(self, sender: Object, updated: IndicatorDataPoint):
        if not self.macdEMA.IsReady:
            return

        self.plotIndicatorCharts()

        tradeInsight = self.predictTradeInsight(updated.EndTime, updated)
        if tradeInsight is not None:
            self.tradeInsight = tradeInsight
            for listener in self.tradeInsightListeners:
                listener.onEmitTradeInsight(self.tradeInsight)
        return

    def onMonitorBarUpdated(self, bar: Bar):
        if self.getSymbol() == bar.Symbol:
            self.dataConsolidator.Update(bar)

    def plotIndicatorCharts(self):
        plot(self.mainChart.name, "Price", self.securityMonitor.getMarketPrice())
        if self.heikinAshiPlies:
            plot(self.mainChart.name, "Heikin", self.heikinAshi.Current.Value)
        plot(self.mainChart.name, "Fast", self.macdEMA.Fast.Current.Value)
        plot(self.mainChart.name, "Slow", self.macdEMA.Slow.Current.Value)
        if self.longEMAPeriod:
            plot(self.mainChart.name, "EMA", self.longEMA.Current.Value)
        plot(self.macdChart.name, "Signal", self.macdEMA.Signal.Current.Value)
        plot(self.macdChart.name, "Histogram", self.macdEMA.Histogram.Current.Value)
        plot(self.macdChart.name, "Divergence", self.macdEMA.Current.Value)
        if self.auxRSIPeriod:
            plot(self.auxChart.name, "RSI", int(self.auxRSI.Current.Value))

    def predictTradeInsight(self, timestamp=None, updated=None) -> LITradeInsight:
        tradeInsight = self.getTrendTradeInsight(timestamp, updated)
        # tradeInsight = self.getBiasTradeInsight(timestamp, updated)
        return tradeInsight

    def getTrendTradeInsight(self, timestamp=None, updated=None) -> LITradeInsight:
        symbolStr = updated.Symbol.Value if updated else self.getSymbol().Value

        if self.macdEMA.Histogram.Current.Value > self.macdIndicatorTolerance:
            return LITradeInsight(serialId=self.tradeInsight.serialId + 1,
                                  symbolStr=symbolStr,
                                  signalType=LISignalType.LONG,
                                  timestamp=timestamp)

        if self.macdEMA.Histogram.Current.Value < -self.macdIndicatorTolerance:
            return LITradeInsight(serialId=self.tradeInsight.serialId + 1,
                                  symbolStr=symbolStr,
                                  signalType=LISignalType.SHORT,
                                  timestamp=timestamp)

    def getBiasTradeInsight(self, timestamp=None, updated=None):
        symbolStr = updated.Symbol.Value if updated else self.getSymbol().Value

        # if self.macdEMA.Histogram.Current.Value > self.macdIndicatorTolerance:
        # if self.macdEMA.Histogram.Current.Value > self.macdIndicatorTolerance and \
        #         self.macdEMA.Slow.Current.Value > self.longEMA.Current.Value:
        if self.macdEMA.Histogram.Current.Value > self.macdIndicatorTolerance and \
                self.macdEMA.Current.Value < -self.macdIndicatorTolerance and \
                self.macdEMA.Slow.Current.Value > self.longEMA.Current.Value:
            return LITradeInsight(serialId=self.tradeInsight.serialId + 1,
                                  symbolStr=symbolStr,
                                  signalType=LISignalType.LONG,
                                  timestamp=timestamp)

        # if self.macdEMA.Histogram.Current.Value < -self.macdIndicatorTolerance:
        # if self.macdEMA.Histogram.Current.Value < -self.macdIndicatorTolerance and \
        #         self.macdEMA.Slow.Current.Value < self.longEMA.Current.Value:
        if self.macdEMA.Histogram.Current.Value < -self.macdIndicatorTolerance and \
                self.macdEMA.Current.Value > self.macdIndicatorTolerance and \
                self.macdEMA.Slow.Current.Value < self.longEMA.Current.Value:
            return LITradeInsight(serialId=self.tradeInsight.serialId + 1,
                                  symbolStr=symbolStr,
                                  signalType=LISignalType.SHORT,
                                  timestamp=timestamp)

    def onSecurityChanged(self, removedSecurity: Security):
        if removedSecurity is None:
            self.resetIndicators(None, None)

    def onDayOpenGapUpOrDownEvent(self):
        self.resetIndicators(dailyHistoryCount=None, minsHistoryCount=0)
