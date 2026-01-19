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
            LIConfigKey.gridLotMinAmount: 100,
            LIConfigKey.gridMaintainOpenOrders: 3,
            LIConfigKey.tradeSpreadsheetUrl: "https://docs.google.com/spreadsheets/d/1b4rwApU3ggHpeCGZuBP_aWpCVwynsdV65tf_feT2uNk/export?format=csv",
            LIConfigKey.gridInitializeSession: True,
        }

        investAmount = LIInvestAmount(maxHolding=1)
        self.liStrategies.append(LIEquitySpreadsheetTrading("SPY", investAmount, **configs))


"""
┌────────────────────────────┬───────────────────┬─────────────────────────────┬─────────────┐
│ Statistic                  │ Value             │ Statistic                   │ Value       │
├────────────────────────────┼───────────────────┼─────────────────────────────┼─────────────┤
│ Equity                     │ $1,003,594.43     │ Fees                        │ -$72.83     │
│ Holdings                   │ $602,641.63       │ Net Profit                  │ $-146.15    │
│ Probabilistic Sharpe Ratio │ 50.197%           │ Return                      │ 0.36 %      │
│ Unrealized                 │ $3,693.10         │ Volume                      │ $730,510.46 │
├────────────────────────────┼───────────────────┼─────────────────────────────┼─────────────┤
│ Total Orders               │ 12                │ Average Win                 │ 0%          │
│ Average Loss               │ -0.01%            │ Compounding Annual Return   │ 14.246%     │
│ Drawdown                   │ 2.000%            │ Expectancy                  │ -1          │
│ Start Equity               │ 1000000           │ End Equity                  │ 1003594.42  │
│ Net Profit                 │ 0.359%            │ Sharpe Ratio                │ 0.546       │
│ Sortino Ratio              │ 0.951             │ Probabilistic Sharpe Ratio  │ 50.197%     │
│ Loss Rate                  │ 100%              │ Win Rate                    │ 0%          │
│ Profit-Loss Ratio          │ 0                 │ Alpha                       │ 0           │
│ Beta                       │ 0                 │ Annual Standard Deviation   │ 0.102       │
│ Annual Variance            │ 0.01              │ Information Ratio           │ 1.083       │
│ Tracking Error             │ 0.102             │ Treynor Ratio               │ 0           │
│ Total Fees                 │ $72.83            │ Estimated Strategy Capacity │ $9600000.00 │
│ Lowest Capacity Asset      │ UPST XKEDQOEEEPUT │ Portfolio Turnover          │ 7.34%       │
│ Drawdown Recovery          │ 3                 │                             │             │
└────────────────────────────┴───────────────────┴─────────────────────────────┴─────────────┘
"""
