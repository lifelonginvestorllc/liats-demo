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

        self.equitySpreadsheetRebalance()

    def equitySpreadsheetRebalance(self):
        self.set_cash(100_000)
        self.set_start_date(date(2025, 3, 3))
        self.set_end_date(date(2025, 3, 3))

        configs = {
            LIConfigKey.warmupAlgo: False,
            LIConfigKey.aliasName: "Rebalance",
            LIConfigKey.monitorPeriod: (1, LIResolution.HOUR),
            LIConfigKey.extendedMarketHours: False,
            LIConfigKey.extendDataBarStream: False,
            LIConfigKey.gridLongLots: 5,
            LIConfigKey.gridLotMinAmount: 500,
            LIConfigKey.tradeSpreadsheetUrl: "https://docs.google.com/spreadsheets/d/1jErcLYgF0EgIpXBnl5wtBOIf3pKZ7yiPkOp1ck3YYgk/export?format=csv",
            LIConfigKey.gridInitializeSession: True,
        }

        investAmount = LIInvestAmount(maxHolding=1)
        self.liStrategies.append(LIEquitySpreadsheetRebalance("SPY", investAmount, **configs))


"""
┌────────────────────────────┬───────────────────┬─────────────────────────────┬─────────────┐
│ Statistic                  │ Value             │ Statistic                   │ Value       │
├────────────────────────────┼───────────────────┼─────────────────────────────┼─────────────┤
│ Equity                     │ $98,094.66        │ Fees                        │ -$18.60     │
│ Holdings                   │ $97,477.03        │ Net Profit                  │ $-18.60     │
│ Probabilistic Sharpe Ratio │ 0%                │ Return                      │ -1.91 %     │
│ Unrealized                 │ $-1,905.34        │ Volume                      │ $99,363.77  │
├────────────────────────────┼───────────────────┼─────────────────────────────┼─────────────┤
│ Total Orders               │ 15                │ Average Win                 │ 0%          │
│ Average Loss               │ 0%                │ Compounding Annual Return   │ 0%          │
│ Drawdown                   │ 0%                │ Expectancy                  │ 0           │
│ Start Equity               │ 100000            │ End Equity                  │ 98094.66    │
│ Net Profit                 │ 0%                │ Sharpe Ratio                │ 0           │
│ Sortino Ratio              │ 0                 │ Probabilistic Sharpe Ratio  │ 0%          │
│ Loss Rate                  │ 0%                │ Win Rate                    │ 0%          │
│ Profit-Loss Ratio          │ 0                 │ Alpha                       │ 0           │
│ Beta                       │ 0                 │ Annual Standard Deviation   │ 0           │
│ Annual Variance            │ 0                 │ Information Ratio           │ 0           │
│ Tracking Error             │ 0                 │ Treynor Ratio               │ 0           │
│ Total Fees                 │ $18.60            │ Estimated Strategy Capacity │ $1500000.00 │
│ Lowest Capacity Asset      │ CSIQ TNII135YAI5H │ Portfolio Turnover          │ 101.29%     │
│ Drawdown Recovery          │ 0                 │                             │             │
└────────────────────────────┴───────────────────┴─────────────────────────────┴─────────────┘
"""
