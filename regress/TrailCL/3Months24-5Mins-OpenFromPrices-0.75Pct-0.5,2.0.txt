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

        self.futureGridTrading_Oil_Contrarian()

    def futureGridTrading_Oil_Contrarian(self):
        self.SetCash(300_000)
        self.SetStartDate(date(2024, 6, 1))
        self.SetEndDate(date(2024, 9, 1))

        configs = {
            LIConfigKey.aliasName: "OilTrail",
            LIConfigKey.futurePeriodDays: 35,
            LIConfigKey.liquidateOnStopLossAmount: 100_000,
            LIConfigKey.gridLongLots: 20,
            LIConfigKey.gridShortLots: 20,
            LIConfigKey.gridLotLevelPercent: 0.75,
            LIConfigKey.gridLotStopLossFactor: 25,
            LIConfigKey.gridLotStopProfitFactors: (0.5, 2),
            LIConfigKey.gridFixedStartPrices: {LIGridSide.BTD: 79, LIGridSide.STU: 79},
            LIConfigKey.gridFixedOpenFromPrices: {LIGridSide.BTD: 74, LIGridSide.STU: 84},
            LIConfigKey.gridInitializeSession: True,
        }
        investAmount = LIInvestAmount(lotQuantity=1)
        self.liStrategies.append(LIFutureGridTradingContrarian(Futures.Energies.CRUDE_OIL_WTI, investAmount, **configs))


"""
┌────────────────────────────┬─────────────────┬─────────────────────────────┬───────────────┐
│ Statistic                  │ Value           │ Statistic                   │ Value         │
├────────────────────────────┼─────────────────┼─────────────────────────────┼───────────────┤
│ Equity                     │ $412,517.82     │ Fees                        │ -$224.77      │
│ Holdings                   │ $219,060.00     │ Net Profit                  │ $113,348.48   │
│ Probabilistic Sharpe Ratio │ 98.547%         │ Return                      │ 37.51 %       │
│ Unrealized                 │ $-830.66        │ Volume                      │ $6,991,120.00 │
├────────────────────────────┼─────────────────┼─────────────────────────────┼───────────────┤
│ Total Orders               │ 96              │ Average Win                 │ 0.79%         │
│ Average Loss               │ -0.15%          │ Compounding Annual Return   │ 249.039%      │
│ Drawdown                   │ 6.900%          │ Expectancy                  │ 5.168         │
│ Start Equity               │ 300000          │ End Equity                  │ 412517.82     │
│ Net Profit                 │ 37.506%         │ Sharpe Ratio                │ 6.1           │
│ Sortino Ratio              │ 11.65           │ Probabilistic Sharpe Ratio  │ 98.547%       │
│ Loss Rate                  │ 5%              │ Win Rate                    │ 95%           │
│ Profit-Loss Ratio          │ 5.47            │ Alpha                       │ 0             │
│ Beta                       │ 0               │ Annual Standard Deviation   │ 0.229         │
│ Annual Variance            │ 0.053           │ Information Ratio           │ 6.34          │
│ Tracking Error             │ 0.229           │ Treynor Ratio               │ 0             │
│ Total Fees                 │ $224.77         │ Estimated Strategy Capacity │ $67000000.00  │
│ Lowest Capacity Asset      │ CL YLZ9Z50BJCU9 │ Portfolio Turnover          │ 21.20%        │
└────────────────────────────┴─────────────────┴─────────────────────────────┴───────────────┘
"""
