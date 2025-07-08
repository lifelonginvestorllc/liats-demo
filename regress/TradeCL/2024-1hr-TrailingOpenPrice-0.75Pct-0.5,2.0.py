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

        self.futureGridTrading_Contrarian_Oil()

    def futureGridTrading_Contrarian_Oil(self):
        self.SetCash(300_000)
        self.SetStartDate(date(2024, 1, 1))
        self.SetEndDate(date(2024, 12, 31))

        amplifier = 1
        configs = {
            LIConfigKey.aliasName: "OilBoth",
            # LIConfigKey.verbose: True,
            # LIConfigKey.monitorPeriod: 5 * 3,
            LIConfigKey.monitorPeriod: 1,
            LIConfigKey.resolution: LIResolution.HOUR,
            LIConfigKey.futurePeriodDays: 35,
            LIConfigKey.futureRolloverDays: 3,
            LIConfigKey.liquidateOnStopLossAmount: 150_000 * amplifier,
            # LIConfigKey.liquidateLossAndRestartTrading: True,
            LIConfigKey.liquidateOnTakeProfitAmount: 75_000 * amplifier,
            LIConfigKey.gridLongLots: 20,  # 20
            LIConfigKey.gridShortLots: 20,  # 20
            LIConfigKey.gridLotLevelPercent: 0.75,
            LIConfigKey.gridLotStopLossFactor: 25,
            LIConfigKey.gridLotStopProfitFactors: (0.5, 2),
            LIConfigKey.gridTrailingOpenPriceFactor: 1,
            # Enable banding open from price for both sides contrarian
            LIConfigKey.gridBandingStartPrices: {LIGridSide.BTD: "band-#0-middle", LIGridSide.STU: "band-#0-middle"},
            LIConfigKey.gridBandingOpenFromPrices: {LIGridSide.BTD: "band-#1-lower", LIGridSide.STU: "band-#1-upper"},
            LIConfigKey.bollingerBandsParams: [(365, 1.25), (365, 2.5)],
            LIConfigKey.investAmountTierFactors: [0, 1, 0, 0, 1, 0],
            LIConfigKey.gridInitializeSession: True,  # Be careful!
        }

        investAmount = LIInvestAmount(lotQuantity=1 * amplifier)
        self.liStrategies.append(LIFutureGridTradingContrarian(Futures.Energies.CrudeOilWTI, investAmount, **configs))


"""
┌────────────────────────────┬─────────────────┬─────────────────────────────┬────────────────┐
│ Statistic                  │ Value           │ Statistic                   │ Value          │
├────────────────────────────┼─────────────────┼─────────────────────────────┼────────────────┤
│ Equity                     │ $889,916.44     │ Fees                        │ -$1,304.16     │
│ Holdings                   │ $1,437,400.00   │ Net Profit                  │ $559,105.84    │
│ Probabilistic Sharpe Ratio │ 91.091%         │ Return                      │ 196.64 %       │
│ Unrealized                 │ $30,810.60      │ Volume                      │ $38,124,930.00 │
├────────────────────────────┼─────────────────┼─────────────────────────────┼────────────────┤
│ Total Orders               │ 251             │ Average Win                 │ 2.62%          │
│ Average Loss               │ -1.23%          │ Compounding Annual Return   │ 195.759%       │
│ Drawdown                   │ 21.400%         │ Expectancy                  │ 1.600          │
│ Start Equity               │ 300000          │ End Equity                  │ 889916.44      │
│ Net Profit                 │ 196.639%        │ Sharpe Ratio                │ 3.181          │
│ Sortino Ratio              │ 2.736           │ Probabilistic Sharpe Ratio  │ 91.091%        │
│ Loss Rate                  │ 17%             │ Win Rate                    │ 83%            │
│ Profit-Loss Ratio          │ 2.14            │ Alpha                       │ 0              │
│ Beta                       │ 0               │ Annual Standard Deviation   │ 0.385          │
│ Annual Variance            │ 0.149           │ Information Ratio           │ 3.323          │
│ Tracking Error             │ 0.385           │ Treynor Ratio               │ 0              │
│ Total Fees                 │ $1304.16        │ Estimated Strategy Capacity │ $9400000.00    │
│ Lowest Capacity Asset      │ CL YOFW7JXIF9A9 │ Portfolio Turnover          │ 18.14%         │
└────────────────────────────┴─────────────────┴─────────────────────────────┴────────────────┘
"""
