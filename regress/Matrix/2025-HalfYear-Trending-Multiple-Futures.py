from AlgorithmImports import *
from core.LIAlgorithm import *


class LifelongInvestorMain(LIAlgorithm):

    def initialize(self):
        super().initialize()
        setAlgoName("LifelongInvest")
        setAccountOwner("Lifelong Investor")
        # startBenchmark("SPY", date(2025, 8, 29), 628557.04, 600000.00)
        # setIbkrReportKey("30157805795961367017216", "1269879")
        # setPortfolioRepute("Staircase Project Private Fund")
        addNotifySetting(LINotifyType.TELEGRAM, "-609042762")  # LIATS Live
        addAlertSetting(LINotifyType.EMAIL, "lifelonginvestorllc@gmail.com")
        # liquidateAndStopTrading() # Liquidate all strategies in emergency!
        # replicateMetadataFrom(18995218)  # Replicate metadata from this project
        self.settings.liquidate_enabled = False  # Enable for company trading account

        # Backtest settings
        self.set_cash(300_000)
        self.set_start_date(date(2025, 1, 1))
        self.set_end_date(date(2025, 7, 1))

        self.futureGridTrading_Gold_Trend_Indicator()
        self.futureGridTrading_Nasdaq_Trend_Indicator()

    def futureGridTrading_Gold_Trend_Indicator(self):
        amplifier = 4  # Amplify invest amount by n times! Adjust based on win rate!
        configs = {
            LIConfigKey.aliasName: "GoldTrend",
            # LIConfigKey.monitorPeriod: (5, LIResolution.MINUTE),
            LIConfigKey.monitorPeriod: (1, LIResolution.HOUR),
            LIConfigKey.indicatorPeriod: (1, LIResolution.DAY),
            LIConfigKey.futureRolloverDays: 35,  # Rolling 30+ days before expiry often improves performance because of liquidity, spreads, and carry costs.
            LIConfigKey.futureExpirationCycles: FutureExpirationCycles.GJMQVZ,
            # LIConfigKey.fetchHistoryBarData: False,
            # LIConfigKey.closeWithStopOrderType: True,
            # LIConfigKey.closeWithMarketOrderType: False,
            LIConfigKey.liquidateOnStopLossAmount: 10_000 * amplifier,
            LIConfigKey.liquidateLossAndRestartTrading: True,
            LIConfigKey.liquidateOnTakeProfitAmount: 5_000 * amplifier,
            # LIConfigKey.liquidateAndStopTrading: True,
            # LIConfigKey.gridRetainOpenedLots: 1,
            LIConfigKey.gridLongLots: 10,
            # LIConfigKey.gridShortLots: 10, # Never short gold in a long run!
            LIConfigKey.gridLotLevelPercent: 0.7,
            LIConfigKey.gridLotLevelAugment: 0.0175,
            LIConfigKey.gridLotStopLossFactor: 11,
            LIConfigKey.gridLotStopProfitFactors: (0.5, 2),
            # LIConfigKey.gridLotPauseAfterStopLoss: True,
            LIConfigKey.gridCancelOrdersAfterClosed: True,
            LIConfigKey.gridTrailingOpenPriceFactor: 1.0,  # Enable for bullish market only to avoid acquiring too many open positions!
            # LIConfigKey.gridRealignOpenPositions: True,
            LIConfigKey.heikinAshiPlies: 1,
            # LIConfigKey.comboTrendingParams: {LIIndicator.EMA: 50},
            LIConfigKey.comboTrendingParams: {LIIndicator.WEEKLY: 1},
            LIConfigKey.staticTradingSignals: weeklyTrendingSignals[Futures.Metals.MICRO_GOLD],
            LIConfigKey.gridInitializeSession: True,  # Be careful! (mostly used in backtest)
        }
        investAmount = LIInvestAmount(lotQuantity=1 * amplifier)
        self.liStrategies.append(LIFutureGridTradingContrarian(Futures.Metals.MICRO_GOLD, investAmount, **configs))

    def futureGridTrading_Nasdaq_Trend_Indicator(self):
        amplifier = 3  # Amplify invest amount by n times!
        configs = {
            LIConfigKey.aliasName: "NasdaqTrend",
            # LIConfigKey.verbose: True,
            # LIConfigKey.monitorPeriod: (5, LIResolution.MINUTE),  # Not always better!
            LIConfigKey.monitorPeriod: (1, LIResolution.HOUR),
            LIConfigKey.indicatorPeriod: (1, LIResolution.DAY),
            # LIConfigKey.marketBias: LIMarketBias.BEARISH,
            # LIConfigKey.marketBias: LIMarketBias.BULLISH,
            # LIConfigKey.extendedMarketHours: True,
            # LIConfigKey.extendDataBarStream: True,
            # LIConfigKey.openWithMarketOrderType: False,
            # LIConfigKey.closeWithMarketOrderType: False,
            # LIConfigKey.closeWithStopOrderType: True,
            # LIConfigKey.plotDefaultChart: False,  # Not plot Price and Filled
            # LIConfigKey.gridHeikinAshiPlies: 1, # Performs better without HeikinAshi
            # LIConfigKey.enableLimitMarketOrder: True,
            # LIConfigKey.gridNoMoreOpenOrders: True,
            # LIConfigKey.disableBuyingPowerModel: True,
            LIConfigKey.liquidateOnStopLossAmount: 10_000 * amplifier,  # Better for volatile market
            LIConfigKey.liquidateLossAndRestartTrading: True,
            LIConfigKey.liquidateOnTakeProfitAmount: 10_000 * amplifier,  # Better for volatile market
            LIConfigKey.gridLongLots: 10,  # 10
            LIConfigKey.gridShortLots: 10,  # 10
            LIConfigKey.gridLotLevelPercent: 0.60,
            LIConfigKey.gridLotLevelAugment: 0.015,  # Perform better in a long run with volatile market
            LIConfigKey.gridLotStopLossFactor: 11,
            LIConfigKey.gridLotStopProfitFactors: (0.5, 2),
            # LIConfigKey.gridLotPauseAfterStopLoss: True,
            LIConfigKey.gridCancelOrdersAfterClosed: True,
            LIConfigKey.gridTrailingOpenPriceFactor: 1.0,  # Enable for bullish market only to avoid acquiring too many open positions!
            # LIConfigKey.gridLotStopProfitFactors: (0.5, 1),
            # LIConfigKey.gridLotPauseAfterProfit: True, # Test out why it's better
            # LIConfigKey.gridLotPauseAfterStopLoss: True, # Test out why it's better
            # LIConfigKey.gridLotCloseUponTradeInsight: True,
            # LIConfigKey.gridLotOpenUponTradeInsight: True,
            # LIConfigKey.gridRestartIfAllLotsPaused: False,
            # LIConfigKey.gridCancelOrdersAfterClosed: True,
            # LIConfigKey.gridCloseCounterpartLots: False,
            # LIConfigKey.gridRealignOpenPositions: True,
            # LIConfigKey.gridFixLeakingPositions: True,
            # LIConfigKey.gridResetLotsMetadata: True,
            LIConfigKey.heikinAshiPlies: 3,  # Better with EMA, no impact to WEEKLY
            # LIConfigKey.comboTrendingParams: {LIIndicator.EMA: 50},
            LIConfigKey.comboTrendingParams: {LIIndicator.WEEKLY: 1},
            # LIConfigKey.candlestickBodyTolerance: 0.5,
            LIConfigKey.staticTradingSignals: weeklyTrendingSignals[Futures.Indices.MICRO_NASDAQ_100_E_MINI],
            LIConfigKey.gridInitializeSession: True,  # Be careful!
        }

        investAmount = LIInvestAmount(lotQuantity=1 * amplifier)
        self.liStrategies.append(LIFutureGridTradingContrarian(Futures.Indices.MICRO_NASDAQ_100_E_MINI, investAmount, **configs))


