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

        self.futureGridTrading_Contrarian_Nasdaq_Long()

    def futureGridTrading_Contrarian_Nasdaq_Long(self):
        self.SetCash(500_000)
        self.SetStartDate(date(2024, 8, 5))
        self.SetEndDate(date(2025, 4, 30))

        amplifier = 1  # Amplify invest amount by n times!
        configs = {
            # LIConfigKey.verbose: True,
            LIConfigKey.aliasName: "NasdaqLong",
            LIConfigKey.monitorPeriod: 5 * 12,
            # LIConfigKey.monitorPeriod: 1,
            # LIConfigKey.resolution: LIResolution.HOUR, # Performs worse than 60 mins
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
            # LIConfigKey.gridBandingStartPrices: True,
            # LIConfigKey.gridBandingOpenFromPrices: True,
            # LIConfigKey.bollingerBandsParams: [(365, 1)],
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
│ Equity                     │ $659,658.90     │ Fees                        │ -$116.10       │
│ Holdings                   │ $0.00           │ Net Profit                  │ $159,658.90    │
│ Probabilistic Sharpe Ratio │ 48.046%         │ Return                      │ 31.93 %        │
│ Unrealized                 │ $0.00           │ Volume                      │ $22,072,375.00 │
├────────────────────────────┼─────────────────┼─────────────────────────────┼────────────────┤
│ Total Orders               │ 38              │ Average Win                 │ 7.62%          │
│ Average Loss               │ -7.54%          │ Compounding Annual Return   │ 45.646%        │
│ Drawdown                   │ 18.000%         │ Expectancy                  │ 0.508          │
│ Start Equity               │ 500000          │ End Equity                  │ 659658.9       │
│ Net Profit                 │ 31.932%         │ Sharpe Ratio                │ 0.882          │
│ Sortino Ratio              │ 0.942           │ Probabilistic Sharpe Ratio  │ 48.046%        │
│ Loss Rate                  │ 25%             │ Win Rate                    │ 75%            │
│ Profit-Loss Ratio          │ 1.01            │ Alpha                       │ 0              │
│ Beta                       │ 0               │ Annual Standard Deviation   │ 0.27           │
│ Annual Variance            │ 0.073           │ Information Ratio           │ 1.086          │
│ Tracking Error             │ 0.27            │ Treynor Ratio               │ 0              │
│ Total Fees                 │ $116.10         │ Estimated Strategy Capacity │ $670000000.00  │
│ Lowest Capacity Asset      │ NQ YQYHC5L1GPA9 │ Portfolio Turnover          │ 12.75%         │
└────────────────────────────┴─────────────────┴─────────────────────────────┴────────────────┘
"""
