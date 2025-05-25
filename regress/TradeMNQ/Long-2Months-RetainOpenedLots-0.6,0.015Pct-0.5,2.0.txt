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

        self.futureGridTrading_Nasdaq_Contrarian()

    def futureGridTrading_Nasdaq_Contrarian(self):
        self.SetCash(200_000)
        self.SetStartDate(date(2024, 11, 1))
        self.SetEndDate(date(2025, 1, 31))

        amplifier = 1  # Amplify invest amount by n times!
        configs = {
            LIConfigKey.aliasName: "NasdaqTrail",
            LIConfigKey.monitorPeriod: 5 * 12,
            LIConfigKey.liquidateOnStopLossAmount: 100_000 * amplifier,
            LIConfigKey.liquidateOnTakeProfitAmount: 50_000 * amplifier,
            LIConfigKey.gridLongLots: 20,
            LIConfigKey.gridLotLevelPercent: 0.60,
            LIConfigKey.gridLotLevelAugment: 0.015,  # Perform better in a long run with volatile market
            LIConfigKey.gridLotStopLossFactor: 25,
            LIConfigKey.gridLotStopProfitFactors: (0.5, 2),
            LIConfigKey.gridLotPauseAfterStopLoss: False,
            LIConfigKey.gridRetainOpenedLots: 1,
            LIConfigKey.gridInitializeSession: True,  # Be careful!
        }
        investAmount = LIInvestAmount(lotQuantity=1 * amplifier)
        self.liStrategies.append(LIFutureGridTradingContrarian(Futures.Indices.MicroNASDAQ100EMini, investAmount, **configs))


"""
┌────────────────────────────┬──────────────────┬─────────────────────────────┬───────────────┐
│ Statistic                  │ Value            │ Statistic                   │ Value         │
├────────────────────────────┼──────────────────┼─────────────────────────────┼───────────────┤
│ Equity                     │ $222,471.14      │ Fees                        │ -$26.79       │
│ Holdings                   │ $43,143.00       │ Net Profit                  │ $21,156.47    │
│ Probabilistic Sharpe Ratio │ 87.925%          │ Return                      │ 11.24 %       │
│ Unrealized                 │ $1,314.67        │ Volume                      │ $1,993,071.50 │
├────────────────────────────┼──────────────────┼─────────────────────────────┼───────────────┤
│ Total Orders               │ 49               │ Average Win                 │ 0.46%         │
│ Average Loss               │ -0.09%           │ Compounding Annual Return   │ 52.540%       │
│ Drawdown                   │ 4.200%           │ Expectancy                  │ 4.719         │
│ Start Equity               │ 200000           │ End Equity                  │ 222471.14     │
│ Net Profit                 │ 11.236%          │ Sharpe Ratio                │ 2.647         │
│ Sortino Ratio              │ 4.21             │ Probabilistic Sharpe Ratio  │ 87.925%       │
│ Loss Rate                  │ 4%               │ Win Rate                    │ 96%           │
│ Profit-Loss Ratio          │ 4.98             │ Alpha                       │ 0             │
│ Beta                       │ 0                │ Annual Standard Deviation   │ 0.111         │
│ Annual Variance            │ 0.012            │ Information Ratio           │ 3.144         │
│ Tracking Error             │ 0.111            │ Treynor Ratio               │ 0             │
│ Total Fees                 │ $26.79           │ Estimated Strategy Capacity │ $370000000.00 │
│ Lowest Capacity Asset      │ MNQ YQYHC5L1GPA9 │ Portfolio Turnover          │ 10.31%        │
└────────────────────────────┴──────────────────┴─────────────────────────────┴───────────────┘
"""
