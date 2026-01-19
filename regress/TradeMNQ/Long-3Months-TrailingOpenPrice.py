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
│ Equity                     │ $206,169.47      │ Fees                        │ -$40.47       │
│ Holdings                   │ $345,144.00      │ Net Profit                  │ $9,009.32     │
│ Probabilistic Sharpe Ratio │ 36.920%          │ Return                      │ 3.08 %        │
│ Unrealized                 │ $-2,839.85       │ Volume                      │ $3,471,861.50 │
├────────────────────────────┼──────────────────┼─────────────────────────────┼───────────────┤
│ Total Orders               │ 77               │ Average Win                 │ 0.46%         │
│ Average Loss               │ -0.07%           │ Compounding Annual Return   │ 12.804%       │
│ Drawdown                   │ 20.700%          │ Expectancy                  │ 2.307         │
│ Start Equity               │ 200000           │ End Equity                  │ 206169.47     │
│ Net Profit                 │ 3.085%           │ Sharpe Ratio                │ 0.284         │
│ Sortino Ratio              │ 0.274            │ Probabilistic Sharpe Ratio  │ 36.920%       │
│ Loss Rate                  │ 56%              │ Win Rate                    │ 44%           │
│ Profit-Loss Ratio          │ 6.44             │ Alpha                       │ 0             │
│ Beta                       │ 0                │ Annual Standard Deviation   │ 0.319         │
│ Annual Variance            │ 0.102            │ Information Ratio           │ 0.456         │
│ Tracking Error             │ 0.319            │ Treynor Ratio               │ 0             │
│ Total Fees                 │ $40.47           │ Estimated Strategy Capacity │ $70000000.00  │
│ Lowest Capacity Asset      │ MNQ YQYHC5L1GPA9 │ Portfolio Turnover          │ 18.23%        │
│ Drawdown Recovery          │ 7                │                             │               │
└────────────────────────────┴──────────────────┴─────────────────────────────┴───────────────┘
"""
