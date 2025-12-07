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

        self.futureGridTrading_Oil_Contrarian()

    def futureGridTrading_Oil_Contrarian(self):
        self.set_cash(300_000)
        self.set_start_date(date(2024, 6, 1))
        self.set_end_date(date(2024, 9, 1))

        configs = {
            LIConfigKey.aliasName: "OilTrail",
            LIConfigKey.futurePeriodDays: 35,
            LIConfigKey.monitorPeriod: (1, LIResolution.HOUR),
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
│ Equity                     │ $410,397.46     │ Fees                        │ -$195.13      │
│ Holdings                   │ $220,965.00     │ Net Profit                  │ $110,102.37   │
│ Probabilistic Sharpe Ratio │ 95.909%         │ Return                      │ 36.80 %       │
│ Unrealized                 │ $295.09         │ Volume                      │ $6,034,930.00 │
├────────────────────────────┼─────────────────┼─────────────────────────────┼───────────────┤
│ Total Orders               │ 80              │ Average Win                 │ 0.98%         │
│ Average Loss               │ -0.37%          │ Compounding Annual Return   │ 242.051%      │
│ Drawdown                   │ 9.600%          │ Expectancy                  │ 2.456         │
│ Start Equity               │ 300000          │ End Equity                  │ 410397.46     │
│ Net Profit                 │ 36.799%         │ Sharpe Ratio                │ 5.149         │
│ Sortino Ratio              │ 10.52           │ Probabilistic Sharpe Ratio  │ 95.909%       │
│ Loss Rate                  │ 6%              │ Win Rate                    │ 94%           │
│ Profit-Loss Ratio          │ 2.66            │ Alpha                       │ 0             │
│ Beta                       │ 0               │ Annual Standard Deviation   │ 0.27          │
│ Annual Variance            │ 0.073           │ Information Ratio           │ 5.353         │
│ Tracking Error             │ 0.27            │ Treynor Ratio               │ 0             │
│ Total Fees                 │ $195.13         │ Estimated Strategy Capacity │ $15000000.00  │
│ Lowest Capacity Asset      │ CL YLZ9Z50BJCU9 │ Portfolio Turnover          │ 18.22%        │
│ Drawdown Recovery          │ 10              │                             │               │
└────────────────────────────┴─────────────────┴─────────────────────────────┴───────────────┘
"""
