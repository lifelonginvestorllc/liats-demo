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
        # 2024: (225/157.36%/-24.5%); trailingOpenPrice: (257/202.28%/-20.8%)
        self.SetStartDate(date(2024, 1, 1))
        self.SetEndDate(date(2024, 12, 31))

        configs = {
            LIConfigKey.aliasName: "OilBoth",
            LIConfigKey.monitorPeriod: 1,
            LIConfigKey.resolution: LIResolution.HOUR,
            LIConfigKey.futurePeriodDays: 35,
            LIConfigKey.futureRolloverDays: 3,
            LIConfigKey.liquidateOnTakeProfitAmount: 75_000,
            LIConfigKey.liquidateOnStopLossAmount: 150_000,
            LIConfigKey.liquidateLossAndRestartTrading: True,
            LIConfigKey.gridLongLots: 20,  # 20
            LIConfigKey.gridShortLots: 20,  # 20
            LIConfigKey.gridLotLevelPercent: 0.75,
            LIConfigKey.gridLotStopLossFactor: 25,
            LIConfigKey.gridLotStopProfitFactors: (0.5, 2),
            LIConfigKey.gridTrailingOpenPriceFactor: 1,
            LIConfigKey.gridBandingStartPrices: True,
            LIConfigKey.gridBandingOpenFromPrices: True,
            LIConfigKey.bollingerBandsParams: [(365, 1.25)],
            LIConfigKey.gridInitializeSession: True, # Be careful!
        }
        investAmount = LIInvestAmount(lotQuantity=1)
        self.liStrategies.append(LIFutureGridTradingContrarian(Futures.Energies.CrudeOilWTI, investAmount, **configs))


"""
┌────────────────────────────┬─────────────────┬─────────────────────────────┬────────────────┐
│ Statistic                  │ Value           │ Statistic                   │ Value          │
├────────────────────────────┼─────────────────┼─────────────────────────────┼────────────────┤
│ Equity                     │ $879,587.52     │ Fees                        │ -$1,398.02     │
│ Holdings                   │ $1,293,660.00   │ Net Profit                  │ $535,371.98    │
│ Probabilistic Sharpe Ratio │ 90.428%         │ Return                      │ 193.20 %       │
│ Unrealized                 │ $44,215.54      │ Volume                      │ $40,817,250.00 │
├────────────────────────────┼─────────────────┼─────────────────────────────┼────────────────┤
│ Total Orders               │ 275             │ Average Win                 │ 2.65%          │
│ Average Loss               │ -1.45%          │ Compounding Annual Return   │ 192.335%       │
│ Drawdown                   │ 20.800%         │ Expectancy                  │ 1.295          │
│ Start Equity               │ 300000          │ End Equity                  │ 879587.52      │
│ Net Profit                 │ 193.196%        │ Sharpe Ratio                │ 3.109          │
│ Sortino Ratio              │ 2.728           │ Probabilistic Sharpe Ratio  │ 90.428%        │
│ Loss Rate                  │ 19%             │ Win Rate                    │ 81%            │
│ Profit-Loss Ratio          │ 1.82            │ Alpha                       │ 0              │
│ Beta                       │ 0               │ Annual Standard Deviation   │ 0.39           │
│ Annual Variance            │ 0.152           │ Information Ratio           │ 3.25           │
│ Tracking Error             │ 0.39            │ Treynor Ratio               │ 0              │
│ Total Fees                 │ $1398.02        │ Estimated Strategy Capacity │ $260000000.00  │
│ Lowest Capacity Asset      │ CL YPCDYN02Y5KX │ Portfolio Turnover          │ 19.07%         │
└────────────────────────────┴─────────────────┴─────────────────────────────┴────────────────┘
"""
