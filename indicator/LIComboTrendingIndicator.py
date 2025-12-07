from AlgorithmImports import *

from indicator.LIBollingerBand import *
from indicator.LIInsightIndicator import *
from indicator.LIDailyTrendingIndicator import *
from indicator.LIWeeklyTrendingIndicator import *


def getStochasticJ(kValue, dValue):
    return 3 * kValue - 2 * dValue


class LIComboTrendingIndicator(LIInsightIndicator):
    """
    This combo trending indicator can optionally enable Heikin Ashi, MACD, KDJ, RSI/SRSI EMA to identify the trade insight!
    [Indicators](https://www.quantconnect.com/docs/v2/writing-algorithms/indicators/supported-indicators)
    [MACD: A Primer](https://www.investopedia.com/trading/macd)
    [MACD Indicator](https://www.investopedia.com/terms/m/macd.asp)
    [KDJ: Stochastic KDJ](https://www.quantconnect.com/docs/v2/writing-algorithms/indicators/supported-indicators/stochastic)
    [SRSI: Stochastic RSI](https://www.quantconnect.com/docs/v2/writing-algorithms/indicators/supported-indicators/stochastic-relative-strength-index
    """

    def __init__(self, securityMonitor, positionManager, mainChart, configs):
        super().__init__(securityMonitor, positionManager, mainChart, configs)

        self.comboTrendingParams = configs.get(LIConfigKey.comboTrendingParams, LIDefault.comboTrendingParams)
        if LIIndicator.DAILY in self.comboTrendingParams and LIIndicator.WEEKLY in self.comboTrendingParams:
            raise ValueError("Cannot enable both DAILY and WEEKLY trending indicators at the same time!")

        self.macdIndicatorTolerance = configs.get(LIConfigKey.macdIndicatorTolerance, LIDefault.macdIndicatorTolerance)
        self.heikinAshiIndicatorTolerance = 0  # 3~50, adjust dynamically if range ATR is enabled!
        self.rollingWindowSize = 10

        self.lastBar = None
        self.dataConsolidator = None
        self.heikinAshies: list[HeikinAshi] = []
        self.rangeATR: ExponentialMovingAverage = None
        self.trendEMA: ExponentialMovingAverage = None
        self.macdEMA: MovingAverageConvergenceDivergence = None
        self.standardRSI: RelativeStrengthIndex = None
        self.stochasticKDJ: Stochastic = None
        self.stochasticRSI: StochasticRelativeStrengthIndex = None
        self.trendingIndicator: LIInsightIndicator = None

        if self.heikinAshiPlies:
            for n in range(self.heikinAshiPlies):
                heikinAshi = HeikinAshi(str(n))
                heikinAshi.window.size = self.rollingWindowSize
                heikinAshi.updated += self.onHeikinAshiUpdated  # Call back to update other indicators
                self.heikinAshies.append(heikinAshi)

        if LIIndicator.ATR in self.comboTrendingParams:
            params = self.comboTrendingParams[LIIndicator.ATR]
            self.rangeATR = ExponentialMovingAverage(params[0])
        if LIIndicator.EMA in self.comboTrendingParams:
            self.trendEMA = ExponentialMovingAverage(self.comboTrendingParams[LIIndicator.EMA])
        if LIIndicator.RSI in self.comboTrendingParams:
            self.standardRSI = RelativeStrengthIndex(self.comboTrendingParams[LIIndicator.RSI])
        if LIIndicator.KDJ in self.comboTrendingParams:
            params = self.comboTrendingParams[LIIndicator.KDJ]
            self.stochasticKDJ = Stochastic(params[0], params[1], params[2])
            self.stochasticKDJ.window.size = self.rollingWindowSize
            self.stochasticKDJ.stoch_k.window.size = self.rollingWindowSize
            self.stochasticKDJ.stoch_d.window.size = self.rollingWindowSize
        if LIIndicator.MACD in self.comboTrendingParams:
            params = self.comboTrendingParams[LIIndicator.MACD]
            self.macdEMA = MovingAverageConvergenceDivergence(params[0], params[1], params[2], MovingAverageType.SIMPLE)
            # self.macdEMA.updated += self.onMacdIndicatorUpdated  # Callback to emit trade insights/signals
        if LIIndicator.SRSI in self.comboTrendingParams:
            params = self.comboTrendingParams[LIIndicator.SRSI]
            self.stochasticRSI = StochasticRelativeStrengthIndex(params[0], params[1], params[2], params[3], MovingAverageType.SIMPLE)
            self.stochasticRSI.window.size = self.rollingWindowSize
            self.stochasticRSI.k.window.size = self.rollingWindowSize
            self.stochasticRSI.d.window.size = self.rollingWindowSize
            # self.stochasticRSI.updated += self.onStochasticRSIUpdated  # Callback to emit trade insights/signals
        if LIIndicator.DAILY in self.comboTrendingParams:
            self.trendingIndicator = LIDailyTrendingIndicator(self.securityMonitor, self.positionManager, self.mainChart, self.configs)
        if LIIndicator.WEEKLY in self.comboTrendingParams:
            self.trendingIndicator = LIWeeklyTrendingIndicator(self.securityMonitor, self.positionManager, self.mainChart, self.configs)

        self.mainChart.add_series(getSeries("Price", unit="$"))
        self.mainChart.add_series(getSeries("Filled", type=SeriesType.SCATTER, unit="$", color=Color.ORANGE, marker=ScatterMarkerSymbol.CIRCLE, z_index=10))
        self.mainChart.add_series(
            getSeries(LISignalType.LONG, type=SeriesType.SCATTER, unit="$", color=Color.GREEN, marker=ScatterMarkerSymbol.TRIANGLE, z_index=100))
        self.mainChart.add_series(
            getSeries(LISignalType.SHORT, type=SeriesType.SCATTER, unit="$", color=Color.RED, marker=ScatterMarkerSymbol.TRIANGLE_DOWN, z_index=101))
        self.mainChart.add_series(
            getSeries(LISignalType.CLOSE, type=SeriesType.SCATTER, unit="$", color=Color.GOLD, marker=ScatterMarkerSymbol.DIAMOND, z_index=102))
        if self.addVolumeSeries:
            self.mainChart.add_series(getSeries("Volume", type=SeriesType.BAR, index=1, color=Color.GRAY))
        if self.trendingIndicator:
            self.mainChart.add_series(getSeries(f"{self.indicatorPeriod[1]}Price", unit="$", color=Color.BEIGE, z_index=-10))
        else:
            self.mainChart.add_series(getCandlestickSeries(f"{self.indicatorPeriod[1]}Price", unit="$", color=Color.BEIGE, z_index=-10))
        if self.rangeATR:
            self.auxChart = Chart(f"{self.securityMonitor.getSymbolStr()}-aux")
            getAlgo().add_chart(self.auxChart)
            self.auxChart.add_series(getSeries("Range", type=SeriesType.LINE, color=Color.BROWN))
        if self.trendEMA:
            self.mainChart.add_series(getSeries("Trend", unit="$", color=Color.GRAY, z_index=-100))
        if self.macdEMA:
            # self.mainChart.add_series(getSeries("Fast", unit="$", color=Color.PURPLE))
            # self.mainChart.add_series(getSeries("Slow", unit="$", color=Color.ORANGE))
            self.macdChart = Chart(f"{self.securityMonitor.getSymbolStr()}-macd")
            getAlgo().add_chart(self.macdChart)
            self.macdChart.add_series(getSeries("Signal", color=Color.ORANGE))
            self.macdChart.add_series(getSeries("Divergence", color=Color.BLUE))
            self.macdChart.add_series(getSeries("Histogram", type=SeriesType.BAR, color=Color.GRAY, z_index=-10))
        if self.standardRSI or self.stochasticRSI or self.stochasticKDJ:
            self.stochasticChart = Chart(f"{self.securityMonitor.getSymbolStr()}-stochastic")
            getAlgo().add_chart(self.stochasticChart)
        if self.standardRSI:
            self.stochasticChart.add_series(getSeries(LIIndicator.RSI, color=Color.PURPLE, z_index=-100))
        if self.stochasticRSI:
            self.stochasticChart.add_series(getSeries("srsiK", color=Color.BLUE))
            self.stochasticChart.add_series(getSeries("srsiD", color=Color.ORANGE))
            self.stochasticChart.add_series(getSeries("srsiJ", color=Color.GRAY, z_index=-10))
            self.stochasticChart.add_series(getSeries("srsiUpper", color=Color.GRAY, z_index=-11))
            self.stochasticChart.add_series(getSeries("srsiLower", color=Color.GRAY, z_index=-12))
        if self.stochasticKDJ:
            self.stochasticChart.add_series(getSeries("K", color=Color.BLUE, index=1))
            self.stochasticChart.add_series(getSeries("D", color=Color.ORANGE, index=1))
            self.stochasticChart.add_series(getSeries("J", color=Color.GRAY, index=1, z_index=-10))
            self.stochasticChart.add_series(getSeries("upper", color=Color.GRAY, index=1, z_index=-11))
            self.stochasticChart.add_series(getSeries("lower", color=Color.GRAY, index=1, z_index=-12))

        # To be called in onSecurityChanged()
        # self.resetIndicators(None, None)

    def resetIndicators(self, dailyHistoryCount=None, minsHistoryCount=None):
        self.isWarmedUp = False

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
            self.dataConsolidator.data_consolidated -= self.onDataConsolidated
            getAlgo().subscription_manager.remove_consolidator(self.getSymbol(), self.dataConsolidator)
        self.dataConsolidator = self.securityMonitor.getConsolidator(self.indicatorPeriod)
        self.dataConsolidator.only_emit_on_close = True
        self.dataConsolidator.time_zone = LIGlobal.timezone
        self.dataConsolidator.data_consolidated += self.onDataConsolidated
        getAlgo().subscription_manager.add_consolidator(self.getSymbol(), self.dataConsolidator)

        # Warm up with history data
        maxPeriods = max(self.trendEMA.warm_up_period if self.trendEMA else 1,
                         self.macdEMA.warm_up_period if self.macdEMA else 1,
                         self.stochasticRSI.warm_up_period if self.stochasticRSI else 1,
                         self.stochasticKDJ.warm_up_period if self.stochasticKDJ else 1)
        maxPeriods = maxPeriods * self.rollingWindowSize * self.heikinAshiPlies if self.heikinAshies else 1
        resolution = getResolution(self.indicatorPeriod[1])
        totalPeriods = (maxPeriods + 1) * self.indicatorPeriod[0]
        bars = self.securityMonitor.getHistoryBars(totalPeriods, resolution)
        barsCount = 0
        for bar in bars:
            barsCount += 1
            self.dataConsolidator.update(bar)

        self.isWarmedUp = True
        if self.lastBar:
            self.updateIndicators(self.lastBar)
        log(f"{self.getSymbol().value}: Reset combo trending indicator with totalPeriods={totalPeriods}({str(resolution)}), "
            f"updated with {barsCount} history trade bars.")

    def onSecurityChanged(self, removedSecurity: Security):
        if removedSecurity is None:
            self.resetIndicators(None, None)

    def onDataConsolidated(self, sender: Object, bar: Bar):
        if bar is None:
            return  # Just in case

        self.lastBar = bar  # Cache closed bar

        if self.heikinAshies:
            self.heikinAshies[0].update(bar)
        else:
            self.updateIndicators(bar)

    def onHeikinAshiUpdated(self, sender: HeikinAshi, updated: IndicatorDataPoint):
        if not sender.is_ready:
            return
        bar = TradeBar(self.lastBar.time,
                       sender.current.symbol,
                       sender.open.current.value,
                       sender.high.current.value,
                       sender.low.current.value,
                       sender.close.current.value,
                       sender.volume.current.value,
                       self.lastBar.period)
        n = int(sender.name)
        if n < len(self.heikinAshies) - 1:
            self.heikinAshies[n + 1].update(bar)  # Call next ply
        else:
            self.updateIndicators(bar)

    def updateIndicators(self, bar: Bar):
        if self.rangeATR:
            if self.positionManager.isExchangeOpen():  # Avoid using extend data bar streaming!
                self.rangeATR.update(bar.end_time, abs(bar.open - bar.close))
        if self.trendEMA:
            self.trendEMA.update(bar)
        if self.macdEMA:
            self.macdEMA.update(bar)
        if self.standardRSI:
            self.standardRSI.update(bar)
        if self.stochasticRSI:
            self.stochasticRSI.update(bar)
        if self.stochasticKDJ:
            self.stochasticKDJ.update(bar)

        if not self.isWarmedUp:
            return  # Not warmed up yet

        self.plotIndicatorCharts(bar)

        tradeInsight = self.predictTradeInsight(bar)
        if tradeInsight.signalType != LISignalType.NONE:
            cachedInsight = self.tradeInsight
            self.tradeInsight = tradeInsight
            # Notify downstream listeners for trading signal changed
            for listener in self.tradeInsightListeners:
                listener.onEmitTradeInsight(self.tradeInsight)
            # Update charts if trade signal changed
            if cachedInsight.signalType != tradeInsight.signalType:
                if tradeInsight.isLongSignal():
                    plot(self.mainChart.name, LISignalType.LONG, self.securityMonitor.getMarketPrice())
                elif tradeInsight.isShortSignal():
                    plot(self.mainChart.name, LISignalType.SHORT, self.securityMonitor.getMarketPrice())
                elif tradeInsight.isCloseSignal():
                    plot(self.mainChart.name, LISignalType.CLOSE, self.securityMonitor.getMarketPrice())

    def plotIndicatorCharts(self, bar: Bar):
        if LIDefault.verbose:
            log(f"{self.getSymbol().value}: Plot indicator charts for period={bar.period}, endTime={bar.end_time}, {bar}")
        plot(self.mainChart.name, f"{self.indicatorPeriod[1]}Price", bar.close if self.trendingIndicator else bar)
        if self.addVolumeSeries:
            plot(self.mainChart.name, "Volume", bar.volume)
        if self.rangeATR and self.rangeATR.is_ready:
            plot(self.auxChart.name, "Range", self.rangeATR.current.value)
        if self.trendEMA and self.trendEMA.is_ready:
            plot(self.mainChart.name, "Trend", self.trendEMA.current.value)
        if self.macdEMA and self.macdEMA.is_ready:
            # plot(self.mainChart.name, "Fast", self.macdEMA.fast.current.value)
            # plot(self.mainChart.name, "Slow", self.macdEMA.slow.current.value)
            plot(self.macdChart.name, "Signal", self.macdEMA.signal.current.value)
            plot(self.macdChart.name, "Histogram", self.macdEMA.histogram.current.value)
            plot(self.macdChart.name, "Divergence", self.macdEMA.current.value)
        if self.standardRSI and self.standardRSI.is_ready:
            plot(self.stochasticChart.name, LIIndicator.RSI, int(self.standardRSI.current.value))
        if self.stochasticRSI and self.stochasticRSI.is_ready:
            plot(self.stochasticChart.name, "srsiK", int(self.stochasticRSI.k.current.value))
            plot(self.stochasticChart.name, "srsiD", int(self.stochasticRSI.d.current.value))
            plot(self.stochasticChart.name, "srsiJ", int(getStochasticJ(self.stochasticRSI.k.current.value, self.stochasticRSI.d.current.value)))
            plot(self.stochasticChart.name, "srsiUpper", self.comboTrendingParams[LIIndicator.SRSI][4])
            plot(self.stochasticChart.name, "srsiLower", self.comboTrendingParams[LIIndicator.SRSI][5])
        if self.stochasticKDJ and self.stochasticKDJ.is_ready:
            plot(self.stochasticChart.name, "K", int(self.stochasticKDJ.stoch_k.current.value))
            plot(self.stochasticChart.name, "D", int(self.stochasticKDJ.stoch_d.current.value))
            plot(self.stochasticChart.name, "J", int(getStochasticJ(self.stochasticKDJ.stoch_k.current.value, self.stochasticKDJ.stoch_d.current.value)))
            plot(self.stochasticChart.name, "upper", self.comboTrendingParams[LIIndicator.KDJ][3])
            plot(self.stochasticChart.name, "lower", self.comboTrendingParams[LIIndicator.KDJ][4])

    def predictTradeInsight(self, updated: IBaseData) -> LITradeInsight:
        signalType = LISignalType.NONE
        symbolValue = updated.symbol.value if updated else self.getSymbol().value
        # Only use the trending indicator if enabled!
        if self.trendingIndicator:
            tradeInsight = self.trendingIndicator.tradeInsight
            return tradeInsight
        if self.trendEMA:
            signalType = self.getTrendEMASignal(updated)
        elif self.heikinAshies:
            signalType = self.getHeikinAshiSignal(updated)
        # Here we can use multiple indicators to determine the signal type
        # kdjSignalType = self.getStochasticKDJSignal()
        # if signalType == LISignalType.LONG and kdjSignalType == LISignalType.SHORT:
        #     signalType = LISignalType.CLOSE
        # Adjusted by market bias if been specified!
        if self.isBullishBias() or (signalType == LISignalType.LONG and not self.isBearishBias()):
            signalType = LISignalType.LONG
        if self.isBearishBias() or (signalType == LISignalType.SHORT and not self.isBullishBias()):
            signalType = LISignalType.SHORT
        serialId = (self.tradeInsight.serialId if self.tradeInsight else 0) + 1
        timestamp = updated.end_time if updated else getAlgoTime()
        return LITradeInsight(serialId=serialId, symbolValue=symbolValue, signalType=signalType, timestamp=timestamp)

    def getTrendEMASignal(self, bar: Bar = None) -> LISignalType:
        signalType = LISignalType.NONE
        price = bar.close if bar else self.getMarketPrice()
        if price > self.trendEMA.current.value:
            signalType = LISignalType.LONG
        elif price < self.trendEMA.current.value:
            signalType = LISignalType.SHORT
        return signalType

    def getMacdEMASignal(self) -> LISignalType:
        signalType = LISignalType.NONE
        if self.macdEMA.histogram.current.value > self.macdIndicatorTolerance:
            signalType = LISignalType.LONG
        elif self.macdEMA.histogram.current.value < -self.macdIndicatorTolerance:
            signalType = LISignalType.SHORT
        return signalType

    def getHeikinAshiSignal(self, bar: Bar = None) -> LISignalType:
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
            params = self.comboTrendingParams[LIIndicator.ATR]
            return self.rangeATR.current.value / params[1]
        return self.heikinAshiIndicatorTolerance

    def getStochasticRSISignal(self) -> LISignalType:
        signalType = LISignalType.NONE
        params = self.comboTrendingParams[LIIndicator.SRSI]
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
        params = self.comboTrendingParams[LIIndicator.KDJ]
        upperBound, lowerBound = params[3], params[4]
        k, kPrev = self.stochasticKDJ.stoch_k.current.value, self.stochasticKDJ.stoch_k.previous.value
        d, dPrev = self.stochasticKDJ.stoch_d.current.value, self.stochasticKDJ.stoch_d.previous.value
        # Cong still need to refine below
        if k > d and kPrev < lowerBound < k:
            signalType = LISignalType.LONG
        elif k < d and kPrev > upperBound > k:
            signalType = LISignalType.SHORT
        return signalType

    def __str__(self) -> str:
        result = ""
        if self.rangeATR:
            result += f"atr={self.rangeATR.current.value}"
        if self.trendEMA:
            result += f"emaSignal={self.getTrendEMASignal()}, "
        if self.macdEMA:
            result += f"macdEMASignal={self.getMacdEMASignal()}, "
        if self.heikinAshies:
            result += f"heikinAshiSignal={self.getHeikinAshiSignal()}"
        if self.stochasticRSI:
            result += f"stochasticRSISignal={self.getStochasticRSISignal()}, "
        if self.stochasticKDJ:
            result += f"stochasticKDJSignal={self.getStochasticKDJSignal()}, "
        if self.trendingIndicator:
            result += f"trendingInsight={self.trendingIndicator.tradeInsight}, "
        return result
