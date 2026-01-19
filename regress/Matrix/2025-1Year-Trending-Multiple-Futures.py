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
        self.set_end_date(date(2026, 1, 1))

        self.futureGridTrading_Gold_Trend_Indicator()
        self.futureGridTrading_Nasdaq_Trend_Indicator()

    def futureGridTrading_Gold_Trend_Indicator(self):
        amplifier = 3  # Amplify invest amount by n times! Adjust based on win rate!
        configs = {
            LIConfigKey.aliasName: "GoldTrend",
            # LIConfigKey.monitorPeriod: (5, LIResolution.MINUTE),
            LIConfigKey.monitorPeriod: (1, LIResolution.HOUR),
            LIConfigKey.indicatorPeriod: (1, LIResolution.DAY),
            LIConfigKey.futureRolloverDays: 35,  # Rolling 30+ days before expiry often improves performance because of liquidity, spreads, and carry costs.
            LIConfigKey.futureExpirationCycles: FutureExpirationCycles.GJMQVZ,
            # LIConfigKey.marketBias: LIMarketBias.BEARISH,
            # LIConfigKey.marketBias: LIMarketBias.BULLISH,
            # LIConfigKey.fetchHistoryBarData: False,
            # LIConfigKey.closeWithStopOrderType: True,
            # LIConfigKey.closeWithMarketOrderType: False,
            LIConfigKey.liquidateBaselinePrice: 4000,
            LIConfigKey.liquidateOnStopLossAmount: 20_000 * amplifier,
            # LIConfigKey.flipSignalAtLiquidateFactor: 0.5,
            # LIConfigKey.liquidateLossAndLimitTrading: True,
            LIConfigKey.liquidateLossAndRestartTrading: True,
            LIConfigKey.liquidateLossAndBackfillEquity: "UGL",
            LIConfigKey.liquidateOnTakeProfitAmount: 15_000 * amplifier,
            # LIConfigKey.liquidateAndStopTrading: True,
            # LIConfigKey.gridNoMoreOpenOrders: True,
            # LIConfigKey.gridNoMoreCloseOrders: True,
            LIConfigKey.gridLongLots: 10,
            # LIConfigKey.gridShortLots: 10,  # Never short gold in a long run!
            LIConfigKey.gridLotLevelPercent: 1.0,
            # LIConfigKey.gridLotLevelAugment: 0.0175,
            LIConfigKey.gridLotStopLossFactor: 11,
            LIConfigKey.gridLotStopProfitFactors: (0.5, 2),
            LIConfigKey.gridLotPauseAfterStopLoss: True,
            LIConfigKey.gridCancelOrdersAfterClosed: True,
            LIConfigKey.gridTrailingOpenPriceFactor: 1.0,  # Enable for bullish market only to avoid acquiring too many open positions!
            # LIConfigKey.gridRealignOpenPositions: True,
            LIConfigKey.heikinAshiPlies: 3,
            # LIConfigKey.comboTrendingParams: {LIIndicator.EMA: 50},
            LIConfigKey.comboTrendingParams: {LIIndicator.WEEKLY: 1},
            # LIConfigKey.staticTrendingSignals: weeklyTrendingSignals[Futures.Metals.MICRO_GOLD],
            LIConfigKey.pullTrendingSignalsApi: "api/signals",
            LIConfigKey.gridInitializeSession: True,  # Be careful! (mostly used in backtest)
        }
        investAmount = LIInvestAmount(lotQuantity=1 * amplifier)
        self.liStrategies.append(LIFutureGridTradingContrarian(Futures.Metals.MICRO_GOLD, investAmount, **configs))

    def futureGridTrading_Nasdaq_Trend_Indicator(self):
        amplifier = 2  # Amplify invest amount by n times!
        configs = {
            LIConfigKey.aliasName: "NasdaqTrend",
            LIConfigKey.verbose: True,
            # LIConfigKey.skipWeekendDays: True,
            # LIConfigKey.extendedMarketHours: False,
            LIConfigKey.monitorPeriod: (1, LIResolution.HOUR),
            # LIConfigKey.monitorPeriod: (5, LIResolution.MINUTE),  # Not always better!
            LIConfigKey.indicatorPeriod: (1, LIResolution.DAY),
            # LIConfigKey.marketBias: LIMarketBias.BEARISH,
            # LIConfigKey.marketBias: LIMarketBias.BULLISH,
            # LIConfigKey.closeWithMarketOrderType: False,
            # LIConfigKey.closeWithStopOrderType: True,
            # LIConfigKey.enableLimitMarketOrder: True,
            # LIConfigKey.liquidateBaselinePrice: 25_000,
            # LIConfigKey.liquidateOnStopLossAmount: 20_000 * amplifier,  # Double it if only Long!
            LIConfigKey.liquidateOnStopLossAmount: 10_000 * amplifier,
            # LIConfigKey.flipSignalAtLiquidateFactor: 0.5,
            # LIConfigKey.liquidateLossAndLimitTrading: True,
            LIConfigKey.liquidateLossAndRestartTrading: True,
            LIConfigKey.liquidateLossAndBackfillEquity: "TECL",
            LIConfigKey.liquidateOnTakeProfitAmount: 10_000 * amplifier,  # Better for volatile market
            # LIConfigKey.gridHeikinAshiPlies: 1, # Performs better without HeikinAshi
            # LIConfigKey.gridNoMoreOpenOrders: True,
            # LIConfigKey.gridNoMoreCloseOrders: True,
            LIConfigKey.gridLongLots: 10,
            LIConfigKey.gridShortLots: 10,
            LIConfigKey.gridLotLevelPercent: 0.60,
            LIConfigKey.gridLotLevelAugment: 0.015,  # Perform better in a long run with volatile market
            LIConfigKey.gridLotStopLossFactor: 11,
            LIConfigKey.gridLotStopProfitFactors: (0.5, 2),
            LIConfigKey.gridLotPauseAfterStopLoss: True,
            LIConfigKey.gridCancelOrdersAfterClosed: True,
            LIConfigKey.gridTrailingOpenPriceFactor: 1.0,  # Enable for bullish market only to avoid acquiring too many open positions!
            # LIConfigKey.gridRestartIfAllLotsPaused: False,
            # LIConfigKey.gridCloseCounterpartLots: False,
            # LIConfigKey.gridFixLeakingPositions: True,
            # LIConfigKey.gridResetLotsMetadata: True,
            LIConfigKey.heikinAshiPlies: 3,  # Better with EMA, no impact to WEEKLY
            # LIConfigKey.comboTrendingParams: {LIIndicator.EMA: 50},
            LIConfigKey.comboTrendingParams: {LIIndicator.WEEKLY: 1},
            # LIConfigKey.comboTrendingParams: {LIIndicator.DAILY: 1},
            # LIConfigKey.candlestickBodyTolerance: 0.5,
            # LIConfigKey.staticTrendingSignals: weeklyTrendingSignals[Futures.Indices.MICRO_NASDAQ_100_E_MINI],
            LIConfigKey.pullTrendingSignalsApi: "api/signals",
            # LIConfigKey.pullTrendingSignalsApi: "api/signals",
            # LIConfigKey.useClosedTrendingSignal: False,
            LIConfigKey.gridInitializeSession: True,  # Be careful!
        }

        investAmount = LIInvestAmount(lotQuantity=1 * amplifier)
        self.liStrategies.append(LIFutureGridTradingContrarian(Futures.Indices.MICRO_NASDAQ_100_E_MINI, investAmount, **configs))


