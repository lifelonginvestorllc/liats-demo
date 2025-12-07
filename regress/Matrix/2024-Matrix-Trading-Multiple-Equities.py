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

        self.equitySpreadsheetTrading()

    def equitySpreadsheetTrading(self):
        self.set_cash(1_000_000)
        self.set_start_date(date(2024, 5, 15))
        self.set_end_date(date(2024, 5, 25))

        configs = {
            LIConfigKey.warmupAlgo: False,
            LIConfigKey.monitorPeriod: (1, LIResolution.HOUR),
            LIConfigKey.extendedMarketHours: True,
            LIConfigKey.extendDataBarStream: True,
            LIConfigKey.gridLongLots: 10,
            LIConfigKey.gridShortLots: 10,
            LIConfigKey.gridInitializeSession: True,
        }

        investAmount = LIInvestAmount(maxHolding=1)
        self.liStrategies.append(LIEquitySpreadsheetTrading("SPY", investAmount, **configs))


"""
┌────────────────────────────┬───────────────────┬─────────────────────────────┬─────────────┐
│ Statistic                  │ Value             │ Statistic                   │ Value       │
├────────────────────────────┼───────────────────┼─────────────────────────────┼─────────────┤
│ Equity                     │ $998,847.73       │ Fees                        │ -$53.38     │
│ Holdings                   │ $629,585.13       │ Net Profit                  │ $-53.38     │
│ Probabilistic Sharpe Ratio │ 41.308%           │ Return                      │ -0.12 %     │
│ Unrealized                 │ $-1,152.27        │ Volume                      │ $630,684.02 │
├────────────────────────────┼───────────────────┼─────────────────────────────┼─────────────┤
│ Total Orders               │ 7                 │ Average Win                 │ 0%          │
│ Average Loss               │ 0%                │ Compounding Annual Return   │ -4.189%     │
│ Drawdown                   │ 2.300%            │ Expectancy                  │ 0           │
│ Start Equity               │ 1000000           │ End Equity                  │ 998847.73   │
│ Net Profit                 │ -0.115%           │ Sharpe Ratio                │ -0.722      │
│ Sortino Ratio              │ -1.186            │ Probabilistic Sharpe Ratio  │ 41.308%     │
│ Loss Rate                  │ 0%                │ Win Rate                    │ 0%          │
│ Profit-Loss Ratio          │ 0                 │ Alpha                       │ 0           │
│ Beta                       │ 0                 │ Annual Standard Deviation   │ 0.113       │
│ Annual Variance            │ 0.013             │ Information Ratio           │ -0.234      │
│ Tracking Error             │ 0.113             │ Treynor Ratio               │ 0           │
│ Total Fees                 │ $53.38            │ Estimated Strategy Capacity │ $6600000.00 │
│ Lowest Capacity Asset      │ UPST XKEDQOEEEPUT │ Portfolio Turnover          │ 6.35%       │
│ Drawdown Recovery          │ 3                 │                             │             │
└────────────────────────────┴───────────────────┴─────────────────────────────┴─────────────┘
"""
