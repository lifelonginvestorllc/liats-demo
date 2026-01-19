from AlgorithmImports import *
from core.LIAlgorithm import *


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

        self.futureGridTrading_Nasdaq_Contrarian_Short()

    def futureGridTrading_Nasdaq_Contrarian_Short(self):
        self.set_cash(200_000)
        self.set_start_date(date(2024, 11, 1))
        self.set_end_date(date(2025, 1, 31))

        amplifier = 1  # Amplify invest amount by n times!
        configs = {
            LIConfigKey.aliasName: "NasdaqShort",
            LIConfigKey.monitorPeriod: (5 * 3, LIResolution.MINUTE),  # 5 * 6,  # 5 * 12
            LIConfigKey.liquidateOnStopLossAmount: 100_000 * amplifier,  # 100_000 * amplifier,
            LIConfigKey.liquidateOnTakeProfitAmount: 50_000 * amplifier,  # 50_000 * amplifier,
            LIConfigKey.gridFollowAdverseTrend: True,  # Enable once market is stable!
            LIConfigKey.gridShortLots: 20,  # 30
            LIConfigKey.gridLotLevelPercent: 0.60,
            LIConfigKey.gridLotLevelAugment: 0.015,  # Perform better in a long run with volatile market
            LIConfigKey.gridLotStopLossFactor: 25,  # 35
            LIConfigKey.gridLotStopProfitFactors: (0.5, 2),
            LIConfigKey.gridInitializeSession: True,  # Be careful!
        }
        investAmount = LIInvestAmount(lotQuantity=1 * amplifier)
        self.liStrategies.append(LIFutureGridTradingContrarian(Futures.Indices.MicroNASDAQ100EMini, investAmount, **configs))


"""
┌────────────────────────────┬──────────────────┬─────────────────────────────┬───────────────┐
│ Statistic                  │ Value            │ Statistic                   │ Value         │
├────────────────────────────┼──────────────────┼─────────────────────────────┼───────────────┤
│ Equity                     │ $221,012.33      │ Fees                        │ -$45.03       │
│ Holdings                   │ $86,286.00       │ Net Profit                  │ $21,245.27    │
│ Probabilistic Sharpe Ratio │ 50.567%          │ Return                      │ 10.51 %       │
│ Unrealized                 │ $-232.94         │ Volume                      │ $3,740,389.50 │
├────────────────────────────┼──────────────────┼─────────────────────────────┼───────────────┤
│ Total Orders               │ 86               │ Average Win                 │ 0.32%         │
│ Average Loss               │ -0.15%           │ Compounding Annual Return   │ 48.612%       │
│ Drawdown                   │ 14.000%          │ Expectancy                  │ 1.871         │
│ Start Equity               │ 200000           │ End Equity                  │ 221012.33     │
│ Net Profit                 │ 10.506%          │ Sharpe Ratio                │ 1.031         │
│ Sortino Ratio              │ 2.038            │ Probabilistic Sharpe Ratio  │ 50.567%       │
│ Loss Rate                  │ 6%               │ Win Rate                    │ 94%           │
│ Profit-Loss Ratio          │ 2.04             │ Alpha                       │ 0             │
│ Beta                       │ 0                │ Annual Standard Deviation   │ 0.317         │
│ Annual Variance            │ 0.101            │ Information Ratio           │ 1.204         │
│ Tracking Error             │ 0.317            │ Treynor Ratio               │ 0             │
│ Total Fees                 │ $45.03           │ Estimated Strategy Capacity │ $20000000.00  │
│ Lowest Capacity Asset      │ MNQ YQYHC5L1GPA9 │ Portfolio Turnover          │ 19.74%        │
│ Drawdown Recovery          │ 33               │                             │               │
└────────────────────────────┴──────────────────┴─────────────────────────────┴───────────────┘
"""
