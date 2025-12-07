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

        self.equityGridTrading_IXN_DCA()

    def equityGridTrading_IXN_DCA(self):
        self.set_cash(100_000)
        self.set_start_date(date(2023, 1, 1))
        self.set_end_date(date(2023, 12, 31))

        configs = {
            LIConfigKey.monitorPeriod: (60, LIResolution.MINUTE),
            LIConfigKey.extendedMarketHours: True,
            LIConfigKey.dcaInvestCapital: 5_000,
            LIConfigKey.dcaInvestPeriodicity: LIPeriodicity.WEEKLY,
            LIConfigKey.gridLongLots: 20,
            LIConfigKey.gridLotMinQuantity: 10,
            LIConfigKey.gridLotLevelPercent: 2,
            LIConfigKey.gridHeikinAshiPlies: 1,
            LIConfigKey.gridInitializeSession: True, # Be careful!
        }
        investAmount = LIInvestAmount(maxCapital=100_000)
        self.liStrategies.append(LIEquityGridTradingBuyAndHold("IXN", investAmount, **configs))


"""
┌────────────────────────────┬──────────────────┬─────────────────────────────┬─────────────┐
│ Statistic                  │ Value            │ Statistic                   │ Value       │
├────────────────────────────┼──────────────────┼─────────────────────────────┼─────────────┤
│ Equity                     │ $188,113.03      │ Fees                        │ -$62.22     │
│ Holdings                   │ $358,400.00      │ Net Profit                  │ $4,121.74   │
│ Probabilistic Sharpe Ratio │ 56.332%          │ Return                      │ 88.11 %     │
│ Unrealized                 │ $54,935.29       │ Volume                      │ $322,858.68 │
├────────────────────────────┼──────────────────┼─────────────────────────────┼─────────────┤
│ Total Orders               │ 104              │ Average Win                 │ 2.37%       │
│ Average Loss               │ 0%               │ Compounding Annual Return   │ 88.824%     │
│ Drawdown                   │ 30.400%          │ Expectancy                  │ 0           │
│ Start Equity               │ 100000           │ End Equity                  │ 188113.03   │
│ Net Profit                 │ 88.113%          │ Sharpe Ratio                │ 1.411       │
│ Sortino Ratio              │ 1.88             │ Probabilistic Sharpe Ratio  │ 56.332%     │
│ Loss Rate                  │ 0%               │ Win Rate                    │ 100%        │
│ Profit-Loss Ratio          │ 0                │ Alpha                       │ 0           │
│ Beta                       │ 0                │ Annual Standard Deviation   │ 0.497       │
│ Annual Variance            │ 0.247            │ Information Ratio           │ 1.516       │
│ Tracking Error             │ 0.497            │ Treynor Ratio               │ 0           │
│ Total Fees                 │ $62.22           │ Estimated Strategy Capacity │ $60000.00   │
│ Lowest Capacity Asset      │ IXN S9RFV0RX457P │ Portfolio Turnover          │ 0.74%       │
│ Drawdown Recovery          │ 145              │                             │             │
└────────────────────────────┴──────────────────┴─────────────────────────────┴─────────────┘
"""
