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
│ Equity                     │ $898,651.40     │ Fees                        │ -$906.49       │
│ Holdings                   │ $934,245.00     │ Net Profit                  │ $563,286.37    │
│ Probabilistic Sharpe Ratio │ 90.965%         │ Return                      │ 199.55 %       │
│ Unrealized                 │ $35,365.03      │ Volume                      │ $30,763,310.00 │
├────────────────────────────┼─────────────────┼─────────────────────────────┼────────────────┤
│ Total Orders               │ 308             │ Average Win                 │ 1.62%          │
│ Average Loss               │ -0.27%          │ Compounding Annual Return   │ 198.654%       │
│ Drawdown                   │ 20.800%         │ Expectancy                  │ 5.181          │
│ Start Equity               │ 300000          │ End Equity                  │ 898651.4       │
│ Net Profit                 │ 199.550%        │ Sharpe Ratio                │ 3.154          │
│ Sortino Ratio              │ 2.795           │ Probabilistic Sharpe Ratio  │ 90.965%        │
│ Loss Rate                  │ 10%             │ Win Rate                    │ 90%            │
│ Profit-Loss Ratio          │ 5.88            │ Alpha                       │ 0              │
│ Beta                       │ 0               │ Annual Standard Deviation   │ 0.396          │
│ Annual Variance            │ 0.157           │ Information Ratio           │ 3.293          │
│ Tracking Error             │ 0.396           │ Treynor Ratio               │ 0              │
│ Total Fees                 │ $906.49         │ Estimated Strategy Capacity │ $98000000.00   │
│ Lowest Capacity Asset      │ CL YOFW7JXIF9A9 │ Portfolio Turnover          │ 15.08%         │
│ Drawdown Recovery          │ 25              │                             │                │
└────────────────────────────┴─────────────────┴─────────────────────────────┴────────────────┘
"""
