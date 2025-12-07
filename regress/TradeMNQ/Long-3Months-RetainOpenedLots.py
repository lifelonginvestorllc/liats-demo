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

        self.futureGridTrading_Nasdaq_Contrarian()

    def futureGridTrading_Nasdaq_Contrarian(self):
        self.set_cash(200_000)
        self.set_start_date(date(2024, 11, 1))
        self.set_end_date(date(2025, 2, 1))

        amplifier = 1  # Amplify invest amount by n times!
        configs = {
            LIConfigKey.aliasName: "NasdaqTrail",
            LIConfigKey.monitorPeriod: (5 * 12, LIResolution.MINUTE),
            LIConfigKey.liquidateOnStopLossAmount: 100_000 * amplifier,
            LIConfigKey.liquidateOnTakeProfitAmount: 50_000 * amplifier,
            LIConfigKey.gridLongLots: 20,
            LIConfigKey.gridLotLevelPercent: 0.60,
            LIConfigKey.gridLotLevelAugment: 0.015,  # Perform better in a long run with volatile market
            LIConfigKey.gridLotStopLossFactor: 25,
            LIConfigKey.gridLotStopProfitFactors: (0.5, 2),
            LIConfigKey.gridLotPauseAfterStopLoss: False,
            LIConfigKey.gridRetainOpenedLots: 1,
            LIConfigKey.gridInitializeSession: True,  # Be careful!
        }
        investAmount = LIInvestAmount(lotQuantity=1 * amplifier)
        self.liStrategies.append(LIFutureGridTradingContrarian(Futures.Indices.MicroNASDAQ100EMini, investAmount, **configs))


"""
┌────────────────────────────┬──────────────────┬─────────────────────────────┬───────────────┐
│ Statistic                  │ Value            │ Statistic                   │ Value         │
├────────────────────────────┼──────────────────┼─────────────────────────────┼───────────────┤
│ Equity                     │ $214,087.00      │ Fees                        │ -$26.22       │
│ Holdings                   │ $172,572.00      │ Net Profit                  │ $11,172.21    │
│ Probabilistic Sharpe Ratio │ 57.293%          │ Return                      │ 7.04 %        │
│ Unrealized                 │ $2,914.79        │ Volume                      │ $1,956,221.50 │
├────────────────────────────┼──────────────────┼─────────────────────────────┼───────────────┤
│ Total Orders               │ 48               │ Average Win                 │ 0.36%         │
│ Average Loss               │ -0.18%           │ Compounding Annual Return   │ 30.986%       │
│ Drawdown                   │ 7.000%           │ Expectancy                  │ 1.435         │
│ Start Equity               │ 200000           │ End Equity                  │ 214087        │
│ Net Profit                 │ 7.044%           │ Sharpe Ratio                │ 1.071         │
│ Sortino Ratio              │ 1.577            │ Probabilistic Sharpe Ratio  │ 57.293%       │
│ Loss Rate                  │ 19%              │ Win Rate                    │ 81%           │
│ Profit-Loss Ratio          │ 2.01             │ Alpha                       │ 0             │
│ Beta                       │ 0                │ Annual Standard Deviation   │ 0.153         │
│ Annual Variance            │ 0.023            │ Information Ratio           │ 1.431         │
│ Tracking Error             │ 0.153            │ Treynor Ratio               │ 0             │
│ Total Fees                 │ $26.22           │ Estimated Strategy Capacity │ $350000000.00 │
│ Lowest Capacity Asset      │ MNQ YQYHC5L1GPA9 │ Portfolio Turnover          │ 10.32%        │
│ Drawdown Recovery          │ 20               │                             │               │
└────────────────────────────┴──────────────────┴─────────────────────────────┴───────────────┘
"""
