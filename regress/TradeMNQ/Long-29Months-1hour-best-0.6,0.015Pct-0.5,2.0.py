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

        self.futureGridTrading_Contrarian_Nasdaq()

    def futureGridTrading_Contrarian_Nasdaq(self):
        self.SetCash(300_000)
        # 2021 annual performance: short(328/-71.86%/-85.2%); long(313/101.89%/-26.8%)
        # self.SetStartDate(date(2021, 1, 1))
        # self.SetEndDate(date(2021, 12, 31))
        # 2022 annual performance: short(1035/90.41%/-35.3%); long(386/-86.43%/-90.1%)
        # self.SetStartDate(date(2022, 1, 1))
        # self.SetEndDate(date(2022, 12, 31))
        # 2023 annual performance: short(253/-89.81%/-94.8%); long(364/108.3%/-19.8%)
        # self.SetStartDate(date(2023, 1, 1))
        # self.SetEndDate(date(2023, 12, 31))
        # 2024 annual performance: short(274/-15.16%/-62.2%); long(324/78.27%/-50.9%)
        self.SetStartDate(date(2024, 1, 1))
        # self.SetEndDate(date(2024, 12, 31))
        # self.SetStartDate(date(2024, 12, 31))
        self.SetEndDate(date(2025, 6, 1))
        # self.SetStartDate(date(2024, 7, 1))
        # self.SetEndDate(date(2024, 8, 15))
        # A small wave for 1 month
        # self.SetStartDate(date(2024, 7, 22))
        # self.SetEndDate(date(2024, 8, 22))
        # self.SetStartDate(date(2025, 2, 15))
        # self.SetEndDate(date(2025, 5, 15))
        # self.SetStartDate(date(2024, 1, 1))
        # self.SetEndDate(date(2025, 2, 15))
        # self.SetEndDate(date(2025, 5, 15))
        # self.SetStartDate(datetime.now() - timedelta(days=365))
        # self.SetEndDate(datetime.now())

        # Summary: Based on last 4 years performance, still need to predict bearish/bullish market

        amplifier = 2  # Amplify invest amount by n times!
        configs = {
            LIConfigKey.aliasName: "NasdaqTrail",
            # LIConfigKey.monitorPeriod: 5 * 3,  # 5 * 3,
            LIConfigKey.monitorPeriod: 1,  # 5 * 3,
            LIConfigKey.resolution: LIResolution.HOUR,
            # LIConfigKey.futureContractExpiry: date(2025, 6, 20),
            # LIConfigKey.closeWithStopOrderType: True,
            # LIConfigKey.openWithMarketOrderType: False,
            # LIConfigKey.closeWithMarketOrderType: False,
            # Better to liquidate at some point to exit one side of trading
            LIConfigKey.liquidateOnStopLossAmount: 100_000 * amplifier,  # 100_000 * amplifier,
            # LIConfigKey.liquidateLossAndLimitTrading: True,
            LIConfigKey.liquidateLossAndRestartTrading: True,
            # Adjust it dynamically based on current market trend/volatility and paired strategy's profit loss!
            LIConfigKey.liquidateOnTakeProfitAmount: 50_000 * amplifier,  # 50_000 * amplifier,
            # LIConfigKey.gridNoMoreOpenOrders: True,
            LIConfigKey.gridLongLots: 20,
            # LIConfigKey.gridShortLots: 20,
            LIConfigKey.gridLotLevelPercent: 0.6,  # 0.60,
            LIConfigKey.gridLotLevelAugment: 0.015,  # Perform better in a long run with volatile market
            LIConfigKey.gridLotStopLossFactor: 25,
            LIConfigKey.gridLotStopProfitFactors: (0.5, 2),
            LIConfigKey.gridLotPauseAfterStopLoss: False,
            LIConfigKey.gridRestartIfAllLotsPaused: False,
            LIConfigKey.gridCancelOrdersAfterClosed: True,
            LIConfigKey.gridTrailingOpenPriceFactor: 1.0,  # Fill back open orders eagerly! Enable for clear market trend!
            # LIConfigKey.gridRetainOpenedLots: 2,
            # LIConfigKey.gridRealignOpenPositions: True,
            # LIConfigKey.gridHedgeEnabled: True,
            # LIConfigKey.gridHedgeOverLosingLots: 5,
            # LIConfigKey.gridFollowAdverseTrend: True,
            LIConfigKey.gridInitializeSession: True,  # Be careful!
        }
        investAmount = LIInvestAmount(lotQuantity=1 * amplifier)
        self.liStrategies.append(LIFutureGridTradingContrarian(Futures.Indices.MicroNASDAQ100EMini, investAmount, **configs))

"""
┌────────────────────────────┬──────────────────┬─────────────────────────────┬────────────────┐
│ Statistic                  │ Value            │ Statistic                   │ Value          │
├────────────────────────────┼──────────────────┼─────────────────────────────┼────────────────┤
│ Equity                     │ $636,839.76      │ Fees                        │ -$918.84       │
│ Holdings                   │ $854,750.00      │ Net Profit                  │ $328,718.49    │
│ Probabilistic Sharpe Ratio │ 46.228%          │ Return                      │ 112.28 %       │
│ Unrealized                 │ $8,121.27        │ Volume                      │ $63,020,728.00 │
├────────────────────────────┼──────────────────┼─────────────────────────────┼────────────────┤
│ Total Orders               │ 678              │ Average Win                 │ 0.47%          │
│ Average Loss               │ -1.62%           │ Compounding Annual Return   │ 69.969%        │
│ Drawdown                   │ 43.400%          │ Expectancy                  │ 0.171          │
│ Start Equity               │ 300000           │ End Equity                  │ 636839.76      │
│ Net Profit                 │ 112.280%         │ Sharpe Ratio                │ 1.114          │
│ Sortino Ratio              │ 1.355            │ Probabilistic Sharpe Ratio  │ 46.228%        │
│ Loss Rate                  │ 9%               │ Win Rate                    │ 91%            │
│ Profit-Loss Ratio          │ 0.29             │ Alpha                       │ 0              │
│ Beta                       │ 0                │ Annual Standard Deviation   │ 0.531          │
│ Annual Variance            │ 0.282            │ Information Ratio           │ 1.218          │
│ Tracking Error             │ 0.531            │ Treynor Ratio               │ 0              │
│ Total Fees                 │ $918.84          │ Estimated Strategy Capacity │ $990000000.00  │
│ Lowest Capacity Asset      │ MNQ YTG30NVEFCW1 │ Portfolio Turnover          │ 26.06%         │
└────────────────────────────┴──────────────────┴─────────────────────────────┴────────────────┘
"""
