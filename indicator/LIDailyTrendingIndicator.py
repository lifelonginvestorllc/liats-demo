from AlgorithmImports import *
from core.LIConfiguration import *
from indicator.LICandlestickRollingWindow import *
from indicator.LIInsightIndicator import *


class LIDailyTrendingIndicator(LIInsightIndicator):
    """
    A daily trending indicator that consolidates any type of trade bars into daily candlesticks.
    It can be used to predict daily trade insights with a mid-term trending.
    """

    def __init__(self, securityMonitor, positionManager, mainChart, configs):
        super().__init__(securityMonitor, positionManager, mainChart, configs)

        self.comboTrendingParams = configs.get(LIConfigKey.comboTrendingParams, LIDefault.comboTrendingParams)

        if LIIndicator.DAILY in self.comboTrendingParams:
            self.heikinAshiPlies = self.comboTrendingParams[LIIndicator.DAILY]

        self.dailyDays = 1
        self.rollingWindowSize = 10
        self.plotDailyChart = True

        self.lastBar = None
        self.heikinAshies: list[HeikinAshi] = []
        self.dataConsolidator = None

        self.candlestickRollingWindow = LICandlestickRollingWindow(self.rollingWindowSize, configs)

        if self.heikinAshiPlies:
            for n in range(self.heikinAshiPlies):
                heikinAshi = HeikinAshi(str(n))
                heikinAshi.window.size = self.rollingWindowSize
                heikinAshi.updated += self.onHeikinAshiUpdated  # Call back to update other indicators
                self.heikinAshies.append(heikinAshi)

        if self.plotDailyChart:
            self.mainChart.add_series(getCandlestickSeries("Daily", unit="$", color=Color.CYAN, z_index=-5))

    def resetIndicators(self, dailyHistoryCount=None, minsHistoryCount=None):
        self.isWarmedUp = False

        # Recreate a new consolidator
        if self.dataConsolidator is not None:
            self.dataConsolidator.data_consolidated -= self.onDataConsolidated
            getAlgo().subscription_manager.remove_consolidator(self.getSymbol(), self.dataConsolidator)
        self.dataConsolidator = TradeBarConsolidator(timedelta(days=self.dailyDays))
        self.dataConsolidator.only_emit_on_close = True
        self.dataConsolidator.time_zone = LIGlobal.timezone
        self.dataConsolidator.data_consolidated += self.onDataConsolidated
        getAlgo().subscription_manager.add_consolidator(self.getSymbol(), self.dataConsolidator)

        self.candlestickRollingWindow.reset()

        # Warm up with history data
        resolution = getResolution(self.indicatorPeriod[1])
        gapPeriods = getResolutionTimedelta(LIResolution.DAY) // getResolutionTimedelta(self.indicatorPeriod[1])
        totalPeriods = self.rollingWindowSize * gapPeriods * self.indicatorPeriod[0] * self.dailyDays
        bars = self.securityMonitor.getHistoryBars(totalPeriods, resolution)
        barsCount = 0
        for bar in bars:
            barsCount += 1
            log(f"{self.getSymbolAlias()}: Warming up daily trending indicator with {bar.period} history bar #{barsCount}: "
                f"start: {bar.time} end: {bar.end_time} {bar}.", self.verbose)
            self.dataConsolidator.update(bar)
        self.isWarmedUp = True
        if self.lastBar:
            self.updateIndicators(self.lastBar)
        log(f"{self.getSymbolAlias()}: Reset daily trending indicator with totalPeriods={totalPeriods}({str(resolution)}), "
            f"updated with {barsCount} history trade bars, windowSize={self.candlestickRollingWindow.size()}.")

    def updateIndicators(self, bar: Bar):
        if not self.isWarmedUp:
            return  # Not warmed up yet

        self.plotIndicatorChart(bar)
        self.candlestickRollingWindow.append(LICandlestick(bar, self.configs))

        tradeInsight = self.predictTradeInsight(bar)

        self.publishTradeInsight(tradeInsight)

    def onSecurityChanged(self, removedSecurity: Security):
        if removedSecurity is None:
            self.resetIndicators(None, None)

    def plotIndicatorChart(self, bar):
        if self.plotDailyChart:
            plot(self.mainChart.name, "Daily", bar)

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

    def predictTradeInsight(self, updated: IBaseData) -> LITradeInsight:
        timestamp = getAlgoTime()
        signalType = LISignalType.NONE
        symbolValue = updated.symbol.value if updated else self.getSymbol().value
        timestamp = updated.end_time if updated else timestamp
        candlestick = self.candlestickRollingWindow.candlestick()
        log(f"{self.getSymbolAlias()}: Predicting with dailyTrendingIndicator for {timestamp}, barStartTime={updated.time}, "
            f"barEndTime={updated.end_time}, barBody={candlestick.body()}, algoTime={getAlgoTime()}.", self.verbose)
        if candlestick.isUp():
            signalType = LISignalType.LONG
        elif candlestick.isDown():
            signalType = LISignalType.SHORT
        elif self.tradeInsight:
            signalType = self.tradeInsight.signalType
        if self.isBullishBias() or (signalType == LISignalType.LONG and not self.isBearishBias()):
            signalType = LISignalType.LONG
        if self.isBearishBias() or (signalType == LISignalType.SHORT and not self.isBullishBias()):
            signalType = LISignalType.SHORT
        serialId = (self.tradeInsight.serialId if self.tradeInsight else 0) + 1
        tradeInsight = LITradeInsight(serialId=serialId, symbolValue=symbolValue, signalType=signalType, timestamp=timestamp)
        log(f"{self.getSymbolAlias()}: Predicted trade insight: {tradeInsight}.", self.verbose)
        return tradeInsight
