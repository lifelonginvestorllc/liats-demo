# region imports
from core.LIConfiguration import *


# endregion

def printSecurities(securities):
    return f"{list(map(lambda x: (cleanSymbolValue(x.Symbol) + '|' + (x.Expiry.strftime(LIGlobal.fullDateFormat) if isDerivative(x.Type) and x.Expiry else 'None') + '|' + str(x.Volume)), securities))}"


def printOptionSymbol(symbol: Symbol):
    identifier = symbol.ID
    result = f"{cleanSymbolValue(symbol)}\t{getEnumName(identifier.OptionRight, OptionRight)}\t{identifier.StrikePrice}\t{identifier.Date.strftime(LIGlobal.fullDateFormat)}"
    return result


def printOptionContract(option: Option):
    result = (f"symbol={cleanSymbolValue(option.Symbol)}, right={getEnumName(option.Right, OptionRight)}, strike={option.StrikePrice}, "
              f"expiry={option.Expiry.strftime(LIGlobal.fullDateFormat)}, price={option.Price}, multiplier={option.ContractMultiplier}, "
              f"openInterest={option.OpenInterest}, volume={option.Volume}, bidSize={option.BidSize}, bidPrice={option.BidPrice}, "
              f"askSize={option.AskSize}, askPrice={option.AskPrice}")
    return result


def isExpiredAfterDays(expiryDate, expiryDays):
    backwardDate = roundDownTime(expiryDate - timedelta(days=expiryDays), delta=timedelta(days=1))
    currentDate = roundDownTime(getAlgo().Time, delta=timedelta(days=1))
    return backwardDate >= currentDate


def getResolution(resolution: LIResolution) -> Resolution:
    if resolution == LIResolution.SECOND:
        return Resolution.Second
    elif resolution == LIResolution.MINUTE:
        return Resolution.Minute
    elif resolution == LIResolution.HOUR:
        return Resolution.Hour
    elif resolution == LIResolution.DAY:
        return Resolution.Daily


