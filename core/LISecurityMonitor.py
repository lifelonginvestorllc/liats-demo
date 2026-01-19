from AlgorithmImports import *
from core.LIConfiguration import *


def printSecurities(securities):
    return f"{list(map(lambda x: printSecurity(x), securities))}"


def printSecurity(x: Security) -> str:
    return cleanSymbolValue(x.symbol) + '|' + (x.expiry.strftime(LIGlobal.dateFormat) if isDerivative(x.type) and x.expiry else 'None') + '|' + str(
        x.volume) if x else 'None'


def printOptionSymbol(symbol: Symbol):
    identifier = symbol.ID
    result = f"{cleanSymbolValue(symbol)}\t{str(identifier.option_right)}\t{identifier.strike_price}\t{identifier.date.strftime(LIGlobal.dateFormat)}"
    return result


def printOptionContract(option: Option):
    result = (f"symbol={cleanSymbolValue(option.symbol)}, right={str(option.right)}, strike={option.strike_price}, "
              f"expiry={option.expiry.strftime(LIGlobal.dateFormat)}, price={option.price}, multiplier={option.contract_multiplier}, "
              f"openInterest={option.open_interest}, volume={option.volume}, bidSize={option.bid_size}, bidPrice={option.bid_price}, "
              f"askSize={option.ask_size}, askPrice={option.ask_price}")
    return result


def isExpiredAfterDays(expiryDate, expiryDays):
    backwardDate = roundDownTime(expiryDate - timedelta(days=expiryDays), delta=timedelta(days=1))
    currentDate = roundDownTime(getAlgoTime(), delta=timedelta(days=1))
    return backwardDate >= currentDate


def getResolution(resolution: LIResolution) -> Resolution:
    if resolution == LIResolution.SECOND:
        return Resolution.SECOND
    elif resolution == LIResolution.MINUTE:
        return Resolution.MINUTE
    elif resolution == LIResolution.HOUR:
        return Resolution.HOUR
    elif resolution == LIResolution.DAY:
        return Resolution.DAILY
    else:
        terminate(f"Not support {LIConfigKey.resolution}={resolution}")
        return None


def getResolutionTimedelta(resolution: LIResolution) -> timedelta:
    if resolution == LIResolution.SECOND:
        return timedelta(seconds=1)
    elif resolution == LIResolution.MINUTE:
        return timedelta(minutes=1)
    elif resolution == LIResolution.HOUR:
        return timedelta(hours=1)
    elif resolution == LIResolution.DAY:
        return timedelta(days=1)
    else:
        terminate(f"Not support {LIConfigKey.resolution}={resolution}")
        return None


def getDefaultWarmupPeriods(resolution: LIResolution) -> int:
    warmupPeriods = 0
    if resolution == LIResolution.SECOND:
        warmupPeriods = 1 * 60  # 1 minute history data, not applicable for marketOpenPrice/marketClosePrice!
    elif resolution == LIResolution.MINUTE:
        warmupPeriods = 1 * 60  # 1 hour history data
    elif resolution == LIResolution.HOUR:
        warmupPeriods = 1 * 24  # 1 day history data
    elif resolution == LIResolution.DAY:
        warmupPeriods = 1 * 30  # 1 month history data
    return warmupPeriods


