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
│ Equity                     │ $210,743.07      │ Fees                        │ -$25.65       │
│ Holdings                   │ $172,572.00      │ Net Profit                  │ $7,572.48     │
│ Probabilistic Sharpe Ratio │ 46.240%          │ Return                      │ 5.37 %        │
│ Unrealized                 │ $3,170.59        │ Volume                      │ $2,123,308.00 │
├────────────────────────────┼──────────────────┼─────────────────────────────┼───────────────┤
│ Total Orders               │ 48               │ Average Win                 │ 0.28%         │
│ Average Loss               │ -0.12%           │ Compounding Annual Return   │ 23.058%       │
│ Drawdown                   │ 11.900%          │ Expectancy                  │ 1.699         │
│ Start Equity               │ 200000           │ End Equity                  │ 210743.07     │
│ Net Profit                 │ 5.372%           │ Sharpe Ratio                │ 0.623         │
│ Sortino Ratio              │ 0.675            │ Probabilistic Sharpe Ratio  │ 46.240%       │
│ Loss Rate                  │ 21%              │ Win Rate                    │ 79%           │
│ Profit-Loss Ratio          │ 2.42             │ Alpha                       │ 0             │
│ Beta                       │ 0                │ Annual Standard Deviation   │ 0.192         │
│ Annual Variance            │ 0.037            │ Information Ratio           │ 0.909         │
│ Tracking Error             │ 0.192            │ Treynor Ratio               │ 0             │
│ Total Fees                 │ $25.65           │ Estimated Strategy Capacity │ $340000000.00 │
│ Lowest Capacity Asset      │ MNQ YQYHC5L1GPA9 │ Portfolio Turnover          │ 11.31%        │
│ Drawdown Recovery          │ 13               │                             │               │
└────────────────────────────┴──────────────────┴─────────────────────────────┴───────────────┘
"""
