# region imports

from indicator.LIBollingerBand import *
from indicator.LIInsightIndicator import *
from indicator.LIHeikinAshiScalpingIndicator import *


# endregion

def getStochasticJ(kValue, dValue):
    return 3 * kValue - 2 * dValue


class LIStochasticComboIndicator(LIInsightIndicator):
    """
    Stochastic combo indicator can optionally enable Heikin Ashi, MACD, KDJ, RSI/SRSI EMA to identify the trade insight!
    [Indicators](https://www.quantconnect.com/docs/v2/writing-algorithms/indicators/supported-indicators)
    [MACD: A Primer](https://www.investopedia.com/trading/macd)
    [MACD Indicator](https://www.investopedia.com/terms/m/macd.asp)
    [KDJ: Stochastic KDJ](https://www.quantconnect.com/docs/v2/writing-algorithms/indicators/supported-indicators/stochastic)
    [SRSI: Stochastic RSI](https://www.quantconnect.com/docs/v2/writing-algorithms/indicators/supported-indicators/stochastic-relative-strength-index
    """

    def __init__(self, securityMonitor, positionManager, mainChart, configs):
        super().__init__(securityMonitor, positionManager, mainChart, configs)

        self.heikinAshiPlies = configs.get(LIConfigKey.heikinAshiPlies, LIDefault.heikinAshiPlies)
        self.addVolumeSeries = configs.get(LIConfigKey.addVolumeSeries, LIDefault.addVolumeSeries)
        self.stochasticComboParams = configs.get(LIConfigKey.stochasticComboParams, LIDefault.stochasticComboParams)
        self.macdIndicatorTolerance = configs.get(LIConfigKey.macdIndicatorTolerance, LIDefault.macdIndicatorTolerance)
        self.heikinAshiIndicatorTolerance = 5  # 3~50, adjust dynamically if range ATR is enabled!

        self.dataConsolidator = None
        self.heikinAshies: list[HeikinAshi] = []
        self.rangeATR: ExponentialMovingAverage = None
        self.trendEMA: ExponentialMovingAverage = None
        self.macdEMA: MovingAverageConvergenceDivergence = None
        self.standardRSI: RelativeStrengthIndex = None
        self.stochasticKDJ: Stochastic = None
        self.stochasticRSI: StochasticRelativeStrengthIndex = None

        self.rollingWindowSize = 5

        if self.heikinAshiPlies:
            for n in range(self.heikinAshiPlies):
                heikinAshi = HeikinAshi(str(n))
                heikinAshi.updated += self.onHeikinAshiUpdated  # Call back to update other indicators
                self.heikinAshies.append(heikinAshi)
        if LIIndicator.ATR in self.stochasticComboParams:
            params = self.stochasticComboParams[LIIndicator.KDJ]
            self.rangeATR = ExponentialMovingAverage(params[0])
        if LIIndicator.EMA in self.stochasticComboParams:
            self.trendEMA = ExponentialMovingAverage(self.stochasticComboParams[LIIndicator.EMA])
        if LIIndicator.RSI in self.stochasticComboParams:
            self.standardRSI = RelativeStrengthIndex(self.stochasticComboParams[LIIndicator.RSI])
        if LIIndicator.KDJ in self.stochasticComboParams:
            params = self.stochasticComboParams[LIIndicator.KDJ]
            self.stochasticKDJ = Stochastic(params[0], params[1], params[2])
            self.stochasticKDJ.window.size = self.rollingWindowSize
            self.stochasticKDJ.stoch_k.window.size = self.rollingWindowSize
            self.stochasticKDJ.stoch_d.window.size = self.rollingWindowSize
        if LIIndicator.MACD in self.stochasticComboParams:
            params = self.stochasticComboParams[LIIndicator.MACD]
            self.macdEMA = MovingAverageConvergenceDivergence(params[0], params[1], params[2], MovingAverageType.SIMPLE)
            # self.macdEMA.Updated += self.onMacdIndicatorUpdated  # Callback to emit trade insights/signals
        if LIIndicator.SRSI in self.stochasticComboParams:
            params = self.stochasticComboParams[LIIndicator.SRSI]
            self.stochasticRSI = StochasticRelativeStrengthIndex(params[0], params[1], params[2], params[3], MovingAverageType.SIMPLE)
            self.stochasticRSI.window.size = self.rollingWindowSize
            self.stochasticRSI.k.window.size = self.rollingWindowSize
            self.stochasticRSI.d.window.size = self.rollingWindowSize
            # self.stochasticRSI.Updated += self.onStochasticRSIUpdated  # Callback to emit trade insights/signals

        self.mainChart.AddSeries(getSeries("Price", unit="$"))
        self.mainChart.AddSeries(getSeries("Filled", type=SeriesType.SCATTER, unit="$", color=Color.ORANGE, marker=ScatterMarkerSymbol.CIRCLE, z_index=10))
        self.mainChart.AddSeries(
            getSeries(LISignalType.LONG, type=SeriesType.SCATTER, unit="$", color=Color.GREEN, marker=ScatterMarkerSymbol.TRIANGLE, z_index=100))
        self.mainChart.AddSeries(
            getSeries(LISignalType.SHORT, type=SeriesType.SCATTER, unit="$", color=Color.RED, marker=ScatterMarkerSymbol.TRIANGLE_DOWN, z_index=101))
        self.mainChart.AddSeries(
            getSeries(LISignalType.CLOSE, type=SeriesType.SCATTER, unit="$", color=Color.GOLD, marker=ScatterMarkerSymbol.DIAMOND, z_index=102))
        if self.addVolumeSeries:
            self.mainChart.AddSeries(getSeries("Volume", type=SeriesType.BAR, index=1, color=Color.GRAY))
        self.mainChart.AddSeries(getCandlestickSeries("Heikin" if self.heikinAshies else "Candle", unit="$", z_index=-10))
        if self.rangeATR:
            self.auxChart.AddSeries(getSeries("Range", type=SeriesType.LINE, color=Color.BROWN))
        if self.trendEMA:
            self.mainChart.AddSeries(getSeries("Trend", unit="$", color=Color.GRAY, z_index=-100))
        if self.macdEMA:
            # self.mainChart.AddSeries(getSeries("Fast", unit="$", color=Color.PURPLE))
            # self.mainChart.AddSeries(getSeries("Slow", unit="$", color=Color.ORANGE))
            self.macdChart = Chart(f"{self.securityMonitor.getSymbolStr()}-macd")
            getAlgo().AddChart(self.macdChart)
            self.macdChart.AddSeries(getSeries("Signal", color=Color.ORANGE))
            self.macdChart.AddSeries(getSeries("Divergence", color=Color.BLUE))
            self.macdChart.AddSeries(getSeries("Histogram", type=SeriesType.BAR, color=Color.GRAY, z_index=-10))
        self.stochasticChart = Chart(f"{self.securityMonitor.getSymbolStr()}-stochastic")
        getAlgo().AddChart(self.stochasticChart)
        if self.standardRSI:
            self.stochasticChart.AddSeries(getSeries(LIIndicator.RSI, color=Color.PURPLE, z_index=-100))
        if self.stochasticRSI:
            self.stochasticChart.AddSeries(getSeries("srsiK", color=Color.BLUE))
            self.stochasticChart.AddSeries(getSeries("srsiD", color=Color.ORANGE))
            self.stochasticChart.AddSeries(getSeries("srsiJ", color=Color.GRAY, z_index=-10))
            self.stochasticChart.AddSeries(getSeries("srsiUpper", color=Color.GRAY, z_index=-11))
            self.stochasticChart.AddSeries(getSeries("srsiLower", color=Color.GRAY, z_index=-12))
        if self.stochasticKDJ:
            self.stochasticChart.AddSeries(getSeries("K", color=Color.BLUE, index=1))
            self.stochasticChart.AddSeries(getSeries("D", color=Color.ORANGE, index=1))
            self.stochasticChart.AddSeries(getSeries("J", color=Color.GRAY, index=1, z_index=-10))
            self.stochasticChart.AddSeries(getSeries("upper", color=Color.GRAY, index=1, z_index=-11))
            self.stochasticChart.AddSeries(getSeries("lower", color=Color.GRAY, index=1, z_index=-12))

        # To be called in onSecurityChanged()
        # self.resetIndicators(None, None)

    def resetIndicators(self, dailyHistoryCount=None, minsHistoryCount=None):
        # Reset all indicators
        if self.heikinAshies:
            for heikinAshi in self.heikinAshies:
                heikinAshi.reset()
        if self.rangeATR:
            self.rangeATR.reset()
        if self.trendEMA:
            self.trendEMA.reset()
        if self.macdEMA:
            self.macdEMA.reset()
        if self.standardRSI:
            self.standardRSI.reset()
        if self.stochasticRSI:
            self.stochasticRSI.reset()
        if self.stochasticKDJ:
            self.stochasticKDJ.reset()

        # Recreate a new consolidator
        if self.dataConsolidator is not None:
            self.dataConsolidator.DataConsolidated -= self.onDataConsolidated
        self.dataConsolidator = self.securityMonitor.getConsolidator(self.indicatorPeriod)
        self.dataConsolidator.DataConsolidated += self.onDataConsolidated

        # Warm up with history data
        period = self.trendEMA.warm_up_period if self.trendEMA else self.macdEMA.warm_up_period if self.macdEMA else self.stochasticRSI.warm_up_period \
            if self.stochasticRSI else self.stochasticKDJ.warm_up_period
        totalPeriods = (period + 1) * self.indicatorPeriod
        bars = self.getHistoryBars(self.getSymbol(), totalPeriods, self.securityMonitor.getResolution())
        barsCount = 0
        for bar in bars:
            self.dataConsolidator.Update(bar)
            barsCount += 1
        self.isWarmedUp = True
        log(f"{self.getSymbol().Value}: Reset Stochastic combo indicator with totalPeriods={totalPeriods}, updated with {barsCount} history trade bars.")

    def onMonitorBarUpdated(self, bar: Bar):
        if self.getSymbol() == bar.Symbol:
            self.dataConsolidator.Update(bar)

    def onDataConsolidated(self, sender: Object, bar: Bar):
        if bar is None:
            return  # Just in case

        if self.heikinAshies:
            self.heikinAshies[0].update(bar)
        else:
            self.updateIndicators(bar)
            self.plotIndicatorCharts(bar)

        if not self.isWarmedUp:
            return  # Abort

        tradeInsight = self.predictTradeInsight()
        if tradeInsight and tradeInsight.signalType != LISignalType.NONE:
            # Update charts if trade signal changed
            if self.tradeInsight.signalType != tradeInsight.signalType:
                self.tradeInsight = tradeInsight
                if tradeInsight.isLongSignal() and not self.isBearishBias():
                    plot(self.mainChart.name, LISignalType.LONG, self.securityMonitor.getMarketPrice())
                elif tradeInsight.isShortSignal() and not self.isBullishBias():
                    plot(self.mainChart.name, LISignalType.SHORT, self.securityMonitor.getMarketPrice())
                elif tradeInsight.isCloseSignal():
                    plot(self.mainChart.name, LISignalType.CLOSE, self.securityMonitor.getMarketPrice())
                # Notify downstream listeners for trading
                for listener in self.tradeInsightListeners:
                    listener.onEmitTradeInsight(self.tradeInsight)

    def onHeikinAshiUpdated(self, sender: HeikinAshi, updated: IndicatorDataPoint):
        if not sender.is_ready:
            return
        tradeBar = TradeBar(sender.Current.EndTime,
                            sender.Current.Symbol,
                            sender.Open.Current.Value,
                            sender.High.Current.Value,
                            sender.Low.Current.Value,
                            sender.Close.Current.Value,
                            sender.Volume.Current.Value,
                            timedelta(minutes=self.indicatorPeriod))
        n = int(sender.name)
        if n < len(self.heikinAshies) - 1:
            self.heikinAshies[n + 1].update(tradeBar)  # Call next ply
        else:
            self.updateIndicators(tradeBar)
            self.plotIndicatorCharts(tradeBar)

    def updateIndicators(self, data: IBaseData):
        if self.rangeATR:
            if self.positionManager.isExchangeOpen():  # Avoid using extend data bar streaming!
                self.rangeATR.update(data.end_time, abs(data.open - data.close))
        if self.trendEMA:
            self.trendEMA.update(data)
        if self.macdEMA:
            self.macdEMA.update(data)
        if self.standardRSI:
            self.standardRSI.update(data)
        if self.stochasticRSI:
            self.stochasticRSI.update(data)
        if self.stochasticKDJ:
            self.stochasticKDJ.update(data)

    def plotIndicatorCharts(self, bar: Bar):
        if not self.isWarmedUp:
            return  # Abort
        if LIDefault.verbose:
            log(f"{self.getSymbol().value}: Plot indicator charts for endTime={bar.EndTime}, {bar}")
        plot(self.mainChart.name, "Heikin" if self.heikinAshies else "Candle", bar)
        if self.addVolumeSeries:
            plot(self.mainChart.name, "Volume", bar.Volume)
        if self.rangeATR and self.rangeATR.is_ready:
            plot(self.auxChart.name, "Range", self.rangeATR.current.value)
        if self.trendEMA and self.trendEMA.is_ready:
            plot(self.mainChart.name, "Trend", self.trendEMA.Current.Value)
        if self.macdEMA and self.macdEMA.is_ready:
            # plot(self.mainChart.name, "Fast", self.macdEMA.Fast.Current.Value)
            # plot(self.mainChart.name, "Slow", self.macdEMA.Slow.Current.Value)
            plot(self.macdChart.name, "Signal", self.macdEMA.Signal.Current.Value)
            plot(self.macdChart.name, "Histogram", self.macdEMA.Histogram.Current.Value)
            plot(self.macdChart.name, "Divergence", self.macdEMA.Current.Value)
        if self.standardRSI and self.standardRSI.is_ready:
            plot(self.stochasticChart.name, LIIndicator.RSI, int(self.standardRSI.Current.Value))
        if self.stochasticRSI and self.stochasticRSI.is_ready:
            plot(self.stochasticChart.name, "srsiK", int(self.stochasticRSI.k.Current.Value))
            plot(self.stochasticChart.name, "srsiD", int(self.stochasticRSI.d.Current.Value))
            plot(self.stochasticChart.name, "srsiJ", int(getStochasticJ(self.stochasticRSI.k.current.value, self.stochasticRSI.d.current.value)))
            plot(self.stochasticChart.name, "srsiUpper", self.stochasticComboParams[LIIndicator.SRSI][4])
            plot(self.stochasticChart.name, "srsiLower", self.stochasticComboParams[LIIndicator.SRSI][5])
        if self.stochasticKDJ and self.stochasticKDJ.is_ready:
            plot(self.stochasticChart.name, "K", int(self.stochasticKDJ.stoch_k.current.value))
            plot(self.stochasticChart.name, "D", int(self.stochasticKDJ.stoch_d.current.value))
            plot(self.stochasticChart.name, "J", int(getStochasticJ(self.stochasticKDJ.stoch_k.current.value, self.stochasticKDJ.stoch_d.current.value)))
            plot(self.stochasticChart.name, "upper", self.stochasticComboParams[LIIndicator.KDJ][3])
            plot(self.stochasticChart.name, "lower", self.stochasticComboParams[LIIndicator.KDJ][4])

    def predictTradeInsight(self, timestamp=None, updated=None) -> LITradeInsight:
        symbolStr = updated.Symbol.Value if updated else self.getSymbol().Value
        signalType = self.getHeikinAshiSignal()
        # kdjSignalType = self.getStochasticKDJSignal()
        # if signalType == LISignalType.LONG and kdjSignalType == LISignalType.SHORT:
        #     signalType = LISignalType.CLOSE
        serialId = (self.tradeInsight.serialId if self.tradeInsight else 0) + 1
        tradeInsight = None
        if signalType != LISignalType.NONE:
            return LITradeInsight(serialId=serialId, symbolStr=symbolStr, signalType=signalType, timestamp=timestamp)
        return tradeInsight

    def getEMASignal(self) -> LISignalType:
        signalType = LISignalType.NONE
        marketPrice = self.securityMonitor.getMarketPrice()
        if marketPrice > self.trendEMA.current.value:
            signalType = LISignalType.LONG
        elif marketPrice < self.trendEMA.current.value:
            signalType = -LISignalType.SHORT
        return signalType

    def getMacdEMASignal(self) -> LISignalType:
        signalType = LISignalType.NONE
        if self.macdEMA.Histogram.Current.Value > self.macdIndicatorTolerance:
            signalType = LISignalType.LONG
        elif self.macdEMA.Histogram.Current.Value < -self.macdIndicatorTolerance:
            signalType = LISignalType.SHORT
        return signalType

    def getHeikinAshiSignal(self) -> LISignalType:
        signalType = LISignalType.NONE
        heikinAshi = self.heikinAshies[-1]  # Use the last one!
        difference = heikinAshi.close.current.value - heikinAshi.open.current.value
        if difference > self.getHeikinAshiTolerance():
            signalType = LISignalType.LONG
        elif difference < -self.getHeikinAshiTolerance():
            signalType = LISignalType.SHORT
        return signalType

    def getHeikinAshiTolerance(self):
        if self.rangeATR and self.rangeATR.is_ready:
            params = self.stochasticComboParams[LIIndicator.ATR]
            return self.rangeATR.current.value / params[1]
        return self.heikinAshiIndicatorTolerance

    def getStochasticRSISignal(self) -> LISignalType:
        signalType = LISignalType.NONE
        jTolerance, stochasticJs = 0, []  # 15
        for i in range(min(self.stochasticRSI.k.window.count, self.stochasticRSI.d.window.count)):
            stochasticJs.append(getStochasticJ(self.stochasticRSI.k.window[i].value, self.stochasticRSI.d.window[i].value))
        averageKD = ((sum(v.value for v in self.stochasticRSI.k.window) + sum(v.value for v in self.stochasticRSI.d.window)) /
                     (self.stochasticRSI.k.window.count + self.stochasticRSI.d.window.count))
        upperBand, lowerBand = params[4], params[5]
        # Check long side
        if self.stochasticRSI.k.current.value >= self.stochasticRSI.d.current.value:
            hasUptrendJs = stochasticJs[2] < stochasticJs[1] < stochasticJs[0] and stochasticJs[2] < 0 - jTolerance
            if self.stochasticRSI.k.current.value > lowerBand > self.stochasticRSI.k.previous.value and hasUptrendJs:
                signalType = LISignalType.LONG  # Cross low boundary and reverse to up/long trend
            elif self.positionManager.getUnrealizedProfitPercent() < -1 and averageKD - 50 < 0:
                signalType = LISignalType.SHORT  # Flip it upon the unrealized loss and score
        # Check short side
        if self.stochasticRSI.k.current.value <= self.stochasticRSI.d.current.value:
            hasDownTrendJs = stochasticJs[2] > stochasticJs[1] > stochasticJs[0] and stochasticJs[2] > 100 + jTolerance
            if self.stochasticRSI.k.current.value < upperBand < self.stochasticRSI.k.previous.value and hasDownTrendJs:
                signalType = LISignalType.SHORT  # Cross high boundary and reverse to down/short trend
            elif self.positionManager.getUnrealizedProfitPercent() < -1 and averageKD - 50 > 0:
                signalType = LISignalType.LONG  # Flip it upon the unrealized loss and score
        return signalType

    def getStochasticKDJSignal(self) -> LISignalType:
        signalType = LISignalType.NONE
        params = self.stochasticComboParams[LIIndicator.KDJ]
        upperBound, lowerBound = params[3], params[4]
        k, kPrev = self.stochasticKDJ.stoch_k.current.value, self.stochasticKDJ.stoch_k.previous.value
        d, dPrev = self.stochasticKDJ.stoch_d.current.value, self.stochasticKDJ.stoch_d.previous.value
        # Cong still need to refine below
        if k > d and kPrev < lowerBound < k:
            signalType = LISignalType.LONG
        elif k < d and kPrev > upperBound > k:
            signalType = LISignalType.SHORT
        return signalType

    def onSecurityChanged(self, removedSecurity: Security):
        if removedSecurity is None:
            self.resetIndicators(None, None)

    def __str__(self) -> str:
        result = ""
        if self.rangeATR:
            result += f"atr={self.rangeATR.current.value}"
        if self.trendEMA:
            result += f"emaSignal={self.getEMASignal()}, "
        if self.macdEMA:
            result += f"macdEMASignal={self.getMacdEMASignal()}, "
        if self.heikinAshies:
            result += f"heikinAshiSignal={self.getHeikinAshiSignal()}"
        if self.stochasticRSI:
            result += f"stochasticRSISignal={self.getStochasticRSISignal()}, "
        if self.stochasticKDJ:
            result += f"stochasticKDJSignal={self.getStochasticKDJSignal()}, "
        return result
