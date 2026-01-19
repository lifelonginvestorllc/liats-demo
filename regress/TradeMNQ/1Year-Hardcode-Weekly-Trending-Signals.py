from AlgorithmImports import *
from core.LIAlgorithm import *
from indicator.LIWeeklyTrendingSignals import *


class LifelongInvestorMain(LIAlgorithm):

    def initialize(self):
        super().initialize()
        setLogSize(500)  # Only for backtesting
        setAlgoName("Backtest")  # Invest account name
        addNotifySetting(LINotifyType.TELEGRAM, "-913280749")
        addAlertSetting(LINotifyType.EMAIL, "lifelonginvestorllc@gmail.com")
        # liquidateAndStopTrading() # Liquidate all strategies in emergency!
        # replicateMetadataFrom(15964868)  # Replicate metadata from this project

        if self.live_mode:
            terminate(f"This project is for backtest only!")

        self.futureGridTrading_Nasdaq_Trend_Indicator()

    def futureGridTrading_Nasdaq_Trend_Indicator(self):
        self.set_cash(200_000)
        self.set_start_date(date(2024, 9, 1))
        self.set_end_date(date(2025, 9, 1))

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
│ Equity                     │ $437,173.46      │ Fees                        │ -$660.06       │
│ Holdings                   │ $658,077.00      │ Net Profit                  │ $235,789.14    │
│ Probabilistic Sharpe Ratio │ 77.858%          │ Return                      │ 118.59 %       │
│ Unrealized                 │ $1,384.32        │ Volume                      │ $48,833,912.50 │
├────────────────────────────┼──────────────────┼─────────────────────────────┼────────────────┤
│ Total Orders               │ 495              │ Average Win                 │ 1.26%          │
│ Average Loss               │ -1.09%           │ Compounding Annual Return   │ 118.120%       │
│ Drawdown                   │ 20.300%          │ Expectancy                  │ 0.465          │
│ Start Equity               │ 200000           │ End Equity                  │ 437173.46      │
│ Net Profit                 │ 118.587%         │ Sharpe Ratio                │ 2.115          │
│ Sortino Ratio              │ 2.311            │ Probabilistic Sharpe Ratio  │ 77.858%        │
│ Loss Rate                  │ 32%              │ Win Rate                    │ 68%            │
│ Profit-Loss Ratio          │ 1.16             │ Alpha                       │ 0              │
│ Beta                       │ 0                │ Annual Standard Deviation   │ 0.37           │
│ Annual Variance            │ 0.137            │ Information Ratio           │ 2.264          │
│ Tracking Error             │ 0.37             │ Treynor Ratio               │ 0              │
│ Total Fees                 │ $660.06          │ Estimated Strategy Capacity │ $1300000000.00 │
│ Lowest Capacity Asset      │ MNQ YVXOP65RE0HT │ Portfolio Turnover          │ 51.45%         │
│ Drawdown Recovery          │ 107              │                             │                │
└────────────────────────────┴──────────────────┴─────────────────────────────┴────────────────┘
"""
