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
│ Equity                     │ $192,551.86      │ Fees                        │ -$63.29     │
│ Holdings                   │ $366,940.00      │ Net Profit                  │ $4,544.13   │
│ Probabilistic Sharpe Ratio │ 57.012%          │ Return                      │ 92.55 %     │
│ Unrealized                 │ $58,259.38       │ Volume                      │ $328,835.88 │
├────────────────────────────┼──────────────────┼─────────────────────────────┼─────────────┤
│ Total Orders               │ 102              │ Average Win                 │ 2.73%       │
│ Average Loss               │ 0%               │ Compounding Annual Return   │ 93.307%     │
│ Drawdown                   │ 30.500%          │ Expectancy                  │ 0           │
│ Start Equity               │ 100000           │ End Equity                  │ 192551.86   │
│ Net Profit                 │ 92.552%          │ Sharpe Ratio                │ 1.453       │
│ Sortino Ratio              │ 1.967            │ Probabilistic Sharpe Ratio  │ 57.012%     │
│ Loss Rate                  │ 0%               │ Win Rate                    │ 100%        │
│ Profit-Loss Ratio          │ 0                │ Alpha                       │ 0           │
│ Beta                       │ 0                │ Annual Standard Deviation   │ 0.511       │
│ Annual Variance            │ 0.261            │ Information Ratio           │ 1.554       │
│ Tracking Error             │ 0.511            │ Treynor Ratio               │ 0           │
│ Total Fees                 │ $63.29           │ Estimated Strategy Capacity │ $84000.00   │
│ Lowest Capacity Asset      │ IXN S9RFV0RX457P │ Portfolio Turnover          │ 0.76%       │
│ Drawdown Recovery          │ 145              │                             │             │
└────────────────────────────┴──────────────────┴─────────────────────────────┴─────────────┘
"""
