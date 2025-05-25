# region imports
from System import *
from core.LICommon import *


# endregion

def sendDailyMetadataAlert():
    LIGlobal.sendDailyMetadataAlert = True


def liquidateAndStopTrading():
    LIDefault.liquidateAndStopTrading = True


def checkDefaultSettings():
    if isLiveMode():
        # NOT working properly as the liquidation could still happen before termination!
        # if LIDefault.gridInitializeSession:
        #     terminate(f"LIDefault.gridInitializeSession should NOT be True for live mode!")
        pass


class LIDefault:
    verbose = False
    aliasName = None
    resolution = LIResolution.MINUTE
    marketBias = LIMarketBias.NEUTRAL
    monitorPeriod = 5
    indicatorPeriod = 60
    # Trading indicator
    signalPeriod = 9
    fastEMAPeriod = 13
    slowEMAPeriod = 47  # 26
    longEMAPeriod = 147
    dailyEMAPeriod = 21
    auxRSIPeriod = 13
    # Hedging indicator
    # signalPeriod = 30  # 21, 22, 26 could be better
    # fastEMAPeriod = 50
    # slowEMAPeriod = 200
    # longEMAPeriod = None
    # dailyEMAPeriod = None
    # auxRSIPeriod = 14
    heikinAshiPlies = None
    addVolumeSeries = False
    plotDefaultChart = True
    isVolatilePeriod = False
    signalSymbolStr = None  # No default!
    signalSecurityType = None  # No default!
    benchmarkSymbolStr = None
    enableAutoRollover = True
    forceExchangeOpen = False
    extendedMarketHours = True
    extendDataBarStream = True
    fetchHistoryBarData = True
    canOpenLongPosition = True
    canOpenShortPosition = True
    futureQuarterly = None  # No default!
    futurePeriodDays = 98
    futureRolloverDays = 1
    futureContractCode = None
    futureContractExpiry = None
    optionRight = None
    putContractCode = None
    callContractCode = None
    optionContractCode = None
    optionContractOTMLevel = 8
    optionMinMaxExpiryDays = [10, 35]
    optionMinMaxStrikeLevel = [-100, +100]  # Out of Money only
    addFutureOptionUniverse = False
    stopLossLevelAmount = None
    stopLossLevelPercent = None
    takeProfitLevelPercent = None
    enableTrailingStopLoss = False
    openWithStopOrderType = False
    openWithMarketOrderType = False
    closeWithStopOrderType = False
    closeWithMarketOrderType = True
    submitStopMarketOrder = False
    submitTrailingStopOrder = False
    updateTrailingStopPrice = False
    dayLossPriceTolerance = 0.98
    dayTradePerOrderPauseMins = 0  # 0 means no pausing
    stopTradingOnInvalidOrders = 10  # 0 means no stopping
    canTradeAtMarketClosingTime = True
    liquidateRemovedSecurity = True
    liquidateAndStopTrading = False
    liquidateWithStopOrderType = False
    liquidateOnMarginCall = False
    liquidateOnFridayClose = False
    liquidateOnReachedPrices = None
    liquidateOnStopLossAmount = None
    liquidateOnStopLossPercent = None
    liquidateOnTakeProfitAmount = None
    liquidateOnTakeProfitAmounts = None
    liquidateOnTakeProfitPercent = None
    liquidateByTrailingProfitPercent = None
    liquidateAtMarketClosingTime = 0  # 0(False), 1(True), 2(Only on Gain), 3(Only on Loss)
    liquidateLossAndPauseTrading = False
    liquidateLossAndRestartTrading = False
    liquidateProfitAndRestartTrading = True
    limitOrderJitterTicks = 3
    limitOrderJitterRatio = 0.001
    enableLimitMarketOrder = False
    limitMarketOrderRetryTimes = 2
    dayOpenGapUpDownPercent = 4
    scalpingWindowStartTime = "09:34"
    scalpingWindowStopTime = "10:11"
    candlestickDojiBodyMaxRatio = 0.0666
    candlestickSpinningTopBodyMaxRatio = 0.333
    shortToLongInverseSymbol = None
    macdIndicatorTolerance = 5  # 5 - 10
    bollingerBandsParams = None  # [(300, 1), (300, 2), (300, 3, LIResolution.HOUR)]
    stochasticComboParams = None  # {"MACD": (12, 26, 5), "RSI": 14, "KDJ": (14, 3, 3), "SRSI": (14, 14, 3, 3)},
    investAmountTierFactors = None  # [4, 3, 2, 1, 1, 2, 3, 4]

    disableBuyingPowerModel = False
    dcaInvestCapital = None
    dcaInvestQuantity = None
    dcaInvestPeriodicity = None
    riskProposeHedgeInsights = False
    riskHedgeOptionExpiryDays = 60
    gridLongLots = 0
    gridShortLots = 0
    gridLongLotsQty = None
    gridShortLotsQty = None
    gridSortSkewedLots = True
    gridHeikinAshiPlies = None
    gridUseTradeInsight = False
    gridBaselinePrice = None  # No default!
    gridLimitStartPrices = None  # No default!
    gridResetStartPrices = None  # No default!
    gridFixedStartPrices = None  # No default!
    gridFixedOpenFromPrices = None  # No default!
    gridBandingStartPrices = False
    gridBandingOpenFromPrices = False
    gridBandingFixedStartBand = None
    gridResetLotsMetadata = False
    gridRolloverCriteria = None
    gridInitializeSession = None
    gridLotMinQuantity = None  # Case by case!
    gridLotLevelAmount = None  # No default!
    gridLotLevelPercent = None  # No default!
    gridLotLevelAugment = 0
    gridLotStopLossFactor = None  # No default!
    gridLotMaxProfitFactor = None  # No default!
    gridLotTakeProfitFactor = 1.0
    gridLotStopProfitFactors = None  # No default!
    gridLotPauseAfterProfit = False
    gridLotPauseAfterStopLoss = False
    gridLotBoostingProfitFactor = None
    gridLotBoostingDesireProfit = False
    gridRestartOnFridayClose = False
    gridRestartIfAllLotsPaused = False
    gridInitOpenedLots = 0  # Disabled
    gridRetainOpenedLots = 0  # Disabled
    gridTradeRetainedLots = False
    gridNoMoreOpenOrders = False
    gridNoMoreCloseOrders = False
    gridMaintainOpenOrders = 1
    gridKeepOpenOrdersApart = False
    gridMaintainCloseOrders = 2  # 5 -> 2 to avoid stressing IB APIs!
    gridKeepStartCloseOrders = 1
    gridFollowAdverseTrend = False
    gridStickToMarketTrend = False
    gridCancelOrdersOnExit = False
    gridNotifyTargetPrices = True
    gridMonitorPeriodFactors = None  # No default!
    gridTransfer2Counterpart = False
    gridCloseCounterpartLots = False
    gridFixLeakingPositions = False
    gridRealignOpenPositions = False
    gridLotsInStopProfitFactor = True
    gridPriceInStopProfitFactor = False
    gridCancelOrdersAfterClosed = False
    gridTrailingOpenPriceFactor = None  # No default!
    gridPauseTradingProfitHours = None
    gridBoostingKeepTrading = False
    gridBoostingTriggerAmount = None  # No Default!
    gridBoostingTriggerPercent = None  # No default!
    gridBoostingMaxHoldQuantity = None  # No Default!
    gridBoostingStopProfitAmounts = None  # No Default!
    gridBoostingStopProfitPercents = None  # No Default!
    gridBoostingTrailingStopQuantity = False
    gridHedgeEnabled = False
    gridHedgeOverLosingLots = None


