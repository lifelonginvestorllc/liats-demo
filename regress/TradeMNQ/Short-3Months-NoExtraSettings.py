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

        self.futureGridTrading_Nasdaq_Contrarian_Short()

    def futureGridTrading_Nasdaq_Contrarian_Short(self):
        self.set_cash(200_000)
        self.set_start_date(date(2024, 11, 1))
        self.set_end_date(date(2025, 1, 31))

        amplifier = 1  # Amplify invest amount by n times!
        configs = {
            LIConfigKey.aliasName: "NasdaqShort",
            LIConfigKey.monitorPeriod: (5 * 3, LIResolution.MINUTE),  # 5 * 6,  # 5 * 12
            LIConfigKey.liquidateOnStopLossAmount: 100_000 * amplifier,  # 100_000 * amplifier,
            LIConfigKey.liquidateOnTakeProfitAmount: 50_000 * amplifier,  # 50_000 * amplifier,
            LIConfigKey.gridFollowAdverseTrend: True,  # Enable once market is stable!
            LIConfigKey.gridShortLots: 20,  # 30
            LIConfigKey.gridLotLevelPercent: 0.60,
            LIConfigKey.gridLotLevelAugment: 0.015,  # Perform better in a long run with volatile market
            LIConfigKey.gridLotStopLossFactor: 25,  # 35
            LIConfigKey.gridLotStopProfitFactors: (0.5, 2),
            LIConfigKey.gridInitializeSession: True,  # Be careful!
        }
        investAmount = LIInvestAmount(lotQuantity=1 * amplifier)
        self.liStrategies.append(LIFutureGridTradingContrarian(Futures.Indices.MicroNASDAQ100EMini, investAmount, **configs))


"""
┌────────────────────────────┬──────────────────┬─────────────────────────────┬───────────────┐
│ Statistic                  │ Value            │ Statistic                   │ Value         │
├────────────────────────────┼──────────────────┼─────────────────────────────┼───────────────┤
│ Equity                     │ $208,657.94      │ Fees                        │ -$30.78       │
│ Holdings                   │ $172,572.00      │ Net Profit                  │ $3,544.08     │
│ Probabilistic Sharpe Ratio │ 38.464%          │ Return                      │ 4.33 %        │
│ Unrealized                 │ $5,113.86        │ Volume                      │ $2,325,429.00 │
├────────────────────────────┼──────────────────┼─────────────────────────────┼───────────────┤
│ Total Orders               │ 36               │ Average Win                 │ 0.71%         │
│ Average Loss               │ -7.85%           │ Compounding Annual Return   │ 18.300%       │
│ Drawdown                   │ 12.500%          │ Expectancy                  │ 0.018         │
│ Start Equity               │ 200000           │ End Equity                  │ 208657.94     │
│ Net Profit                 │ 4.329%           │ Sharpe Ratio                │ 0.396         │
│ Sortino Ratio              │ 0.764            │ Probabilistic Sharpe Ratio  │ 38.464%       │
│ Loss Rate                  │ 7%               │ Win Rate                    │ 93%           │
│ Profit-Loss Ratio          │ 0.09             │ Alpha                       │ 0             │
│ Beta                       │ 0                │ Annual Standard Deviation   │ 0.289         │
│ Annual Variance            │ 0.084            │ Information Ratio           │ 0.587         │
│ Tracking Error             │ 0.289            │ Treynor Ratio               │ 0             │
│ Total Fees                 │ $30.78           │ Estimated Strategy Capacity │ $7900000.00   │
│ Lowest Capacity Asset      │ MNQ YQYHC5L1GPA9 │ Portfolio Turnover          │ 13.35%        │
│ Drawdown Recovery          │ 33               │                             │               │
└────────────────────────────┴──────────────────┴─────────────────────────────┴───────────────┘
"""
