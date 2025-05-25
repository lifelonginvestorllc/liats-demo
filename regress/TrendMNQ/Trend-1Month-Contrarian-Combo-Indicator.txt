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

        self.futureGridTrading_Nasdaq_Contrarian_Indicator()

    def futureGridTrading_Nasdaq_Contrarian_Indicator(self):
        self.SetCash(50_000)
        # MES: (119/3.32%/-4.9%); MNQ: (115/13.46%/-6.9%)
        self.SetStartDate(date(2025, 4, 1))
        self.SetEndDate(date(2025, 5, 1))

        amplifier = 1  # Amplify invest amount by n times!
        configs = {
            LIConfigKey.aliasName: "NasdaqTrend",
            # LIConfigKey.verbose: True,
            LIConfigKey.monitorPeriod: 5,
            LIConfigKey.indicatorPeriod: 60,
            # LIConfigKey.extendedMarketHours: True,
            LIConfigKey.extendDataBarStream: True,  # True for MES; False for MNQ
            LIConfigKey.openWithMarketOrderType: False,
            LIConfigKey.closeWithMarketOrderType: False,
            # LIConfigKey.closeWithStopOrderType: True,
            LIConfigKey.heikinAshiPlies: 3,
            LIConfigKey.gridUseTradeInsight: True,
            LIConfigKey.gridLongLots: 2,  # 8
            LIConfigKey.gridShortLots: 2,  # 6
            LIConfigKey.gridLotLevelPercent: 0.6,
            LIConfigKey.gridLotStopLossFactor: 3,  # 2
            LIConfigKey.gridLotTakeProfitFactor: 20,  # 4
            LIConfigKey.stochasticComboParams: {LIIndicator.EMA: 100,
                                                LIIndicator.RSI: 14,
                                                LIIndicator.ATR: (30, 2),
                                                LIIndicator.MACD: (12, 26, 5),
                                                LIIndicator.KDJ: (14, 3, 3, 80, 20),
                                                LIIndicator.SRSI: (14, 14, 3, 3, 90, 10)},
            LIConfigKey.gridInitializeSession: True,  # Be careful!
        }

        investAmount = LIInvestAmount(lotQuantity=1 * amplifier)
        self.liStrategies.append(LIFutureGridTradingContrarian(Futures.Indices.MICRO_NASDAQ_100_E_MINI, investAmount, **configs))


"""
┌────────────────────────────┬──────────────────┬─────────────────────────────┬────────────────┐
│ Statistic                  │ Value            │ Statistic                   │ Value          │
├────────────────────────────┼──────────────────┼─────────────────────────────┼────────────────┤
│ Equity                     │ $66,904.32       │ Fees                        │ -$155.04       │
│ Holdings                   │ $79,910.00       │ Net Profit                  │ $16,762.46     │
│ Probabilistic Sharpe Ratio │ 91.419%          │ Return                      │ 33.81 %        │
│ Unrealized                 │ $141.86          │ Volume                      │ $10,247,151.50 │
├────────────────────────────┼──────────────────┼─────────────────────────────┼────────────────┤
│ Total Orders               │ 289              │ Average Win                 │ 1.33%          │
│ Average Loss               │ -0.51%           │ Compounding Annual Return   │ 2984.956%      │
│ Drawdown                   │ 15.700%          │ Expectancy                  │ 0.487          │
│ Start Equity               │ 50000            │ End Equity                  │ 66904.32       │
│ Net Profit                 │ 33.809%          │ Sharpe Ratio                │ 29.584         │
│ Sortino Ratio              │ 36.852           │ Probabilistic Sharpe Ratio  │ 91.419%        │
│ Loss Rate                  │ 59%              │ Win Rate                    │ 41%            │
│ Profit-Loss Ratio          │ 2.61             │ Alpha                       │ 0              │
│ Beta                       │ 0                │ Annual Standard Deviation   │ 0.603          │
│ Annual Variance            │ 0.363            │ Information Ratio           │ 29.675         │
│ Tracking Error             │ 0.603            │ Treynor Ratio               │ 0              │
│ Total Fees                 │ $155.04          │ Estimated Strategy Capacity │ $33000000.00   │
│ Lowest Capacity Asset      │ MNQ YTG30NVEFCW1 │ Portfolio Turnover          │ 560.31%        │
└────────────────────────────┴──────────────────┴─────────────────────────────┴────────────────┘
"""
