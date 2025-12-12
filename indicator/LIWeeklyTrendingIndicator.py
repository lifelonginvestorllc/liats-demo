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
        self.staticTradingSignals = configs.get(LIConfigKey.staticTradingSignals, LIDefault.staticTradingSignals)
        self.fetchTradingSignalsApi = configs.get(LIConfigKey.fetchTradingSignalsApi, LIDefault.fetchTradingSignalsApi)

        if self.staticTradingSignals and self.fetchTradingSignalsApi:
            raise ValueError("Both staticTradingSignals and fetchTradingSignalsApi are set. Please choose only one method for providing trading signals.")

        if self.fetchTradingSignalsApi:
            endpointUrl = LIGlobal.websiteUrl + "/" + self.fetchTradingSignalsApi
            symbolStr = self.securityMonitor.getSymbolStr()
            endpointUrl += "?symbol=%s" % symbolStr
            endpointUrl += "&category=WEEKLY_TREND&page=0&sort=date,desc&size=10"
            self.staticTradingSignals = self.fetchTradingSignals(symbolStr, endpointUrl)

        if self.staticTradingSignals:
            self.validateTradingSignals()
            if isLiveMode():  # Just keep the latest 5 signals
                for key in list(self.staticTradingSignals.keys())[:-5]:
                    del self.staticTradingSignals[key]

        if LIIndicator.WEEKLY in self.comboTrendingParams:
            self.heikinAshiPlies = self.comboTrendingParams[LIIndicator.WEEKLY]

        self.weeklyDays = 7
        self.rollingWindowSize = 10
        self.plotWeeklyChart = True

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

        if self.plotWeeklyChart:
            self.mainChart.add_series(getCandlestickSeries("Weekly", unit="$", color=Color.CYAN, z_index=-5))

    def fetchTradingSignals(self, symbolStr, endpointUrl: str | Any):
        headers = getHttpHeader(getWebApiToken())
        log(f"{symbolStr}: Calling API endpoint {endpointUrl} with headers={headers}")
        try:
            response = getAlgo().download(address=endpointUrl, headers=headers)
            log(f"{self.getSymbol().value}: Fetched trading signals: {response}.", self.verbose)
            signals = json.loads(response)
            signalsMap = {}
            for signal in signals:
                # Extract date in format "YYYY-MM-DD"
                signalDate = datetime.strptime(signal.get('date'), '%Y-%m-%d').date()
                # Parse the content JSON to get signalType
                signalContent = json.loads(signal.get('content'))
                signalTypeStr = signalContent.get('signalType')
                signalType = LISignalType.NONE
                if signalTypeStr == 'LONG':
                    signalType = LISignalType.LONG
                elif signalTypeStr == 'SHORT':
                    signalType = LISignalType.SHORT
                elif signalTypeStr == 'CLOSE':
                    signalType = LISignalType.CLOSE
                signalsMap[signalDate] = signalType
            return dict(sorted(signalsMap.items()))
            log(f"{symbolStr}: Converted trading signals: {self.staticTradingSignals}.", self.verbose)
        except Exception as exc:
            log(f"{symbolStr}: Failed to fetch trading signals: {exc}")

    def validateTradingSignals(self):
        keys = list(self.staticTradingSignals.keys())
        # values = list(self.staticTradingSignals.values())
        if (datetime.now().date() - keys[-1]).days < 5:
            raise ValueError(f"The last date {keys[-1]} in weeklyTrendingSignals must be at least 5 days before today.")
        for i in range(len(keys) - 1):
            if (keys[i + 1] - keys[i]).days != 7:
                raise ValueError(f"The days between {keys[i]} and {keys[i + 1]} in weeklyTrendingSignals should be 7 days.")
        # Flag dates that are NOT Monday (weekday 0) and show the closest prior Monday
        invalidNonMondays = [(k, k - timedelta(days=k.weekday())) for k in keys if k.weekday() != 0]
        if invalidNonMondays:
            details = ", ".join([f"{d} -> prior Monday {m}" for d, m in invalidNonMondays])
            raise ValueError(f"All weeklyTrendingSignals dates must be Mondays. Please correct following dates: {details}")

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
        for bar in bars:
            barsCount += 1
            log(f"{self.getSymbol().value}: Warming up weekly trending indicator with {bar.period} history bar #{barsCount}: "
                f"start: {bar.time} end: {bar.end_time} {bar}.", self.verbose)
            self.dataConsolidator.update(bar)
        self.isWarmedUp = True
        if self.lastBar:
            self.updateIndicators(self.lastBar)
        log(f"{self.getSymbol().value}: Reset weekly trending indicator with totalPeriods={totalPeriods}({str(resolution)}), "
            f"updated with {barsCount} history trade bars, windowSize={self.candlestickRollingWindow.size()}.")

    def updateIndicators(self, bar: Bar):
        if not self.isWarmedUp:
            return  # Not warmed up yet

        self.plotIndicatorChart(bar)
        self.candlestickRollingWindow.append(LICandlestick(bar, self.configs))

        tradeInsight = self.predictTradeInsight(bar)
        self.notifyTradeInsight(tradeInsight)

    def notifyTradeInsight(self, tradeInsight: LITradeInsight):
        if tradeInsight.signalType != LISignalType.NONE:
            self.tradeInsight = tradeInsight
            # Notify downstream listeners for trading
            for listener in self.tradeInsightListeners:
                listener.onEmitTradeInsight(self.tradeInsight)

    def onSecurityChanged(self, removedSecurity: Security):
        if removedSecurity is None:
            self.resetIndicators(None, None)

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
        if self.staticTradingSignals:
            algoDate = timestamp.date()
            log(f"{self.getSymbol().value}: Predicting with weeklyTrendingSignals for {algoDate}, timestamp={timestamp}.", self.verbose)
            # The algorithm date is intentionally shifted back by 7 days to refer to the previous Monday's weekly signal.
            # This means that the trading decision for the current week is based on the signal generated for the previous week.
            # As a result, there is a one-week lag between the signal date and the trading date, which should be taken into account
            # when interpreting backtests and live trading results. This logic ensures that only fully-formed weekly signals
            # (i.e., signals based on complete weekly data) are used for trading decisions.
            algoDate -= timedelta(days=5)
            for (key, value) in sorted(self.staticTradingSignals.items()):
                if key > algoDate:
                    break  # Found the latest signal type that is before the algoDate
                signalType = value
        else:
            timestamp = updated.end_time if updated else timestamp
            candlestick = self.candlestickRollingWindow.candlestick()
            log(f"{self.getSymbol().value}: Predicting with weeklyTrendingIndicator for {timestamp}, barStartTime={updated.time}, "
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
        log(f"{self.getSymbol().value}: Predicted trade insight: {tradeInsight}.", self.verbose)
        return tradeInsight
