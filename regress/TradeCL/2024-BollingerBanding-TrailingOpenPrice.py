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

        self.futureGridTrading_Contrarian_Oil()

    def futureGridTrading_Contrarian_Oil(self):
        self.set_cash(300_000)
        self.set_start_date(date(2024, 1, 1))
        self.set_end_date(date(2024, 12, 31))

        amplifier = 1
        configs = {
            LIConfigKey.aliasName: "OilBoth",
            LIConfigKey.monitorPeriod: (1, LIResolution.HOUR),
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
│ Equity                     │ $854,130.54     │ Fees                        │ -$1,247.35     │
│ Holdings                   │ $934,245.00     │ Net Profit                  │ $535,600.51    │
│ Probabilistic Sharpe Ratio │ 92.236%         │ Return                      │ 184.71 %       │
│ Unrealized                 │ $18,530.03      │ Volume                      │ $36,214,510.00 │
├────────────────────────────┼─────────────────┼─────────────────────────────┼────────────────┤
│ Total Orders               │ 261             │ Average Win                 │ 1.94%          │
│ Average Loss               │ -0.46%          │ Compounding Annual Return   │ 183.897%       │
│ Drawdown                   │ 20.400%         │ Expectancy                  │ 2.984          │
│ Start Equity               │ 300000          │ End Equity                  │ 854130.54      │
│ Net Profit                 │ 184.710%        │ Sharpe Ratio                │ 3.225          │
│ Sortino Ratio              │ 2.564           │ Probabilistic Sharpe Ratio  │ 92.236%        │
│ Loss Rate                  │ 24%             │ Win Rate                    │ 76%            │
│ Profit-Loss Ratio          │ 4.22            │ Alpha                       │ 0              │
│ Beta                       │ 0               │ Annual Standard Deviation   │ 0.352          │
│ Annual Variance            │ 0.124           │ Information Ratio           │ 3.381          │
│ Tracking Error             │ 0.352           │ Treynor Ratio               │ 0              │
│ Total Fees                 │ $1247.35        │ Estimated Strategy Capacity │ $9400000.00    │
│ Lowest Capacity Asset      │ CL YOFW7JXIF9A9 │ Portfolio Turnover          │ 17.77%         │
│ Drawdown Recovery          │ 37              │                             │                │
└────────────────────────────┴─────────────────┴─────────────────────────────┴────────────────┘
"""