class LISecurityMonitor:
    def __init__(self, symbolStr, securityType, strategyCode, configs):
        self.symbolStr = symbolStr
        self.securityType = securityType
        self.strategyCode = strategyCode
        self.configs = configs

        self.verbose = configs.get(LIConfigKey.verbose, LIDefault.verbose)
        self.aliasName = configs.get(LIConfigKey.aliasName, LIDefault.aliasName)
        self.warmupAlgo = configs.get(LIConfigKey.warmupAlgo, LIDefault.warmupAlgo)

        self.monitorPeriod = configs.get(LIConfigKey.monitorPeriod, LIDefault.monitorPeriod)
        self.forceExchangeOpen = configs.get(LIConfigKey.forceExchangeOpen, LIDefault.forceExchangeOpen)
        self.enableAutoRollover = configs.get(LIConfigKey.enableAutoRollover, LIDefault.enableAutoRollover)
        self.extendedMarketHours = configs.get(LIConfigKey.extendedMarketHours, LIDefault.extendedMarketHours)
        self.extendDataBarStream = configs.get(LIConfigKey.extendDataBarStream, LIDefault.extendDataBarStream)
        self.fetchHistoryBarData = configs.get(LIConfigKey.fetchHistoryBarData, LIDefault.fetchHistoryBarData)
        self.disableBuyingPowerModel = configs.get(LIConfigKey.disableBuyingPowerModel, LIDefault.disableBuyingPowerModel)
        self.dayOpenGapUpDownPercent = configs.get(LIConfigKey.dayOpenGapUpDownPercent, LIDefault.dayOpenGapUpDownPercent)

        self.liquidateLossAndBackfillEquity = configs.get(LIConfigKey.liquidateLossAndBackfillEquity, LIDefault.liquidateLossAndBackfillEquity)

        self.futurePeriodDays = configs.get(LIConfigKey.futurePeriodDays, LIDefault.futurePeriodDays)
        self.futureRolloverDays = configs.get(LIConfigKey.futureRolloverDays, LIDefault.futureRolloverDays)
        self.futureContractCode = configs.get(LIConfigKey.futureContractCode, LIDefault.futureContractCode)
        self.futureContractExpiry = configs.get(LIConfigKey.futureContractExpiry, LIDefault.futureContractExpiry)
        self.futureContractMarket = configs.get(LIConfigKey.futureContractMarket, LIDefault.futureContractMarket)
        self.futureExpirationCycles = configs.get(LIConfigKey.futureExpirationCycles, LIDefault.futureExpirationCycles)

        self.optionRight = configs.get(LIConfigKey.optionRight, LIDefault.optionRight)
        self.optionContractCode = configs.get(LIConfigKey.optionContractCode, LIDefault.optionContractCode)
        self.optionContractOTMLevel = configs.get(LIConfigKey.optionContractOTMLevel, LIDefault.optionContractOTMLevel)
        self.optionMinMaxExpiryDays = configs.get(LIConfigKey.optionMinMaxExpiryDays, LIDefault.optionMinMaxExpiryDays)
        self.optionMinMaxStrikeLevel = configs.get(LIConfigKey.optionMinMaxStrikeLevel, LIDefault.optionMinMaxStrikeLevel)
        self.addFutureOptionUniverse = configs.get(LIConfigKey.addFutureOptionUniverse, LIDefault.addFutureOptionUniverse)

        if self.securityType == SecurityType.OPTION and self.optionRight is None:
            terminate(f"Please specify {LIConfigKey.optionRight} as securityType={str(self.securityType)}!")
        if self.futureRolloverDays < 1:
            terminate(f"Please specify '{LIConfigKey.futureRolloverDays} > 0' to avoid 'Liquidate from delisting' unexpectedly!")
        if self.futureContractCode and self.futureContractExpiry:
            terminate(f"Please specify either {LIConfigKey.futureContractCode} or {LIConfigKey.futureContractExpiry}!")

        self.security: Security = None
        self.contract: Security = None
        self.nextSecurity: Security = None
        self.expiredSecurity: Security = None
        self.backfillSecurity: Security = None

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

        # Have securities initialized right after deployment
        if self.warmupAlgo and not getAlgo().is_warming_up:
            getAlgo().set_warmup(10, self.getResolution())

        # Simulate market data stream if not available yet!
        if self.extendDataBarStream:
            getAlgo().schedule.on(getAlgo().date_rules.every_day(),
                                  getAlgo().time_rules.every(getResolutionTimedelta(self.monitorPeriod[1])),
                                  self.updateDataConsolidator)

    def getSymbol(self) -> Symbol:
        return self.getSecurity().symbol

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
        return getResolution(self.monitorPeriod[1])

    def atMarketOpeningTime(self, timestamp=None) -> bool:
        return atMarketOpeningTime(timestamp=timestamp, delta=self.getMonitorPeriodDelta())

    def atMarketClosingTime(self, timestamp=None) -> bool:
        return atMarketClosingTime(timestamp=timestamp, delta=self.getMonitorPeriodDelta())

    def getMonitorPeriodDelta(self) -> timedelta:
        return getResolutionTimedelta(self.monitorPeriod[1]) * self.monitorPeriod[0]

    def getSecurityMultiplier(self):
        return self.getSecurity().symbol_properties.contract_multiplier  # 1.0 for other securities

    def getSecurityType(self):
        return self.securityType

    def getStrategyCode(self):
        return self.strategyCode

    def getCanonicalSymbol(self) -> Symbol:
        symbol = self.getSymbol()
        if isDerivative(symbol.security_type):
            return symbol.canonical
        return symbol

    def setupSecurityUniverse(self):
        if self.securityType == SecurityType.EQUITY:
            self.security = getAlgo().add_equity(ticker=self.symbolStr,
                                                 resolution=self.getResolution(),
                                                 extended_market_hours=self.extendedMarketHours,
                                                 data_normalization_mode=DataNormalizationMode.RAW)  # DO NOT normalize history data!
        elif self.securityType == SecurityType.FOREX:
            self.security = getAlgo().add_forex(ticker=self.symbolStr,
                                                resolution=self.getResolution())
        elif self.securityType == SecurityType.CFD:
            self.security = getAlgo().add_cfd(ticker=self.symbolStr,
                                              resolution=self.getResolution())
        elif self.securityType == SecurityType.FUTURE:
            self.security = getAlgo().add_future(ticker=self.symbolStr,
                                                 resolution=self.getResolution(),
                                                 extended_market_hours=self.extendedMarketHours,
                                                 data_mapping_mode=DataMappingMode.LAST_TRADING_DAY,
                                                 data_normalization_mode=DataNormalizationMode.RAW,  # DO NOT normalize history data!
                                                 contract_depth_offset=0)
            if self.futureContractExpiry:
                self.contract = getAlgo().add_future_contract(Symbol.create_future(self.symbolStr, self.futureContractMarket, self.futureContractExpiry),
                                                              resolution=self.getResolution(),
                                                              extended_market_hours=self.extendedMarketHours)
                self.security.set_filter(timedelta(days=0), timedelta(days=0))  # No filter as just use the specified contract
            elif self.futureContractCode:
                self.contract = getAlgo().add_future_contract(SymbolRepresentation.parse_future_symbol(self.futureContractCode),
                                                              resolution=self.getResolution(),
                                                              extended_market_hours=self.extendedMarketHours)
                self.security.set_filter(timedelta(days=0), timedelta(days=0))  # No filter as just use the specified contract
            else:
                # Set expiry filter and accept contracts between these days
                expirationCycle = FutureExpirationCycles.ALL_YEAR
                if self.futureExpirationCycles is not None:
                    expirationCycle = self.futureExpirationCycles
                elif self.futurePeriodDays > 85:
                    expirationCycle = FutureExpirationCycles.MARCH
                self.security.set_filter(
                    lambda f: f.expiration_cycle(expirationCycle).expiration(timedelta(days=0), timedelta(days=self.getFutureMaxExpiryDays())))
            # self.security.set_fill_model(LatestPriceFillModel())
            # getQcAlgo().set_security_initializer(lambda security: security.set_margin_model(SecurityMarginModel.NULL))
            if self.addFutureOptionUniverse:
                getAlgo().add_future_option(self.security.symbol, lambda universe: universe
                                            .standards_only()
                                            .strikes(self.optionMinMaxStrikeLevel[0], self.optionMinMaxStrikeLevel[1])
                                            .expiration(timedelta(days=self.optionMinMaxExpiryDays[0]), timedelta(days=self.optionMinMaxExpiryDays[1]))
                                            .only_apply_filter_at_market_open())
        elif self.securityType == SecurityType.OPTION:
            # underlyingEquity = getQcAlgo().add_equity(self.symbolStr, resolution=self.getResolution())
            self.security = getAlgo().add_option(underlying=self.symbolStr,
                                                 resolution=self.getResolution())
            # The filter will be shared by both put and call
            if self.optionContractCode:
                spanDays = (extractExpiryDate(self.optionContractCode) - getAlgoTime()).days
                strikePrice = extractStrikePrice(self.optionContractCode)
                log(f"{self.getSymbolStrAlias()}: Use reserved option contract {self.optionContractCode}, spanDays={spanDays}, strikePrice={strikePrice}.")
                self.security.set_filter(lambda universe: universe
                                         .standards_only()
                                         .strikes(self.optionMinMaxStrikeLevel[0], self.optionMinMaxStrikeLevel[1])
                                         .expiration(timedelta(days=spanDays - 5), timedelta(days=spanDays + 5))
                                         .only_apply_filter_at_market_open())
            else:
                self.security.set_filter(lambda universe: universe
                                         .standards_only()
                                         .strikes(self.optionMinMaxStrikeLevel[0], self.optionMinMaxStrikeLevel[1])
                                         .expiration(timedelta(days=self.optionMinMaxExpiryDays[0]), timedelta(days=self.optionMinMaxExpiryDays[1]))
                                         .only_apply_filter_at_market_open())
        elif self.securityType == SecurityType.CRYPTO_FUTURE:
            self.security = getAlgo().add_crypto_future(ticker=self.symbolStr, resolution=self.getResolution())
            # Set expiry filter and accept contracts between these days
            self.security.set_filter(timedelta(days=0), timedelta(days=self.futurePeriodDays + self.futureRolloverDays))
        else:
            terminate(f"Invalid securityType={str(self.securityType)}")
        # Add other ancillary securities if specified
        if self.liquidateLossAndBackfillEquity:
            self.backfillSecurity = getAlgo().add_equity(ticker=self.liquidateLossAndBackfillEquity,
                                                         resolution=self.getResolution(),
                                                         extended_market_hours=self.extendedMarketHours,
                                                         data_normalization_mode=DataNormalizationMode.RAW)  # DO NOT normalize history data!

    def getFutureMaxExpiryDays(self):
        if self.futureContractCode or self.futureContractExpiry:
            return 365  # Return contracts in one year for now
        else:
            return self.futurePeriodDays + self.futureRolloverDays

    def resetConsolidator(self, security):
        if self.consolidators.get(security.symbol) is not None:
            consolidator = self.consolidators.pop(security.symbol)
            consolidator.data_consolidated -= self.onDataConsolidated
            getAlgo().subscription_manager.remove_consolidator(security.symbol, consolidator)
            log(f"Removed consolidator of the security: {security.symbol.value}")
        consolidator = self.getConsolidator(self.monitorPeriod)
        consolidator.only_emit_on_close = True
        consolidator.time_zone = LIGlobal.timezone
        consolidator.data_consolidated += self.onDataConsolidated
        getAlgo().subscription_manager.add_consolidator(security.symbol, consolidator)
        self.consolidators[security.symbol] = consolidator

    def initSecurityMonitor(self, totalPeriods=0):
        if not self.fetchHistoryBarData and totalPeriods == 0:
            log(f"{self.getSymbolAlias()}: Skipped resetting security monitor as {LIConfigKey.fetchHistoryBarData}={self.fetchHistoryBarData}")
            return  # Abort on demand

        resolution = self.monitorPeriod[1]
        if totalPeriods == 0:  # Use default periods
            totalPeriods = getDefaultWarmupPeriods(resolution)

        for bar in self.getHistoryBars(totalPeriods):
            if bar and bar.close:
                self.latestDataBar = bar
                if self.atMarketOpeningTime(timestamp=bar.end_time):
                    self.marketOpenPrice = bar.close
                if self.atMarketClosingTime(timestamp=bar.end_time):
                    self.marketClosePrice = bar.close

        log(f"{self.getSymbolAlias()}: Reset security monitor, marketOpenPrice={self.marketOpenPrice:.2f}, "
            f"marketClosePrice={self.marketClosePrice:.2f}, latestDataBar={self.latestDataBar.close if self.latestDataBar else -1:.2f}")

    def getHistoryBars(self, periods, resolution=None):
        bars = getAlgo().history[getBarType(self.getSecurityType())](self.getSymbol(), periods,
                                                                     resolution=resolution if resolution else self.getResolution(),
                                                                     extended_market_hours=self.extendedMarketHours,
                                                                     data_mapping_mode=DataMappingMode.LAST_TRADING_DAY,
                                                                     data_normalization_mode=DataNormalizationMode.RAW,  # DO NOT normalize history data!
                                                                     contract_depth_offset=0)
        return bars

    def getHistoryDataFrame(self, periods, resolution=None):
        dataFrame = getAlgo().history(getBarType(self.getSecurityType()), self.getSymbol(), periods,
                                      resolution=resolution if resolution else self.getResolution(),
                                      extended_market_hours=self.extendedMarketHours,
                                      data_mapping_mode=DataMappingMode.LAST_TRADING_DAY,
                                      data_normalization_mode=DataNormalizationMode.RAW,  # DO NOT normalize history data!
                                      contract_depth_offset=0)
        return dataFrame

    def addSecurity(self, security: Security):
        if security is None:
            return  # Ignore possible null symbol

        # self.security.set_fill_model(LatestPriceFillModel())
        if self.disableBuyingPowerModel:
            security.set_margin_model(SecurityMarginModel.NULL)
            # security.set_buying_power_model(BuyingPowerModel.NULL)

        self.resetConsolidator(security)
        self.initSecurityMonitor()

        for (priority, listener) in self.securityChangedListeners:
            listener.onSecurityChanged(removedSecurity=None)

    def getConsolidator(self, period):
        consolidator = None
        if useQuoteBar(self.securityType):
            if period[1] == LIResolution.SECOND:
                consolidator = QuoteBarConsolidator(timedelta(seconds=period[0]))
            elif period[1] == LIResolution.MINUTE:
                consolidator = QuoteBarConsolidator(timedelta(minutes=period[0]))
            elif period[1] == LIResolution.HOUR:
                consolidator = QuoteBarConsolidator(timedelta(hours=period[0]))
            elif period[1] == LIResolution.DAY:
                consolidator = QuoteBarConsolidator(timedelta(days=period[0]))
        else:
            if period[1] == LIResolution.SECOND:
                consolidator = TradeBarConsolidator(timedelta(seconds=period[0]))
            elif period[1] == LIResolution.MINUTE:
                consolidator = TradeBarConsolidator(timedelta(minutes=period[0]))
            elif period[1] == LIResolution.HOUR:
                consolidator = TradeBarConsolidator(timedelta(hours=period[0]))
            elif period[1] == LIResolution.DAY:
                consolidator = TradeBarConsolidator(timedelta(days=period[0]))
        return consolidator

    def removeSecurity(self, security: Security):
        if security is None:
            return  # Ignore possible null symbol
        if self.consolidators.get(security.symbol) is not None:
            consolidator = self.consolidators.pop(security.symbol)
            consolidator.data_consolidated -= self.onDataConsolidated
            getAlgo().subscription_manager.remove_consolidator(security.symbol, consolidator)
            log(f"Removed consolidator of the security: {security.symbol.value}")
        for (priority, listener) in self.securityChangedListeners:
            listener.onSecurityChanged(removedSecurity=security)

    def isOption(self) -> bool:
        return isOption(self.getSymbol().security_type if self.getSymbol() else self.securityType)

    def isDerivative(self) -> bool:
        return isDerivative(self.getSymbol().security_type if self.getSymbol() else self.securityType)

    def addFutureOptionContract(self, symbol: Symbol) -> Option:
        return getAlgo().add_future_option_contract(symbol, resolution=self.getResolution())

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
            contractExpiry = roundDownTime(self.contract.expiry, delta=timedelta(days=1))
            rolloverDate = roundDownTime(self.contract.expiry - timedelta(days=(expiryDays if expiryDays else self.futureRolloverDays)),
                                         delta=timedelta(days=1))
            currentDate = roundDownTime(getAlgoTime(), delta=timedelta(days=1))
            log(f"{self.getSymbolAlias()}: contractExpiry={contractExpiry}, rolloverDate={rolloverDate}, currentDate={currentDate}.", self.verbose)
            return rolloverDate <= currentDate
        return None

    def isExchangeOpen(self):
        # if self.forceExchangeOpen:
        #     log(f"Always return true as {LIConfigKey.forceExchangeOpen}={self.forceExchangeOpen}")
        return (not getAlgo().is_warming_up and
                (self.isTempTradable or self.forceExchangeOpen or self.getSecurity().exchange.exchange_open or
                 getAlgo().is_market_open(self.getSecurity().symbol) or
                 getAlgo().securities[self.getSymbol()].exchange.hours.is_open(getAlgoTime(), self.extendedMarketHours)))

    def enableTempTradable(self):
        self.isTempTradable = True

    def disableTempTradable(self):
        self.isTempTradable = False

    def getMarketPrice(self):
        # In favor of limit market order to be filled after retry
        marketPrice = getAlgo().securities[self.getSymbol()].price
        if not marketPrice and self.latestDataBar:
            marketPrice = self.latestDataBar.close
        return marketPrice
        # The last price bar can reflect the price better???
        # return self.latestDataBar.close if self.latestDataBar else getQcAlgo().securities[self.getSymbol()].price

    def getMaintenanceMargin(self):
        return getMaintenanceMargin(self.getSymbol(), self.getMarketPrice())

    def manageExpiredSecurity(self):
        if not self.isExchangeOpen():
            return  # Abort, wait for market open!

        if self.expiredSecurity or self.nextSecurity:
            log(f"{self.getSymbolAlias()}: Manage expired security, isExchangeOpen={self.isExchangeOpen()}, "
                f"expiredSecurity={cleanSymbolValue(self.expiredSecurity.symbol) if self.expiredSecurity else None}, "
                f"nextSecurity={cleanSymbolValue(self.nextSecurity.symbol) if self.nextSecurity else None}.", self.verbose)

        if self.isOption():
            log(f"{self.getSymbolAlias()}: Skipped managing expired option as it should be managed within the strategy!")
            return  # Abort, managed within strategy

        if isDerivative(self.securityType):
            # Remove any expired security
            if self.expiredSecurity and self.expiredSecurity != self.contract:
                log(f"{self.getSymbolAlias()}: Remove an expiredSecurity={cleanSymbolValue(self.expiredSecurity.symbol)}.")
                self.removeSecurity(self.expiredSecurity)
                self.expiredSecurity = None

            # Switch to next security
            nextSecurity = self.nextSecurity
            if self.isContractExpired():
                if nextSecurity is None:
                    if isLiveMode():
                        alert(f"{self.getSymbolAlias()}: Failed to find next security, please investigate as it's approaching rollover date!")
                    else:
                        getAlgo().quit(f"{self.getSymbolAlias()}: Failed to find next security!")
                elif self.contract == nextSecurity:
                    if isLiveMode():
                        alert(f"{self.getSymbolAlias()}: The next security is the same, please investigate as it's approaching rollover date!")
                    else:
                        getAlgo().quit(f"{self.getSymbolAlias()}: The next security is the same!")
                else:
                    self.removeSecurity(self.contract)  # Remove expired/existing security first!
                    self.contract = nextSecurity
                    self.addSecurity(self.contract)
                    self.nextSecurity = None
                    investedQuantity = getAlgo().portfolio[nextSecurity.symbol].quantity
                    notify(f"{self.getSymbolAlias()}: Switched to contract: symbol={cleanSymbolValue(nextSecurity.symbol)}, invested={investedQuantity}, "
                           f"price={nextSecurity.price}, volume={nextSecurity.volume}, openInterest={nextSecurity.open_interest}, "
                           f"expiry={nextSecurity.expiry.strftime(LIGlobal.minuteFormat)}")

    def updateDataConsolidator(self):
        # if not getQcAlgo().live_mode:
        #     return  # Enable only for live mode!
        if not self.latestDataBar:
            return  # Abort as not warm up yet!
        resolutionTimedelta = getResolutionTimedelta(self.monitorPeriod[1])
        nextUpdateTime = self.latestDataBar.end_time + resolutionTimedelta * self.monitorPeriod[0]
        # log(f"latestDataBar: {self.latestDataBar} endTime: {self.latestDataBar.end_time}, nextUpdateTime={nextUpdateTime}")
        if getAlgoTime() <= nextUpdateTime:
            # log(f"{self.getSymbolAlias()}: The data consolidator is in sync with market data stream!")
            return  # Abort as no need to update yet!

        dataBar = None
        isFakedBar = False
        barEndTime = getAlgoTime() - resolutionTimedelta
        if self.fetchHistoryBarData:
            totalPeriods = 10
            bars = self.getHistoryBars(totalPeriods)
            if bars:  # Pick the last bar
                bar = None
                for b in bars:
                    bar = b
                    # log(f"{self.getSymbolAlias()}: history bar: {bar} endTime: {bar.end_time.strftime(LIGlobal.secondFormat)}")
                if bar:
                    if useQuoteBar(self.securityType):
                        dataBar = QuoteBar(barEndTime, self.getSymbol(), bar.bid, bar.last_bid_size, bar.ask, bar.last_ask_size, resolutionTimedelta)
                    else:
                        dataBar = TradeBar(barEndTime, self.getSymbol(), bar.open, bar.high, bar.low, bar.close, bar.volume, resolutionTimedelta)
        if dataBar is None:
            marketPrice = self.getMarketPrice()
            # log(f"{self.getSymbolAlias()}: Faked a trade bar with current market price: {marketPrice}")
            dataBar = TradeBar(barEndTime, self.getSymbol(), marketPrice, marketPrice, marketPrice, marketPrice, 0, resolutionTimedelta)
            isFakedBar = True

        consolidator = self.consolidators.get(self.getSymbol())
        if consolidator:
            # log(f"{self.getSymbolAlias()}: Updating consolidator with the {'faked' if isFakedBar else 'last'} data bar: {dataBar} "
            #     f"endTime: {dataBar.end_time.strftime(LIGlobal.secondFormat)}", self.verbose)
            consolidator.update(dataBar)

    def onDataConsolidated(self, sender: Object, bar: Bar):
        self.latestDataBar = bar
        # log(f"{self.getSymbolStrAlias()}: On data consolidated as symbol={bar.symbol.value}, endTime={bar.end_time}, {bar}", self.verbose)

        if self.atMarketOpeningTime():
            self.marketOpenPrice = bar.close
            self.dayLowPrice = bar.close
            self.dayHighPrice = bar.close
            # Calculate day open gap up or down percent
            openGapPercent = abs(self.getMarketOpenGapPercent())
            if openGapPercent > self.dayOpenGapUpDownPercent:  # Notify day open gap up/down event
                self.isDayOpenWithGap = True
                for (priority, listener) in self.dayOpenGapUpDownListeners:
                    listener.onDayOpenGapUpOrDownEvent()

        if self.atMarketClosingTime():
            self.isDayOpenWithGap = False
            self.marketClosePrice = bar.close

        if isActiveMarketTime(getAlgoTime()):
            if bar.high > self.dayHighPrice:
                self.dayHighPrice = bar.high
                for (priority, listener) in self.dayHighBreachEventListeners:  # Notify day high breach event
                    listener.onDayHighBreachEvent()

            if bar.low < self.dayLowPrice:
                self.dayLowPrice = bar.low
                for (priority, listener) in self.dayLowBreachEventListeners:  # Notify day low breach event
                    listener.onDayLowBreachEvent()

        if self.atMarketOpeningTime() or self.atMarketClosingTime():
            self.manageExpiredSecurity()

        for (priority, listener) in self.dataBarUpdatedListeners:  # Notify price update by resolution time
            listener.onMonitorBarUpdated(bar)

    def getMatchedSecurities(self, securities):
        return [x for x in securities if (self.security is None) or ((x.symbol.canonical if isDerivative(x.type) else x.symbol) == self.security.symbol)]

    def searchOptionContract(self, contractCode):
        for option in getAlgo().option_chain(self.security.symbol):
            log(f"{self.getSymbolStrAlias()}: Search option contract: {option.symbol}.")
            if contractCode == cleanSymbolValue(option.symbol):
                return option
        return None

    def filterAndSortSecurities(self, securities):
        if self.isOption() and self.contract is None:
            # Sort by strike price to find the latest OTM (out-of-the-money) puts
            latestExpiry = min([x.expiry for x in securities])
            if self.optionRight == OptionRight.PUT:
                securities = sorted(
                    [x for x in securities if x.expiry == latestExpiry and x.right == OptionRight.PUT and x.underlying.price > x.strike_price],
                    key=lambda x: x.strike_price, reverse=True)[self.optionContractOTMLevel:self.optionContractOTMLevel + 2]
            if self.optionRight == OptionRight.CALL:
                securities = sorted(
                    [x for x in securities if x.expiry == latestExpiry and x.right == OptionRight.CALL and x.underlying.price < x.strike_price],
                    key=lambda x: x.strike_price, reverse=False)[self.optionContractOTMLevel:self.optionContractOTMLevel + 2]
            if len(securities) == 0:
                log(f"{self.getSymbolStrAlias()}: Not found any matched option contracts in added securities: {printSecurities(securities)}.")
                return None
            else:
                log(f"{self.getSymbolStrAlias()}: Filtered option contracts in added securities: {printSecurities(securities)}.")
        if self.isDerivative():
            # Sort by expiry to get the closest contract
            securities.sort(key=lambda x: x.expiry)
        return securities

    def onWarmupFinished(self):
        warmupSecurities = getAlgo().securities.values()
        if warmupSecurities:
            log(f"{self.getSymbolStrAlias()}: Warmup securities: {printSecurities(warmupSecurities)}", self.verbose)
        warmupSecurities = self.getMatchedSecurities(warmupSecurities)
        if len(warmupSecurities) == 0:
            return  # Not found any matched securities!
        self.addSecurities(warmupSecurities)

    # Handle dynamic security (e.g. future chains) by updating consolidators
    def onSecuritiesChanged(self, changes: SecurityChanges):
        if changes.count == 0 or (len(changes.added_securities) == 0 and len(changes.removed_securities) == 0):
            return  # Could be empty based on the filter!

        # Handle added securities if any!
        if changes.added_securities:
            log(f"{self.getSymbolStrAlias()}: Added securities: {printSecurities(changes.added_securities)}.", self.verbose)
        addedSecurities = self.getMatchedSecurities(changes.added_securities)
        if len(addedSecurities) == 0:
            return  # Not found any matched securities!
        self.addSecurities(addedSecurities)

        # Handle removed securities if any!
        if changes.removed_securities:
            log(f"{self.getSymbolStrAlias()}: Removed securities: {printSecurities(changes.removed_securities)}.", self.verbose)
        removedSecurities = self.getMatchedSecurities(changes.removed_securities)
        if len(removedSecurities) == 0:
            return  # Not found any matched securities!
        self.removeSecurities(removedSecurities)

    def addSecurities(self, addedSecurities: list[Security]):
        # Log matched securities for verification purpose
        if addedSecurities:
            log(f"{self.getSymbolStrAlias()}: Adding securities: {printSecurities(addedSecurities)}.", self.verbose)

        if self.futureContractCode:
            if self.contract is None or cleanSymbolValue(self.contract.symbol) != self.futureContractCode:
                matchedSecurities = [x for x in addedSecurities if self.futureContractCode == cleanSymbolValue(x.symbol)]
                if not matchedSecurities:
                    terminate(f"Failed to find {self.futureContractCode} in added securities: {printSecurities(addedSecurities)}.")
                self.contract = matchedSecurities[0]
            if self.contract:
                log(f"{self.getSymbolStrAlias()}: Continue with the specified future contract {self.contract}.")
                self.addSecurity(self.contract)
            return  # Abort, use the reserved contract!

        if self.futureContractExpiry:
            if self.contract is None or self.contract.expiry.date() != self.futureContractExpiry:
                matchedSecurities = [x for x in addedSecurities if self.futureContractExpiry == x.expiry.date()]
                if not matchedSecurities:
                    terminate(f"Failed to find expiry date {self.futureContractExpiry} in added securities: {printSecurities(addedSecurities)}.")
                self.contract = matchedSecurities[0]
            if self.contract:
                log(f"{self.getSymbolStrAlias()}: Continue with the specified future contract {self.contract}.")
                self.addSecurity(self.contract)
            return  # Abort, use the reserved contract!

        if self.optionContractCode:
            if self.contract is None or cleanSymbolValue(self.contract.symbol) != self.optionContractCode:
                matchedSecurities = [x for x in addedSecurities if self.optionContractCode == cleanSymbolValue(x.symbol)]
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
            if isDerivative(security.type):
                if security.symbol.is_canonical():
                    # log(f"{self.getSymbolAlias()}: Skip the canonical security: {symbol.value}")
                    continue
                securityExpiry = roundDownTime(security.expiry, delta=timedelta(days=1))
                rolloverDate = roundDownTime(security.expiry - timedelta(self.futureRolloverDays), delta=timedelta(days=1))
                currentDate = roundDownTime(getAlgoTime(), delta=timedelta(days=1))
                log(f"{self.getSymbolStrAlias()}: securityExpiry={securityExpiry}, rolloverDate={rolloverDate}, currentDate={currentDate}, "
                    f"isNotInvested={isNotInvested(security.symbol)}.", self.verbose)
                if rolloverDate <= currentDate and isNotInvested(security.symbol):
                    log(f"{self.getSymbolStrAlias()}: Will remove the security expiring in {self.futureRolloverDays} days: {security.symbol.value}.")
                    self.expiredSecurity = security
                    self.manageExpiredSecurity()
                    continue
            if not thisSecurity:
                thisSecurity = security
                log(f"{self.getSymbolStrAlias()}: #1. thisSecurity={printSecurity(thisSecurity)}, nextSecurity={printSecurity(nextSecurity)}.")
            elif not nextSecurity:
                nextSecurity = security  # Pick the second closed (front month) security
                log(f"{self.getSymbolStrAlias()}: #2. thisSecurity={printSecurity(thisSecurity)}, nextSecurity={printSecurity(nextSecurity)}.")
            elif thisSecurity.expiry > security.expiry:
                nextSecurity = thisSecurity  # Reserve as the second closed (front month) security!
                thisSecurity = security  # Pick the closest (front month) security!
                log(f"{self.getSymbolStrAlias()}: #3. thisSecurity={printSecurity(thisSecurity)}, nextSecurity={printSecurity(nextSecurity)}.")

        # Do nothing if thisSecurity is None, Stop Algo only when manual intervene required!
        if thisSecurity is not None:
            self.nextSecurity = nextSecurity  # Save it for daily manageExpiredSecurity.
            if isDerivative(thisSecurity.type):
                if self.contract != thisSecurity:
                    self.contract = thisSecurity
                    log(f"{self.getSymbolStrAlias()}: #4. contract={printSecurity(self.contract)}, "
                        f"thisSecurity={printSecurity(thisSecurity)}, "
                        f"nextSecurity={printSecurity(self.nextSecurity)}.")
                    self.addSecurity(self.contract)
                    log(f"{self.getSymbolStrAlias()}: Use contract: symbol={cleanSymbolValue(thisSecurity.symbol)}, invested={thisSecurity.invested}, "
                        f"price={thisSecurity.price}, volume={thisSecurity.volume}, openInterest={thisSecurity.open_interest}, "
                        f"expiry={thisSecurity.expiry.strftime(LIGlobal.minuteFormat)}, "
                        f"{'strikePrice=' + str(thisSecurity.strike_price) + ', ' if isOption(thisSecurity.type) else ''}"
                        f"{'marketPrice=' + str(thisSecurity.underlying.price) + ', ' if isOption(thisSecurity.type) else ''}"
                        f"nextSecurity={cleanSymbolValue(nextSecurity.symbol) if nextSecurity else None}.")
                self.manageExpiredSecurity()
            else:
                if self.security and self.security != thisSecurity:
                    self.removeSecurity(self.security)  # Remove expired/existing security first!
                self.security = thisSecurity
                self.addSecurity(self.security)
                log(f"{self.getSymbolStrAlias()}: Use security: symbol={thisSecurity.symbol.value}, invested={thisSecurity.invested}, "
                    f"price={thisSecurity.price}, volume={thisSecurity.volume}, openInterest={thisSecurity.open_interest}.")

    def removeSecurities(self, removedSecurities: list[Security]):
        # Log matched security for verification purpose
        if removedSecurities:
            log(f"{self.getSymbolStrAlias()}: Removing securities: {printSecurities(removedSecurities)}.")

        if self.isOption() and self.contract:
            log(f"{self.getSymbolAlias()}: Skipped removing option contract as it should be managed within the strategy!")
            return  # Abort, managed within strategy

        for security in removedSecurities:
            if (self.contract if isDerivative(security.type) else self.security) == security:
                alert(f"{self.getSymbolAlias()}: Failed to manage expired security, please switch over to next security!")
                getAlgo().quit("Quit algorithm on EXPIRED SECURITY!")
                return  # Quit execution immediately!
                # if security != self.nextSecurity:
                #     self.enableTempTradable()
                #     self.manageExpiredSecurity()
                #     self.disableTempTradable()
                # else:
                #     alert(f"{self.getSymbolStrAlias()}: Failed to manage expired security, please switch over to next security!")
                #     getQcAlgo().quit("Quit algorithm on EXPIRED SECURITY!")
                #     return
            self.removeSecurity(security)
            # Will be reset by new added security later
            if self.security and security.symbol == self.security.symbol:
                self.security = None
            if self.contract and security.symbol == self.contract.symbol:
                self.contract = None
