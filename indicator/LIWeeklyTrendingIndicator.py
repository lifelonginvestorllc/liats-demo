from AlgorithmImports import *
from core.LIConfiguration import *
from indicator.LICandlestickRollingWindow import *
from indicator.LIInsightIndicator import *


class LIWeeklyTrendingIndicator(LIInsightIndicator):
    """
    A weekly trending indicator that consolidates any type of trade bars into weekly candlesticks.
    It can be used to predict weekly trade insights with a mid-term trending.
    """

    def __init__(self, securityMonitor, positionManager, mainChart, configs):
        super().__init__(securityMonitor, positionManager, mainChart, configs)

        self.comboTrendingParams = configs.get(LIConfigKey.comboTrendingParams, LIDefault.comboTrendingParams)
        self.staticTrendingSignals = configs.get(LIConfigKey.staticTrendingSignals, LIDefault.staticTrendingSignals)
        self.pullTrendingSignalsApi = configs.get(LIConfigKey.pullTrendingSignalsApi, LIDefault.pullTrendingSignalsApi)
        self.useClosedTrendingSignal = configs.get(LIConfigKey.useClosedTrendingSignal, LIDefault.useClosedTrendingSignal)

        if self.staticTrendingSignals and self.pullTrendingSignalsApi:
            raise ValueError("Both staticTrendingSignals and pullTrendingSignalsApi are set. Please choose only one method for providing trading signals.")

        self.weeklyDays = 7
        self.rollingWindowSize = 10
        self.plotWeeklyChart = True

        self.lastBar = None
        self.heikinAshies: list[HeikinAshi] = []
        self.dataConsolidator = None

        if LIIndicator.WEEKLY in self.comboTrendingParams:
            self.heikinAshiPlies = self.comboTrendingParams[LIIndicator.WEEKLY]

        self.candlestickRollingWindow = LICandlestickRollingWindow(self.rollingWindowSize, configs)

        if self.heikinAshiPlies:
            for n in range(self.heikinAshiPlies):
                heikinAshi = HeikinAshi(str(n))
                heikinAshi.window.size = self.rollingWindowSize
                heikinAshi.updated += self.onHeikinAshiUpdated  # Call back to update other indicators
                self.heikinAshies.append(heikinAshi)

        if self.plotWeeklyChart:
            self.mainChart.add_series(getCandlestickSeries("Weekly", unit="$", color=Color.CYAN, z_index=-5))

    def pullWeeklyTrendingSignals(self, size: int = 5):
        endpointUrl = LIGlobal.websiteUrl + "/" + self.pullTrendingSignalsApi
        endpointUrl += "?symbol.equals=%s" % self.securityMonitor.getSymbolStr()
        dateFrom = getAlgoUtcTime() - timedelta(days=self.weeklyDays * 3)
        endpointUrl += f"&category.equals=WEEKLY_TREND&datetime.greaterThanOrEqual={dateFrom.strftime('%Y-%m-%dT%H:%MZ')}&sort=datetime,asc&size={size}"
        self.trendingSignals = self.fetchTrendingSignals(endpointUrl)
        log(f"{self.getSymbolAlias()}: Fetched weekly trending signals as: {self.trendingSignals}.", self.verbose)
        self.validateTrendingSignals()

    def validateTrendingSignals(self):
        if not self.trendingSignals:
            return  # Nothing to validate
        keys = list(self.trendingSignals.keys())
        # No need to check the last date is at least 5 days before today, as we are using the latest week's signal
        # if (datetime.now(timezone.utc) - keys[-1]).days < 5:
        #     raise ValueError(f"The last date {keys[-1]} in weeklyTrendingSignals must be at least 5 days before today.")
        if len(keys) >= 2:
            for i in range(len(keys) - 1):
                if (keys[i + 1] - keys[i]).days != self.weeklyDays:
                    raise ValueError(f"The days between {keys[i]} and {keys[i + 1]} in weeklyTrendingSignals should be {self.weeklyDays} days.")
        # Flag datetimes that are NOT Sunday (weekday 6) and show the closest prior Sunday
        invalidNonSundays = [(k, k - timedelta(days=k.weekday())) for k in keys if k.weekday() != 6]
        if invalidNonSundays:
            details = ", ".join([f"{d} -> prior Sunday {m}" for d, m in invalidNonSundays])
            raise ValueError(f"All weeklyTrendingSignals datetimes must be Sundays. Please correct following datetimes: {details}.")

    def resetIndicators(self, dailyHistoryCount=None, minsHistoryCount=None):
        self.isWarmedUp = False

        # Recreate a new consolidator
        if self.dataConsolidator is not None:
            self.dataConsolidator.data_consolidated -= self.onDataConsolidated
            getAlgo().subscription_manager.remove_consolidator(self.getSymbol(), self.dataConsolidator)
        self.dataConsolidator = TradeBarConsolidator(Calendar.WEEKLY)
        self.dataConsolidator.only_emit_on_close = True
        self.dataConsolidator.time_zone = LIGlobal.timezone
        self.dataConsolidator.data_consolidated += self.onDataConsolidated
        getAlgo().subscription_manager.add_consolidator(self.getSymbol(), self.dataConsolidator)

        self.candlestickRollingWindow.reset()

        # Warm up with history data
        resolution = Resolution.DAILY
        totalPeriods = self.rollingWindowSize * self.weeklyDays + 1  # Days
        bars = self.securityMonitor.getHistoryBars(totalPeriods, resolution)

        barsCount = 0
        barsList = list(bars)
        totalBars = len(barsList)
        for idx, bar in enumerate(barsList, start=1):
            barsCount += 1
            if idx <= 3 or idx > totalBars - 3:
                log(f"{self.getSymbolAlias()}: Warming up weekly trending indicator with {bar.period} history bar #{barsCount}: "
                    f"start: {bar.time} end: {bar.end_time} {bar}.", self.verbose)
            self.dataConsolidator.update(bar)

        self.isWarmedUp = True

        if self.staticTrendingSignals:
            self.trendingSignals = self.staticTrendingSignals
            self.validateTrendingSignals()
            if isLiveMode():  # Just keep the latest 5 signals
                for key in list(self.staticTrendingSignals.keys())[:-3]:
                    del self.staticTrendingSignals[key]
            else:  # Backtest mode: remove old signals by start date
                startDate = getAlgo().start_date - timedelta(days=self.weeklyDays * 3)
                for key in list(self.staticTrendingSignals.keys()):
                    if key < startDate:
                        del self.staticTrendingSignals[key]

        if self.pullTrendingSignalsApi:
            self.pullWeeklyTrendingSignals(5 if isLiveMode() else 1000)

        if self.lastBar:
            self.updateIndicators(self.lastBar)
        log(f"{self.getSymbolAlias()}: Reset weekly trending indicator with totalPeriods={totalPeriods}({str(resolution)}), "
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

    def onMonitorBarUpdated(self, bar: Bar):
        if not self.isWarmedUp:
            return  # Not warmed up yet

        if self.pullTrendingSignalsApi:
            if isLiveMode():
                self.pullWeeklyTrendingSignals()
                tradeInsight = self.predictTradeInsight(bar)
                self.publishTradeInsight(tradeInsight)

    def plotIndicatorChart(self, bar):
        if self.plotWeeklyChart:
            plot(self.mainChart.name, "Weekly", bar)

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
        if self.trendingSignals:
            log(f"{self.getSymbolAlias()}: Predicting with weeklyTrendingSignals as timestamp={timestamp}, "
                f"barStartTime={updated.time}, barEndTime={updated.end_time}, algoTime={getAlgoTime()}.", self.verbose)
            # The algorithm date is intentionally shifted back by 7 days to refer to the previous Sunday's weekly signal.
            # This means that the trading decision for the current week is based on the signal generated for the previous week.
            # As a result, there is a one-week lag between the signal date and the trading date, which should be taken into account
            # when interpreting backtests and live trading results. This logic ensures that only fully-formed weekly signals
            # (i.e., signals based on complete weekly data) are used for trading decisions.
            if self.useClosedTrendingSignal:
                timestamp -= timedelta(days=5)
            for (key, value) in self.trendingSignals.items():
                if key > timestamp:
                    break  # Found the latest signal type that is before the zoneTimestamp
                signalType = value
        else:
            timestamp = updated.end_time if updated else timestamp
            candlestick = self.candlestickRollingWindow.candlestick()
            log(f"{self.getSymbolAlias()}: Predicting with weeklyTrendingIndicator as timestamp={timestamp}, "
                f"barStartTime={updated.time}, barEndTime={updated.end_time}, algoTime={getAlgoTime()}, "
                f"candlestickBody={candlestick.body()}.", self.verbose)
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
