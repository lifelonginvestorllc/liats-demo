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
│ Equity                     │ $650,096.80     │ Fees                        │ -$103.20       │
│ Holdings                   │ $0.00           │ Net Profit                  │ $150,096.80    │
│ Probabilistic Sharpe Ratio │ 45.466%         │ Return                      │ 30.02 %        │
│ Unrealized                 │ $0.00           │ Volume                      │ $19,561,480.00 │
├────────────────────────────┼─────────────────┼─────────────────────────────┼────────────────┤
│ Total Orders               │ 38              │ Average Win                 │ 7.26%          │
│ Average Loss               │ -7.20%          │ Compounding Annual Return   │ 42.789%        │
│ Drawdown                   │ 14.700%         │ Expectancy                  │ 0.507          │
│ Start Equity               │ 500000          │ End Equity                  │ 650096.8       │
│ Net Profit                 │ 30.019%         │ Sharpe Ratio                │ 0.808          │
│ Sortino Ratio              │ 0.84            │ Probabilistic Sharpe Ratio  │ 45.466%        │
│ Loss Rate                  │ 25%             │ Win Rate                    │ 75%            │
│ Profit-Loss Ratio          │ 1.01            │ Alpha                       │ 0              │
│ Beta                       │ 0               │ Annual Standard Deviation   │ 0.275          │
│ Annual Variance            │ 0.076           │ Information Ratio           │ 1.007          │
│ Tracking Error             │ 0.275           │ Treynor Ratio               │ 0              │
│ Total Fees                 │ $103.20         │ Estimated Strategy Capacity │ $530000000.00  │
│ Lowest Capacity Asset      │ NQ YQYHC5L1GPA9 │ Portfolio Turnover          │ 11.40%         │
│ Drawdown Recovery          │ 49              │                             │                │
└────────────────────────────┴─────────────────┴─────────────────────────────┴────────────────┘
"""
