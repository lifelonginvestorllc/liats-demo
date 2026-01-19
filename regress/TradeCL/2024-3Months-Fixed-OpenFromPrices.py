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
│ Equity                     │ $411,629.39     │ Fees                        │ -$145.73      │
│ Holdings                   │ $294,620.00     │ Net Profit                  │ $110,433.12   │
│ Probabilistic Sharpe Ratio │ 88.815%         │ Return                      │ 37.21 %       │
│ Unrealized                 │ $1,196.27       │ Volume                      │ $5,635,895.00 │
├────────────────────────────┼─────────────────┼─────────────────────────────┼───────────────┤
│ Total Orders               │ 68              │ Average Win                 │ 1.39%         │
│ Average Loss               │ 0%              │ Compounding Annual Return   │ 246.098%      │
│ Drawdown                   │ 13.400%         │ Expectancy                  │ 0             │
│ Start Equity               │ 300000          │ End Equity                  │ 411629.39     │
│ Net Profit                 │ 37.210%         │ Sharpe Ratio                │ 4.397         │
│ Sortino Ratio              │ 7.947           │ Probabilistic Sharpe Ratio  │ 88.815%       │
│ Loss Rate                  │ 0%              │ Win Rate                    │ 100%          │
│ Profit-Loss Ratio          │ 0               │ Alpha                       │ 0             │
│ Beta                       │ 0               │ Annual Standard Deviation   │ 0.33          │
│ Annual Variance            │ 0.109           │ Information Ratio           │ 4.563         │
│ Tracking Error             │ 0.33            │ Treynor Ratio               │ 0             │
│ Total Fees                 │ $145.73         │ Estimated Strategy Capacity │ $6100000.00   │
│ Lowest Capacity Asset      │ CL YL4R48O35YV5 │ Portfolio Turnover          │ 17.14%        │
│ Drawdown Recovery          │ 16              │                             │               │
└────────────────────────────┴─────────────────┴─────────────────────────────┴───────────────┘
"""