class LISecurityMonitor:
    def __init__(self, symbolStr, securityType, strategyCode, configs):
        self.symbolStr = symbolStr
        self.securityType = securityType
        self.strategyCode = strategyCode
        self.configs = configs

        self.aliasName = configs.get(LIConfigKey.aliasName, LIDefault.aliasName)
        self.verbose = configs.get(LIConfigKey.verbose, LIDefault.verbose)

        self.resolution = configs.get(LIConfigKey.resolution, LIDefault.resolution)
        self.monitorPeriod = configs.get(LIConfigKey.monitorPeriod, LIDefault.monitorPeriod)
        self.benchmarkSymbolStr = configs.get(LIConfigKey.benchmarkSymbolStr, LIDefault.benchmarkSymbolStr)
        self.enableAutoRollover = configs.get(LIConfigKey.enableAutoRollover, LIDefault.enableAutoRollover)
        self.forceExchangeOpen = configs.get(LIConfigKey.forceExchangeOpen, LIDefault.forceExchangeOpen)
        self.extendedMarketHours = configs.get(LIConfigKey.extendedMarketHours, LIDefault.extendedMarketHours)
        self.extendDataBarStream = configs.get(LIConfigKey.extendDataBarStream, LIDefault.extendDataBarStream)
        self.fetchHistoryBarData = configs.get(LIConfigKey.fetchHistoryBarData, LIDefault.fetchHistoryBarData)
        self.disableBuyingPowerModel = configs.get(LIConfigKey.disableBuyingPowerModel, LIDefault.disableBuyingPowerModel)
        self.dayOpenGapUpDownPercent = configs.get(LIConfigKey.dayOpenGapUpDownPercent, LIDefault.dayOpenGapUpDownPercent)

        self.futureQuarterly = configs.get(LIConfigKey.futureQuarterly, LIDefault.futureQuarterly)
        self.futurePeriodDays = configs.get(LIConfigKey.futurePeriodDays, LIDefault.futurePeriodDays)
        self.futureRolloverDays = configs.get(LIConfigKey.futureRolloverDays, LIDefault.futureRolloverDays)
        self.futureContractCode = configs.get(LIConfigKey.futureContractCode, LIDefault.futureContractCode)
        self.futureContractExpiry = configs.get(LIConfigKey.futureContractExpiry, LIDefault.futureContractExpiry)

        self.optionRight = configs.get(LIConfigKey.optionRight, LIDefault.optionRight)
        self.optionContractCode = configs.get(LIConfigKey.optionContractCode, LIDefault.optionContractCode)
        self.optionContractOTMLevel = configs.get(LIConfigKey.optionContractOTMLevel, LIDefault.optionContractOTMLevel)
        self.optionMinMaxExpiryDays = configs.get(LIConfigKey.optionMinMaxExpiryDays, LIDefault.optionMinMaxExpiryDays)
        self.optionMinMaxStrikeLevel = configs.get(LIConfigKey.optionMinMaxStrikeLevel, LIDefault.optionMinMaxStrikeLevel)
        self.addFutureOptionUniverse = configs.get(LIConfigKey.addFutureOptionUniverse, LIDefault.addFutureOptionUniverse)

        if self.securityType == SecurityType.OPTION and self.optionRight is None:
            terminate(f"Please specify {LIConfigKey.optionRight} as securityType={getEnumName(self.securityType, SecurityType)}!")
        if self.futureRolloverDays < 1:
            terminate(f"Please specify '{LIConfigKey.futureRolloverDays} > 0' to avoid 'Liquidate from delisting' unexpectedly!")
        if self.futureContractCode and self.futureContractExpiry:
            terminate(f"Please specify either {LIConfigKey.futureContractCode} or {LIConfigKey.futureContractExpiry}!")

        self.security: Security = None
        self.contract: Security = None
        self.nextSecurity: Security = None
        self.expiredSecurity: Security = None

        self.latestDataBar = None
        self.marketOpenPrice = -1  # Could be last/previous day or today open price, upon current time
        self.marketClosePrice = -1  # Mostly last/previous market day close price, upon current time
        self.dayLowPrice = -1
        self.dayHighPrice = -1
        self.isDayOpenWithGap = False
        self.isTempTradable = False

        self.dataBarUpdatedListeners = []
        self.securityChangedListeners = []
        self.dayOpenGapUpDownListeners = []
        self.dayLowBreachEventListeners = []
        self.dayHighBreachEventListeners = []

        # Map a symbol to a consolidator
        self.consolidators: dict[Symbol, DataConsolidator] = dict()

        # Get trading days within range
        # self.tradingDays = getAlgo().get_trading_days(getAlgo().start_date, getAlgo().end_date)

        self.setupSecurityUniverse()

        # To be called in onSecuritiesChanged()
        # self.resetSecurityMonitor()  # Warm up with some history data

        # Simulate market data stream if not available yet!
        if self.extendDataBarStream:
            getAlgo().Schedule.On(getAlgo().DateRules.EveryDay(),
                                  getAlgo().TimeRules.Every(self.getResolutionTimedelta()),
                                  self.updateDataConsolidator)

    def getSymbol(self) -> Symbol:
        return self.getSecurity().Symbol

    def getSecurity(self) -> Security:
        """Final resolved security or contract for derivative!"""
        return self.security if not self.contract else self.contract

    def getContract(self) -> Security:
        return self.contract

    def getSymbolValue(self) -> str:
        return cleanSymbolValue(self.getSymbol())

    def getSymbolAlias(self) -> str:
        return f"{self.aliasName}({self.getSymbolValue()})" if self.aliasName else self.getSymbolValue()

    def getSymbolStrAlias(self) -> str:
        return f"{self.aliasName}({self.getSymbolStr()})" if self.aliasName else self.getSymbolStr()

    def getOptionRight(self) -> OptionRight:
        return self.optionRight

    def getTradingDays(self) -> int:
        return self.tradingDays

    def getResolution(self) -> Resolution:
        return getResolution(self.resolution)

    def atMarketOpeningTime(self, timestamp=None) -> bool:
        return atMarketOpeningTime(timestamp=timestamp, delta=self.getMonitorPeriodDelta())

    def atMarketClosingTime(self, timestamp=None) -> bool:
        return atMarketClosingTime(timestamp=timestamp, delta=self.getMonitorPeriodDelta())

    def getResolutionTimedelta(self) -> timedelta:
        if self.resolution == LIResolution.SECOND:
            return timedelta(seconds=1)
        elif self.resolution == LIResolution.MINUTE:
            return timedelta(minutes=1)
        elif self.resolution == LIResolution.HOUR:
            return timedelta(hours=1)
        elif self.resolution == LIResolution.DAY:
            return timedelta(days=1)
        else:
            terminate(f"Not support {LIConfigKey.resolution}={self.resolution}")

    def getMonitorPeriodDelta(self) -> timedelta:
        return self.getResolutionTimedelta() * self.monitorPeriod

    def getSecurityMultiplier(self):
        return self.getSecurity().SymbolProperties.ContractMultiplier  # 1.0 for other securities

    def getSecurityType(self):
        return self.securityType

    def getStrategyCode(self):
        return self.strategyCode

    def getCanonicalSymbol(self) -> Symbol:
        symbol = self.getSymbol()
        if isDerivative(symbol.SecurityType):
            return symbol.Canonical
        return symbol

    def setupSecurityUniverse(self):
        if self.benchmarkSymbolStr:
            benchmark = getAlgo().AddEquity(self.benchmarkSymbolStr)
            getAlgo().SetBenchmark(benchmark.Symbol)

        if self.securityType == SecurityType.EQUITY:
            self.security = getAlgo().AddEquity(ticker=self.symbolStr,
                                                resolution=self.getResolution(),
                                                extendedMarketHours=self.extendedMarketHours,
                                                dataNormalizationMode=DataNormalizationMode.Raw)  # DO NOT normalize history data!
        elif self.securityType == SecurityType.FOREX:
            self.security = getAlgo().AddForex(ticker=self.symbolStr,
                                               resolution=self.getResolution())
        elif self.securityType == SecurityType.Cfd:
            self.security = getAlgo().AddCfd(ticker=self.symbolStr,
                                             resolution=self.getResolution())
        elif self.securityType == SecurityType.FUTURE:
            self.security = getAlgo().AddFuture(ticker=self.symbolStr,
                                                resolution=self.getResolution(),
                                                extendedMarketHours=self.extendedMarketHours,
                                                dataMappingMode=DataMappingMode.LastTradingDay,
                                                dataNormalizationMode=DataNormalizationMode.Raw,  # DO NOT normalize history data!
                                                contractDepthOffset=0)
            if self.futureContractExpiry:
                self.contract = getAlgo().AddFutureContract(Symbol.CreateFuture(self.symbolStr, Market.CME, self.futureContractExpiry),
                                                            resolution=self.getResolution(),
                                                            extendedMarketHours=self.extendedMarketHours)
                self.security.SetFilter(minExpiryDays=0, maxExpiryDays=0)  # No filter as just use the specified contract
            elif self.futureContractCode:
                self.contract = getAlgo().AddFutureContract(SymbolRepresentation.ParseFutureSymbol(self.futureContractCode),
                                                            resolution=self.getResolution(),
                                                            extendedMarketHours=self.extendedMarketHours)
                self.security.SetFilter(minExpiryDays=0, maxExpiryDays=0)  # No filter as just use the specified contract
            else:
                # Set expiry filter and accept contracts between these days
                expirationCycle = FutureExpirationCycles.AllYear
                if self.futureQuarterly is not None:
                    if self.futureQuarterly:
                        expirationCycle = FutureExpirationCycles.March
                elif self.futurePeriodDays > 85:
                    expirationCycle = FutureExpirationCycles.March
                self.security.SetFilter(lambda futureFilter: futureFilter.Expiration(minExpiryDays=0,
                                                                                     maxExpiryDays=self.getFutureMaxExpiryDays()).
                                        ExpirationCycle(expirationCycle))
            # self.security.SetFillModel(LatestPriceFillModel())
            # getQcAlgo().SetSecurityInitializer(lambda security: security.SetMarginModel(SecurityMarginModel.Null))
            if self.addFutureOptionUniverse:
                getAlgo().AddFutureOption(self.security.Symbol, lambda universe: universe
                                          .StandardsOnly()
                                          .Strikes(self.optionMinMaxStrikeLevel[0], self.optionMinMaxStrikeLevel[1])
                                          .Expiration(self.optionMinMaxExpiryDays[0], self.optionMinMaxExpiryDays[1])
                                          .OnlyApplyFilterAtMarketOpen())
        elif self.securityType == SecurityType.OPTION:
            # underlyingEquity = getQcAlgo().AddEquity(self.symbolStr, resolution=self.getResolution())
            self.security = getAlgo().AddOption(underlying=self.symbolStr,
                                                resolution=self.getResolution())
            # The filter will be shared by both put and call
            if self.optionContractCode:
                spanDays = (extractExpiryDate(self.optionContractCode) - getAlgo().Time).days
                strikePrice = extractStrikePrice(self.optionContractCode)
                log(f"{self.getSymbolStrAlias()}: Use reserved option contract {self.optionContractCode}, spanDays={spanDays}, strikePrice={strikePrice}.")
                self.security.SetFilter(lambda universe: universe
                                        .StandardsOnly()
                                        .Strikes(self.optionMinMaxStrikeLevel[0], self.optionMinMaxStrikeLevel[1])
                                        .Expiration(spanDays - 5, spanDays + 5)
                                        .OnlyApplyFilterAtMarketOpen())
            else:
                self.security.SetFilter(lambda universe: universe
                                        .StandardsOnly()
                                        .Strikes(self.optionMinMaxStrikeLevel[0], self.optionMinMaxStrikeLevel[1])
                                        .Expiration(self.optionMinMaxExpiryDays[0], self.optionMinMaxExpiryDays[1])
                                        .OnlyApplyFilterAtMarketOpen())
        elif self.securityType == SecurityType.CryptoFuture:
            self.security = getAlgo().AddCryptoFuture(ticker=self.symbolStr, resolution=self.getResolution())
            # Set expiry filter and accept contracts between these days
            self.security.SetFilter(minExpiryDays=0, maxExpiryDays=self.futurePeriodDays + self.futureRolloverDays)
        else:
            terminate(f"Invalid securityType={getEnumName(self.securityType, SecurityType)}")

    def getFutureMaxExpiryDays(self):
        if self.futureContractCode or self.futureContractExpiry:
            return 365  # Return contracts in one year for now
        else:
            return self.futurePeriodDays + self.futureRolloverDays

    def resetConsolidator(self, security):
        if self.consolidators.get(security.Symbol) is not None:
            consolidator = self.consolidators.pop(security.Symbol)
            consolidator.DataConsolidated -= self.onDataConsolidated
            getAlgo().SubscriptionManager.RemoveConsolidator(security.Symbol, consolidator)
            log(f"Removed consolidator of the security: {security.Symbol.Value}")
        consolidator = self.getConsolidator(self.monitorPeriod)
        consolidator.DataConsolidated += self.onDataConsolidated
        getAlgo().SubscriptionManager.AddConsolidator(security.Symbol, consolidator)
        self.consolidators[security.Symbol] = consolidator

    def initSecurityMonitor(self, totalPeriods=0):
        if not self.fetchHistoryBarData and totalPeriods == 0:
            log(f"{self.getSymbolAlias()}: Skipped resetting security monitor as {LIConfigKey.fetchHistoryBarData}={self.fetchHistoryBarData}")
            return  # Abort on demand

        totalPeriods = 0
        if totalPeriods == 0:  # Use default periods
            if self.resolution == LIResolution.SECOND:
                totalPeriods = 1 * 60  # 1 minute history data, not applicable for marketOpenPrice/marketClosePrice!
            elif self.resolution == LIResolution.MINUTE:
                totalPeriods = 1 * 60  # 1 hour history data
            elif self.resolution == LIResolution.HOUR:
                totalPeriods = 1 * 24  # 1 day history data
            elif self.resolution == LIResolution.DAY:
                totalPeriods = 1 * 30  # 1 month history data

        for bar in self.getHistoryBars(totalPeriods):
            if bar and bar.Close:
                self.latestDataBar = bar
                if self.atMarketOpeningTime(timestamp=bar.EndTime):
                    self.marketOpenPrice = bar.Close
                if self.atMarketClosingTime(timestamp=bar.EndTime):
                    self.marketClosePrice = bar.Close

        log(f"{self.getSymbolAlias()}: Reset security monitor, marketOpenPrice={self.marketOpenPrice:.2f}, "
            f"marketClosePrice={self.marketClosePrice:.2f}, latestDataBar={self.latestDataBar.Close if self.latestDataBar else -1:.2f}")

    def getHistoryBars(self, totalPeriods):
        barType = QuoteBar if useQuoteBar(self.securityType) else TradeBar
        bars = getAlgo().History[barType](self.getSymbol(), totalPeriods, self.getResolution())
        return bars

    def addSecurity(self, security: Security):
        if security is None:
            return  # Ignore possible null symbol

        # self.security.SetFillModel(LatestPriceFillModel())
        if self.disableBuyingPowerModel:
            security.SetMarginModel(SecurityMarginModel.Null)
            # security.SetBuyingPowerModel(BuyingPowerModel.Null)

        self.resetConsolidator(security)
        self.initSecurityMonitor()

        for (priority, listener) in self.securityChangedListeners:
            listener.onSecurityChanged(removedSecurity=None)

    def getConsolidator(self, period):
        consolidator = None
        if useQuoteBar(self.securityType):
            if self.resolution == LIResolution.SECOND:
                consolidator = QuoteBarConsolidator(timedelta(seconds=period))
            elif self.resolution == LIResolution.MINUTE:
                consolidator = QuoteBarConsolidator(timedelta(minutes=period))
            elif self.resolution == LIResolution.HOUR:
                consolidator = QuoteBarConsolidator(timedelta(hours=period))
            elif self.resolution == LIResolution.DAY:
                consolidator = QuoteBarConsolidator(timedelta(days=period))
        else:
            if self.resolution == LIResolution.SECOND:
                consolidator = TradeBarConsolidator(timedelta(seconds=period))
            elif self.resolution == LIResolution.MINUTE:
                consolidator = TradeBarConsolidator(timedelta(minutes=period))
            elif self.resolution == LIResolution.HOUR:
                consolidator = TradeBarConsolidator(timedelta(hours=period))
            elif self.resolution == LIResolution.DAY:
                consolidator = TradeBarConsolidator(timedelta(days=period))
        return consolidator

    def removeSecurity(self, security: Security):
        if security is None:
            return  # Ignore possible null symbol
        if self.consolidators.get(security.Symbol) is not None:
            consolidator = self.consolidators.pop(security.Symbol)
            consolidator.DataConsolidated -= self.onDataConsolidated
            getAlgo().SubscriptionManager.RemoveConsolidator(security.Symbol, consolidator)
            log(f"Removed consolidator of the security: {security.Symbol.Value}")
        for (priority, listener) in self.securityChangedListeners:
            listener.onSecurityChanged(removedSecurity=security)

    def isOption(self) -> bool:
        return isOption(self.getSymbol().SecurityType if self.getSymbol() else self.securityType)

    def isDerivative(self) -> bool:
        return isDerivative(self.getSymbol().SecurityType if self.getSymbol() else self.securityType)

    def addFutureOptionContract(self, symbol: Symbol) -> Option:
        return getAlgo().AddFutureOptionContract(symbol, resolution=self.getResolution())

    def subscribeSecurityChanged(self, listener, priority):
        if listener in self.securityChangedListeners:
            return  # Already subscribed
        nextPriority = getNextPriority(self.securityChangedListeners, priority)
        self.securityChangedListeners.append((nextPriority, listener))
        self.securityChangedListeners.sort(reverse=True)

    def subscribeDataBarUpdated(self, listener, priority):
        if listener in self.dataBarUpdatedListeners:
            return  # Already subscribed
        nextPriority = getNextPriority(self.dataBarUpdatedListeners, priority)
        self.dataBarUpdatedListeners.append((nextPriority, listener))
        self.dataBarUpdatedListeners.sort(reverse=True)

    def subscribeDayOpenGapUpOrDown(self, listener, priority):
        if listener in self.dayOpenGapUpDownListeners:
            return  # Already subscribed
        nextPriority = getNextPriority(self.dayOpenGapUpDownListeners, priority)
        self.dayOpenGapUpDownListeners.append((nextPriority, listener))
        self.dayOpenGapUpDownListeners.sort(reverse=True)

    def subscribeDayHighBreachEvent(self, listener, priority):
        if listener in self.dayHighBreachEventListeners:
            return  # Already subscribed
        nextPriority = getNextPriority(self.dayHighBreachEventListeners, priority)
        self.dayHighBreachEventListeners.append((nextPriority, listener))
        self.dayHighBreachEventListeners.sort(reverse=True)

    def subscribeDayLowBreachEvent(self, listener, priority):
        if listener in self.dayLowBreachEventListeners:
            return  # Already subscribed
        nextPriority = getNextPriority(self.dayLowBreachEventListeners, priority)
        self.dayLowBreachEventListeners.append((nextPriority, listener))
        self.dayLowBreachEventListeners.sort(reverse=True)

    def getSymbolKey(self):
        return getSymbolKey(self.symbolStr, self.securityType)

    def getSymbolStr(self):
        return self.symbolStr

    def getMarketOpenPrice(self):
        return self.marketOpenPrice

    def getMarketClosePrice(self):
        return self.marketClosePrice

    def getMarketOpenGapPercent(self):
        return (self.getMarketOpenPrice() - self.getMarketClosePrice()) / self.getMarketClosePrice() * 100

    def isContractExpired(self, expiryDays=None):
        if self.contract:
            contractExpiry = roundDownTime(self.contract.Expiry, delta=timedelta(days=1))
            rolloverDate = roundDownTime(self.contract.Expiry - timedelta(days=(expiryDays if expiryDays else self.futureRolloverDays)),
                                         delta=timedelta(days=1))
            currentDate = roundDownTime(getAlgo().Time, delta=timedelta(days=1))
            log(f"{self.getSymbolAlias()}: contractExpiry={contractExpiry}, rolloverDate={rolloverDate}, currentDate={currentDate}.", self.verbose)
            return rolloverDate <= currentDate

    def isExchangeOpen(self):
        # if self.forceExchangeOpen:
        #     log(f"Always return true as {LIConfigKey.forceExchangeOpen}={self.forceExchangeOpen}")
        return self.isTempTradable or \
            self.forceExchangeOpen or \
            self.getSecurity().Exchange.ExchangeOpen or \
            getAlgo().IsMarketOpen(self.getSecurity().Symbol) or \
            getAlgo().Securities[self.getSymbol()].Exchange.Hours.IsOpen(getAlgo().Time, self.extendedMarketHours)

    def enableTempTradable(self):
        self.isTempTradable = True

    def disableTempTradable(self):
        self.isTempTradable = False

    def getMarketPrice(self):
        # In favor of limit market order to be filled after retry
        marketPrice = getAlgo().Securities[self.getSymbol()].Price
        if not marketPrice and self.latestDataBar:
            marketPrice = self.latestDataBar.Close
        return marketPrice
        # The last price bar can reflect the price better???
        # return self.latestDataBar.Close if self.latestDataBar else getQcAlgo().Securities[self.getSymbol()].Price

    def getMaintenanceMargin(self):
        return getMaintenanceMargin(self.getSymbol(), self.getMarketPrice())

    def manageExpiredSecurity(self):
        if not self.isExchangeOpen():
            return  # Abort, wait for market open!

        if self.verbose and (self.expiredSecurity or self.nextSecurity):
            log(f"{self.getSymbolAlias()}: Manage expired security, isExchangeOpen={self.isExchangeOpen()}, "
                f"expiredSecurity={cleanSymbolValue(self.expiredSecurity.Symbol) if self.expiredSecurity else None}, "
                f"nextSecurity={cleanSymbolValue(self.nextSecurity.Symbol) if self.nextSecurity else None}.")

        if self.isOption():
            log(f"{self.getSymbolAlias()}: Skipped managing expired option as it should be managed within the strategy!")
            return  # Abort, managed within strategy

        if isDerivative(self.securityType):
            # Remove any expired security
            if self.expiredSecurity and self.expiredSecurity != self.contract:
                log(f"{self.getSymbolAlias()}: Remove an expiredSecurity={cleanSymbolValue(self.expiredSecurity.Symbol)}.")
                self.removeSecurity(self.expiredSecurity)
                self.expiredSecurity = None

            # Switch to next security
            nextSecurity = self.nextSecurity
            if self.isContractExpired():
                if nextSecurity is None:
                    alert(f"{self.getSymbolAlias()}: Failed to find next security, please investigate and redeploy!")
                elif self.contract == nextSecurity:
                    alert(f"{self.getSymbolAlias()}: The next security is the same, please investigate and redeploy!")
                else:
                    self.removeSecurity(self.contract)  # Remove expired/existing security first!
                    self.contract = nextSecurity
                    self.addSecurity(self.contract)
                    self.nextSecurity = None
                    investedQuantity = getAlgo().Portfolio[nextSecurity.Symbol].Quantity
                    notify(f"{self.getSymbolAlias()}: Switched to contract: symbol={cleanSymbolValue(nextSecurity.Symbol)}, invested={investedQuantity}, "
                           f"price={nextSecurity.Price}, volume={nextSecurity.Volume}, openInterest={nextSecurity.OpenInterest}, "
                           f"expiry={nextSecurity.Expiry.strftime(LIGlobal.fullTimeFormat)}")

    def updateDataConsolidator(self):
        # if not getQcAlgo().LiveMode:
        #     return  # Enable only for live mode!
        if not self.latestDataBar:
            return  # Abort as not warm up yet!
        resolutionTimedelta = self.getResolutionTimedelta()
        nextUpdateTime = self.latestDataBar.EndTime + resolutionTimedelta * self.monitorPeriod
        # log(f"latestDataBar: {self.latestDataBar} endTime: {self.latestDataBar.EndTime}, nextUpdateTime={nextUpdateTime}")
        if getAlgo().Time <= nextUpdateTime:
            # log(f"{self.getSymbolAlias()}: The data consolidator is in sync with market data stream!")
            return  # Abort as no need to update yet!

        dataBar = None
        isFakedBar = False
        barEndTime = getAlgo().Time - resolutionTimedelta
        if self.fetchHistoryBarData:
            totalPeriods = 10
            bars = self.getHistoryBars(totalPeriods)
            if bars:  # Pick the last bar
                bar = None
                for b in bars:
                    bar = b
                    # log(f"{self.getSymbolAlias()}: history bar: {bar} endTime: {bar.EndTime.strftime(LIGlobal.secondFormat)}")
                if bar:
                    if useQuoteBar(self.securityType):
                        dataBar = QuoteBar(barEndTime, self.getSymbol(), bar.Bid, bar.LastBidSize, bar.Ask, bar.LastAskSize, resolutionTimedelta)
                    else:
                        dataBar = TradeBar(barEndTime, self.getSymbol(), bar.Open, bar.High, bar.Low, bar.Close, bar.Volume, resolutionTimedelta)
        if dataBar is None:
            marketPrice = self.getMarketPrice()
            # log(f"{self.getSymbolAlias()}: Faked a trade bar with current market price: {marketPrice}")
            dataBar = TradeBar(barEndTime, self.getSymbol(), marketPrice, marketPrice, marketPrice, marketPrice, 0, resolutionTimedelta)
            isFakedBar = True

        consolidator = self.consolidators.get(self.getSymbol())
        if consolidator:
            # if self.verbose:
            #     log(f"{self.getSymbolAlias()}: Updating consolidator with the {'faked' if isFakedBar else 'last'} data bar: {dataBar} "
            #         f"endTime: {dataBar.EndTime.strftime(LIGlobal.secondFormat)}")
            consolidator.Update(dataBar)

    def onDataConsolidated(self, sender: Object, bar: Bar):
        self.latestDataBar = bar
        # log(f"{self.getSymbolStrAlias()}: On data consolidated as symbol={bar.Symbol.Value}, endTime={bar.EndTime}, {bar}", self.verbose)

        if self.atMarketOpeningTime():
            self.marketOpenPrice = bar.Close
            self.dayLowPrice = bar.Close
            self.dayHighPrice = bar.Close
            # Calculate day open gap up or down percent
            openGapPercent = abs(self.getMarketOpenGapPercent())
            if openGapPercent > self.dayOpenGapUpDownPercent:  # Notify day open gap up/down event
                self.isDayOpenWithGap = True
                for (priority, listener) in self.dayOpenGapUpDownListeners:
                    listener.onDayOpenGapUpOrDownEvent()

        if self.atMarketClosingTime():
            self.isDayOpenWithGap = False
            self.marketClosePrice = bar.Close

        if isActiveMarketTime(getAlgo().Time):
            if bar.High > self.dayHighPrice:
                self.dayHighPrice = bar.High
                for (priority, listener) in self.dayHighBreachEventListeners:  # Notify day high breach event
                    listener.onDayHighBreachEvent()

            if bar.Low < self.dayLowPrice:
                self.dayLowPrice = bar.Low
                for (priority, listener) in self.dayLowBreachEventListeners:  # Notify day low breach event
                    listener.onDayLowBreachEvent()

        if self.atMarketOpeningTime() or self.atMarketClosingTime():
            self.manageExpiredSecurity()

        for (priority, listener) in self.dataBarUpdatedListeners:  # Notify price update by resolution time
            listener.onMonitorBarUpdated(bar)

    def getMatchedSecurities(self, securities):
        return [x for x in securities if (self.security is None) or ((x.Symbol.Canonical if isDerivative(x.Type) else x.Symbol) == self.security.Symbol)]

    def searchOptionContract(self, contractCode):
        for contractSymbol in getAlgo().OptionChainProvider.GetOptionContractList(self.security.Symbol, getAlgo().Time):
            log(f"{self.getSymbolStrAlias()}: Search option contract: {contractSymbol.Value}")
            if contractCode == cleanSymbolValue(contractSymbol):
                return contractSymbol

    def filterAndSortSecurities(self, securities):
        if self.isOption() and self.contract is None:
            # Sort by strike price to find the latest OTM (out-of-the-money) puts
            latestExpiry = min([x.Expiry for x in securities])
            if self.optionRight == OptionRight.Put:
                securities = sorted(
                    [x for x in securities if x.Expiry == latestExpiry and x.Right == OptionRight.Put and x.Underlying.Price > x.StrikePrice],
                    key=lambda x: x.StrikePrice, reverse=True)[self.optionContractOTMLevel:self.optionContractOTMLevel + 2]
            if self.optionRight == OptionRight.Call:
                securities = sorted(
                    [x for x in securities if x.Expiry == latestExpiry and x.Right == OptionRight.Call and x.Underlying.Price < x.StrikePrice],
                    key=lambda x: x.StrikePrice, reverse=False)[self.optionContractOTMLevel:self.optionContractOTMLevel + 2]
            if len(securities) == 0:
                log(f"{self.getSymbolStrAlias()}: Not found any matched option contracts in added securities: {printSecurities(securities)}")
                return  # Not found any matched options!
            else:
                log(f"{self.getSymbolStrAlias()}: Filtered option contracts in added securities: {printSecurities(securities)}")
        if self.isDerivative():
            # Sort by expiry to get the closest contract
            securities.sort(key=lambda x: x.Expiry)
        return securities

    # Handle dynamic security (e.g. future chains) by updating consolidators
    def onSecuritiesChanged(self, changes: SecurityChanges):
        if changes.Count == 0 or (len(changes.AddedSecurities) == 0 and len(changes.RemovedSecurities) == 0):
            return  # Could be empty based on the filter!

        # Log the changes for verification purpose
        if self.verbose and changes.AddedSecurities:
            log(f"{self.getSymbolStrAlias()}: Added securities: {printSecurities(changes.AddedSecurities)}")
        if self.verbose and changes.RemovedSecurities:
            log(f"{self.getSymbolStrAlias()}: Removed securities: {printSecurities(changes.RemovedSecurities)}")

        # Handle added securities if any!
        addedSecurities = self.getMatchedSecurities(changes.AddedSecurities)
        if len(addedSecurities) == 0:
            return  # Not found any matched securities!

        # Log matched securities for verification purpose
        if self.verbose and addedSecurities:
            log(f"{self.getSymbolStrAlias()}: Matched added securities: {printSecurities(addedSecurities)}.")

        if self.futureContractCode:
            if self.contract is None or cleanSymbolValue(self.contract.Symbol) != self.futureContractCode:
                matchedSecurities = [x for x in addedSecurities if self.futureContractCode == cleanSymbolValue(x.Symbol)]
                if not matchedSecurities:
                    terminate(f"Failed to find {self.futureContractCode} in added securities: {printSecurities(addedSecurities)}.")
                self.contract = matchedSecurities[0]
            if self.contract:
                log(f"{self.getSymbolStrAlias()}: Continue with the specified future contract {self.contract}.")
                self.addSecurity(self.contract)
            return  # Abort, use the reserved contract!

        if self.futureContractExpiry:
            if self.contract is None or self.contract.Expiry.date() != self.futureContractExpiry:
                matchedSecurities = [x for x in addedSecurities if self.futureContractExpiry == x.Expiry.date()]
                if not matchedSecurities:
                    terminate(f"Failed to find expiry date {self.futureContractExpiry} in added securities: {printSecurities(addedSecurities)}.")
                self.contract = matchedSecurities[0]
            if self.contract:
                log(f"{self.getSymbolStrAlias()}: Continue with the specified future contract {self.contract}.")
                self.addSecurity(self.contract)
            return  # Abort, use the reserved contract!

        if self.optionContractCode:
            if self.contract is None or cleanSymbolValue(self.contract.Symbol) != self.optionContractCode:
                matchedSecurities = [x for x in addedSecurities if self.optionContractCode == cleanSymbolValue(x.Symbol)]
                if not matchedSecurities:
                    terminate(f"Failed to find {self.optionContractCode} in added securities: {printSecurities(addedSecurities)}.")
                self.contract = matchedSecurities[0]
            if self.contract:
                log(f"{self.getSymbolStrAlias()}: Continue with the specified option contract {self.optionContractCode}.")
                self.addSecurity(self.contract)
            return  # Abort, use the reserved contract!

        addedSecurities = self.filterAndSortSecurities(addedSecurities)
        if addedSecurities:
            log(f"{self.getSymbolStrAlias()}: Filtered and sorted securities: {printSecurities(addedSecurities)}.", self.verbose)
        else:
            log(f"{self.getSymbolStrAlias()}: Got empty list after filtered the added securities: {printSecurities(addedSecurities)}.")
            return  # Abort, empty filtered list

        # Pick a specific security/contract to trade
        thisSecurity = None
        nextSecurity = None
        for security in addedSecurities:
            if isDerivative(security.Type):
                if security.Symbol.IsCanonical():
                    # log(f"{self.getSymbolAlias()}: Skip the canonical security: {symbol.Value}")
                    continue
                securityExpiry = roundDownTime(security.Expiry, delta=timedelta(days=1))
                rolloverDate = roundDownTime(security.Expiry - timedelta(self.futureRolloverDays), delta=timedelta(days=1))
                currentDate = roundDownTime(getAlgo().Time, delta=timedelta(days=1))
                log(f"{self.getSymbolStrAlias()}: securityExpiry={securityExpiry}, rolloverDate={rolloverDate}, currentDate={currentDate}, "
                    f"isNotInvested={isNotInvested(security.Symbol)}", self.verbose)
                if rolloverDate <= currentDate and isNotInvested(security.Symbol):
                    log(f"{self.getSymbolStrAlias()}: Will remove the security expiring in {self.futureRolloverDays} days: {security.Symbol.Value}")
                    self.expiredSecurity = security
                    self.manageExpiredSecurity()
                    continue
            if not thisSecurity:
                thisSecurity = security
            elif not nextSecurity:
                nextSecurity = security  # Pick the second closed (front month) security
            elif thisSecurity.Expiry > security.Expiry:
                nextSecurity = thisSecurity  # Reserve as the second closed (front month) security!
                thisSecurity = security  # Pick the closest (front month) security!
                log(f"{self.getSymbolStrAlias()}: thisSecurity={thisSecurity.Symbol.Value}, nextSecurity={nextSecurity.Symbol.Value}")

        # Do nothing if thisSecurity is None, Stop Algo only when manual intervene required!
        if thisSecurity is not None:
            self.nextSecurity = nextSecurity  # Save it for daily manageExpiredSecurity.
            if isDerivative(thisSecurity.Type):
                if self.contract is None:
                    self.contract = thisSecurity
                    self.addSecurity(self.contract)
                    log(f"{self.getSymbolStrAlias()}: Use contract: symbol={cleanSymbolValue(thisSecurity.Symbol)}, invested={thisSecurity.Invested}, "
                        f"price={thisSecurity.Price}, volume={thisSecurity.Volume}, openInterest={thisSecurity.OpenInterest}, "
                        f"expiry={thisSecurity.Expiry.strftime(LIGlobal.fullTimeFormat)}, "
                        f"{'strikePrice=' + str(thisSecurity.StrikePrice) + ', ' if isOption(thisSecurity.Type) else ''}"
                        f"{'marketPrice=' + str(thisSecurity.Underlying.Price) + ', ' if isOption(thisSecurity.Type) else ''}"
                        f"nextSecurity={cleanSymbolValue(nextSecurity.Symbol) if nextSecurity else None}")
                    self.manageExpiredSecurity()
                else:
                    self.nextSecurity = thisSecurity  # Save it for when current contract expired
                    self.manageExpiredSecurity()
            else:
                if self.security and self.security != thisSecurity:
                    self.removeSecurity(self.security)  # Remove expired/existing security first!
                self.security = thisSecurity
                self.addSecurity(self.security)
                log(f"{self.getSymbolStrAlias()}: Use security: symbol={thisSecurity.Symbol.Value}, invested={thisSecurity.Invested}, "
                    f"price={thisSecurity.Price}, volume={thisSecurity.Volume}, openInterest={thisSecurity.OpenInterest}")

        # Handle removed securities if any!
        removedSecurities = self.getMatchedSecurities(changes.RemovedSecurities)
        if len(removedSecurities) == 0:
            return  # Not found any matched securities!

        # Log matched security for verification purpose
        if removedSecurities:
            log(f"{self.getSymbolStrAlias()}: Matched removed securities: {printSecurities(removedSecurities)}")

        if self.isOption() and self.contract:
            log(f"{self.getSymbolAlias()}: Skipped removing option contract as it should be managed within the strategy!")
            return  # Abort, managed within strategy

        for security in removedSecurities:
            if (self.contract if isDerivative(security.Type) else self.security) == security:
                alert(f"{self.getSymbolAlias()}: Failed to manage expired security, please switch over to next security!")
                getAlgo().Quit("Quit algorithm on EXPIRED SECURITY!")
                return  # Quit execution immediately!
                # if security != self.nextSecurity:
                #     self.enableTempTradable()
                #     self.manageExpiredSecurity()
                #     self.disableTempTradable()
                # else:
                #     alert(f"{self.getSymbolStrAlias()}: Failed to manage expired security, please switch over to next security!")
                #     getQcAlgo().Quit("Quit algorithm on EXPIRED SECURITY!")
                #     return
            self.removeSecurity(security)
            # Will be reset by new added security later
            if self.security and security.Symbol == self.security.Symbol:
                self.security = None
            if self.contract and security.Symbol == self.contract.Symbol:
                self.contract = None