"""
┌────────────────────────────┬──────────────────┬─────────────────────────────┬────────────────┐
│ Statistic                  │ Value            │ Statistic                   │ Value          │
├────────────────────────────┼──────────────────┼─────────────────────────────┼────────────────┤
│ Equity                     │ $930,994.01      │ Fees                        │ -$1,142.41     │
│ Holdings                   │ $1,571,850.43    │ Net Profit                  │ $618,466.08    │
│ Probabilistic Sharpe Ratio │ 95.818%          │ Return                      │ 210.33 %       │
│ Unrealized                 │ $12,519.35       │ Volume                      │ $85,089,898.77 │
├────────────────────────────┼──────────────────┼─────────────────────────────┼────────────────┤
│ Total Orders               │ 792              │ Average Win                 │ 0.85%          │
│ Average Loss               │ -0.81%           │ Compounding Annual Return   │ 209.373%       │
│ Drawdown                   │ 18.200%          │ Expectancy                  │ 0.569          │
│ Start Equity               │ 300000           │ End Equity                  │ 930994.01      │
│ Net Profit                 │ 210.331%         │ Sharpe Ratio                │ 3.475          │
│ Sortino Ratio              │ 4.122            │ Probabilistic Sharpe Ratio  │ 95.818%        │
│ Loss Rate                  │ 23%              │ Win Rate                    │ 77%            │
│ Profit-Loss Ratio          │ 1.05             │ Alpha                       │ 0              │
│ Beta                       │ 0                │ Annual Standard Deviation   │ 0.368          │
│ Annual Variance            │ 0.135            │ Information Ratio           │ 3.624          │
│ Tracking Error             │ 0.368            │ Treynor Ratio               │ 0              │
│ Total Fees                 │ $1142.41         │ Estimated Strategy Capacity │ $9600000.00    │
│ Lowest Capacity Asset      │ MNQ YYFADOG4CO3L │ Portfolio Turnover          │ 42.52%         │
│ Drawdown Recovery          │ 17               │                             │                │
└────────────────────────────┴──────────────────┴─────────────────────────────┴────────────────┘
"""
