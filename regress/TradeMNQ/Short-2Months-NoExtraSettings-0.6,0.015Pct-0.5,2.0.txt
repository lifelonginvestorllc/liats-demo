# region imports
from core.LIAlgorithm import *


# endregion

class LifelongInvestorMain(LIAlgorithm):

    def Initialize(self):
        super().Initialize()
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
        self.SetCash(200_000)
        self.SetStartDate(date(2024, 11, 1))
        self.SetEndDate(date(2025, 1, 31))

        amplifier = 1  # Amplify invest amount by n times!
        configs = {
            LIConfigKey.aliasName: "NasdaqShort",
            LIConfigKey.monitorPeriod: 5 * 3,  # 5 * 6,  # 5 * 12
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
│ Equity                     │ $207,172.02      │ Fees                        │ -$60.42       │
│ Holdings                   │ $345,144.00      │ Net Profit                  │ $13,404.91    │
│ Probabilistic Sharpe Ratio │ 37.178%          │ Return                      │ 3.59 %        │
│ Unrealized                 │ $-6,232.89       │ Volume                      │ $4,496,252.00 │
├────────────────────────────┼──────────────────┼─────────────────────────────┼───────────────┤
│ Total Orders               │ 103              │ Average Win                 │ 0.24%         │
│ Average Loss               │ -0.34%           │ Compounding Annual Return   │ 14.995%       │
│ Drawdown                   │ 12.100%          │ Expectancy                  │ 0.463         │
│ Start Equity               │ 200000           │ End Equity                  │ 207172.02     │
│ Net Profit                 │ 3.586%           │ Sharpe Ratio                │ 0.32          │
│ Sortino Ratio              │ 0.568            │ Probabilistic Sharpe Ratio  │ 37.178%       │
│ Loss Rate                  │ 15%              │ Win Rate                    │ 85%           │
│ Profit-Loss Ratio          │ 0.71             │ Alpha                       │ 0             │
│ Beta                       │ 0                │ Annual Standard Deviation   │ 0.299         │
│ Annual Variance            │ 0.09             │ Information Ratio           │ 0.504         │
│ Tracking Error             │ 0.299            │ Treynor Ratio               │ 0             │
│ Total Fees                 │ $60.42           │ Estimated Strategy Capacity │ $17000000.00  │
│ Lowest Capacity Asset      │ MNQ YQYHC5L1GPA9 │ Portfolio Turnover          │ 24.02%        │
└────────────────────────────┴──────────────────┴─────────────────────────────┴───────────────┘
"""
