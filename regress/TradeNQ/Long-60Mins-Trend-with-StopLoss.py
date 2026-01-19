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

        self.futureGridTrading_Contrarian_Nasdaq_Long()

    def futureGridTrading_Contrarian_Nasdaq_Long(self):
        self.set_cash(500_000)
        self.set_start_date(date(2024, 8, 5))
        self.set_end_date(date(2025, 4, 30))

        amplifier = 1  # Amplify invest amount by n times!
        configs = {
            # LIConfigKey.verbose: True,
            LIConfigKey.aliasName: "NasdaqLong",
            LIConfigKey.monitorPeriod: (5 * 12, LIResolution.MINUTE),
            # LIConfigKey.monitorPeriod: (1, LIResolution.HOUR),
            # LIConfigKey.futureContractCode: "MNQ20Z24",
            # LIConfigKey.futureContractExpiry: date(2025, 3, 21),
            # LIConfigKey.closeWithStopOrderType: True,
            LIConfigKey.liquidateOnStopLossAmount: 100_000 * amplifier,
            # LIConfigKey.liquidateLossAndRestartTrading: True,
            # Adjust it dynamically based on current market trend/volatility and paired momentum strategy's profit loss!
            LIConfigKey.liquidateOnTakeProfitAmount: 50_000 * amplifier,
            # LIConfigKey.gridNoMoreCloseOrders: True,
            LIConfigKey.gridLongLots: 5,
            LIConfigKey.gridLotLevelPercent: 2,
            LIConfigKey.gridLotLevelAugment: 0.015,  # Perform better in a long run with volatile market
            LIConfigKey.gridLotStopLossFactor: 6,
            LIConfigKey.gridLotTakeProfitFactor: 2,
            LIConfigKey.gridLotStopProfitFactors: (0.5, 2),
            LIConfigKey.gridLotPauseAfterStopLoss: True,
            # LIConfigKey.gridTrailingOpenPriceFactor: 1.0,
            LIConfigKey.gridRetainOpenedLots: 1,
            # LIConfigKey.gridRealignOpenPositions: True,
            LIConfigKey.gridInitializeSession: True,  # Be careful!
        }
        investAmount = LIInvestAmount(lotQuantity=1 * amplifier)
        self.liStrategies.append(LIFutureGridTradingContrarian(Futures.Indices.NASDAQ100EMini, investAmount, **configs))


"""
┌────────────────────────────┬─────────────────┬─────────────────────────────┬────────────────┐
│ Statistic                  │ Value           │ Statistic                   │ Value          │
├────────────────────────────┼─────────────────┼─────────────────────────────┼────────────────┤
│ Equity                     │ $648,901.50     │ Fees                        │ -$86.00        │
│ Holdings                   │ $0.00           │ Net Profit                  │ $148,901.50    │
│ Probabilistic Sharpe Ratio │ 44.289%         │ Return                      │ 29.78 %        │
│ Unrealized                 │ $0.00           │ Volume                      │ $17,927,157.50 │
├────────────────────────────┼─────────────────┼─────────────────────────────┼────────────────┤
│ Total Orders               │ 36              │ Average Win                 │ 7.26%          │
│ Average Loss               │ -7.36%          │ Compounding Annual Return   │ 42.433%        │
│ Drawdown                   │ 15.900%         │ Expectancy                  │ 0.490          │
│ Start Equity               │ 500000          │ End Equity                  │ 648901.5       │
│ Net Profit                 │ 29.780%         │ Sharpe Ratio                │ 0.783          │
│ Sortino Ratio              │ 0.8             │ Probabilistic Sharpe Ratio  │ 44.289%        │
│ Loss Rate                  │ 25%             │ Win Rate                    │ 75%            │
│ Profit-Loss Ratio          │ 0.99            │ Alpha                       │ 0              │
│ Beta                       │ 0               │ Annual Standard Deviation   │ 0.286          │
│ Annual Variance            │ 0.082           │ Information Ratio           │ 0.975          │
│ Tracking Error             │ 0.286           │ Treynor Ratio               │ 0              │
│ Total Fees                 │ $86.00          │ Estimated Strategy Capacity │ $430000000.00  │
│ Lowest Capacity Asset      │ NQ YQYHC5L1GPA9 │ Portfolio Turnover          │ 10.35%         │
│ Drawdown Recovery          │ 49              │                             │                │
└────────────────────────────┴─────────────────┴─────────────────────────────┴────────────────┘
"""
