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
            LIConfigKey.gridTrailingOpenPriceFactor: 1.0,
            LIConfigKey.gridInitializeSession: True,  # Be careful!
        }
        investAmount = LIInvestAmount(lotQuantity=1 * amplifier)
        self.liStrategies.append(LIFutureGridTradingContrarian(Futures.Indices.MicroNASDAQ100EMini, investAmount, **configs))


"""
┌────────────────────────────┬──────────────────┬─────────────────────────────┬───────────────┐
│ Statistic                  │ Value            │ Statistic                   │ Value         │
├────────────────────────────┼──────────────────┼─────────────────────────────┼───────────────┤
│ Equity                     │ $219,158.02      │ Fees                        │ -$61.56       │
│ Holdings                   │ $258,858.00      │ Net Profit                  │ $18,872.28    │
│ Probabilistic Sharpe Ratio │ 56.835%          │ Return                      │ 9.58 %        │
│ Unrealized                 │ $285.74          │ Volume                      │ $4,591,420.00 │
├────────────────────────────┼──────────────────┼─────────────────────────────┼───────────────┤
│ Total Orders               │ 98               │ Average Win                 │ 0.37%         │
│ Average Loss               │ -0.38%           │ Compounding Annual Return   │ 43.728%       │
│ Drawdown                   │ 11.500%          │ Expectancy                  │ 0.557         │
│ Start Equity               │ 200000           │ End Equity                  │ 219158.02     │
│ Net Profit                 │ 9.579%           │ Sharpe Ratio                │ 1.226         │
│ Sortino Ratio              │ 1.654            │ Probabilistic Sharpe Ratio  │ 56.835%       │
│ Loss Rate                  │ 21%              │ Win Rate                    │ 79%           │
│ Profit-Loss Ratio          │ 0.97             │ Alpha                       │ 0             │
│ Beta                       │ 0                │ Annual Standard Deviation   │ 0.214         │
│ Annual Variance            │ 0.046            │ Information Ratio           │ 1.482         │
│ Tracking Error             │ 0.214            │ Treynor Ratio               │ 0             │
│ Total Fees                 │ $61.56           │ Estimated Strategy Capacity │ $200000000.00 │
│ Lowest Capacity Asset      │ MNQ YQYHC5L1GPA9 │ Portfolio Turnover          │ 23.63%        │
└────────────────────────────┴──────────────────┴─────────────────────────────┴───────────────┘
"""
