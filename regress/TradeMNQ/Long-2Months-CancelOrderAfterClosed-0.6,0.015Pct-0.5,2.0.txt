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
            LIConfigKey.gridCancelOrdersAfterClosed: True,
            LIConfigKey.gridInitializeSession: True,  # Be careful!
        }
        investAmount = LIInvestAmount(lotQuantity=1 * amplifier)
        self.liStrategies.append(LIFutureGridTradingContrarian(Futures.Indices.MicroNASDAQ100EMini, investAmount, **configs))


"""
┌────────────────────────────┬──────────────────┬─────────────────────────────┬───────────────┐
│ Statistic                  │ Value            │ Statistic                   │ Value         │
├────────────────────────────┼──────────────────┼─────────────────────────────┼───────────────┤
│ Equity                     │ $217,114.22      │ Fees                        │ -$55.29       │
│ Holdings                   │ $302,001.00      │ Net Profit                  │ $14,309.87    │
│ Probabilistic Sharpe Ratio │ 57.471%          │ Return                      │ 8.56 %        │
│ Unrealized                 │ $2,804.35        │ Volume                      │ $4,151,139.50 │
├────────────────────────────┼──────────────────┼─────────────────────────────┼───────────────┤
│ Total Orders               │ 105              │ Average Win                 │ 0.31%         │
│ Average Loss               │ -0.34%           │ Compounding Annual Return   │ 38.486%       │
│ Drawdown                   │ 9.800%           │ Expectancy                  │ 0.527         │
│ Start Equity               │ 200000           │ End Equity                  │ 217114.22     │
│ Net Profit                 │ 8.557%           │ Sharpe Ratio                │ 1.183         │
│ Sortino Ratio              │ 1.778            │ Probabilistic Sharpe Ratio  │ 57.471%       │
│ Loss Rate                  │ 21%              │ Win Rate                    │ 79%           │
│ Profit-Loss Ratio          │ 0.92             │ Alpha                       │ 0             │
│ Beta                       │ 0                │ Annual Standard Deviation   │ 0.188         │
│ Annual Variance            │ 0.035            │ Information Ratio           │ 1.476         │
│ Tracking Error             │ 0.188            │ Treynor Ratio               │ 0             │
│ Total Fees                 │ $55.29           │ Estimated Strategy Capacity │ $69000000.00  │
│ Lowest Capacity Asset      │ MNQ YQYHC5L1GPA9 │ Portfolio Turnover          │ 21.91%        │
└────────────────────────────┴──────────────────┴─────────────────────────────┴───────────────┘
"""
