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

        self.equityGridTrading_IXN_DCA()

    def equityGridTrading_IXN_DCA(self):
        self.SetCash(500_000)
        self.SetStartDate(date(2023, 1, 1))
        self.SetEndDate(date(2023, 12, 31))

        configs = {
            LIConfigKey.monitorPeriod: 60,
            LIConfigKey.extendedMarketHours: True,
            LIConfigKey.dcaInvestCapital: 5_000,
            LIConfigKey.dcaInvestPeriodicity: LIPeriodicity.WEEKLY,
            LIConfigKey.gridLongLots: 20,
            LIConfigKey.gridLotMinQuantity: 10,
            LIConfigKey.gridLotLevelPercent: 2,
            LIConfigKey.gridHeikinAshiPlies: 1,
            # LIConfigKey.gridResetStartPrices: {LIGridSide.BTD: 70},
            LIConfigKey.gridInitializeSession: True, # Be careful!
        }
        investAmount = LIInvestAmount(maxCapital=100_000)
        self.liStrategies.append(LIEquityGridTradingBuyAndHold("IXN", investAmount, **configs))


"""
┌────────────────────────────┬──────────────────┬─────────────────────────────┬─────────────┐
│ Statistic                  │ Value            │ Statistic                   │ Value       │
├────────────────────────────┼──────────────────┼─────────────────────────────┼─────────────┤
│ Equity                     │ $614,831.85      │ Fees                        │ -$87.00     │
│ Holdings                   │ $543,200.00      │ Net Profit                  │ $2,257.18   │
│ Probabilistic Sharpe Ratio │ 48.485%          │ Return                      │ 22.97 %     │
│ Unrealized                 │ $68,536.67       │ Volume                      │ $430,625.33 │
├────────────────────────────┼──────────────────┼─────────────────────────────┼─────────────┤
│ Total Orders               │ 127              │ Average Win                 │ 0%          │
│ Average Loss               │ 0%               │ Compounding Annual Return   │ 23.118%     │
│ Drawdown                   │ 10.700%          │ Expectancy                  │ 0           │
│ Start Equity               │ 500000           │ End Equity                  │ 614831.85   │
│ Net Profit                 │ 22.966%          │ Sharpe Ratio                │ 0.728       │
│ Sortino Ratio              │ 0.884            │ Probabilistic Sharpe Ratio  │ 48.485%     │
│ Loss Rate                  │ 0%               │ Win Rate                    │ 0%          │
│ Profit-Loss Ratio          │ 0                │ Alpha                       │ 0           │
│ Beta                       │ 0                │ Annual Standard Deviation   │ 0.162       │
│ Annual Variance            │ 0.026            │ Information Ratio           │ 1.049       │
│ Tracking Error             │ 0.162            │ Treynor Ratio               │ 0           │
│ Total Fees                 │ $87.00           │ Estimated Strategy Capacity │ $180000.00  │
│ Lowest Capacity Asset      │ IXN S9RFV0RX457P │ Portfolio Turnover          │ 0.22%       │
└────────────────────────────┴──────────────────┴─────────────────────────────┴─────────────┘
"""
