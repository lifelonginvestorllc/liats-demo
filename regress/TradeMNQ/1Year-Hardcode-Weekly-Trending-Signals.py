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
│ Equity                     │ $385,445.60      │ Fees                        │ -$744.42       │
│ Holdings                   │ $658,077.00      │ Net Profit                  │ $182,252.29    │
│ Probabilistic Sharpe Ratio │ 61.922%          │ Return                      │ 92.72 %        │
│ Unrealized                 │ $3,193.31        │ Volume                      │ $53,312,910.00 │
├────────────────────────────┼──────────────────┼─────────────────────────────┼────────────────┤
│ Total Orders               │ 514              │ Average Win                 │ 1.35%          │
│ Average Loss               │ -1.65%           │ Compounding Annual Return   │ 92.378%        │
│ Drawdown                   │ 37.000%          │ Expectancy                  │ 0.261          │
│ Start Equity               │ 200000           │ End Equity                  │ 385445.6       │
│ Net Profit                 │ 92.723%          │ Sharpe Ratio                │ 1.537          │
│ Sortino Ratio              │ 1.768            │ Probabilistic Sharpe Ratio  │ 61.922%        │
│ Loss Rate                  │ 31%              │ Win Rate                    │ 69%            │
│ Profit-Loss Ratio          │ 0.82             │ Alpha                       │ 0              │
│ Beta                       │ 0                │ Annual Standard Deviation   │ 0.44           │
│ Annual Variance            │ 0.193            │ Information Ratio           │ 1.662          │
│ Tracking Error             │ 0.44             │ Treynor Ratio               │ 0              │
│ Total Fees                 │ $744.42          │ Estimated Strategy Capacity │ $440000000.00  │
│ Lowest Capacity Asset      │ MNQ YVXOP65RE0HT │ Portfolio Turnover          │ 67.05%         │
│ Drawdown Recovery          │ 104              │                             │                │
└────────────────────────────┴──────────────────┴─────────────────────────────┴────────────────┘
"""