class LIConfigKey:
    verbose = "verbose"  # Whether to log more details!
    aliasName = "aliasName"  # An easy to recognize name
    resolution = "resolution"  # Resolution of market data requested
    marketBias = "marketBias"  # Forecast market bias to drive indicator
    monitorPeriod = "monitorPeriod"  # The minimum span of time before emitting a consolidated bar
    indicatorPeriod = "indicatorPeriod"  # The minimum span of time before emitting a consolidated bar
    auxRSIPeriod = "auxRSIPeriod"  # Auxiliary RSI (Relative Strength Index) period
    signalPeriod = "signalPeriod"  # Signal smoothing for a MACD line
    fastEMAPeriod = "fastEMAPeriod"  # Fast EMA period for an indicator
    slowEMAPeriod = "slowEMAPeriod"  # Slow EMA period for an indicator
    longEMAPeriod = "longEMAPeriod"  # Long EMA Period for an indicator
    dailyEMAPeriod = "dailyEMAPeriod"  # Daily EMA period for a daily indicator
    heikinAshiPlies = "heikinAshiPlies"  # Use Heikin-Ashi with specific plies to smooth candlestick first
    addVolumeSeries = "addVolumeSeries"  # Whether to add Volume bar at the bottom of the chart
    plotDefaultChart = "plotDefaultChart"  # Whether to plot the default chart with market/order prices
    isVolatilePeriod = "isVolatilePeriod"  # Whether the signal symbol is in a high volatile period, e.g. 3x Leveraged ETF
    signalSymbolStr = "signalSymbolStr"  # Alternative signal symbol's string to populate the indicator
    signalSecurityType = "signalSecurityType"  # Alternative signal symbol's security type for the indicator
    benchmarkSymbolStr = "benchmarkSymbolStr"  # Add a relevant benchmark for computing statistics of the algorithm to the specified ticker
    enableAutoRollover = "enableAutoRollover"  # Rollover metadata and holdings (with market order) for this removed/expired contract to next one
    forceExchangeOpen = "forceExchangeOpen"  # Override or force exchange open to be True or False for this security until disabled!
    extendedMarketHours = "extendedMarketHours"  # Extended market hours could mean trading 24hrs around the clock
    extendDataBarStream = "extendDataBarStream"  # Simulate market data bar streaming out of the regular market timeframe and make it always beating for this security
    fetchHistoryBarData = "fetchHistoryBarData"  # Stop fetching history bar data if not required for this strategy, in order to avoid the error: No market data permissions for CME FUT...
    canOpenLongPosition = "canOpenLongPosition"  # Indicate whether allow to open Long position
    canOpenShortPosition = "canOpenShortPosition"  # Indicate whether allow to open Short position
    futureQuarterly = "futureQuarterly"  # Contract Quarterly Cycle: Expirations in March, June, September, December (third month), will calculate by futurePeriodDays if not specified
    futurePeriodDays = "futurePeriodDays"  # Contract's period term, could be Weekly (~7 days), Monthly (~30 days), Quarterly (~90 days), Yearly (~365 days)
    futureRolloverDays = "futureRolloverDays"  # Contract should be rolled over within these days, make sure contract.Expiry - timedelta(self.futureRolloverDays) > currentTime
    futureContractCode = "futureContractCode"  # Optional, within futurePeriodDays, pick a future contract identifier for this strategy (e.g. MNQ15U23, CL22K24)
    futureContractExpiry = "futureContractExpiry"  # Optional, within futurePeriodDays, pick a future contract expiry date for this strategy (e.g. date(2024, 9, 20))
    optionRight = "optionRight"  # Options right could be either put or call, but NOT both! You can combine a put strategy and a call strategy to trade on both sides
    putContractCode = "putContractCode"  # Optional, specify a preselected put option contract identifier for this strategy
    callContractCode = "callContractCode"  # Optional, specify a preselected call option contract identifier for this strategy
    optionContractCode = "optionContractCode"  # Optional, specify a preselected option contract identifier for this strategy
    optionContractOTMLevel = "optionContractOTMLevel"  # Which level of contract (Out of The Money) to pick? 10 means the 10th strike price
    optionMinMaxExpiryDays = "optionMinMaxExpiryDays"  # Options that expire within a range of dates relative to the current day, e.g. [25, 35] to pick options around 1 month
    optionMinMaxStrikeLevel = "optionMinMaxStrikeLevel"  # Options with strike level relative to the underlying price. For example, say the underlying price is $302 and there are strikes at every $5. If you set minStrike to -1 and maxStrike to 1, LEAN selects the contracts that have a strike of $300 or $305.
    addFutureOptionUniverse = "addFutureOptionUniverse"  # Add a universe of Future Option right after added a Future universe, in the initialize method
    stopLossLevelAmount = "stopLossLevelAmount"  # A stop-loss (SL) amount level is the predetermined price of an asset, at which the position gets closed in order to limit an investor's loss on this position.
    stopLossLevelPercent = "stopLossLevelPercent"  # A stop-loss (SL) percent level is the predetermined price of an asset, at which the position gets closed in order to limit an investor's loss on this position.
    takeProfitLevelPercent = "takeProfitLevelPercent"  # A take-profit (TP) level is a preset price at which traders liquidate and close a profitable position. (e.g. 2.5=2.5%)
    openWithStopOrderType = "openWithStopOrderType"  # Leverage stop limit/market order or trailing stop order to open positions, please mind the live market slippage, might not efficient as market order. NOTE: stop limit order not working for extend market time!
    openWithMarketOrderType = "openWithMarketOrderType"  # Use (limit) market order to open positions whenever it's suitable/applicable, please mind the live market slippage
    closeWithStopOrderType = "closeWithStopOrderType"  # Leverage stop limit/market order or trailing stop order to close positions, please mind the live market slippage, might not efficient as market order. NOTE: stop limit order not working for extend market time!
    closeWithMarketOrderType = "closeWithMarketOrderType"  # Use (limit) market order to close positions, please mind the live market slippage
    enableTrailingStopLoss = "enableTrailingStopLoss"  # Manage a stop limit/market order with dynamically calculated (by Algo or Brokerage) trailing stop price
    submitStopMarketOrder = "submitStopMarketOrder"  # Submit stop market order directly, use Brokerage to submit market price once triggered the stop price
    submitTrailingStopOrder = "submitTrailingStopOrder"  # Submit trailing stop (limit) order directly, use Brokerage to manage the trailing stop price
    updateTrailingStopPrice = "updateTrailingStopPrice"  # Whether to set/use stop price while submitting trailing stop order to Brokerage
    dayLossPriceTolerance = "dayLossPriceTolerance"  # Day loss price gap allowance threshold
    dayTradePerOrderPauseMins = "dayTradePerOrderPauseMins"  # Increase waiting/pausing time exponentially based on dayTradeOrderCount
    stopTradingOnInvalidOrders = "stopTradingOnInvalidOrders"  # Stop trading after reached/exceeded the max number of invalid orders
    canTradeAtMarketClosingTime = "canTradeAtMarketClosingTime"  # Indicate whether allow to trade at market closing time
    liquidateAndStopTrading = "liquidateAndStopTrading"  # Liquidate this invested security and pause/stop trading for now, wait for next redeploy!
    liquidateLossAndPauseTrading = "liquidateLossAndPauseTrading"  # Liquidate loss and pause the trading session until market revert back to exceed stopped loss price!
    liquidateLossAndRestartTrading = "liquidateLossAndRestartTrading"  # Liquidate loss and restart the trading session with fresh settings!
    liquidateProfitAndRestartTrading = "liquidateProfitAndRestartTrading"  # Liquidate profit and restart the trading session with fresh settings!
    liquidateRemovedSecurity = "liquidateRemovedSecurity"  # Liquidate the removed security automatically in position manager by default!
    liquidateOnMarginCall = "liquidateOnMarginCall"  # Liquidate this security's all positions and quit algorithm upon receiving the first margin call! Need to study current market situation and decide next step.
    liquidateOnFridayClose = "liquidateOnFridayClose"  # Liquidate managed/invested securities at the end of Friday's market time.
    liquidateOnReachedPrices = "liquidateOnReachedPrices"  # Liquidate if current session's either side's reference price reached specified price, and then restart or redeploy!
    liquidateOnStopLossAmount = "liquidateOnStopLossAmount"  # Liquidate if current session's combined loss reached this amount! (e.g. 10_000), and then restart or redeploy!
    liquidateOnStopLossPercent = "liquidateOnStopLossPercent"  # Liquidate if current session's combined loss reached this percent! (e.g. 10=10%) and the restart or redeploy!
    liquidateOnTakeProfitAmount = "liquidateOnTakeProfitAmount"  # Liquidate if current session's combined profit reached this amount, and then restart or redeploy! (e.g. 10_000=$10,000)
    liquidateOnTakeProfitAmounts = "liquidateOnTakeProfitAmounts"  # Liquidate if current session's combined profit reached this side's amount, and then restart or redeploy! (e.g. {LIGridSide.BTU:1_000, LIGridSide.STD: 2_000}})
    liquidateOnTakeProfitPercent = "liquidateOnTakeProfitPercent"  # Liquidate if current session's combined profit reached this percent, and then restart or redeploy! (e.g. 10=10%)
    liquidateWithStopOrderType = "liquidateWithCloseOrderType"  # Liquidate with stop limit/market order or trailing stop order, please mind the live market slippage, might not efficient as market order. NOTE: stop limit order not working for extend market time!
    liquidateByTrailingProfitPercent = "liquidateByTrailingProfitPercent"  # An extra trailing stop percent applied on top of above liquidate amount/percent, allow specific percent of drawback in favor of maximizing the profit.
    liquidateAtMarketClosingTime = "liquidateAtMarketClosingTime"  # Liquidate managed/invested securities at around marketClosingTime. Value: 0(False), 1(True), 2(Only on Gain), 3(Only on Loss)
    limitOrderJitterTicks = "limitOrderJitterTicks"  # Allow limit order to jitter by specified ticks to soft or hard the order price
    limitOrderJitterRatio = "limitOrderJitterRatio"  # Allow limit order to jitter by specified ratio to soft or hard the order price
    enableLimitMarketOrder = "enableLimitMarketOrder"  # Try limit order a few times before submitting a market order at last
    limitMarketOrderRetryTimes = "limitMarketOrderRetryTimes"  # 0 means no retry, but will still submit first limit order
    disableBuyingPowerModel = "disableBuyingPowerModel"  # Disable validations of default buying power model, skip checking order margin!
    dayOpenGapUpDownPercent = "dayOpenGapUpDownPercent"  # Market open gap percent, positive for up and negative for down (e.g. 2.5=2.5%)
    scalpingWindowStartTime = "scalpingWindowStartTime"  # Doing scalping strategy within this time window
    scalpingWindowStopTime = "scalpingWindowStopTime"  # Doing scalping strategy within this time window
    candlestickAvgBodySize = "candlestickAvgBodySize"  # Calculate dynamically if not specified
    candlestickAvgWickSize = "candlestickAvgWickSize"  # Calculate dynamically if not specified
    candlestickDojiBodyMaxRatio = "candlestickDojiBodyMaxRatio"  # 0.01=1%, Less than or equals to this percent of average body size
    candlestickSpinningTopBodyMaxRatio = "candlestickSpinningTopBodyMaxRatio"  # 0.1=10%, Not Doji, but less than or equals to this percent of average body size
    shortToLongInverseSymbol = "shortToLongInverseSymbol"  # Never short, instead to long inverse symbol
    macdIndicatorTolerance = "macdIndicatorTolerance"  # MACD indicator threshold for histogram or divergence
    bollingerBandsParams = "bollingerBandsParams"  # A list of bollinger bands params which can specify the period of moving average, the standard deviation (the distance between middle and upper or lower bands) and resolution (daily by default).
    stochasticComboParams = "stochasticComboParams"  # Specify the params for all supported indicators in map, e.g. {"EMA": 200, "MACD": (12, 26, 5), "RSI": 14, "KDJ": (14, 3, 3), "SRSI": (14, 14, 3, 3)}
    investAmountTierFactors = "investAmountTierFactors"  # A list of factors for each tier/band, usually equals to bollingerBandsParams * 2 + 1. Apply to contrarian strategy, trade more upon outer/higher band, in order to leverage mean reversion.
    dcaInvestCapital = "dcaInvestCapital"  # Execute Dollar-Cost Averaging (DCA), invest with a specified capital.
    dcaInvestQuantity = "dcaInvestQuantity"  # Execute Dollar-Cost Averaging (DCA), invest with a specified quantity.
    dcaInvestPeriodicity = "dcaInvestPeriodicity"  # Execute Dollar-Cost Averaging (DCA), invest with a specified periodicity.
    riskProposeHedgeInsights = "riskProposeHedgeInsights"  # Sort out what/which options to acquire in order to hedge current positions.
    riskHedgeOptionExpiryDays = "riskHedgeOptionExpiryDays"  # The proposed hedge option contract expiry days should be greater than this.
    gridMode = "gridMode"  # Grid mode decides the trading behavior and strategy
    gridLongLots = "gridLongLots"  # Number of grid lots in a session which can open long position (e.g. 10)
    gridShortLots = "gridShortLots"  # Number of grid lots in a session which can open short position (e.g. 10)
    gridLongLotsQty = "gridLongLotsQty"  # Optional, specify each long lot's quantity to overwrite the default lotQuantity (e.g. [1, 1, 2, 2, 3, 3])
    gridShortLotsQty = "gridShortLotsQty"  # Optional, specify each short lot's quantity to overwrite the default lotQuantity (e.g. [1, 1, 2, 2, 3, 3])
    gridSortSkewedLots = "gridSortSkewedLots"  # Sort skewed lots by filled/open price automatically so that they will be closed in order as well
    gridHeikinAshiPlies = "gridHeikinAshiPlies"  # Use Heikin Ashi with specific plies to smooth the trading bars, hence the high/low/open/close prices
    gridUseTradeInsight = "gridUseTradeInsight"  # Use trade insight (market bias or emitted by indicators) to decide open/close orders
    gridStartPrices = "gridStartPrices"  # Current grid start prices for trading, to be updated dynamically as per strategy
    gridBaselinePrice = "gridBaselinePrice"  # Baseline prices can be used to adjust the lot level amount or liquidate amount dynamically: amount = amount * (marketPrice / baselinePrice)
    gridLimitStartPrices = "gridLimitStartPrices"  # Limit start prices exceeding the boundary/stop prices, make sure Long lot's startPrice <= maxHighPrice and Short lot's startPrice >= minLowPrice. (e.g. {LIGridSide.BTD: 12400.0})
    gridResetStartPrices = "gridResetStartPrices"  # Need to deploy twice for live mode! first to reset start prices and quit algorithm, then remove it and redeploy to continue. (e.g. {LIGridSide.BTD: 12346.0} or {} to use market price)
    gridFixedStartPrices = "gridFixedStartPrices"  # Always use this fixed start prices! never dynamically adjusted start prices based on market price, (e.g. {LIGridSide.BTD: 12346.0})
    gridFixedOpenFromPrices = "gridFixedOpenFromPrices"  # Start placing open orders from the specified prices, so that we can wait patiently for market to reach a certain price before long or short.
    gridBandingStartPrices = "gridBandingStartPrices"  # Keep adjusting the fixed/limit start prices dynamically according to bollinger bands indicator, so to follow the market trend closely on some loss.
    gridBandingOpenFromPrices = "gridBandingOpenFromPrices"  # Start opening lot's positions from the dynamic prices, so that we can wait patiently for market to reach a certain price before long or short.
    gridBandingFixedStartBand = "gridBandingFixedStartBand"  # Have the fixed (relatively) start prices to follow a specified bollinger band. Otherwise, will apply self-driven dynamic band tiers according to market trend.
    gridResetLotsMetadata = "gridResetLotsMetadata"  # Simply remove <Prefix>/gridLotsMetadata (could be skewed) in order to start over with current session and reset filled open prices and positions.
    gridRolloverCriteria = "gridRolloverCriteria"  # Algo could fail to figure out the rollover criteria, It's to specify contract, how many grid lots, invested quantity, profit loss to rollover. (e.g. (MNQ21H25, 3, 3 * 2, -10000))
    gridInitializeSession = "gridInitializeSession"  # Need to deploy twice for live mode! first to initialize a new session, liquidate open positions, delete metadata and reset all grid lots, then remove it and redeploy to continue!
    gridLotMinQuantity = "gridLotMinQuantity"  # This is required for LIInvestAmount(maxHolding=?) so that we can avoid submitting small size of orders!
    gridLotLevelAmount = "gridLotLevelAmount"  # Calculate Arithmetic open price for each grid lot
    gridLotLevelPercent = "gridLotLevelPercent"  # Calculate Geometric open price for each grid lot
    gridLotLevelAugment = "gridLotLevelAugment"  # Augment each grid lot level: gridLotLevelPercent/Amount (+/-)= gridLotLevelAugment * (abs(lotId) - 1)
    gridLotStopLossFactor = "gridLotStopLossFactor"  # Stop loss factor for each grid lot, stopLossPrice = lotOpenPrice * (1 (+/-) gridLotLevelPercent/Amount * gridLotStopLossFactor)
    gridLotMaxProfitFactor = "gridLotMaxProfitFactor"  # At what factor to close the trailing stop profit limit order right away and realize the profit, stopPrice = marketPrice * (1 (+/-) gridLotLevelPercent/Amount * gridLotMaxProfitFactor)
    gridLotTakeProfitFactor = "gridLotTakeProfitFactor"  # Apply on top of Lot level percent/amount. e.g. profitTargetPrice = lotOpenPrice * (1 (+/-) gridLotLevelPercent/Amount * gridLotTakeProfitFactor)
    gridLotStopProfitFactors = "gridLotStopProfitFactors"  # A pair of (min, max) factors, the deeper lot, the bigger factor. This is the buffer for trailing stop profit limit order, will follow the market ramping up until fall back to this stop price: stopPrice = marketPrice * (1 (+/-) gridLotLevelPercent/Amount * dynamicStopProfitFactor)
    gridLotPauseAfterProfit = "gridLotPauseAfterProfit"  # Pause trading for this lot once got a profit/gain, until restart a new grid trading session.
    gridLotPauseAfterStopLoss = "gridLotPauseAfterStopLoss"  # Pause trading for this lot once got a stop loss, until restart a new grid trading session.
    gridLotBoostingProfitFactor = "gridLotBoostingProfitFactor"  # Fill more if the lot reached the specified profit factor (e.g. percent = gridLotLevelPercent (gridLotLevelAugment|gridLotStopProfitFactors) * factor), it's a way to blend momentum into contrarian.
    gridLotBoostingDesireProfit = "gridLotBoostingDesireProfit"  # Prefer to take profit earlier by setting dynamic stop profit down to the take profit price. But it could reduce the potential profit.
    gridRestartOnFridayClose = "gridRestartOnFridayClose"  # Restart grid session at the end of Friday's market time, will reset start prices and start a new session!
    gridRestartIfAllLotsPaused = "gridRestartIfAllLotsPaused"  # Restart a new grid trading session after all lots (the same long or short side) were paused.
    gridFollowAdverseTrend = "gridFollowAdverseTrend"  # Once the grid is fully filled with all long/short lots, allow to push/force the start prices to further down/up, therefore sell some losing positions in order to catch up with the even unfavorable/adverse trending!
    gridStickToMarketTrend = "gridStickToMarketTrend"  # Have grid trading lots stick to or align with current market price, always follow the market trend closely in favor of more orders to be filled/executed.
    gridInitOpenedLots = "gridInitOpenedLots"  # Adjust start prices dynamically to initiate certain long(positive)/short(negative) filled/opened positions at the beginning and continue the normal trading behavior
    gridRetainOpenedLots = "gridRetainOpenedLots"  # Adjust start prices dynamically to retain certain long(positive)/short(negative) filled/opened positions all the time until been reset to normal behavior
    gridTradeRetainedLots = "gridTradeRetainedLots"  # Set as false to avoid trading retained open lots in favor of reducing trades
    gridNoMoreOpenOrders = "gridNoMoreOpenOrders"  # No more open orders, use this flag to close all open positions and stop trading on this security!
    gridNoMoreCloseOrders = "gridNoMoreCloseOrders"  # No more close orders, use this flag to stop placing close orders on this security!
    gridKeepOpenOrdersApart = "gridKeepOpenOrdersApart"  # Avoid filling multiple open orders with almost the same prices during a big swing market
    gridMaintainOpenOrders = "gridMaintainOpenOrders"  # Maintain how many active/open order tickets on each side at a time, can select 1, 2 or 3. 2 means maintain 2 open orders for both Long and Short lots, total 4!
    gridMaintainCloseOrders = "gridMaintainCloseOrders"  # Maintain how many active/close order tickets on either side at a time, can select between 2 and 10. 5 means maintain 5 close orders for either Long and Short lots, first 4 lots + always last lot!
    gridKeepStartCloseOrders = "gridKeepStartCloseOrders"  # Keep how many active/close order tickets (starts from the start lot) within gridMaintainCloseOrders. Always starts/counts from the first long lot or the first short lot.
    gridCancelOrdersOnExit = "gridCancelOrdersOnExit"  # Cancel all open/active order tickets at the end of Algorithm and recreate them after redeployed!
    gridNotifyTargetPrices = "gridNotifyTargetPrices"  # Notify grid target prices layout, to review each lot's open and close target prices.
    gridMonitorPeriodFactors = "gridMonitorPeriodFactors"  # Apply different monitor periods (monitorPeriod * factor) on each grid sides. (e.g. {LIGridSide.STD: 1, LIGridSide.BTU: 12})
    gridTransfer2Counterpart = "gridTransfer2Counterpart"  # Allow to transfer the OPEN order event to it's counterpart lot as a CLOSE order event, to simulate a FIFO transaction.
    gridCloseCounterpartLots = "gridCloseCounterpartLots"  # Allow to close all counterpart lots when this trading side filled the first open order ticket within a contrarian strategy.
    gridFixLeakingPositions = "gridFixLeakingPositions"  # Will buy/sell opposite amount of leaking positions to restore the grid in a good shape.
    gridRealignOpenPositions = "gridRealignOpenPositions"  # While starting grid trading session, force to recalculate the start prices to retain all open positions, also realign/reset/assign the filled open positions to grid lots evenly.
    gridLotsInStopProfitFactor = "gridLotsInStopProfitFactor"  # Calculate stop profit factor based on the total filled lots, in an addition to each lot id. The more lots filled the bigger factor, but still within gridLotStopProfitFactors!
    gridPriceInStopProfitFactor = "gridPriceInStopProfitFactor"  # Adjust stop profit factor based on the distance between market price and start price, the bigger distance the bigger factor for contrarian mode, opposite for momentum mode, but still within gridLotStopProfitFactors!
    gridCancelOrdersAfterClosed = "gridCancelOrdersAfterClosed"  # Cancel open orders right after closed a lot in favor of filling back open orders/positions sooner/easier in contrarian mode.
    gridTrailingOpenPriceFactor = "gridTrailingOpenPriceFactor"  # Limit the lot's open price distance from market price in favor of filling back open orders/positions sooner/easier in contrarian mode, could be very aggressive if set to a smaller factor.
    gridPauseTradingProfitHours = "gridPauseTradingProfitHours"  # Pause trading for specified hours after liquidated and took specified amount of profit or above. e.g. (10_000, 3 * 24)
    gridBoostingKeepTrading = "gridBoostingKeepTrading"  # Do not stop trading after triggered the stop profit criteria and liquidated all positions
    gridBoostingTriggerAmount = "gridBoostingTriggerAmount"  # Acquire more positions once reached this profit amount and hold until trigger trailing stop profit, longSideAmount = marketPrice - avgFilledPrice, shortSideAmount = avgFilledPrice - marketPrice
    gridBoostingTriggerPercent = "gridBoostingTriggerPercent"  # Acquire more positions once reached this profit percent and hold until trigger trailing stop profit, percent = aboveAmount / marketPrice * 100
    gridBoostingMaxHoldQuantity = "gridBoostingMaxHoldQuantity"  # Max holding quantity within the margin sufficiency, then wait until trigger the trailing stop profit criteria
    gridBoostingStopProfitAmounts = "gridBoostingStopProfitAmounts"  # A range of (first, last) stop profit amounts, distributed based on holding quantity: stopProfitPrice = marketPrice +/- abs(marketPrice - gainedProfitAmount)
    gridBoostingStopProfitPercents = "gridBoostingStopProfitPercents"  # A range of (first, last) stop profit percents, distributed based on holding quantity: stopProfitPrice = marketPrice +/- abs(marketPrice - averagePrice) * stopProfitPercent / 100
    gridBoostingTrailingStopQuantity = "gridBoostingTrailingStopQuantity"  # Submit trailing stop order to take profit when the holding positions exceeds the specified quantity, it is NOT guaranteed performing better than the market order with frequent checking.
    gridHedgeEnabled = "gridHedgeEnabled"  # Enable hedging mode, which will monitor counterpart's loss, hedge it with trading agilely.
    gridHedgeOverLosingLots = "gridHedgeOverLosingLots"  # Start hedging behavior if counterpart side has over the specified losing lots.