"""
┌────────────────────────────┬──────────────────┬─────────────────────────────┬────────────────┐
│ Statistic                  │ Value            │ Statistic                   │ Value          │
├────────────────────────────┼──────────────────┼─────────────────────────────┼────────────────┤
│ Equity                     │ $686,145.60      │ Fees                        │ -$1,246.59     │
│ Holdings                   │ $1,212,403.50    │ Net Profit                  │ $391,182.45    │
│ Probabilistic Sharpe Ratio │ 98.421%          │ Return                      │ 128.72 %       │
│ Unrealized                 │ $-5,036.85       │ Volume                      │ $81,326,508.00 │
├────────────────────────────┼──────────────────┼─────────────────────────────┼────────────────┤
│ Total Orders               │ 521              │ Average Win                 │ 1.18%          │
│ Average Loss               │ -1.06%           │ Compounding Annual Return   │ 425.689%       │
│ Drawdown                   │ 12.600%          │ Expectancy                  │ 0.491          │
│ Start Equity               │ 300000           │ End Equity                  │ 686145.6       │
│ Net Profit                 │ 128.715%         │ Sharpe Ratio                │ 6.254          │
│ Sortino Ratio              │ 9.635            │ Probabilistic Sharpe Ratio  │ 98.421%        │
│ Loss Rate                  │ 29%              │ Win Rate                    │ 71%            │
│ Profit-Loss Ratio          │ 1.11             │ Alpha                       │ 0              │
│ Beta                       │ 0                │ Annual Standard Deviation   │ 0.372          │
│ Annual Variance            │ 0.139            │ Information Ratio           │ 6.401          │
│ Tracking Error             │ 0.372            │ Treynor Ratio               │ 0              │
│ Total Fees                 │ $1246.59         │ Estimated Strategy Capacity │ $330000000.00  │
│ Lowest Capacity Asset      │ MGC YVB1F0QVMNQ5 │ Portfolio Turnover          │ 103.34%        │
│ Drawdown Recovery          │ 17               │                             │                │
└────────────────────────────┴──────────────────┴─────────────────────────────┴────────────────┘
"""
