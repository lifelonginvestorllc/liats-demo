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
        self.set_end_date(date(2025, 1, 31))

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
            LIConfigKey.gridTrailingOpenPriceFactor: 1.0,
            LIConfigKey.gridInitializeSession: True,  # Be careful!
        }
        investAmount = LIInvestAmount(lotQuantity=1 * amplifier)
        self.liStrategies.append(LIFutureGridTradingContrarian(Futures.Indices.MicroNASDAQ100EMini, investAmount, **configs))


"""
┌────────────────────────────┬──────────────────┬─────────────────────────────┬───────────────┐
│ Statistic                  │ Value            │ Statistic                   │ Value         │
├────────────────────────────┼──────────────────┼─────────────────────────────┼───────────────┤
│ Equity                     │ $218,721.78      │ Fees                        │ -$50.16       │
│ Holdings                   │ $345,144.00      │ Net Profit                  │ $21,238.34    │
│ Probabilistic Sharpe Ratio │ 54.259%          │ Return                      │ 9.36 %        │
│ Unrealized                 │ $-2,516.56       │ Volume                      │ $3,740,510.50 │
├────────────────────────────┼──────────────────┼─────────────────────────────┼───────────────┤
│ Total Orders               │ 94               │ Average Win                 │ 0.45%         │
│ Average Loss               │ -0.04%           │ Compounding Annual Return   │ 42.597%       │
│ Drawdown                   │ 12.600%          │ Expectancy                  │ 6.165         │
│ Start Equity               │ 200000           │ End Equity                  │ 218721.78     │
│ Net Profit                 │ 9.361%           │ Sharpe Ratio                │ 1.12          │
│ Sortino Ratio              │ 1.522            │ Probabilistic Sharpe Ratio  │ 54.259%       │
│ Loss Rate                  │ 40%              │ Win Rate                    │ 60%           │
│ Profit-Loss Ratio          │ 10.94            │ Alpha                       │ 0             │
│ Beta                       │ 0                │ Annual Standard Deviation   │ 0.233         │
│ Annual Variance            │ 0.054            │ Information Ratio           │ 1.356         │
│ Tracking Error             │ 0.233            │ Treynor Ratio               │ 0             │
│ Total Fees                 │ $50.16           │ Estimated Strategy Capacity │ $70000000.00  │
│ Lowest Capacity Asset      │ MNQ YQYHC5L1GPA9 │ Portfolio Turnover          │ 19.16%        │
│ Drawdown Recovery          │ 15               │                             │               │
└────────────────────────────┴──────────────────┴─────────────────────────────┴───────────────┘
"""
